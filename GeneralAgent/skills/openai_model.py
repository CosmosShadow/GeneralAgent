import os
import logging
from openai import OpenAI
from openai import AzureOpenAI
import numpy as np
from numpy.linalg import norm


def _get_openai_client(api_key=None, base_url=None):
    if api_key is None and 'OPENAI_API_KEY' not in os.environ:
        raise ValueError('Please set OPENAI_API_KEY in environment')
    api_key = api_key or os.environ['OPENAI_API_KEY']
    base_url = base_url or os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
    client = OpenAI(api_key=api_key, base_url=base_url, max_retries=3)
    return client


def _get_azure_client(api_key=None, base_url=None):
    if api_key is None and 'OPENAI_API_KEY' not in os.environ:
        raise ValueError('Please set OPENAI_API_KEY (Azure API Key) in environment')
    api_key = api_key or os.environ['OPENAI_API_KEY']
    if base_url is None and 'OPENAI_API_BASE' not in os.environ:
        raise ValueError('Please set OPENAI_API_BASE (Azure API Base URL) in environment')
    base_url = base_url or os.environ['OPENAI_API_BASE']
    api_version = os.environ.get('AZURE_API_VERSION', '2024-05-01-preview')
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=base_url,
    )
    return client


def embedding_texts(texts, model=None) -> [[float]]:
    """
    对文本数组进行embedding
    """
    if model is not None and 'azure_' in model:
        client = _get_azure_client()
        model = model.replace('azure_', '')
    else:
        client = _get_openai_client()
        model = os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-small')
    resp = client.embeddings.create(input=texts, model=model)
    result = [x.embedding for x in resp.data]
    return result


def cos_sim(a, b):
    a = a if isinstance(a, np.ndarray) else np.array(a)
    b = b if isinstance(b, np.ndarray) else np.array(b)
    return np.dot(a, b) / (norm(a) * norm(b))


def search_similar_texts(focal: str, texts: [str], top_k=5):
    """
    search the most similar texts in texts, and return the top_k similar texts
    """
    embeddings = embedding_texts([focal] + texts)
    focal_embedding = embeddings[0]
    texts_embeddings = embeddings[1:]
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
    if 'glm-4v' in model:
        return 8 * 1000
    if 'glm-4' in model:
        return 128 * 1000
    if 'yi-vision' in model:
        return 4 * 1000
    if 'yi-large' in model:
        return 32 * 1000

    return 16 * 1000


def llm_inference(messages, model='gpt-4o', stream=False,  api_key=None, base_url=None, **args):
    """
    Run LLM (large language model) inference on the provided messages using the specified model.

    @messages: Input messages for the model, like [{'role': 'system', 'content': 'You are a helpful assistant'}, {'role': 'user', 'content': 'What is your name?'}]
    @model: Type of model to use. Options are 'normal', 'smart', 'long'
    @stream: Boolean indicating if the function should use streaming inference
    @temperature: Sampling temperature to use during inference. Must be a float between 0 and 1. Defaults to 0.5.
    @api_key: OpenAI API key. If not provided, the function will use the OPENAI_API_KEY environment variable.
    @base_url: Base URL for the OpenAI API. If not provided, the function will use the OPENAI_API_BASE environment variable.
    @frequency_penalty: Frequency penalty to use during inference. Must be a float between -2 and 2. Defaults to null.

    Returns:
    If stream is True, returns a generator that yields the inference results as they become available.
    If stream is False, returns a string containing the inference result.

    Note:
    The total number of tokens in the messages and the returned string must be less than 4000 when model_variant is 'normal', and less than 16000 when model_variant is 'long'.
    """

    logging.debug(messages)
    if model == 'smart':
        model = 'gpt-4o'
    if model == 'long':
        model = 'gpt-4o'
    if model == 'normal':
        model = 'gpt-3.5-turbo'
    if 'azure_' in model:
        model = model.replace('azure_', '')
        client = _get_azure_client(api_key, base_url)
    elif 'doubao' in model:
        client, model = _get_doubao_client(api_key, base_url)
    else:
        client = _get_openai_client(api_key, base_url)
    messages = _process_message(messages, model)
    if stream:
        return _llm_inference_with_stream(client, messages, model, **args)
    else:
        return _llm_inference_without_stream(client, messages, model, **args)


