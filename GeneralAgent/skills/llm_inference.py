# from retrying import retry as _retry
# from tenacity import retry, stop_after_attempt, wait_fixed

class TinyDBCache():
    def __init__(self):
        from tinydb import TinyDB
        import os, json
        llm_path = os.environ.get('CACHE_PATH', None)
        if llm_path is None:
            from GeneralAgent.utils import get_server_dir
            llm_path = os.path.join(get_server_dir(), 'cache.json')
        self.db = TinyDB(llm_path)

    @property
    def cache_llm(self):
        import os
        return os.environ.get('LLM_CACHE', 'no') in ['yes', 'y', 'YES']
    
    @property
    def cache_embedding(self):
        import os
        return os.environ.get('EMBEDDING_CACHE', 'no') in ['yes', 'y', 'YES']

    def get(self, table, key):
        from tinydb import Query
        result = self.db.table(table).get(Query().key == key)
        if result is not None:
            return result['value']
        else:
            return None

    def set(self, table, key, value):
        from tinydb import Query
        self.db.table(table).upsert({'key': key, 'value': value}, Query().key == key)

    def set_llm_cache(self, key, value):
        if self.cache_llm:
            self.set('llm', key, value)

    def get_llm_cache(self, key):
        if self.cache_llm:
            return self.get('llm', key)
    
    def set_embedding_cache(self, key, value):
        if self.cache_embedding:
            self.set('embedding', key, value)

    def get_embedding_cache(self, key):
        if self.cache_embedding:
            return self.get('embedding', key)


global_cache = TinyDBCache()


def embedding_single(text) -> [float]:
    """
    embedding the text and return a embedding (list of float) for the string
    """
    global global_cache
    key = _md5(text)
    embedding = global_cache.get_embedding_cache(key)
    if embedding is not None:
        # print('embedding cache hitted')
        return embedding
    texts = [text]
    from litellm import embedding
    resp = embedding(model = _get_embedding_model(),
                     input=texts
                     )
    result = [x['embedding'] for x in resp['data']]
    embedding = result[0]
    global_cache.set_embedding_cache(key, embedding)
    return embedding


def test_embedding_single():
    size = None
    from GeneralAgent.utils import EnvironmentVariableManager
    with EnvironmentVariableManager('EMBEDDING_CACHE', 'no'):
        for source_type in ['OPENAI', 'AZURE']:
            with EnvironmentVariableManager('LLM_SOURCE', source_type):
                result = embedding_single("Say this is a test")
                # print(source_type, result)
                if size is not None:
                    assert len(result) == size
                size = len(result)

def test_embedding_batch():
    size = None
    from GeneralAgent.utils import EnvironmentVariableManager
    with EnvironmentVariableManager('EMBEDDING_CACHE', 'no'):
        for source_type in ['OPENAI', 'AZURE']:
            with EnvironmentVariableManager('LLM_SOURCE', source_type):
                result = embedding_batch(["Say this is a test"])
                if size is not None:
                    assert len(result[0]) == size
                size = len(result[0])


def embedding_batch(texts) -> [[float]]:
    """
    embedding the texts(list of string), and return a list of embedding (list of float) for every string
    """
    global global_cache
    embeddings = {}
    remain_texts = []
    for text in texts:
        key = _md5(text)
        embedding = global_cache.get_embedding_cache(key)
        if embedding is not None:
            embeddings[text] = embedding
        else:
            remain_texts.append(text)
    if len(remain_texts) > 0:
        result = _embedding_many(remain_texts)
        for text, embedding in zip(remain_texts, result):
            key = _md5(text)
            global_cache.set_embedding_cache(key, embedding)
            embeddings[text] = embedding
    return [embeddings[text] for text in texts]


def _embedding_many(texts) -> [[float]]:
    from litellm import embedding
    # 每次最多embedding 16个
    max_batch_size = 16
    result = []
    for i in range(0, len(texts), max_batch_size):
        resp = embedding(model=_get_embedding_model(),input=texts[i:i+max_batch_size])
        result += [x['embedding'] for x in resp['data']]
    return result


def cos_sim(a, b):
    import numpy as np
    from numpy.linalg import norm
    # This function calculates the cosine similarity (scalar value) between two input vectors 'a' and 'b' (1-D array object), and return the similarity.
    a = a if isinstance(a, np.ndarray) else np.array(a)
    b = b if isinstance(b, np.ndarray) else np.array(b)
    return np.dot(a, b)/(norm(a)*norm(b))


def search_similar_texts(focal:str, texts:[str], top_k=5):
    """
    search the most similar texts in texts, and return the top_k similar texts
    """
    embeddings = embedding_batch([focal] + texts)
    focal_embedding = embeddings[0]
    texts_embeddings = embeddings[1:]
    import numpy as np
    similarities = np.dot(texts_embeddings, focal_embedding)
    sorted_indices = np.argsort(similarities)
    sorted_indices = sorted_indices[::-1]
    return [texts[i] for i in sorted_indices[:top_k]]


