from jinja2 import Template
from GeneralAgent.llm import llm_inference
from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query
import re


prompt_template = \
"""
As a memory assistant, your job is to organize memories and output concise expressions. You can use the following three memory rules:

#01 Fold memory and update memory: Use this rule to fold frequently used information into a keyword, making the conversation record more concise and efficient.

```<<key>>
<content>
```

If you want to update the content of the keyword, recall the keyword and then update the content will be useful.

#02 Ignore memory: Use this rule to ignore information that is irrelevant to the current task, so as to be more focused.

```ignore
<<key1>>
<<key2>>
...
```

#03 Recall memory: Use this rule to recall all informations that are related to the current task or memory to update, so as to better complete the task.

```recall
<<key1>>
<<key2>>
...
```

Use these rules to organize memories and complete tasks more efficiently.

For example, you can use the following rules to organize your home address:
我家住成都市天府新区万安街道海悦汇城西区8栋1702
=> 
我住在<<Home Adress>>
```<<Home Adress>>
成都市天府新区万安街道海悦汇城西区8栋1702
```

当前的记忆节点列表:
{{memory_nodes}}

以下是短期记忆:
{{short_memory}}}

以下是角色{{role}}的最新输入: 
{{input}}

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
    

class LinkMemory():
    def __init__(self, serialize_path='./memory.json') -> None:
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
        self.db.table('short_memory').insert({'content': self.show_memory})

    async def add_content(self, content, role, output_recall=None):
        assert role in ['user', 'system']
        memory_nodes = ', '.join(['<<'+x+'>>' for x in self.concepts.keys()])
        prompt = Template(prompt_template).render(
            memory_nodes=memory_nodes,
            short_memory=self.short_memory,
            role=role,
            input=content
        )
        messages = [{
            'role': 'system',
            'content': prompt
        }]
        result = ''
        response = llm_inference(messages)
        for token in response:
            if output_recall is not None:
                await output_recall(token)
            if token is not None:
                result += token
                parsed, result = self.instant_parse(result)
                if parsed:
                    self.short_memory = self.post_parse(self.short_memory + result)
                    self.save_short_memory()
    
    def instant_parse(self, content):
        return self._parse_recall(content)

    def post_parse(self, content):
        fold_parsed, content = self._parse_fold(content)
        ignore_parsed, content = self._parse_ignore(content)
        return fold_parsed or ignore_parsed, content

    def _parse_ignore(self, content):
        content = content.strip()
        ignore_patten = "```(\n)?ignore\n(.*?)\n```"
        ignore_match = re.search(ignore_patten, content, re.DOTALL)
        if ignore_match is not None:
            values = ignore_match.group(2)
            lines = values.strip().split('\n')
            keys = []
            for line in lines:
                line = line.strip()
                if line.startswith('<<') and line.endswith('>>'):
                    keys.append(line[2:-2])
                else:
                    keys.append(line)
            # ignore the key and its content
            for key in keys:
                if key in self.concepts:
                    content = content.replace(self.concepts[key].content, '')
                content = content.replace('<<' + key + '>>', '')
            return True, content

    def _parse_recall(self, content):
        recall_patten = "```(\n)?recall\n(.*?)\n```"
        recall_match = re.search(recall_patten, content, re.DOTALL)
        if recall_match is not None:
            contents = recall_match.group(2)
            lines = contents.strip().split('\n')
            keys = []
            for line in lines:
                line = line.strip()
                if line.startswith('<<') and line.endswith('>>'):
                    keys.append(line[2:-2])
                else:
                    keys.append(line)
            replaced_value = '\n' + '\n\n'.join(['<<'+key+'>>: ' + self.concepts[key].content for key in keys if key in self.concepts]) + '\n'
            content = content.replace(recall_match.group(0), replaced_value)
            return True, content
        return False, content
    
    def _parse_fold(self, content):
        # TODO: 多个地方需要折叠呢
        update_patten = "```(\n)?<<(.*?)>>\n(.*?)\n```"

        update_match = re.search(update_patten, content, re.DOTALL)
        if update_match is not None:
            key = update_match.group(2)
            value = update_match.group(3)
            if key in self.concepts:
                self.concepts[key].content = value
            else:
                self.concepts[key] = LinkMemoryNode(key=key, content=value)
            self.db.update(self.concepts[key].__dict__, Query().key == key)
            content = content.replace(update_match.group(0), '')
            return True, content
        return False, content