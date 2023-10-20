from jinja2 import Template
from GeneralAgent.llm import async_llm_inference
import re

segment_prompt = """
---------
{{text}}
---------

For the text surrounded by ---------, the number after # is the line number.
Based on semantics, you need to divide the text into blocks, represented by the start and end line numbers, and take a short title for each block.
The output format is as follows
```
<<title for block>>
start_line: end_line

<<title for block>>
start_line: end_line
```
"""

def parse_segment_llm_result(text):
    import logging
    lines = text.strip().split('\n')
    key = None
    nodes = {}
    # print(lines)
    for line in lines:
        # print(line)
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith('<<') and line.endswith('>>'):
            key = line[2:-2]
        else:
            if key is None:
                logging.warning(f'key is None, line: {line}')
                continue
            blocks = line.split(':')
            if len(blocks) >= 2:
                start = int(blocks[0])
                end = int(blocks[1])
                nodes[key] = (start, end)
    return nodes



async def segment_text(text):
    """
    将文本进行语义分段，返回分段后的文本和key组成的字典nodes
    """
    lines = text.strip().split('\n')
    new_lines = []
    for index in range(len(lines)):
        new_lines.append(f'#{index} {lines[index]}')
    new_text = '\n'.join(new_lines)
    prompt = Template(segment_prompt).render({'text': new_text})
    messages = [
        {'role': 'system','content': 'You are a helpful assistant'},
        {'role': 'user','content': prompt}
        ]
    result = await async_llm_inference(messages)
    print(result)
    nodes = parse_segment_llm_result(result)
    for key in nodes:
        start, end = nodes[key]
        nodes[key] = '\n'.join(lines[start:end])
    return nodes


async def summarize_text(text):
    messages = [
        {'role': 'system','content': 'You are a helpful assistant'},
        {'role': 'user','content': f'Summary the text below surrounded by ---------.\n---------\n{text}\n---------'}
        ]
    result = await async_llm_inference(messages)
    return result