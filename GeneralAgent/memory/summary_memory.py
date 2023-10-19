from jinja2 import Template
from GeneralAgent.llm import llm_inference
from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query
import re
import logging

prompt_template = """

对于一下 --------- 包围起来的文本:

---------
{{new_text}}
---------

按语义对全文拆分成块，并按如下格式进行输出

```
<<title>>
block content 1

<<title>>
block content 2

...
```

其中title是block的概要描述短语

"""

prompt_template = """
Imagine you are an intelligent text editor. 
Your first task is to provide a comprehensive summary of the input text, which should be within 100 words. 
Then, divide the input text into different blocks according to their semantic content, and create a corresponding title for each block.
The title needs to accurately reflect the main information of the block content and should be wrapped in << and >> symbols.
Please ensure the relevance of your title to the content and avoid arbitrary naming.
The title should be as short as possible, while each block of content should be moderate in length, less than 200 words.
The output format should be as follows:

```
<<#Summary#>>
Summary content

<<Title>>
Block content 1

<<Title>>
Block content 2

...
```

Input text:
```
{{new_text}}
```

Please start your task
"""


@dataclass
class SummaryMemoryNode:
    key: str
    content: str
    show: bool = True
    childrens: List[str] = None
    parents: List[str] = None

    def __post_init__(self):
        self.childrens = self.childrens if self.childrens else []
        self.parents = self.parents if self.parents else []

    def __str__(self):
        return f'<<{self.key}>>\n{self.content}'
    
    def __repr__(self):
        return str(self)
    

class SummaryMemory():
    def __init__(self, serialize_path='./summary_memory.json') -> None:
        self.serialize_path = serialize_path
        self.db = TinyDB(serialize_path)
        nodes = [SummaryMemoryNode(**node) for node in self.db.all()]
        self.concepts = dict(zip([node.key for node in nodes], nodes))
        if len(self.concepts) == 0:
            self.concepts['ROOT'] = SummaryMemoryNode(key='ROOT', content='', show=False)
            self.db.insert(self.concepts['ROOT'].__dict__)

    def get_show_memory(self):
        return '\n\n'.join([str(node) for node in self.concepts.values() if node.show and len(node.content.strip()) > 0]).strip()

    async def add_content(self, input, role, output_recall=None):
        # 预处理
        assert role in ['user', 'system']
        root_node = self.concepts['ROOT']
        new_text = root_node.content + '\n' + input
        result = ''
        while True:
            keys = ', '.join(['<<'+x+'>>' for x in self.concepts.keys() if x != 'ROOT'])
            prompt = Template(prompt_template).render(
                # keys=keys,
                nodes='\n'.join([str(node) for node in self.concepts.values() if node.show and len(node.content.strip()) > 0]),
                new_text=new_text
            )
            messages = [{
                'role': 'system',
                'content': prompt + result
            }]
            response = llm_inference(messages)
            parsed = False
            for token in response:
                if output_recall is not None:
                    await output_recall(token)
                if token is not None:
                    result += token
                    parsed, result = self.instant_parse(result)
                    if parsed:
                        _, result = self.post_parse(result)
                        break
            if not parsed:
                _, result = self.post_parse(result)
                break
        return self.get_show_memory() + '\n' + self.concepts['ROOT'].content
    
    def instant_parse(self, content):
        return self._parse_show(content)

    def post_parse(self, content):
        hide_parsed, content = self._parse_hide(content)
        fold_parsed, content = self._parse_block(content)
        return fold_parsed or hide_parsed, content
        # return self._parse_block(content)
    
    def _parse_block(self, content):
        nodes = self.get_nodes(content)
        for key, value in nodes.items():
            if key in self.concepts:
                self.concepts[key].content = value
            else:
                self.concepts[key] = SummaryMemoryNode(key=key, content=value, show=False)
            self.db.upsert(self.concepts[key].__dict__, Query().key == key)
        return True, content

    def _parse_hide(self, content):
        keys, hide_matches = self.get_hide_keys(content)
        if len(keys) == 0:
            return False, content
        for key in keys:
            if key in self.concepts:
                self.concepts[key].show = False
                self.db.upsert(self.concepts[key].__dict__, Query().key == key)
            else:
                self.concepts[key] = SummaryMemoryNode(key=key, content='', show=False)
                self.db.insert(self.concepts[key].__dict__)
        hide_matches = re.finditer("```(\n)?hide\n(.*?)\n```", content, re.DOTALL)
        for hide_match in hide_matches:
            content = content.replace(hide_match.group(0), '')
        return True, content

    def _parse_show(self, content):
        keys, _ = self.get_show_keys(content)
        if len(keys) == 0:
            return False, content
        for key in keys:
            if key in self.concepts:
                self.concepts[key].show = True
                self.db.upsert(self.concepts[key].__dict__, Query().key == key)
        # print(keys)
        # print(self.concepts)
        replaced_value = '\n\n'.join([str(self.concepts[key]) for key in keys if key in self.concepts])
        show_patten = "```(\n)?show\n(.*?)\n```"
        show_match = re.search(show_patten, content, re.DOTALL)
        # print(show_match)
        content = content.replace(show_match.group(0), replaced_value)
        return True, content
    
    @classmethod
    def get_nodes(cls, content):
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
    
    @classmethod
    def get_hide_keys(self, content):
        keys = []
        content = content.strip()
        hide_patten = "```(\n)?hide\n(.*?)\n```"
        hide_matches = re.finditer(hide_patten, content, re.DOTALL)
        
        hide_matches = [] if hide_matches is None else hide_matches
        for hide_match in hide_matches:
            logging.debug('hide_match: ' + str(hide_match))
            values = hide_match.group(2)
            lines = values.strip().split('\n')
            for key in lines:
                key = key.strip()
                if key.startswith('<<') and key.endswith('>>'):
                    key = key[2:-2]
                keys.append(key)
        return keys, hide_matches
    
    @classmethod
    def get_show_keys(cls, content):
        show_patten = "```(\n)?show\n(.*?)\n```"
        show_match = re.search(show_patten, content, re.DOTALL)
        if show_match is None:
            return [], None
        else:
            contents = show_match.group(2)
            lines = contents.strip().split('\n')
            keys = []
            for line in lines:
                line = line.strip()
                if line.startswith('<<') and line.endswith('>>'):
                    keys.append(line[2:-2])
                else:
                    keys.append(line)
            return keys, show_match