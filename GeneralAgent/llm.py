# 大语言模型
import openai
import os

def llm_inference(messages):
    model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo-16k')
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    if model.startswith('gpt-4'):
        openai.organization = os.environ.get('OPENAI_ORGANIZATION')
    openai.api_base = os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
    response = openai.ChatCompletion.create(model=model, messages=messages)
    result = response['choices'][0]['message']['content'].strip()
    return result

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
    return llm_inference(messages)

cached_dict = {}
def cache_translate_eng(text):
    if text in cached_dict.keys():
        return cached_dict[text]
    else:
        result = translate_eng(text)
        cached_dict[text] = result
        return result

