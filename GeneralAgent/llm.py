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
from GeneralAgent.keys import OPENAI_MODEL, OPENAI_API_KEY, OPENAI_ORGANIZATION, OPENAI_API_BASE

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
        return hashlib.md5(json.dumps(string, sort_keys=True).encode('utf-8')).hexdigest()
    

llm_cache = TinyDBCache('./llm_cache.json')


def _llm_inference_messages(messages):
    model = OPENAI_MODEL or 'gpt-3.5-turbo-16k'
    openai.api_key = OPENAI_API_KEY
    if model.startswith('gpt-4'):
        openai.organization = OPENAI_ORGANIZATION
    openai.api_base = OPENAI_API_BASE or 'https://api.openai.com/v1'
    response = openai.ChatCompletion.create(model=model, messages=messages)
    result = response['choices'][0]['message']['content'].strip()
    
    print('-' * 50 + 'llm_inference_messages' + '-' * 50)
    for message in messages:
        print(f'[{message["role"]}] {message["content"]}')
    print(f'[response] {result}')
    
    return result



def llm_inference_messages(messages, force_run=False):
    if not force_run:
        key = md5(messages)
        result = llm_cache.get(key)
        if result is not None:
            return result
    result = _llm_inference_messages(messages)
    llm_cache.set(key, result)
    return result



def llm_inference(prompt, force_run):
    # 缓存
    system_prompt = [{"role": "system", "content": 'You are a helpful assistant.'}]
    messages = system_prompt + [{"role": "user", "content": prompt}]
    return llm_inference_messages(messages, force_run=force_run)

def _translate_eng(text, force_run=False):
    system_prompt = [{"role": "system", "content": f"You are a translator, translate the user's input to english. Do not translate the text {{{{}}}}"}]
    messages = system_prompt + [{"role": "user", "content": text}]
    result = llm_inference_messages(messages, force_run=force_run)
    return result

def is_english(text):
    """Check if a string is an English string."""
    import string
    # Remove all whitespace characters
    text = ''.join(text.split())
    # Check if all characters are in the ASCII range
    if all(ord(c) < 128 for c in text):
        # Check if the string contains any non-English characters
        for c in text:
            if c not in string.ascii_letters and c not in string.punctuation and c not in string.digits and c not in string.whitespace:
                return False
        return True
    else:
        return False


def translate_eng(text):
    # 如果是英文，返回原文，不缓存
    if is_english(text):
        return text
    else:
        en = _translate_eng(text, force_run=False)
        retry_count = 0
        while retry_count < 3 and re.findall(r'{{.*?}}', text) != re.findall(r'{{.*?}}', en):
            en = _translate_eng(text, force_run=True)
            retry_count += 1
        if re.findall(r'{{.*?}}', text) != re.findall(r'{{.*?}}', en):
            raise Exception(f"translate_eng failed: {text} -> {en}")
        return en


def fix_llm_json_str(string):
    new_string = string.strip()
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
                
                ctx = [{
                    "role": "system",
                    "content": """Do not change the specific content, fix the json, directly return the repaired JSON, without any explanation and dialogue.
                    ```
                    """+new_string+"""
                    ```"""
                }]

                message = llm_inference_messages(ctx, force_run=True)
                pattern = r'```json(.*?)```'
                match = re.findall(pattern, message, re.DOTALL)
                if match:
                    return match[-1]

                return message

return_json_prompt = """\n\nYou should only directly respond in JSON format without explian as described below, that must be parsed by Python json.loads.
Response Format example: \n"""

def prompt_call(prompt, variables, json_schema=None, force_run=False):
    # 通过prompt将大模型异化成为函数，并可以通过json_schema返回格式化数据
    prompt = translate_eng(prompt)
    prompt = Template(prompt).render(**variables)
    if json_schema is not None:
        prompt += return_json_prompt + json_schema
        result = llm_inference(prompt, force_run=force_run)
        return json.loads(fix_llm_json_str(result))
    else:
        return llm_inference(prompt, force_run=force_run)


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