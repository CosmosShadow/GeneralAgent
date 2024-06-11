
def _get_openai_client(api_key=None, base_url=None):
    from openai import OpenAI
    import os
    if api_key is None and 'OPENAI_API_KEY' not in os.environ:
        raise ValueError('Please set OPENAI_API_KEY in environment')
    api_key = api_key or os.environ['OPENAI_API_KEY']
    base_url = base_url or os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
    client = OpenAI(api_key=api_key, base_url=base_url, max_retries=3)
    return client


def embedding_texts(texts) -> [[float]]:
    """
    对文本数组进行embedding
    """
    import os
    client = _get_openai_client()
    model = os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-small')
    resp = client.embeddings.create(input=texts, model=model)
    result = [x.embedding for x in resp.data]
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


def get_llm_token_limit(model):
    """
    return the token limit for the model
    """
    if 'gpt-3.5' in model:
        return 16 * 1000
    if 'gpt-4' in model:
        return 128 * 1000
    return 16 * 1000


def llm_inference(messages, model='gpt-4o', stream=False, temperature=None, api_key=None, base_url=None):
    """
    Run LLM (large language model) inference on the provided messages using the specified model.
    
    @messages: Input messages for the model, like [{'role': 'system', 'content': 'You are a helpful assistant'}, {'role': 'user', 'content': 'What is your name?'}]
    @model: Type of model to use. Options are 'normal', 'smart', 'long'
    @stream: Boolean indicating if the function should use streaming inference
    @temperature: Sampling temperature to use during inference. Must be a float between 0 and 1. Defaults to 0.5.
    @api_key: OpenAI API key. If not provided, the function will use the OPENAI_API_KEY environment variable.
    @base_url: Base URL for the OpenAI API. If not provided, the function will use the OPENAI_API_BASE environment variable.

    Returns:
    If stream is True, returns a generator that yields the inference results as they become available.
    If stream is False, returns a string containing the inference result.

    Note:
    The total number of tokens in the messages and the returned string must be less than 4000 when model_variant is 'normal', and less than 16000 when model_variant is 'long'.
    """
    if model == 'smart':
        model = 'gpt-4o'
    if model == 'long':
        model = 'gpt-4o'
    if model == 'normal':
        model = 'gpt-3.5-turbo'
    import os
    import logging
    logging.debug(messages)
    temperature = temperature or float(os.environ.get('LLM_TEMPERATURE', 0.5))
    client = _get_openai_client(api_key, base_url)
    if stream:
        return _llm_inference_with_stream(client, messages, model, temperature)
    else:
        return _llm_inference_without_stream(client, messages, model, temperature)


def _llm_inference_with_stream(client, messages, model, temperature):
    import logging
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


def _llm_inference_without_stream(client, messages, model, temperature):
    import logging
    try:
        response = client.chat.completions.create(messages=messages, model=model, stream=False, temperature=temperature)
        result = response.choices[0].message.content
        return result
    except Exception as e:
        logging.exception(e)
        raise ValueError('LLM(Large Languate Model) error, Please check your key or base_url, or network')