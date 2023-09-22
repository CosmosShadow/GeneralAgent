# 大语言模型
# 核心是: prompt_call、embedding_fun、cos_sim 这三个函数
import openai
import os
import json
from jinja2 import Template
from tinydb import TinyDB, Query
import re
from numpy import dot
from numpy.linalg import norm
from GeneralAgent.keys import OPENAI_API_KEY, OPENAI_API_BASE
import logging

class TinyDBCache():
    def __init__(self, save_path):
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), save_path)
        self.db = TinyDB(save_path)

    def get(self, key, table_name='default'):
        result = self.db.table(table_name).get(Query().key == key)
        if result is not None:
            return result['value']
        else:
            return None

    def set(self, key, value, table_name='default'):
        self.db.table(table_name).upsert({'key': key, 'value': value}, Query().key == key)

# 计算一个字符串或者对象(json.dumps)的MD5，如果不是字符串，先json.dumps
def md5(string):
    import hashlib
    if isinstance(string, str):
        return hashlib.md5(string.encode('utf-8')).hexdigest()
    else:
        return hashlib.md5(json.dumps(string).encode('utf-8')).hexdigest()


llm_cache = TinyDBCache('./llm_cache.json')


def _llm_inference_messages(messages, think_deep=False):
    if think_deep:
        model = 'gpt-4'
    else:
        model = 'gpt-3.5-turbo'

    logging.info('\n' + '-' * 50 + f'<{model}>' + '-' * 50)
    for message in messages:
        logging.info(f'[{message["role"]}] {message["content"]}')

    openai.api_key = OPENAI_API_KEY
    # if model.startswith('gpt-4'):
    #     openai.organization = OPENAI_ORGANIZATION
    openai.api_base = OPENAI_API_BASE or 'https://api.openai.com/v1'
    response = openai.ChatCompletion.create(model=model, messages=messages)
    # logging.info(response)
    result = response['choices'][0]['message']['content'].strip()
    
    logging.info(f'[response] {result}')
    logging.info('-' * 50 + f'</{model}>' + '-' * 50 + '\n')
    
    return result



def llm_inference_messages(messages, force_run=False, think_deep=False):
    key = md5(messages)
    if not force_run:
        result = llm_cache.get(key)
        if result is not None:
            logging.info(f'cache {key} hitted')
            return result
        else:
            logging.info('no cache hitted')
    logging.info('key: ', key)
    result = _llm_inference_messages(messages, think_deep=think_deep)
    llm_cache.set(key, result)
    return result


def llm_inference(prompt, force_run, think_deep=False):
    # 缓存
    system_prompt = [{"role": "system", "content": 'You are a helpful assistant.'}]
    messages = system_prompt + [{"role": "user", "content": prompt}]
    return llm_inference_messages(messages, force_run=force_run, think_deep=think_deep)

def fix_llm_json_str(string):
    new_string = string.strip()
    try:
        json.loads(new_string)
        return new_string
    except Exception as e:
        logging.info("fix_llm_json_str failed 1:", e)
        try:
            pattern = r'```json(.*?)```'
            match = re.findall(pattern, new_string, re.DOTALL)
            if match:
                new_string = match[-1]
            
            json.loads(new_string)
            return new_string
        except Exception as e:
            logging.info("fix_llm_json_str failed 2:", e)
            try:
                new_string = new_string.replace("\n", "\\n")
                json.loads(new_string)
                return new_string
            except Exception as e:
                logging.info("fix_llm_json_str failed 3:", e)
                content = f"""Do not change the specific content, fix the json, directly return the repaired JSON (can be load by json.loads in Python), without any explanation and dialogue.\n```\n{new_string}\ n```"""
                ctx = [{"role": "system", "content": content}]

                message = llm_inference_messages(ctx, force_run=False)
                pattern = r'```json(.*?)```'
                match = re.findall(pattern, message, re.DOTALL)
                if match:
                    return match[-1]

                return message

return_json_prompt = """\n\nAttention: You should only directly respond in JSON format without explian as described below, that must be parsed by Python json.loads.
Response Format example: \n"""

def prompt_call(prompt, variables, json_schema=None, force_run=False, think_deep=False):
    # 通过prompt将大模型异化成为函数，并可以通过json_schema返回格式化数据
    prompt = Template(prompt).render(**variables)
    if json_schema is not None:
        prompt += return_json_prompt + json_schema.strip()
        result = llm_inference(prompt, force_run=force_run, think_deep=think_deep)
        return json.loads(fix_llm_json_str(result))
    else:
        return llm_inference(prompt, force_run=force_run, think_deep=think_deep)


embedding_cache = TinyDBCache('./embedding_cache.json')
def embedding_fun(text):
    # embedding the texts(list of string), and return a list of embedding for every string
    embedding = embedding_cache.get(text)
    if embedding is not None:
        return embedding
    texts = [text]
    import openai
    openai.api_key = OPENAI_API_KEY
    openai.api_base = OPENAI_API_BASE
    resp = openai.Embedding.create(input=texts,engine="text-embedding-ada-002")
    result = [x['embedding'] for x in resp['data']]
    embedding = result[0]
    embedding_cache.set(text, embedding)
    return embedding

def cos_sim(a, b): 
    # This function calculates the cosine similarity (scalar value) between two input vectors 'a' and 'b' (1-D array object), and return the similarity.
    return dot(a, b)/(norm(a)*norm(b))

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