from base_setting import *
from GeneralAgent.scratch import Scratch, SparkNode

def test_scratch():
    file_path='./memory.json'
    if os.path.exists(file_path):
        os.remove(file_path)
    scratch = Scratch()
    node1 = SparkNode(role='user', action='input', content='帮我计算0.99的1000次方')
    node2 = SparkNode(role='system', action='write_code', content='计算0.99的1000次方，结果写到变量A中', output_name='code1')
    node3 = SparkNode(role='system', action='run_code', input_name='code1')
    node4 = SparkNode(role='system', action='output', input_name='A')
    scratch.add_node(node1)
    scratch.add_node_in(node1, node2)
    scratch.add_node_after(node2, node3)
    scratch.add_node_after(node3, node4)

    def assert_init_state(scratch):
        node1 = scratch.get_node(1)
        node2 = scratch.get_node(2)
        node3 = scratch.get_node(3)
        node4 = scratch.get_node(4)
        assert node1.role == 'user'
        assert node1.childrens == [2, 3, 4]
        assert node2.parent == 1
        assert node3.parent == 1
        assert node4.parent == 1
        assert node2.childrens == []
        assert node3.childrens == []
        assert node4.childrens == []
        assert scratch.get_node(1).childrens == [2, 3, 4]

    # 初次验证
    # print(scratch)
    assert_init_state(scratch)
    description_1 = str(scratch)

    # 重新加载验证
    scratch = None
    scratch = Scratch()
    print(scratch)
    assert_init_state(scratch)
    description_2 = str(scratch)
    assert description_1 == description_2

    # 输出节点环境
    node2 = scratch.get_node(2)
    env = scratch.get_node_enviroment(node2)
    print(env)

    # 测试获取todo节点
    todo_node = scratch.get_todo_node()
    assert todo_node.node_id == 2

    scratch.finish_node(todo_node)
    assert scratch.get_todo_node().node_id == 3

    # 删除节点
    scratch.delete_node(node3)
    assert scratch.node_count() == 3
    scratch.delete_after_node(node2)
    assert scratch.node_count() == 2
    
    if os.path.exists(file_path):
        os.remove(file_path)

if __name__ == '__main__':
    test_scratch()