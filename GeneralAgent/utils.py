import os
import logging


def set_logging_level():
    for handler in logging.root.handlers[:]:
       logging.root.removeHandler(handler)
    log_level = os.environ.get('AGENT_LOG', 'info')
    log_level = log_level.lower()
    if log_level == 'debug':
        level = logging.DEBUG
    elif log_level == 'info':
        level = logging.INFO
    elif log_level == 'warning':
        level = logging.WARNING
    elif log_level == 'error':
        level = logging.ERROR
    else:
        level = logging.ERROR
    # logging设置显示文件(绝对路径)
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(pathname)s [line:%(lineno)d] %(levelname)s %(funcName)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def encode_image(image_path):
    if image_path.startswith('http'):
        return image_path
    import base64
    with open(image_path, "rb") as image_file:
        bin_data = base64.b64encode(image_file.read()).decode('utf-8')
    image_type = image_path.split('.')[-1].lower()
    virtural_url = f"data:image/{image_type};base64,{bin_data}"
    return virtural_url


def messages_token_count(messages):
    "Calculate and return the total number of tokens in the provided messages."
    import tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens_per_message = 4
    tokens_per_name = 1
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            if isinstance(value, str):
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
            if isinstance(value, list):
                for item in value:
                    if item["type"] == "text":
                        num_tokens += len(encoding.encode(item["text"]))
                    if item["type"] == "image_url":
                        num_tokens += (85 + 170 * 2 * 2)    # 用最简单的模式来计算
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def string_token_count(str):
    """Calculate and return the token count in a given string."""
    import tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(str)
    return len(tokens)


def cut_messages(messages, token_limit):
    while messages_token_count(messages) > token_limit:
        messages.pop(0)
    return messages