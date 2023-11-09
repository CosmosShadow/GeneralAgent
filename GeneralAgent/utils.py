import os
import logging


def default_get_input():
    "input multi lines, end with two empty lines"
    print('[input]')
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    text = '\n'.join(lines)
    return text

async def default_output_callback(token):
    if token is not None:
        print(token, end='', flush=True)
    else:
        print('\n[output end]\n', end='', flush=True)

def confirm_to_run():
    auto_run = os.environ.get('AUTO_RUN', 'n')
    if auto_run == 'y':
        return True
    print('Are you sure to run this script? (y/n)')
    while True:
        line = input()
        if line == 'y':
            return True
        elif line == 'n':
            return False
        else:
            print('Please input y or n')

def set_logging_level(log_level=None):
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'ERROR')
    log_level = log_level.upper()
    if log_level == 'DEBUG':
        level = logging.DEBUG
    elif log_level == 'INFO':
        level = logging.INFO
    elif log_level == 'WARNING':
        level = logging.WARNING
    elif log_level == 'ERROR':
        level = logging.ERROR
    else:
        level = logging.ERROR
    # logging设置显示文件(绝对路径)
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(pathname)s [line:%(lineno)d] %(levelname)s %(funcName)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def get_data_dir():
    default_dir = os.path.join(os.path.dirname(__file__), '../data')
    data_dir = os.environ.get('DATA_DIR', default_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def get_applications_dir():
    data_dir = get_data_dir()
    applications_dir = os.path.join(data_dir, 'applications')
    if not os.path.exists(applications_dir):
        os.makedirs(applications_dir)
    return applications_dir

def get_applications_data_dir():
    data_dir = get_data_dir()
    applications_dir = os.path.join(data_dir, 'applications_data')
    if not os.path.exists(applications_dir):
        os.makedirs(applications_dir)
    return applications_dir

def get_functions_dir():
    data_dir = get_data_dir()
    functions_dir = os.path.join(data_dir, 'functions')
    if not os.path.exists(functions_dir):
        os.makedirs(functions_dir)
    return functions_dir

def get_server_dir():
    data_dir = get_data_dir()
    server_dir = os.path.join(data_dir, 'server')
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)
    return server_dir