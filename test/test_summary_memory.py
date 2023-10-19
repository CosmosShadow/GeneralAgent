from base_setting import *
from GeneralAgent.memory import SummaryMemory
from GeneralAgent.utils import default_output_recall
import asyncio
import pytest
import fitz

def test_get_nodes():
    content = """
<<Home>>
home

<<Name>>
shadow
"""
    nodes = SummaryMemory.get_nodes(content)
    assert len(nodes) == 2
    assert nodes['Home'] == 'home'
    assert nodes['Name'] == 'shadow'

def test_get_hide_keys():
    content = """
<<Home>>
hello

```hide
<<Home>>
<<Introductoin>>
```
```show
<<ROOT>>
```
"""
    keys, _ = SummaryMemory.get_hide_keys(content)
    assert len(keys) == 2
    assert 'Home' in keys
    assert 'Introductoin' in keys

def test_get_show_keys():
    content = """
<<Home>>
hello
```show
<<ROOT>>
<<Introductoin>>
```
"""
    keys, _ = SummaryMemory.get_show_keys(content)
    assert len(keys) == 2
    assert 'ROOT' in keys
    assert 'Introductoin' in keys

def test_parse():
    serialize_path = './summary_memory.json'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    memory = SummaryMemory(serialize_path=serialize_path)
    source = """
<<ROOT>>
我住在<<Home Address>>
<<Home Address>>
成都市天府新区万安街道海悦汇城西区8栋1702
```hide
<<Home Address>>
```
"""
    parsed, content = memory.instant_parse(source)
    assert content == source
    assert not parsed
    parsed, content = memory.post_parse(content)
    assert parsed
    assert '<<ROOT>>' in content
    assert 'hide' not in content

    show_memory = memory.get_show_memory()
    assert '成都市天府新区万安街道海悦汇城西区8栋1702' not in show_memory

    source = """
```show
<<Home Address>>
```
"""
    parsed, content = memory.instant_parse(source)
    assert content != source
    assert parsed
    assert '成都市天府新区万安街道海悦汇城西区8栋1702' in content



@pytest.mark.asyncio
async def test_summary_memory_one_concept():
    serialize_path = './summary_memory.json'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    memory = SummaryMemory(serialize_path=serialize_path)
    role = 'user'
    content = '我家住成都市天府新区万安街道海悦汇城西区8栋1702'
    new_content = await memory.add_content(content, role, output_recall=default_output_recall)
    print(new_content)
# expect to see:

# 我住在<<Home Address>>
# ```<<Home Address>>
# 成都市天府新区万安街道海悦汇城西区8栋1702
# ```
    assert "<<" in new_content


@pytest.mark.asyncio
async def test_summary_memory_read_paper():
    serialize_path = './summary_memory.json'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    memory = SummaryMemory(serialize_path=serialize_path)
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


if __name__ == '__main__':
    # test_get_nodes()
    # test_get_hide_keys()
    # test_get_show_keys()
    # test_parse()
    # asyncio.run(test_summary_memory_one_concept())
    asyncio.run(test_summary_memory_read_paper())