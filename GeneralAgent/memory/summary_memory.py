from jinja2 import Template
from GeneralAgent.llm import llm_inference, async_llm_inference, num_tokens_from_string
from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query
import asyncio

prompt_template = """
Imagine you are an intelligent text editor. 
Your first task is to create a small corresponding title(less than 5 words) for the total input text after <<#Title#>>
Then provide a comprehensive summary of the input text, which should be within 50 words after <<#Summary#>>
Then, 将输入文本拆分成块，同一种类型或者相关联的文本放到同一个块中，每块的单词数在100到300间, and create a small corresponding title (less than 5 words) for each block.
The title needs to accurately reflect the main information of the block content and should be wrapped in << and >> symbols.
Please ensure the relevance of your title to the content, avoid arbitrary naming, and ensure that no part of the text is left out in the division of blocks.
The title should be as short as possible, while each block of content should be moderate in length, less than 200 words.
The output format should be as follows:

对于一下 --------- 包围起来的文本:

---------
{{new_text}}
---------

<<#Summary#>>
the summary of the input text

<<Title>>
Block content

<<Title>>
Block content

...
```

Input text:
```
{{new_text}}
```

Please start your task
"""

prompt_template = """
你是一个文本编辑器。
你需要对输入文本起一个短标题、提供全文概述，然后将全文按语义切分成块，每块单词不小于300字，并为每个块创建一个短标题，短标题不超过5个单词。

输出格式应如下所示：
```
<<#Title#>>
全文短标题

<<#Summary#>>
全文概述

<<title>>
分块内容

<<title>>
分块内容
```

Input text:
```
{{new_text}}
```

Please start your task

"""

divide_prompt = """
---------
{{new_text}}
---------
对于以上 --------- 包围起来的文本，你需要将其按语义对全文拆分成块，并按如下格式进行输出:
```
<<title>>
分块内容

<<title>>
分块内容
```
"""


@dataclass
class SummaryMemoryNode:
    key: str
    content: str
    childrens: List[str] = None
    parents: List[str] = None

    def __post_init__(self):
        self.childrens = self.childrens if self.childrens else []
        self.parents = self.parents if self.parents else []

    def __str__(self):
        return f'<<{self.key}>>\n{self.content}'
    
    def __repr__(self):
        return str(self)


def parse_nodes(content):
    nodes = {}
    lines = content.strip().split('\n')
    key = None
    value = ''
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith('<<') and line.endswith('>>'):
            if key is not None:
                nodes[key] = nodes.get(key, '') + value
                value = ''
            key = line[2:-2]
            continue
        else:
            value += line + '\n'
    if key is not None:
        nodes[key] = nodes.get(key, '') + value
    # strip
    for key in nodes:
        nodes[key] = nodes[key].strip()
    return nodes

async def summarize(text, output_recall=None):
    prompt = Template(prompt_template).render(new_text=text)
    messages = [{'role': 'system','content': prompt}]
    result = await async_llm_inference(messages)
    if output_recall is not None:
        await output_recall(result)
    # parse
    nodes = parse_nodes(result)
    summary = nodes.get('#Summary#', '')
    title = nodes.get('#Title#', '')
    if '#Summary#' in nodes:
        nodes.pop('#Summary#')
    if '#Title#' in nodes:
        nodes.pop('#Title#')
    if len(title) > 0:
        nodes[title] = summary + '\n' + ', '.join('<<' + x + '>>' for x in nodes.keys())
        summary = summary + '\nDetail in <<' + title + '>>'
    if output_recall is None:
        print(summary)
        for key in nodes:
            print(f'<<{key}>>\n{nodes[key]}')
    return summary, nodes

async def oncurrent_summarize(text, output_recall=None):
    inputs = split_text(text)
    print('splited count: ', len(inputs))
    coroutines = [summarize(x, output_recall=output_recall) for x in inputs]
    results = await asyncio.gather(*coroutines)
    summary = ''
    nodes = {}
    for result in results:
        summary += result[0]
        nodes.update(result[1])
    return summary, nodes


def split_text(text, max_token=8000, separators='\n'):
    # paragraphs = text.split(separators)
    # paragraphs = re.split(repr(separators), text)
    import re
    pattern = "[" + re.escape(separators) + "]"
    paragraphs = list(re.split(pattern, text))
    print(len(paragraphs))
    result = []
    current = ''
    for paragraph in paragraphs:
        if num_tokens_from_string(current) + num_tokens_from_string(paragraph) > max_token:
            result.append(current)
            current = ''
        current += paragraph + '\n'
    if len(current) > 0:
        result.append(current)
    new_result = []
    for x in result:
        if num_tokens_from_string(x) > max_token:
            new_result.extend(split_text(x, max_token=max_token, separators="，。,.;；"))
        else:
            new_result.append(x)
    new_result = [x.strip() for x in new_result if len(x.strip()) > 0]
    return new_result


class SummaryMemory():
    def __init__(self, serialize_path='./summary_memory.json', short_memory_limit=1000) -> None:
        self.serialize_path = serialize_path
        self.short_memory_limit = short_memory_limit
        self.db = TinyDB(serialize_path)
        nodes = [SummaryMemoryNode(**node) for node in self.db.all()]
        self.concepts = dict(zip([node.key for node in nodes], nodes))
        self.load_short_memory()

    def load_short_memory(self):
        short_memorys = self.db.table('short_memory').all()
        self.short_memory = '' if len(short_memorys) == 0 else short_memorys[0]['content']

    def save_short_memory(self):
        self.db.table('short_memory').truncate()
        self.db.table('short_memory').insert({'content': self.short_memory})

    async def add_content(self, input, output_recall=None):
        print('input token count:', num_tokens_from_string(input))
        summary, nodes = await oncurrent_summarize(input, output_recall=output_recall)
        # summary, nodes = await summarize(input, output_recall=output_recall)
        self.update(summary, nodes)
        while num_tokens_from_string(self.short_memory) > self.short_memory_limit:
            summary, nodes = await summarize(self.short_memory, output_recall=output_recall)
            self.update(summary, nodes)

    def update(self, summary, nodes):
        self.short_memory += summary
        self.save_short_memory()
        for key in nodes:
            if key in self.concepts:
                self.concepts[key].content += nodes[key]
            else:
                self.concepts[key] = SummaryMemoryNode(key=key, content=nodes[key])
            self.db.upsert(self.concepts[key].__dict__, Query().key == key)