def _md5(obj):
    import hashlib, json
    if isinstance(obj, str):
        return hashlib.md5(obj.encode('utf-8')).hexdigest()
    else:
        return hashlib.md5(json.dumps(obj).encode('utf-8')).hexdigest()


def _get_llm_model(messages, model_type):
    import os
    from GeneralAgent import skills
    assert model_type in ['normal', 'smart', 'long', 'vision']
    if model_type == 'normal' and skills.messages_token_count(messages) > 3000:
        model_type = 'long'
    api_type = os.environ.get('LLM_SOURCE', 'OPENAI')
    model_key = f'{api_type}_LLM_MODEL_{model_type.upper()}'
    model = os.environ.get(model_key, None)
    if model is not None:
        return model
    model_key = f'{api_type}_LLM_MODEL_NORMAL'
    return os.environ.get(model_key, 'gpt-3.5-turbo')


def get_llm_token_limit(model_type='smart'):
    """
    return the token limit for the model
    """
    import os
    assert model_type in ['normal', 'smart', 'long']
    api_type = os.environ.get('LLM_SOURCE', 'OPENAI')
    # OPENAI_LLM_MODEL_SMART_LIMIT
    limit_key = f'{api_type}_LLM_MODEL_{model_type.upper()}_LIMIT'
    limit = os.environ.get(limit_key, None)
    if limit is not None:
        return int(limit)
    limit_key = f'{api_type}_LLM_MODEL_NORMAL_LIMIT'
    return int(os.environ.get(limit_key, 4000))


def test_get_llm_token_limit():
    from GeneralAgent.utils import EnvironmentVariableManager
    with EnvironmentVariableManager('LLM_SOURCE', 'OPENAI'):
        with EnvironmentVariableManager('OPENAI_LLM_MODEL_SMART_LIMIT', '8000'):
            assert get_llm_token_limit('smart') == 8000


def _get_embedding_model():
    import os
    api_type = os.environ.get('LLM_SOURCE', 'OPENAI')
    embedding_model = os.environ.get(f'{api_type}_EMBEDDING_MODEL', 'text-embedding-ada-002')
    return embedding_model

def _get_temperature():
    import os
    temperature = float(os.environ.get('LLM_TEMPERATURE', 0.5))
    return temperature


def llm_inference(messages, model_type='normal', stream=False, json_schema=None):
    """
    Run LLM (large language model) inference on the provided messages using the specified model.
    
    Parameters:
    messages: Input messages for the model, like [{'role': 'system', 'content': 'You are a helpful assistant'}, {'role': 'user', 'content': 'What is your name?'}]
    model_type: Type of model to use. Options are 'normal', 'smart', 'long'
    use_stream: Boolean indicating if the function should use streaming inference
    json_format: Optional JSON schema string

    Returns:
    If use_stream is True, returns a generator that yields the inference results as they become available.
    If use_stream is False, returns a string containing the inference result.
    If json_format is provided, the inference result is parsed according to the provided JSON schema and returned as a dictionary.

    Note:
    The total number of tokens in the messages and the returned string must be less than 4000 when model_variant is 'normal', and less than 16000 when model_variant is 'long'.
    """
    import logging
    messages = messages.copy()
    messages[-1] = messages[-1].copy()
#     messages[-1]['content'] = messages[-1]['content'] + """
# Take a deep breath
# I have no fingers
# I will tip $200
# Do it right and i'll give you a nice doggy treat.
# """
    if stream:
        return _llm_inference_with_stream(messages, model_type)
    else:
        if json_schema is None:
            return _llm_inference_without_stream(messages, model_type)    
        else:
            import json
            if not isinstance(json_schema, str):
                json_schema = json.dumps(json_schema)
            messages[-1]['content'] += '\n' + return_json_prompt + json_schema
            # messages += [{'role': 'user', 'content': return_json_prompt + json_schema}]
            logging.debug(messages)
            result = _llm_inference_without_stream(messages, model_type)
            logging.debug(result)
            return json.loads(fix_llm_json_str(result))


def test_llm_inference():
    from GeneralAgent.utils import EnvironmentVariableManager
    with EnvironmentVariableManager('LLM_CACHE', 'no'):
        for source_type in ['OPENAI', 'AZURE']:
            with EnvironmentVariableManager('LLM_SOURCE', source_type):
                model_types = ['normal', 'smart', 'long']
                for model_type in model_types:
                    result = llm_inference([{"role": "user","content": "Say this is a test",}], model_type=model_type, stream=False)
                    print(source_type, model_type, result)
                    assert 'test' in result
                    result = ''
                    response = llm_inference([{"role": "user","content": "Say this is a test",}], model_type=model_type, stream=True)
                    for token in response:
                        result += token
                    print(source_type, model_type, result)
                    assert 'test' in result


