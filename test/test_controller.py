# 测试Controller
from base_setting import *
import os
import shutil
from GeneralAgent.controller import Controller

def test_plan_1():
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Controller(workspace='./test_workspace')
    controller.run('帮我计算0.99的1000次方', step_count=2)
    print(controller.scratch)
    # [id]: 1 [role]: user, [action]: input, [state]: success, [content]: 帮我计算0.99的1000次方, [input_name]: None, [output_name]: None, [parent]: 0
    # [id]: 2 [role]: system, [action]: write_code, [state]: ready, [content]: Calculate 0.99 power of 1000 and save it in the variable name_0, [input_name]: None, [output_name]: name_1, [parent]: 0
    # [id]: 3 [role]: system, [action]: run_code, [state]: ready, [content]: None, [input_name]: name_1, [output_name]: None, [parent]: 0
    # [id]: 4 [role]: system, [action]: output, [state]: ready, [content]: None, [input_name]: name_0, [output_name]: None, [parent]: 0
    if os.path.exists(workspace): shutil.rmtree(workspace)

def test_plan_2():
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Controller(workspace='./test_workspace')
    controller.run('帮我写一份关于AIGC创业的商业计划', step_count=2)
    print(controller.scratch)
    # [id]: 1 [role]: user, [action]: input, [state]: success, [content]: 帮我写一份关于AIGC创业的商业计划, [input_name]: None, [output_name]: None, [parent]: 0
    # [id]: 2 [role]: system, [action]: output, [state]: ready, [content]: Could you please clarify the key points that you'd like included in the business plan about AIGC startup?, [input_name]: None, [output_name]: name_0, [parent]: 0
    if os.path.exists(workspace): shutil.rmtree(workspace)

def test_plan_3():
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Controller(workspace='./test_workspace')
    controller.run('帮我找一下tesla最新的5条新闻', step_count=2)
    print(controller.scratch)
    # [id]: 1 [role]: user, [action]: input, [state]: success, [content]: 帮我找一下tesla最新的5条新闻, [input_name]: None, [output_name]: None, [parent]: 0
    # [id]: 2 [role]: system, [action]: write_code, [state]: ready, [content]: Find the latest 5 news about Tesla and save them in the variable name_0, [input_name]: None, [output_name]: name_1, [parent]: 0
    # [id]: 3 [role]: system, [action]: run_code, [state]: ready, [content]: None, [input_name]: name_1, [output_name]: None, [parent]: 0
    # [id]: 4 [role]: system, [action]: output, [state]: ready, [content]: None, [input_name]: name_0, [output_name]: None, [parent]: 0
    if os.path.exists(workspace): shutil.rmtree(workspace)


if __name__ == '__main__':
    # test_plan_1()
    # test_plan_2()
    test_plan_3()