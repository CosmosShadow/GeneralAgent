
def _get_openai_client():
    from openai import OpenAI
    import os
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_API_BASE'], max_retries=3)
    return client


def embedding_texts(texts) -> [[float]]:
    """
    对文本数组进行embedding
    """
    client = _get_openai_client()
    # 每次最多embedding 16个
    max_batch_size = 16
    result = []
    for i in range(0, len(texts), max_batch_size):
        resp = client.embeddings.create(input=texts[i:i+max_batch_size], model=_get_embedding_model())
        result += [x['embedding'] for x in resp['data']]
    return result


def cos_sim(a, b):
    import numpy as np
    from numpy.linalg import norm
    a = a if isinstance(a, np.ndarray) else np.array(a)
    b = b if isinstance(b, np.ndarray) else np.array(b)
    return np.dot(a, b)/(norm(a)*norm(b))


def search_similar_texts(focal:str, texts:[str], top_k=5):
    """
    search the most similar texts in texts, and return the top_k similar texts
    """
    embeddings = embedding_texts([focal] + texts)
    focal_embedding = embeddings[0]
    texts_embeddings = embeddings[1:]
    import numpy as np
    similarities = np.dot(texts_embeddings, focal_embedding)
    sorted_indices = np.argsort(similarities)
    sorted_indices = sorted_indices[::-1]
    return [texts[i] for i in sorted_indices[:top_k]]


def _get_llm_model(model_type):
    import os
    assert model_type in ['normal', 'smart', 'long', 'vision']
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


def _get_embedding_model():
    import os
    api_type = os.environ.get('LLM_SOURCE', 'OPENAI')
    embedding_model = os.environ.get(f'{api_type}_EMBEDDING_MODEL', 'text-embedding-ada-002')
    return embedding_model

def _get_temperature():
    import os
    temperature = float(os.environ.get('LLM_TEMPERATURE', 0.5))
    return temperature


def llm_inference(messages, model_type='normal', stream=False):
    """
    Run LLM (large language model) inference on the provided messages using the specified model.
    
    Parameters:
    messages: Input messages for the model, like [{'role': 'system', 'content': 'You are a helpful assistant'}, {'role': 'user', 'content': 'What is your name?'}]
    model_type: Type of model to use. Options are 'normal', 'smart', 'long'
    stream: Boolean indicating if the function should use streaming inference

    Returns:
    If stream is True, returns a generator that yields the inference results as they become available.
    If stream is False, returns a string containing the inference result.

    Note:
    The total number of tokens in the messages and the returned string must be less than 4000 when model_variant is 'normal', and less than 16000 when model_variant is 'long'.
    """
    import logging
    logging.debug(messages)
    if stream:
        return _llm_inference_with_stream(messages, model_type)
    else:
        return _llm_inference_without_stream(messages, model_type)


def _llm_inference_with_stream(messages, model_type='normal'):
    import logging
    client = _get_openai_client()
    model = _get_llm_model(model_type)
    temperature = _get_temperature()
    try:
        response = client.chat.completions.create(messages=messages, model=model, stream=True, temperature=temperature)
        for chunk in response:
            if len(chunk.choices) > 0:
                token = chunk.choices[0].delta.content
                if token is None:
                    continue
                yield token
    except Exception as e:
        logging.exception(e)
        raise ValueError('LLM(Large Languate Model) error, Please check your key or base_url, or network')


def _llm_inference_without_stream(messages, model_type='normal'):
    import logging
    client = _get_openai_client()
    model = _get_llm_model(model_type)
    temperature = _get_temperature()
    try:
        response = client.chat.completions.create(messages=messages, model=model, stream=False, temperature=temperature)
        result = response.choices[0].message.content
        return result
    except Exception as e:
        logging.exception(e)
        raise ValueError('LLM(Large Languate Model) error, Please check your key or base_url, or network')