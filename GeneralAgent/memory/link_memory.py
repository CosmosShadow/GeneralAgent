from jinja2 import Template
from GeneralAgent.llm import llm_inference
from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query
import re
import logging

prompt_template = """
# 链接超文本规则

1. 每块文本包含key和content，不能嵌套，格式如下:
<<key>>
content

2. 可以在content中使用<<key>>对其他块进行链接

3. 可以使用```hide```和```show```对块进行隐藏和显示，命令如下:

```hide
<<key1>>
<<key2>>
```

```show
<<key1>>
<<key2>>
```

4. 最后生成<<ROOT>>块，结合其他块的<<key>>对全文进行概述


# DEMO 1
```
<<Home Address>>
成都市天府新区万安街道海悦汇城西区8栋1702

<<ROOT>>
我家住在<<Home Address>>
```

# DEMO 2
```
<<Paper Title>>
xxx

<<Authors>>
xxx

<<xxx>>
xxx

<<ROOT>>
The paper titled <<Paper Title>>, written by <<Authors>>, xxx
```

# 部分节点详情
{{nodes}}}

# 将下面文档整理成链接超文本格式

{{new_text}}

# 整理后的文档如下:

"""

@dataclass
class LinkMemoryNode:
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
    

class LinkMemory():
    def __init__(self, serialize_path='./link_memory.json') -> None:
        self.serialize_path = serialize_path
        self.db = TinyDB(serialize_path)
        nodes = [LinkMemoryNode(**node) for node in self.db.all()]
        self.concepts = dict(zip([node.key for node in nodes], nodes))
        if len(self.concepts) == 0:
            self.concepts['ROOT'] = LinkMemoryNode(key='ROOT', content='', show=False)
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
                self.concepts[key] = LinkMemoryNode(key=key, content=value, show=False)
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
                self.concepts[key] = LinkMemoryNode(key=key, content='', show=False)
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