def llm_inference_to_json(messages, json_schema):
    """
    Run LLM (large language model) inference on the provided messages and parse the result according to the provided JSON schema.
    
    Parameters:
    messages: Input messages for the model, like [{'role': 'system', 'content': 'You are a helpful assistant'}, {'role': 'user', 'content': 'What is your name?'}]
    json_format: Optional JSON schema string

    Returns:
    If json_format is provided, the inference result is parsed according to the provided JSON schema and returned as a dictionary.
    Else return a string

    Note:
    The total number of tokens in the messages and the returned string must be less than 16000.
    """
    from GeneralAgent import skills
    return skills.llm_inference(messages, json_schema=json_schema)


# @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def _llm_inference_with_stream(messages, model_type='normal'):
    """
    messages: llm messages, model_type: normal, smart, long
    """
    from litellm import completion
    import logging
    # from GeneralAgent import skills
    model = _get_llm_model(messages, model_type)
    logging.debug(messages)
    global global_cache
    key = _md5(messages)
    result = global_cache.get_llm_cache(key)
    if result is not None:
        # print('llm_inference cache hitted')
        for x in result.split(' '):
            yield x + ' '
        yield '\n'
        # yield None
    else:
        temperature = _get_temperature()
        try_count = 3
        while try_count > 0:
            try:
                response = completion(model=model, messages=messages, stream=True, temperature=temperature)
                result = ''
                for chunk in response:
                    # print(chunk)
                    if chunk['choices'][0]['finish_reason'] is None:
                        token = chunk['choices'][0]['delta']['content']
                        if token is None:
                            continue
                        result += token
                        global_cache.set_llm_cache(key, result)
                        yield token
                break
            except Exception as e:
                try_count -= 1
                import time
                time.sleep(3)
            if try_count == 0:
                raise ValueError('LLM(Large Languate Model) error, Please check your key or base_url, or network')
        # logging.info(result)
        # yield None

# if we choose to use local llm for inferce, we can use the following completion function.
#def compeltion(model,messages,temperature):
#    pass


# @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def _llm_inference_without_stream(messages, model_type='normal'):
    from litellm import completion
    import logging
    global global_cache
    logging.debug(messages)
    # print(messages)
    key = _md5(messages)
    result = global_cache.get_llm_cache(key)
    if result is not None:
        return result
    model = _get_llm_model(messages, model_type)
    temperature = _get_temperature()
    try_count = 3
    while try_count > 0:
        try:
            response = completion(model=model, messages=messages, temperature=temperature)
            result = response['choices'][0]['message']['content']
            global_cache.set_llm_cache(key, result)
            return result
        except Exception as e:
            try_count -= 1
            import time
            time.sleep(3)
        if try_count == 0:
                raise ValueError('LLM(Large Languate Model) error, Please check your key or base_url, or network')
    return ''


def fix_llm_json_str(string):
    import json
    import re
    new_string = string.strip()
    if new_string.startswith('```json'):
        new_string = new_string[7:]
        if new_string.endswith('```'):
            new_string = new_string[:-3]
    try:
        json.loads(new_string)
        return new_string
    except Exception as e:
        print("fix_llm_json_str failed 1:", e)
        try:
            pattern = r'```json(.*?)```'
            match = re.findall(pattern, new_string, re.DOTALL)
            if match:
                new_string = match[-1]
            
            json.loads(new_string)
            return new_string
        except Exception as e:
            print("fix_llm_json_str failed 2:", e)
            try:
                new_string = new_string.replace("\n", "\\n")
                json.loads(new_string)
                return new_string
            except Exception as e:
                print("fix_llm_json_str failed 3:", e)
                
                messages = [{
                    "role": "system",
                    "content": """Do not change the specific content, fix the json, directly return the repaired JSON, without any explanation and dialogue.
                    ```
                    """+new_string+"""
                    ```"""
                }]

                message = llm_inference(messages)
                pattern = r'```json(.*?)```'
                match = re.findall(pattern, message, re.DOTALL)
                if match:
                    return match[-1]

                return message

return_json_prompt = """\n\nYou should only directly respond in JSON format without explian as described below, that must be parsed by Python json.loads.
Response JSON schema: \n"""


# def prompt_call(prompt_template, variables, json_schema=None):
#     from jinja2 import Template
#     import json
#     prompt = Template(prompt_template).render(**variables)
#     if json_schema is not None:
#         prompt += return_json_prompt + json_schema
#         result = llm_inference([{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role': 'system', 'content': prompt}], model_type='smart')
#         return json.loads(fix_llm_json_str(result))
#     else:
#         result = llm_inference([{'role': 'system', 'content': prompt}], model_type='smart')

if __name__ == '__main__':
    test_embedding_single()