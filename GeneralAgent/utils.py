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