

def _parse_segment_llm_result(text):
    import logging
    logging.info('-----------<_parse_segment_llm_result>------------')
    logging.info(text)
    logging.info('-----------</_parse_segment_llm_result>------------')
    lines = text.strip().split('\n')
    key = None
    nodes = {}
    for line in lines:
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


def segment_text(text):
    """
    将文本进行语义分段，返回分段后的文本和key组成的字典nodes
    """
    from GeneralAgent import skills
    from jinja2 import Template
    segment_prompt = """
---------
{{text}}
---------

For the text enclosed by ---------, the number following # is the line number.
Your task is to divide the text into segments (up to 6), each represented by the start and end line numbers. Additionally, assign a brief title (not exceeding 10 words) to each segment.
The output format is as follows:
```
<<Title for Segment>>
Start_line: End_line

<<Title for Segment>>
Start_line: End_line
```
For instance:
```
<<Hello>>
0:12

<<World>>
13:20
```
Please note, each title should not exceed 10 words. Titles exceeding this limit will be considered invalid. Strive to keep your titles concise yet reflective of the main content in the segment.
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
    model_type='normal'
    if skills.messages_token_count(messages) > 3500:
        model_type = 'long'
    result = skills.llm_inference(messages, model_type)
    nodes = _parse_segment_llm_result(result)
    for key in nodes:
        start, end = nodes[key]
        nodes[key] = '\n'.join(lines[start:end])
    return nodes


def summarize_text(text):
    from GeneralAgent import skills
    prompt = "Please distill the content between --------- into a concise phrase or sentence that captures the essence without any introductory phrases."
    # prompt = "请将---------之间的内容提炼成一个简洁的短语或句子，抓住要点，无需任何介绍性短语。"
    messages = [
        {'role': 'system','content': 'You are a helpful assistant'},
        {'role': 'user','content': f'{prompt}.\n---------\n{text}\n---------'}
        ]
    result = skills.llm_inference(messages)
    return result

def extract_info(background, task):
    prompt_template = """
Background (line number is indicated by #number, and <<title>> is a link to the details):
---------
{{background}}
---------

Task
---------
{{task}}
---------

Please provide the line numbers in the background that contain information relevant to solving the task.
Then, provide the <<titles>> that provide further details related to the background information.
The expected output format is as follows:
```
#Line Number 1
#Line Number 2
...
<<title 1>>
<<title 2>>
...
```
If no relevant information is found, please output "[Nothing]".
```
[Nothing]
```
Note: <<titles>> and line numbers provide up to 5 items each, so please select the most relevant.
"""

    from GeneralAgent import skills
    from jinja2 import Template
    prompt = Template(prompt_template).render({'background': background, 'task': task})
    messages = [
        {'role': 'system','content': 'You are a helpful assistant'},
        {'role': 'user','content': prompt}
        ]
    result = skills.llm_inference(messages)
    return result


def parse_extract_info(text):
    import re
    numbers = re.findall(r'#(\d+)', text)
    numbers = [int(x) for x in numbers]
    titles = re.findall(r'<<([^>>]+)>>', text)
    return numbers, titles


def extract_title(text, language='english'):
    """
    extract title from text
    """
    if len(text) > 500:
        text = text[:500]
    prompt = f"Please distill the content between --------- into a concise title in {language} of the content, less than five words. Return the title directly without including it in \".\n---------\n{text}\n---------"
    from GeneralAgent import skills
    messages = [
        {'role': 'system','content': 'You are a helpful assistant'},
        {'role': 'user','content': prompt}
        ]
    result = skills.llm_inference(messages)
    return result