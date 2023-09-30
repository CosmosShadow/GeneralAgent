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
            self.db = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), './cache.json'))
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


@retry(stop_max_attempt_number=3)
def llm_inference(messages):
    logging.debug(messages)
    global global_cache
    table = 'llm'
    key = md5(messages)
    result = global_cache.get(table, key)
    if result is not None:
        print('llm_inference cache hitted')
        for x in result.split(' '):
            yield x + ' '
        yield '\n'
        yield None
    else:
        model = os.environ.get('OPENAI_API_MODEL', 'gpt-3.5-turbo')
        response = openai.ChatCompletion.create(model=model, messages=messages, stream=True)
        result = ''
        for chunk in response:
            try:
                token = chunk['choices'][0]['delta']['content']
                # print(token, end='', flush=True)
                result += token
                global_cache.set(table, key, result)
                yield token
            except Exception as e:
                pass
        logging.info(result)
        yield None


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

def cos_sim(a, b):
    # This function calculates the cosine similarity (scalar value) between two input vectors 'a' and 'b' (1-D array object), and return the similarity.
    a = a if isinstance(a, np.ndarray) else np.array(a)
    b = b if isinstance(b, np.ndarray) else np.array(b)
    return np.dot(a, b)/(norm(a)*norm(b))

def num_tokens_from_string(str):
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