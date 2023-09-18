# 测试Controller
from base_setting import *
import os
import shutil
from GeneralAgent.controller import Controller
from GeneralAgent.scratch import SparkNode

def test_write_aigc_business_plan():
    # 测试写一份商业计划
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Controller(workspace='./test_workspace')
    # input_value = '帮我写一份关于AI画画的商业计划'
    for_node_id = None
    try:
        while True:
            input_value = input('user >>> ')
            result = controller.run(input_value, for_node_id=for_node_id, step_count=None)
            if result is None:
                break
            else:
                node, output_value = result
                print('-'*50 + '<controller.scratch>' + '-'*50)
                print(controller.scratch)
                print('-'*50 + '</controller.scratch>' + '-'*50)
                print('\nsys >>> ' + str(output_value) + '\n')
                for_node_id = node.node_id
    except KeyboardInterrupt:
        pass
    finally:
        # print(controller.scratch)
        if os.path.exists(workspace): shutil.rmtree(workspace)

    # 帮我写一份关于AI画画的商业计划
    #  > 业务范围、目标市场、客户群体、竞争优势
    # 业务范围是AI画画，用户输入描述，AI画画输出图片，目标市场是全球，客户群体是喜欢画画的人，竞争优势是AI画画的效果好
    #  > 业务范围、目标市场、客户群体、竞争优势


if __name__ == '__main__':
    # test_plan_1()
    # test_plan_2()
    # test_plan_3()
    # test_math()
    # test_scrape_news()
    test_write_aigc_business_plan()