def _process_message(messages, model):
    if model == "glm-4v":  # 避开 GLM-4V 开源模型，开源模型不需要处理
        for message in messages:
            # remove the base64 prefix in the image_url such as 'data:image/jpeg;base64,' which is for GLM-4V
            if 'content' in message and isinstance(message['content'], list):
                for item in message['content']:
                    if item.get('type') == 'image_url' and 'url' in item.get('image_url', {}):
                        url = item['image_url']['url']
                        base64_index = url.find('base64,')
                        if base64_index != -1:
                            item['image_url']['url'] = url[base64_index + len('base64,'):]
    if model == "yi-vision":  # Yi-Vision Not Support System Role
        for message in messages:
            if message['role'] == 'system':
                message['role'] = 'user'

    return messages


def _get_doubao_client(api_key=None, base_url=None):
    from volcenginesdkarkruntime import Ark
    key = api_key or os.environ.get('OPENAI_API_KEY')
    client = Ark(api_key=key)
    model = base_url or os.environ.get('OPENAI_API_BASE')
    return client, model


def _update_llm_args(model, args):
    if model in ['qwen-vl-max', 'qwen-vl-plus']:
        remove_items = ['temperature', 'frequency_penalty']
        return {k: v for k, v in args.items() if k not in remove_items}
    else:
        return args


def _llm_inference_with_stream(client, messages, model, **args):
    try:
        args = _update_llm_args(model, args)
        response = client.chat.completions.create(
            messages=messages,
            model=model,
            stream=True,
            **args
        )
        for chunk in response:
            if len(chunk.choices) > 0:
                # Compatible with service using Azure API proxies, such as One-API
                if chunk.choices[0].delta is None:
                    continue
                token = chunk.choices[0].delta.content
                if token is None:
                    continue
                yield token
    except Exception as e:
        logging.exception(e)
        raise ValueError('LLM(Large Languate Model) error, Please check your key or base_url, or network')


def _llm_inference_without_stream(client, messages, model, **args):
    try:
        args = _update_llm_args(model, args)
        response = client.chat.completions.create(
            messages=messages,
            model=model,
            stream=False,
            **args
        )
        result = response.choices[0].message.content
        return result
    except Exception as e:
        logging.exception(e)
        raise ValueError('LLM(Large Languate Model) error, Please check your key or base_url, or network')
    
def speech_to_text(audio_file_path):
    """Convert speech in audio to text, return text"""
    from GeneralAgent import skills
    audio_file = open(audio_file_path, "rb")
    client = _get_openai_client()
    content = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file, 
        response_format="text"
    )

    return content

def text_to_speech(text, voice='onyx', save_path=None):
    """
    文本转语音，返回音频文件路径。
    @param text: 要转换的文本
    @param voice: 语音名称, onyx: 男性，nova: 女性
    @return: 音频文件路径
    """
    from GeneralAgent import skills

    # ['nova', 'shimmer', 'echo', 'onyx', 'fable', 'alloy']
    client = _get_openai_client()
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )
    file_path = save_path or skills.unique_name() + '.mp3'
    response.stream_to_file(file_path)
    return file_path


def create_image(prompt) -> str:
    """draw image given a prompt, returns the image path. Note: limit to generate violent, adult, or hateful content"""
    import os
    from openai import OpenAI
    from GeneralAgent import skills

    client = _get_openai_client()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    image_path = skills.try_download_file(image_url)
    return image_path


def edit_image(image_path:str, prompt:str) -> str:
    """Edit image given a prompt, returns the image path"""
    import os
    from openai import OpenAI
    from GeneralAgent import skills
    from pathlib import Path

    client = _get_openai_client()
    response = client.images.edit(
        image = Path(image_path),
        prompt = prompt,
        n=1,
    )
    image_url = response.data[0].url
    image_path = skills.try_download_file(image_url)
    return image_path