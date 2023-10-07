import os, sys

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