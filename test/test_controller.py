# 测试Controller
from base_setting import *
import os
import shutil
from GeneralAgent.controller import Controller

def test_plan():
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Controller(workspace='./test_workspace')
    controller.run('帮我计算0.99的1000次方', step_count=2)
    print(controller.scratch)
    if os.path.exists(workspace): shutil.rmtree(workspace)

if __name__ == '__main__':
    test_plan()