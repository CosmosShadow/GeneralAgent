from base_setting import *
import os
import shutil
from GeneralAgent.agent import Agent

def test_write_aigc_business_plan():
    workspace = './test_workspace'
    if os.path.exists(workspace): shutil.rmtree(workspace)
    controller = Agent(workspace='./test_workspace')
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
                for_node_id = node.node_id
    except KeyboardInterrupt:
        pass
    finally:
        if os.path.exists(workspace): shutil.rmtree(workspace)

    # 帮我写一份关于AI画画的商业计划
    #  > 业务范围、目标市场、客户群体、竞争优势
    # 业务范围是AI画画，用户输入描述，AI画画输出图片，目标市场是全球，客户群体是喜欢画画的人，竞争优势是AI画画的效果好
    #  > 业务范围、目标市场、客户群体、竞争优势


if __name__ == '__main__':
    test_write_aigc_business_plan()