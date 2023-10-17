from base_setting import *
from GeneralAgent.memory import LinkMemory
from GeneralAgent.utils import default_output_recall
import asyncio
import pytest
import fitz

@pytest.mark.asyncio
async def test_link_memory_one_concept():
    serialize_path = './link_memory.json'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    memory = LinkMemory(serialize_path=serialize_path)
    role = 'user'
    content = '我家住成都市天府新区万安街道海悦汇城西区8栋1702'
    new_content = await memory.add_content(content, role, output_recall=default_output_recall)
    print(new_content)
# expect to see:

# 我住在<<Home Adress>>
# ```<<Home Adress>>
# 成都市天府新区万安街道海悦汇城西区8栋1702
# ```
    assert "<<" in new_content


@pytest.mark.asyncio
async def test_link_memory_read_paper():
    serialize_path = './link_memory.json'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    memory = LinkMemory(serialize_path=serialize_path)
    role = 'user'
    content = ''

    file_path = './data/Nougat.pdf'
    doc = fitz.open(file_path)
    documents = []
    for page in doc:
        content = page.get_text()
        print('-' * 100)
        print(content)
        print('-' * 100)
        new_content = await memory.add_content(content, role, output_recall=default_output_recall)
        break
        # print(new_content)


if __name__ == '__main__':
    # asyncio.run(test_link_memory_one_concept())
    asyncio.run(test_link_memory_read_paper())