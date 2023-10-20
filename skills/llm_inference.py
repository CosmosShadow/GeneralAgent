import os
import openai
import logging
from retrying import retry

@retry(stop_max_attempt_number=3)
def llm_inference(messages, model=None):
    if model is None:
        model = os.environ.get('OPENAI_API_MODEL', 'gpt-3.5-turbo')
    temperature = float(os.environ.get('TEMPERATURE', 0.5))
    response = openai.ChatCompletion.create(model=model, messages=messages, stream=True, temperature=temperature)
    result = ''
    for chunk in response:
        if chunk['choices'][0]['finish_reason'] is None:
            token = chunk['choices'][0]['delta']['content']
            # print(token)
            result += token
            yield token
    logging.info(result)


@retry(stop_max_attempt_number=3)
async def async_llm_inference(messages):
    model = os.environ.get('OPENAI_API_MODEL', 'gpt-3.5-turbo')
    temperature = float(os.environ.get('TEMPERATURE', 0.5))
    response = await openai.ChatCompletion.acreate(model=model, messages=messages, temperature=temperature)
    return response['choices'][0]['message']['content']