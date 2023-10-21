

def _parse_segment_llm_result(text):
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
    from skills import skills
    from jinja2 import Template
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
For example:
```
<<Hello>>
0:12

<<World>>
13:20
```
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
    result = await skills.async_llm_inference(messages)
    # print(result)
    nodes = _parse_segment_llm_result(result)
    for key in nodes:
        start, end = nodes[key]
        nodes[key] = '\n'.join(lines[start:end])
    return nodes


async def summarize_text(text):
    from skills import skills
    prompt = "Please distill the content between --------- into a concise phrase or sentence that captures the essence without any introductory phrases."
    # prompt = "请将---------之间的内容提炼成一个简洁的短语或句子，抓住要点，无需任何介绍性短语。"
    messages = [
        {'role': 'system','content': 'You are a helpful assistant'},
        {'role': 'user','content': f'{prompt}.\n---------\n{text}\n---------'}
        ]
    result = await skills.async_llm_inference(messages)
    return result