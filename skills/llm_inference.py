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


# @retry(stop_max_attempt_number=3)
# def llm_inference(messages, model=None):
#     if model is None:
#         model = os.environ.get('OPENAI_API_MODEL', 'gpt-3.5-turbo')
#     temperature = float(os.environ.get('TEMPERATURE', 0.5))
#     # print(messages)
#     response = openai.ChatCompletion.create(model=model, messages=messages, stream=True, temperature=temperature)
#     result = ''
#     for chunk in response:
#         if chunk['choices'][0]['finish_reason'] is None:
#             token = chunk['choices'][0]['delta']['content']
#             # print(token)
#             result += token
#             yield token
#     logging.info(result)


@retry(stop_max_attempt_number=3)
def llm_inference(messages, model_type='normal'):
    """
    messages: llm messages
    model_type: normal, smart, long
    """
    from skills import skills

    # set model
    assert model_type in ['normal', 'smart', 'long']
    if model_type == 'normal' and skills.messages_token_count(messages) > 3000:
        model_type = 'long'
    model = os.environ.get('OPENAI_API_MODEL', 'gpt-3.5-turbo')
    if model_type == 'smart':
        model = 'gpt-4'
    if model_type == 'long':
        model = 'gpt-3.5-turbo-16k'

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
        # yield None
    else:
        temperature = float(os.environ.get('TEMPERATURE', 0.5))
        response = openai.ChatCompletion.create(model=model, messages=messages, stream=True, temperature=temperature)
        result = ''
        for chunk in response:
            if chunk['choices'][0]['finish_reason'] is None:
                token = chunk['choices'][0]['delta']['content']
                result += token
                global_cache.set(table, key, result)
                yield token
        # logging.info(result)
        # yield None


@retry(stop_max_attempt_number=3)
async def async_llm_inference(messages, model=None):
    global global_cache
    table = 'llm'
    key = md5(messages)
    result = global_cache.get(table, key)
    if result is not None:
        return result
    if model is None:
        model = os.environ.get('OPENAI_API_MODEL', 'gpt-3.5-turbo')
    temperature = float(os.environ.get('TEMPERATURE', 0.5))
    response = await openai.ChatCompletion.acreate(model=model, messages=messages, temperature=temperature)
    result = response['choices'][0]['message']['content']
    global_cache.set(table, key, result)
    return result