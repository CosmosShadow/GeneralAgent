from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query
import asyncio

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


async def summarize_and_segment(text, output_callback=None):
    from GeneralAgent import skills
    summary = await skills.summarize_text(text)
    if output_callback is not None:
        await output_callback(f'Summary: {summary}\n')
    segments = await skills.segment_text(text)
    if output_callback is not None:
        for key in segments:
            await output_callback(f'<<{key}>>\n')
    return summary, segments


class LinkMemory():
    def __init__(self, serialize_path='./link_memory.json', short_memory_limit=2000) -> None:
        self.serialize_path = serialize_path
        self.short_memory_limit = short_memory_limit
        self.db = TinyDB(serialize_path)
        nodes = [LinkMemoryNode(**x) for x in self.db.all()]
        self.concepts = dict(zip([node.key for node in nodes], nodes))
        self.short_memory = ''
        self._load_short_memory()

    def is_empty(self):
        return len(self.concepts) == 0

    async def add_memory(self, content, output_callback=None):
        from GeneralAgent import skills
        # await self._oncurrent_summarize_content(content, output_callback)
        await self._summarize_content(content, output_callback)
        while skills.string_token_count(self.short_memory) > self.short_memory_limit:
            content = self.short_memory
            self.short_memory = ''
            # await self._oncurrent_summarize_content(content, output_callback)
            await self._summarize_content(content, output_callback)
    
    async def get_memory(self, messages=None):
        from GeneralAgent import skills
        if len(self.concepts) == 0:
            return ''
        if messages is None:
            return self.short_memory
        else:
            messages = skills.cut_messages(messages, 1000)
            xx = self.short_memory.split('\n')
            background = '\n'.join([f'#{line} {xx[line]}' for line in range(len(xx))])
            task = '\n'.join([f'{x["role"]}: {x["content"]}' for x in messages])
            info = await skills.extract_info(background, task)
            line_numbers, keys = skills.parse_extract_info(info)
            result = []
            for line_number in line_numbers:
                if line_number < len(xx) and line_number >= 0:
                    result.append(xx[line_number])
            for key in keys:
                if key in self.concepts:
                    result.append(f'{key}\n{self.concepts[key]}\n')
            return '\n'.join(result)

    def _load_short_memory(self):
        short_memorys = self.db.table('short_memory').all()
        self.short_memory = '' if len(short_memorys) == 0 else short_memorys[0]['content']

    def _save_short_memory(self):
        self.db.table('short_memory').truncate()
        self.db.table('short_memory').insert({'content': self.short_memory})
    
    async def _oncurrent_summarize_content(self, input):
        from GeneralAgent import skills
        inputs = skills.split_text(input, max_token=3000)
        print('splited count: ', len(inputs))
        coroutines = [summarize_and_segment(x) for x in inputs]
        results = await asyncio.gather(*coroutines)
        for summary, nodes in results:
            new_nodes = {}
            for key in nodes:
                new_key = self._add_node(key, nodes[key])
                new_nodes[new_key] = nodes[key]
            self.short_memory += '\n' + summary + ' Detail in ' + ', '.join([f'<<{key}>>' for key in new_nodes])
        self.short_memory = self.short_memory.strip()
        self._save_short_memory()

    async def _summarize_content(self, input, output_callback=None):
        from GeneralAgent import skills
        inputs = skills.split_text(input, max_token=3000)
        for text in inputs:
            summary, nodes = await summarize_and_segment(text, output_callback)
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