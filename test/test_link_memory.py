import os
import fitz
import pytest
import asyncio
from GeneralAgent.memory import LinkMemory
from GeneralAgent.utils import default_output_recall
from GeneralAgent.utils import set_logging_level
set_logging_level()


@pytest.mark.asyncio
async def test_read_paper():
    serialize_path = './summary_memory.json'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    memory = LinkMemory(serialize_path=serialize_path)
    file_path = './data/Nougat.pdf'
    doc = fitz.open(file_path)
    content = ''
    for page in doc:
        content += '\n' + page.get_text()
    new_content = await memory.add_memory(content, output_recall=None)
    # new_content = await memory.add_memory(content, output_recall=default_output_recall)
    spark = await memory.get_memory()
    assert '<<Introduction>>' in spark
    # print(spark)


if __name__ == '__main__':
    asyncio.run(test_read_paper())