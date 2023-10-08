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

async def default_output_recall(token):
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

def set_logging_level(log_level):
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
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(funcName)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )