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


def test_plan_1():
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Agent(workspace='./test_workspace')
    controller.run('帮我计算0.99的1000次方', step_count=2)
    print(controller.memory)
    if os.path.exists(workspace): shutil.rmtree(workspace)

def test_plan_2():
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Agent(workspace='./test_workspace')
    controller.run('帮我写一份关于AIGC创业的商业计划', step_count=2)
    print(controller.memory)
    if os.path.exists(workspace): shutil.rmtree(workspace)

def test_plan_3():
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Agent(workspace='./test_workspace')
    controller.run('帮我找一下tesla最新的5条新闻', step_count=2)
    print(controller.memory)
    if os.path.exists(workspace): shutil.rmtree(workspace)

def test_math():
    # step
    # 1 input
    # 2 plan
    # 3 write code
    # 4 run code
    # 5 return value
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Agent(workspace='./test_workspace')
    node, result = controller.run('帮我计算0.99的1000次方', step_count=5)
    print(controller.memory)
    write_code_node = controller.memory.get_node(2)
    code = controller.code_workspace.get_variable(write_code_node.output_name)
    # print(code)
    assert '0.99' in code
    assert '1000' in code
    assert result == str(0.99 ** 1000)
    print(result)
    if os.path.exists(workspace): shutil.rmtree(workspace)

def test_scrape_news():
    # 测试抓取新闻
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Agent(workspace='./test_workspace')
    node, result = controller.run('帮我找一下tesla最新的5条新闻，中文返回给我', step_count=5)
    print(controller.memory)
    print(result)
    if os.path.exists(workspace): shutil.rmtree(workspace)


if __name__ == '__main__':
    # test_plan_1()
    # test_plan_2()
    # test_plan_3()
    # test_math()
    # test_scrape_news()
    test_structure_plan()