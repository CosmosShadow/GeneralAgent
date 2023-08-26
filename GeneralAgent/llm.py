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

