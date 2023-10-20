import os
import json
import openai
import numpy as np
from numpy.linalg import norm
import logging
from retrying import retry


def md5(obj):
    import hashlib
    if isinstance(obj, str):
        return hashlib.md5(obj.encode('utf-8')).hexdigest()
    else:
        return hashlib.md5(json.dumps(obj).encode('utf-8')).hexdigest()


@retry(stop_max_attempt_number=3)
def llm_inference(messages):
    logging.debug(messages)
    model = os.environ.get('OPENAI_API_MODEL', 'gpt-3.5-turbo')
    temperature = float(os.environ.get('TEMPERATURE', 0.5))
    response = openai.ChatCompletion.create(model=model, messages=messages, stream=True, temperature=temperature)
    result = ''
    for chunk in response:
        if chunk['choices'][0]['finish_reason'] is None:
            token = chunk['choices'][0]['delta']['content']
            result += token
            yield token
    yield None

@retry(stop_max_attempt_number=3)
async def async_llm_inference(messages):
    # logging.debug(messages)
    model = os.environ.get('OPENAI_API_MODEL', 'gpt-3.5-turbo')
    temperature = float(os.environ.get('TEMPERATURE', 0.5))
    response = await openai.ChatCompletion.acreate(model=model, messages=messages, temperature=temperature)
    return response['choices'][0]['message']['content']

def embedding_fun(text):
    # embedding the texts(list of string), and return a list of embedding for every string
    texts = [text]
    import openai
    resp = openai.Embedding.create(input=texts,engine="text-embedding-ada-002")
    result = [x['embedding'] for x in resp['data']]
    embedding = result[0]
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