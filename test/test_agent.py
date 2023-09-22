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
    pass


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

# test_plan_1、test_plan_2、test_plan_3
# cache 33f1b2856badb977b2e11c1d8ee859c6 hitted
# cache fb160084a5014578338f7440d1e9cf3a hitted
# [id]: 1 [role]: user, [action]: input, [state]: success, [content]: 帮我计算0.99的1000次方, [input_name]: None, [output_name]: None, [parent]: 0
# [id]: 2 [role]: system, [action]: write_code, [state]: ready, [content]: 计算0.99的1000次方并把结果存在变量name_0中, [input_name]: None, [output_name]: name_0, [parent]: 0
# [id]: 3 [role]: system, [action]: run_code, [state]: ready, [content]: None, [input_name]: name_0, [output_name]: None, [parent]: 0
# [id]: 4 [role]: system, [action]: output, [state]: ready, [content]: None, [input_name]: name_0, [output_name]: None, [parent]: 0
# cache 33f1b2856badb977b2e11c1d8ee859c6 hitted
# cache 98fc1bbf5a30e4f12730d8b016cbb6e2 hitted
# [id]: 1 [role]: user, [action]: input, [state]: success, [content]: 帮我写一份关于AIGC创业的商业计划, [input_name]: None, [output_name]: None, [parent]: 0
# [id]: 2 [role]: system, [action]: output, [state]: ready, [content]: 您能不能对AIGC创业的特别要求详细一些，例如业务方向、时间线、人员规模、预期收益等？, [input_name]: None, [output_name]: name_0, [parent]: 0
# cache 33f1b2856badb977b2e11c1d8ee859c6 hitted
# cache 6772f64ce1cb1c6a4b491a042426e2bd hitted
# [id]: 1 [role]: user, [action]: input, [state]: success, [content]: 帮我找一下tesla最新的5条新闻, [input_name]: None, [output_name]: None, [parent]: 0
# [id]: 2 [role]: system, [action]: write_code, [state]: ready, [content]: Find the latest 5 news about tesla and save it in variable name_0, [input_name]: None, [output_name]: name_1, [parent]: 0
# [id]: 3 [role]: system, [action]: run_code, [state]: ready, [content]: None, [input_name]: name_1, [output_name]: None, [parent]: 0
# [id]: 4 [role]: system, [action]: output, [state]: ready, [content]: None, [input_name]: name_0, [output_name]: None, [parent]: 0

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
    pass