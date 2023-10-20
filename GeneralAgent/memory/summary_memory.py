from dataclasses import dataclass
from typing import List
from tinydb import TinyDB, Query
import asyncio

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


async def summarize(text, output_recall=None):
    from skills import skills
    nodes = await skills.segment_text(text)
    if output_recall is not None:
        await output_recall('\n\n'.join([f'<<{key}>>\n{nodes[key]}' for key in nodes]))
    summary = await skills.summarize_text(text)
    if output_recall is not None:
        await output_recall('\n<<Summary>>:\n' + summary)
    return summary, nodes

async def oncurrent_summarize(text, output_recall=None):
    from skills import skills
    inputs = skills.split_text(text)
    print('splited count: ', len(inputs))
    coroutines = [summarize(x, output_recall=output_recall) for x in inputs]
    results = await asyncio.gather(*coroutines)
    summary = ''
    nodes = {}
    for result in results:
        summary += result[0]
        nodes.update(result[1])
    return summary, nodes


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
        from skills import skills
        print('input token count:', skills.num_tokens_from_string(input))
        summary, nodes = await oncurrent_summarize(input, output_recall=output_recall)
        # summary, nodes = await summarize(input, output_recall=output_recall)
        self.update(summary, nodes)
        while skills.num_tokens_from_string(self.short_memory) > self.short_memory_limit:
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