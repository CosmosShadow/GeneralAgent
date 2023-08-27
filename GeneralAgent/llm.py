# 大语言模型
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
    system_prompt = [{"role": "system", "content": f"You are a translator, translate the following text to english. Do not translate the text in the curly braces."}]
    messages = system_prompt + [{"role": "user", "content": text}]
    return llm_inference_messages(messages)


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


def prompt_call(prompt, variables, json_schema=None):
    prompt_en = cache_translate_eng("你是一个翻译官，将下面的文本翻译成为{{target}}: {{text}}")
    prompt = Template(prompt_en).render(**variables)
    if json_schema is not None:
        prompt += json_schema
    result = llm_inference(prompt)
    if json_schema is None:
        return result
    else:
        # TODO: fix json
        return json.loads(result)


def translate(text, target):
    prompt = "你是一个翻译官，将下面的文本翻译成为{{target}}: {{text}}"
    variables = {'target': target, 'text': text}
    # TODO: 修改return schema
    json_schema = """\n return in json."""
    return prompt_call(prompt, variables, json_schema)


def embedding_fun(texts):
    import os
    import openai
    openai.api_key = os.environ['OPENAI_API_KEY']
    openai.api_base = os.environ['OPENAI_API_BASE']
    resp = openai.Embedding.create(input=texts,engine="text-embedding-ada-002")
    result = [x['embedding'] for x in resp['data']]
    return result

def cos_sim(a, b): 
  """
  This function calculates the cosine similarity (scalar value) between two input vectors 'a' and 'b', and return the similarity.
  INPUT: 
    a: 1-D array object 
    b: 1-D array object 
  """
  return dot(a, b)/(norm(a)*norm(b))