import os
import json
import openai
import numpy as np
from tinydb import TinyDB, Query
from numpy.linalg import norm
import logging
from retrying import retry

class TinyDBCache():
    def __init__(self):
        LLM_CACHE = os.environ.get('LLM_CACHE', 'no')
        if LLM_CACHE in ['yes', 'y', 'YES']:
            LLM_CACHE_PATH = os.environ.get('LLM_CACHE_PATH', './llm_cache.json')
            self.db = TinyDB(LLM_CACHE_PATH)
        else:
            self.db = None

    def get(self, table, key):
        if self.db is None:
            return None
        result = self.db.table(table).get(Query().key == key)
        if result is not None:
            return result['value']
        else:
            return None

    def set(self, table, key, value):
        if self.db is None:
            return
        self.db.table(table).upsert({'key': key, 'value': value}, Query().key == key)


global_cache = TinyDBCache()


def md5(obj):
    import hashlib
    if isinstance(obj, str):
        return hashlib.md5(obj.encode('utf-8')).hexdigest()
    else:
        return hashlib.md5(json.dumps(obj).encode('utf-8')).hexdigest()


def embedding_fun(text):
    # embedding the texts(list of string), and return a list of embedding for every string
    global global_cache
    table = 'embedding'
    key = md5(text)
    embedding = global_cache.get(table, key)
    if embedding is not None:
        # print('embedding cache hitted')
        return embedding
    texts = [text]
    import openai
    resp = openai.Embedding.create(input=texts,engine="text-embedding-ada-002")
    result = [x['embedding'] for x in resp['data']]
    embedding = result[0]
    global_cache.set(table, key, embedding)
    return embedding


@retry(stop_max_attempt_number=3)
def _embedding_batch(texts):
    import openai
    resp = openai.Embedding.create(input=texts, engine="text-embedding-ada-002")
    embeddings = [x['embedding'] for x in resp['data']]
    return embeddings


def embedding_batch(texts):
    results = []
    for index in range(0, len(texts), 100):
        embeddings = _embedding_batch(texts[index:index+100])
        results += embeddings
    return results

def cos_sim(a, b):
    # This function calculates the cosine similarity (scalar value) between two input vectors 'a' and 'b' (1-D array object), and return the similarity.
    a = a if isinstance(a, np.ndarray) else np.array(a)
    b = b if isinstance(b, np.ndarray) else np.array(b)
    return np.dot(a, b)/(norm(a)*norm(b))

def string_token_count(str):
    """Calculate and return the token count in a given string."""
    import tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(str)
    return len(tokens)

def num_tokens_from_messages(messages):
    "Calculate and return the total number of tokens in the provided messages."
    import tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens_per_message = 4
    tokens_per_name = 1
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens