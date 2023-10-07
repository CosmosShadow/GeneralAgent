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