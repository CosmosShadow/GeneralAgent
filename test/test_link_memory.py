from base_setting import *
from GeneralAgent.memory import LinkMemory
from GeneralAgent.utils import default_output_recall
import asyncio
import pytest

@pytest.mark.asyncio
async def test_link_memory_basic():
    serialize_path = './link_memory.json'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    memory = LinkMemory(serialize_path=serialize_path)
    role = 'user'
    content = '我家住成都市天府新区万安街道海悦汇城西区8栋1702'
    new_content = await memory.add_content(content, role, output_recall=default_output_recall)
    print(new_content)
    # expect
# 我住在<<Home Adress>>
# ```<<Home Adress>>
# 成都市天府新区万安街道海悦汇城西区8栋1702
# ```
    assert "<<" in new_content


if __name__ == '__main__':
    asyncio.run(test_link_memory_basic())