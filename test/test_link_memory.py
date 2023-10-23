import os
import fitz
import pytest
import asyncio
from GeneralAgent.memory import LinkMemory
from GeneralAgent.utils import default_output_recall
from GeneralAgent.utils import set_logging_level
set_logging_level()


@pytest.mark.asyncio
async def test_summary_memory_read_paper():
    serialize_path = './summary_memory.json'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    memory = LinkMemory(serialize_path=serialize_path)
    file_path = './data/Nougat.pdf'
    doc = fitz.open(file_path)
    content = ''
    for page in doc:
        content += '\n' + page.get_text()
        break
    # lines = content.strip().split('\n')
    # for index in range(len(lines)):
    #     print('#' + str(index) + ' ' + lines[index])
    new_content = await memory.add_content(content, output_recall=default_output_recall)


if __name__ == '__main__':
    # test_get_nodes()
    # test_get_hide_keys()
    # test_get_show_keys()
    # test_parse()
    # asyncio.run(test_summary_memory_one_concept())
    asyncio.run(test_summary_memory_read_paper())