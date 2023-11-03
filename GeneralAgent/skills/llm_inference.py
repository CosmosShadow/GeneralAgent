from retrying import retry as _retry

class TinyDBCache():
    def __init__(self):
        from tinydb import TinyDB
        import os, json
        LLM_CACHE = os.environ.get('LLM_CACHE', 'no')
        if LLM_CACHE in ['yes', 'y', 'YES']:
            LLM_CACHE_PATH = os.environ.get('LLM_CACHE_PATH', './llm_cache.json')
            self.db = TinyDB(LLM_CACHE_PATH)
        else:
            self.db = None

    def get(self, table, key):
        from tinydb import Query
        if self.db is None:
            return None
        result = self.db.table(table).get(Query().key == key)
        if result is not None:
            return result['value']
        else:
            return None

    def set(self, table, key, value):
        from tinydb import Query
        if self.db is None:
            return
        self.db.table(table).upsert({'key': key, 'value': value}, Query().key == key)


global_cache = TinyDBCache()


def _md5(obj):
    import hashlib, json
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


def _get_model(messages, model_type):
    import os
    from GeneralAgent import skills
    assert model_type in ['normal', 'smart', 'long']
    if model_type == 'normal' and skills.messages_token_count(messages) > 3000:
        model_type = 'long'
    model = os.environ.get('OPENAI_API_MODEL', 'gpt-3.5-turbo')
    if model_type == 'smart':
        model = 'gpt-4'
    if model_type == 'long':
        model = 'gpt-3.5-turbo-16k'
    return model

def _get_temperature():
    import os
    temperature = float(os.environ.get('TEMPERATURE', 0.5))
    return temperature


@_retry(stop_max_attempt_number=3)
def llm_inference(messages, model_type='normal'):
    """
    messages: llm messages, model_type: normal, smart, long
    """
    import openai
    import logging
    # from GeneralAgent import skills
    model = _get_model(messages, model_type)
    logging.debug(messages)
    global global_cache
    table = 'llm'
    key = _md5(messages)
    result = global_cache.get(table, key)
    if result is not None:
        # print('llm_inference cache hitted')
        for x in result.split(' '):
            yield x + ' '
        yield '\n'
        # yield None
    else:
        temperature = _get_temperature()
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


@_retry(stop_max_attempt_number=3)
async def async_llm_inference(messages, model_type='normal'):
    import openai
    import logging
    global global_cache
    table = 'llm'
    logging.debug(messages)
    key = _md5(messages)
    result = global_cache.get(table, key)
    if result is not None:
        return result
    model = _get_model(messages, model_type)
    temperature = _get_temperature()
    response = await openai.ChatCompletion.acreate(model=model, messages=messages, temperature=temperature)
    result = response['choices'][0]['message']['content']
    global_cache.set(table, key, result)
    return result

@_retry(stop_max_attempt_number=3)
def sync_llm_inference(messages, model_type='normal'):
    import openai
    import logging
    global global_cache
    table = 'llm'
    logging.debug(messages)
    # print(messages)
    key = _md5(messages)
    result = global_cache.get(table, key)
    if result is not None:
        return result
    model = _get_model(messages, model_type)
    temperature = _get_temperature()
    response = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature)
    result = response['choices'][0]['message']['content']
    global_cache.set(table, key, result)
    return result


@_retry(stop_max_attempt_number=3)
def llm(prompt, model_type='normal'):
    """
    large language model to reason. prompt: llm prompt, model_type: normal, smart, long
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": prompt}]
    result = ''
    for x in llm_inference(messages, model_type):
        result += x
    return result