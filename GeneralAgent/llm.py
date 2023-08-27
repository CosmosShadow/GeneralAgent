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

def llm_inference_messages(messages):
    model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo-16k')
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    if model.startswith('gpt-4'):
        openai.organization = os.environ.get('OPENAI_ORGANIZATION')
    openai.api_base = os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
    response = openai.ChatCompletion.create(model=model, messages=messages)
    result = response['choices'][0]['message']['content'].strip()
    
    if os.environ['REVERSE'] == '1':
        print('-' * 50 + 'llm_inference_messages' + '-' * 50)
        for message in messages:
            print(f'[{message["role"]}] {message["content"]}')
        print(f'[response] {result}')
    
    return result

def llm_inference(prompt):
    system_prompt = [{"role": "system", "content": 'You are a helpful assistant.'}]
    messages = system_prompt + [{"role": "user", "content": prompt}]
    return llm_inference_messages(messages)

def translate_eng(text):
    system_prompt = [{"role": "system", "content": f"You are a translator, translate the user's input to english. Do not translate the text {{{{}}}}"}]
    messages = system_prompt + [{"role": "user", "content": text}]
    result = llm_inference_messages(messages)
    return result


prompt_en_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompt_en.json')
prompt_db = TinyDB(prompt_en_path)

def cache_translate_eng(text):
    # 缓存翻译英文
    result = prompt_db.get(Query().text == text)
    if result is not None:
        return result['en']
    else:
        en = translate_eng(text)
        retry_count = 0
        while retry_count < 3 and re.findall(r'{{.*?}}', text) != re.findall(r'{{.*?}}', en):
            en = translate_eng(text)
            retry_count += 1
        if re.findall(r'{{.*?}}', text) != re.findall(r'{{.*?}}', en):
            raise Exception(f"translate_eng failed: {text} -> {en}")
        prompt_db.insert({'text': text, 'en': en})
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

                message = llm_inference_messages(ctx)
                pattern = r'```json(.*?)```'
                match = re.findall(pattern, message, re.DOTALL)
                if match:
                    return match[-1]

                return message

return_json_prompt = """\n\nYou should only directly respond in JSON format without explian as described below, that must be parsed by Python json.loads.
Response Format example: \n"""

def prompt_call(prompt, variables, json_schema=None):
    # 通过prompt将大模型异化成为函数，并可以通过json_schema返回格式化数据
    prompt = cache_translate_eng(prompt)
    prompt = Template(prompt).render(**variables)
    if json_schema is not None:
        prompt += return_json_prompt + json_schema
        result = llm_inference(prompt)
        return json.loads(fix_llm_json_str(result))
    else:
        return llm_inference(prompt)


def embedding_fun(texts):
    # embedding the texts(list of string), and return a list of embedding for every string
    import os
    import openai
    openai.api_key = os.environ['OPENAI_API_KEY']
    openai.api_base = os.environ['OPENAI_API_BASE']
    resp = openai.Embedding.create(input=texts,engine="text-embedding-ada-002")
    result = [x['embedding'] for x in resp['data']]
    return result

def cos_sim(a, b): 
    # This function calculates the cosine similarity (scalar value) between two input vectors 'a' and 'b' (1-D array object), and return the similarity.
    return dot(a, b)/(norm(a)*norm(b))