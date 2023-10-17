from jinja2 import Template
from GeneralAgent.llm import llm_inference
from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query
import re
import logging


prompt_template = """
你是一个专业的文本整理者。
你的工作是将文本进行结构化，将一些独立且完整的文本整理成块，并用<<key>>的形式进行引用。
要求: 整理后的内容应该是完整的，不应该有任何遗漏。

比如:
我家住成都市天府新区万安街道海悦汇城西区8栋1702
=>
我住在<<Home Adress>>
```<<Home Adress>>
成都市天府新区万安街道海悦汇城西区8栋1702
```

整理过程中，你可能使用下面三种命令:

1. 创建或者更新块
```<<key>>
<content>
```

2. 显示重要的且不知道细节的块
```show
<<key1>>
<<key2>>
```

3. 隐藏不重要的块
```hide
<<key1>>
<<key2>>
```


已有块的keys：
[{{memory_nodes}}]

文本内容：
{{short_memory}}

整理命令和结果:
"""

@dataclass
class LinkMemoryNode:
    key: str
    content: str
    childrens: List[str] = None
    parents: List[str] = None

    def __post_init__(self):
        self.childrens = self.childrens if self.childrens else []
        self.parents = self.parents if self.parents else []

    def __str__(self):
        return f'<<{self.role}>>: {self.content}'
    
    def __repr__(self):
        return str(self)
    
    def show(self):
        return f"```<<{self.key}>>\n{self.content}\n```"
    

class LinkMemory():
    def __init__(self, serialize_path='./link_memory.json') -> None:
        self.serialize_path = serialize_path
        self.db = TinyDB(serialize_path)
        nodes = [LinkMemoryNode(**node) for node in self.db.all()]
        self.concepts = dict(zip([node.key for node in nodes], nodes))
        self.load_short_memory()

    def load_short_memory(self):
        short_memorys = self.db.table('short_memory').all()
        self.short_memory = '' if len(short_memorys) == 0 else short_memorys[0]['content']

    def save_short_memory(self):
        self.db.table('short_memory').truncate()
        self.db.table('short_memory').insert({'content': self.short_memory})

    async def add_content(self, content, role, output_recall=None):
        assert role in ['user', 'system']
        # self.short_memory += f"\n[{role}]:\n{content}"
        self.short_memory += f"\n{content}"
        self.save_short_memory()

        result = ''

        while True:
            memory_nodes = ', '.join(['<<'+x+'>>' for x in self.concepts.keys()])
            prompt = Template(prompt_template).render(
                memory_nodes=memory_nodes,
                short_memory=self.short_memory
            )
            messages = [{
                'role': 'system',
                'content': prompt + '\n' + result
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
                        # if output_recall is not None:
                        #     await output_recall(None)
                        #     await output_recall(result)
                        #     await output_recall(None)
                        break
            if not parsed:
                _, result = self.post_parse(result)
                self.short_memory = result
                self.save_short_memory()
                # if output_recall is not None:
                #     await output_recall(None)
                #     await output_recall(result)
                #     await output_recall(None)
                break
        return self.short_memory
    
    def instant_parse(self, content):
        return self._parse_show(content)

    def post_parse(self, content):
        fold_parsed, content = self._parse_block(content)
        hide_parsed, content = self._parse_hide(content)
        return fold_parsed or hide_parsed, content
    
    def _parse_block(self, content):
        block_patten = "```(\n)?<<(.*?)>>\n(.*?)\n```"
        block_matches = re.finditer(block_patten, content, re.DOTALL)
        
        if not block_matches:
            return False, content
        
        for block_match in block_matches:
            logging.debug('block_match: ' + str(block_match))
            key = block_match.group(2)
            value = block_match.group(3)
            
            if key in self.concepts:
                self.concepts[key].content = value
            else:
                self.concepts[key] = LinkMemoryNode(key=key, content=value)

            # save or update
            self.db.upsert(self.concepts[key].__dict__, Query().key == key)
            # content = content.replace(block_match.group(0), '')
        
        return True, content

    def _parse_hide(self, content):
        content = content.strip()
        hide_patten = "```(\n)?hide\n(.*?)\n```"
        hide_matches = re.finditer(hide_patten, content, re.DOTALL)
        
        if not hide_matches:
            return False, content
        
        for hide_match in hide_matches:
            logging.debug('hide_match: ' + str(hide_match))
            values = hide_match.group(2)
            lines = values.strip().split('\n')
            
            for key in lines:
                key = key.strip()
                if key.startswith('<<') and key.endswith('>>'):
                    key = key[2:-2]
                if key in self.concepts:
                    block_patten = f"```(\n)?<<{key}>>\n{self.concepts[key].content}\n```"
                    match = re.search(block_patten, content, re.DOTALL)
                    if match is not None:
                        content = content.replace(match.group(0), '')
        
        return True, content

    def _parse_show(self, content):
        show_patten = "```(\n)?show\n(.*?)\n```"
        show_match = re.search(show_patten, content, re.DOTALL)
        if show_match is None:
            return False, content
        logging.debug('show_match: ' + str(show_match))
        contents = show_match.group(2)
        lines = contents.strip().split('\n')
        keys = []
        for line in lines:
            line = line.strip()
            if line.startswith('<<') and line.endswith('>>'):
                keys.append(line[2:-2])
            else:
                keys.append(line)
        replaced_value = '\n\n'.join([self.concepts[key].show() for key in keys if key in self.concepts])
        content = content.replace(show_match.group(0), replaced_value)
        return True, content