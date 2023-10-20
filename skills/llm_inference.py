import os
import openai
import logging
from retrying import retry
import time

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