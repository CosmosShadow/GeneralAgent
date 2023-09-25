from base_setting import *
import os
import pytest
import shutil
import asyncio
from GeneralAgent.agent import Agent, check_has_ask, structure_plan
from GeneralAgent.tools import Tools, scrape_web

workspace = './data/test_workspace'

def test_check_has_ask():
    has_ask, result = check_has_ask('find the latest 5 news about tesla and save it in variable name_0')
    assert has_ask is False
    has_ask, result = check_has_ask('###ask where is the moon? ###ask how many times ?')
    assert has_ask is True
    assert result == ' where is the moon?  how many times ?'

def test_structure_plan():
    content = """
1.xxx
    1.1 xxx

2.xxx

"""
    plan_dict = structure_plan(content)
    assert len(plan_dict) == 2
    key0 = list(plan_dict.keys())[0]
    key1 = list(plan_dict.keys())[1]
    assert key0 == '1.xxx'
    assert len(plan_dict[key0]) == 1
    assert len(plan_dict[key1]) == 0

@pytest.mark.asyncio
async def test_math():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace)
    async def _output_recall(result):
        # print(result)
        assert '4.317124741065786e-05' in result
        agent.stop()
    for_node_id = await agent.run('Help me calculate 0.99 raised to the 1000th power', output_recall=_output_recall)
    assert for_node_id == None

@pytest.mark.asyncio
async def test_write_file():
    target_path = './data/a.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace)
    async def _output_recall(result):
        # print(str(result)[:500])
        agent.stop()
    for_node_id = await agent.run('Write the description of Chengdu to the file a.txt', output_recall=_output_recall)
    assert for_node_id == None
    assert os.path.exists(target_path)
    with open(target_path, 'r') as f:
        content = f.read()
        assert 'Chengdu' in content
    if os.path.exists(target_path):
        os.remove(target_path)

@pytest.mark.asyncio
async def test_read_file():
    content = """Chengdu, the capital of China's southwest Sichuan Province, is famed for being the home of cute giant pandas. Apart from the Panda Research base, Chengdu has a lot of other attractions. It is known for its spicy Sichuan cuisine and ancient history, including the site of the ancient Jinsha civilization and the Three Kingdoms-era Wuhou Shrine. The city also features beautiful natural landscapes such as Mount Qingcheng and the Dujiangyan Irrigation System, both UNESCO World Heritage Sites."""
    target_path = './data/b.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    with open(target_path, 'w') as f:
        f.write(content)
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace)
    async def _output_recall(result):
        # print(str(result))
        assert 'Mount Qingcheng' in result
        agent.stop()
    for_node_id = await agent.run('Read the file b.txt and tell me the summary', output_recall=_output_recall)
    assert for_node_id == None
    if os.path.exists(target_path):
        os.remove(target_path)

@pytest.mark.asyncio
async def test_tool_use():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace, tools=Tools([scrape_web]))
    async def _output_recall(result):
        # print(str(result)[:500])
        assert 'AI' in result
        agent.stop()
    for_node_id = await agent.run("what's the tiltle of web page https://tongtianta.ai ?", output_recall=_output_recall)
    assert for_node_id == None

@pytest.mark.asyncio
async def test_bash_interperter():
    pass

# def test_scrape_news():
#     # 测试抓取新闻
#     if os.path.exists(workspace): shutil.rmtree(workspace)
#     agent = Agent(workspace='./test_workspace')
#     node, result = agent.run('帮我找一下tesla最新的5条新闻，中文返回给我', step_count=5)
#     print(agent.memory)
#     print(result)
#     if os.path.exists(workspace): shutil.rmtree(workspace)


if __name__ == '__main__':
    # test_check_has_ask()
    # test_structure_plan()
    asyncio.run(test_math())
    # asyncio.run(test_write_file())
    # asyncio.run(test_read_file())
    # test_scrape_news()
    # asyncio.run(test_tool_use())