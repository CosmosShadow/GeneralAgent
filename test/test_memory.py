from base_setting import *
from GeneralAgent.memory import Memory, MemoryNode

def test_memory():
    file_path='./memory.json'
    if os.path.exists(file_path):
        os.remove(file_path)
    memory = Memory(file_path=file_path)
    node1 = MemoryNode(role='user', action='input', content='帮我计算0.99的1000次方')
    node2 = MemoryNode(role='system', action='write_code', content='计算0.99的1000次方，结果写到变量A中', output_name='code1')
    node3 = MemoryNode(role='system', action='run_code', input_name='code1')
    node4 = MemoryNode(role='system', action='output', input_name='A')
    memory.add_node(node1)
    memory.add_node_in(node1, node2)
    memory.add_node_after(node2, node3)
    memory.add_node_after(node3, node4)

    def _assert_init_state(memory):
        node1 = memory.get_node(1)
        node2 = memory.get_node(2)
        node3 = memory.get_node(3)
        node4 = memory.get_node(4)
        assert node1.role == 'user'
        assert node1.childrens == [2, 3, 4]
        assert node2.parent == 1
        assert node3.parent == 1
        assert node4.parent == 1
        assert node2.childrens == []
        assert node3.childrens == []
        assert node4.childrens == []
        assert memory.get_node(1).childrens == [2, 3, 4]

    # 初次验证
    # print(memory)
    _assert_init_state(memory)
    description_1 = str(memory)

    # 重新加载验证
    memory = None
    memory = Memory(file_path=file_path)
    print('--------memory---------')
    print(memory)
    print('--------memory---------')
    _assert_init_state(memory)
    description_2 = str(memory)
    assert description_1 == description_2

    # 输出节点环境
    node2 = memory.get_node(2)
    env = memory.get_node_enviroment(node2)
    print('-------env-------')
    print(env)
    print('-------env-------')

    # 测试获取todo节点
    todo_node = memory.get_todo_node()
    assert todo_node.node_id == 2

    memory.success_node(todo_node)
    assert memory.get_todo_node().node_id == 3

    # 删除节点
    memory.delete_node(node3)
    assert memory.node_count() == 3
    memory.delete_after_node(node2)
    print('--------memory---------')
    print(memory)
    print('--------memory---------')
    assert memory.node_count() == 2
    
    if os.path.exists(file_path):
        os.remove(file_path)

if __name__ == '__main__':
    test_memory()