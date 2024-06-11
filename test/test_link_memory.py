import os
import fitz
import pytest
import asyncio
from GeneralAgent.memory import LinkMemory


def test_read_paper():
    serialize_path = './summary_memory.json'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    memory = LinkMemory(serialize_path=serialize_path)
    file_path = './data/Nougat_piece.pdf'
    doc = fitz.open(file_path)
    content = ''
    for page in doc:
        content += '\n' + page.get_text()
    memory.add_memory(content, output_callback=None)
    spark = memory.get_memory()
    # print(f'-----------\n{spark}\n-----------')
    assert 'Introduction' in spark

    messages = [
        {'role': 'user', 'content': '论文有哪些贡献?'},
    ]
    spark = memory.get_memory(messages)
    print(f'-----------\n{spark}\n-----------')
    assert 'pdf' in spark.lower()


if __name__ == '__main__':
    asyncio.run(test_read_paper())