# 大语言模型
import openai
import os
import json
from jinja2 import Template

def llm_inference_messages(messages):
    model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo-16k')
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    if model.startswith('gpt-4'):
        openai.organization = os.environ.get('OPENAI_ORGANIZATION')
    openai.api_base = os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
    response = openai.ChatCompletion.create(model=model, messages=messages)
    result = response['choices'][0]['message']['content'].strip()
    return result

def llm_inference(prompt):
    system_prompt = [{"role": "system", "content": 'You are a helpful assistant.'}]
    messages = system_prompt + [{"role": "user", "content": prompt}]
    return llm_inference_messages(messages)


def embedding_fun(texts):
    import os
    import openai
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    openai.api_base = os.environ['OPENAI_API_BASE', 'https://api.openai.com/v1']
    resp = openai.Embedding.create(input=texts,engine="text-embedding-ada-002")
    result = [x['embedding'] for x in resp['data']]
    return result

def translate_eng(text):
    system_prompt = [{"role": "system", "content": f"You are a translator, translate the following text to english."}]
    messages = system_prompt + [{"role": "user", "content": text}]
    return llm_inference_messages(messages)

cached_dict = {}
def cache_translate_eng(text):
    if text in cached_dict.keys():
        return cached_dict[text]
    else:
        # TODO: check {{}} 是匹配的
        result = translate_eng(text)
        cached_dict[text] = result
        return result

# def wrape_prompt_to_function(prompt, variables, return_chema):

#     def wrapped_function(text):
#         system_prompt = [{"role": "system", "content": prompt}]
#         messages = system_prompt + [{"role": "user", "content": text}]
#         return function(messages)
#     return wrapped_function

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