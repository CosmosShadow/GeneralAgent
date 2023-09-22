from base_setting import *
import os
import shutil
from GeneralAgent.agent import Agent, check_has_ask, structure_plan

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

def test_math():
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace='./test_workspace')
    def _output_recall(result):
        print(result)
        assert '4.317124741065786e-05' in result
    for_node_id = agent.run('Help me calculate 0.99 raised to the 1000th power', output_recall=_output_recall)
    assert for_node_id == None

def test_write_file():
    target_path = './a.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace='./test_workspace')
    def _output_recall(result):
        print(str(result)[:500])
    for_node_id = agent.run('Introduce Chengdu and write it to the file a.txt', output_recall=_output_recall)
    assert os.path.exists(target_path)
    with open(target_path, 'r') as f:
        content = f.read()
        assert 'Chengdu' in content

def test_scrape_news():
    # 测试抓取新闻
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace='./test_workspace')
    node, result = agent.run('帮我找一下tesla最新的5条新闻，中文返回给我', step_count=5)
    print(agent.memory)
    print(result)
    if os.path.exists(workspace): shutil.rmtree(workspace)


if __name__ == '__main__':
    # test_check_has_ask()
    # test_structure_plan()
    # test_math()
    test_write_file()
    # test_scrape_news()