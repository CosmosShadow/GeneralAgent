from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

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
        return f'<<{self.key}>>\n{self.content}'
    
    def __repr__(self):
        return str(self)


def summarize_and_segment(text, output_callback=None):
    from GeneralAgent import skills
    summary = skills.summarize_text(text)
    if output_callback is not None:
        output_callback(f'Summary: {summary}\n')
    segments = skills.segment_text(text)
    if output_callback is not None:
        for key in segments:
            output_callback(f'<<{key}>>\n')
    return summary, segments


class LinkMemory():
    def __init__(self, serialize_path='./link_memory.json', short_memory_limit=2000) -> None:
        """
        @serialize_path: str, 序列化路径，默认为'./link_memory.json'。如果为None，则使用内存存储
        @short_memory_limit: int, 短时记忆长度限制
        """
        self.serialize_path = serialize_path
        self.short_memory_limit = short_memory_limit
        if serialize_path is not None:
            self.db = TinyDB(serialize_path)
        else:
            # 内存存储，不序列化
            self.db = TinyDB(storage=MemoryStorage)
        nodes = [LinkMemoryNode(**x) for x in self.db.all()]
        self.concepts = dict(zip([node.key for node in nodes], nodes))
        self.short_memory = ''
        self._load_short_memory()

    def is_empty(self):
        return len(self.concepts) == 0

    def add_memory(self, content, output_callback=None):
        from GeneralAgent import skills
        self._summarize_content(content, output_callback)
        while skills.string_token_count(self.short_memory) > self.short_memory_limit:
            content = self.short_memory
            self.short_memory = ''
            self._summarize_content(content, output_callback)
    
    def get_memory(self, messages=None, limit_token_count=3000):
        from GeneralAgent import skills
        if len(self.concepts) == 0:
            return ''
        if messages is None:
            return self.short_memory
        else:
            # TODO: recursive search
            messages = skills.cut_messages(messages, 10*1000)
            xx = self.short_memory.split('\n')
            background = '\n'.join([f'#{line} {xx[line]}' for line in range(len(xx))])
            task = '\n'.join([f'{x["role"]}: {x["content"]}' for x in messages])
            info = skills.extract_info(background, task)
            line_numbers, keys = skills.parse_extract_info(info)
            result = []
            for line_number in line_numbers:
                if line_number < len(xx) and line_number >= 0:
                    result.append(xx[line_number])
                    if skills.string_token_count('\n'.join(result)) > limit_token_count:
                        return '\n'.join(result[:-1])
            for key in keys:
                if key in self.concepts:
                    result.append(f'{key}\n{self.concepts[key]}\n')
                    if skills.string_token_count('\n'.join(result)) > limit_token_count:
                        return '\n'.join(result[:-1])
            return '\n'.join(result)

    def _load_short_memory(self):
        short_memorys = self.db.table('short_memory').all()
        self.short_memory = '' if len(short_memorys) == 0 else short_memorys[0]['content']

    def _save_short_memory(self):
        self.db.table('short_memory').truncate()
        self.db.table('short_memory').insert({'content': self.short_memory})

    def _summarize_content(self, input, output_callback=None):
        from GeneralAgent import skills
        inputs = skills.split_text(input, max_token=3000)
        for text in inputs:
            summary, nodes = summarize_and_segment(text, output_callback)
            new_nodes = {}
            for key in nodes:
                new_key = self._add_node(key, nodes[key])
                new_nodes[new_key] = nodes[key]
            self.short_memory += '\n' + summary + ' Detail in ' + ', '.join([f'<<{key}>>' for key in new_nodes])
        self.short_memory = self.short_memory.strip()
        self._save_short_memory()

    def _add_node(self, key, value):
        index = 0
        new_key = key
        while new_key in self.concepts:
            index += 1
            new_key = key + str(index)
        self.concepts[new_key] = LinkMemoryNode(key=new_key, content=value)
        self.db.upsert(self.concepts[key].__dict__, Query().key == new_key)
        return new_key
    
    def __str__(self):
        '\n'.join([str(x) for x in self.concepts.values()])