import os
from GeneralAgent.memory import StackMemory, StackMemoryNode
from GeneralAgent.utils import set_logging_level
set_logging_level()

def test_memory():
    serialize_path='./data/memory.json'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    memory = StackMemory(serialize_path=serialize_path)
    node1 = StackMemoryNode(role='user', action='input', content='node1')
    node2 = StackMemoryNode(role='system', action='answer', content='node2')
    node3 = StackMemoryNode(role='system', action='answer', content='node3')
    node4 = StackMemoryNode(role='system', action='answer', content='node4')
    memory.add_node(node1)
    memory.add_node_in(node1, node2)
    memory.add_node_after(node2, node3)
    memory.add_node_after(node3, node4)
    # [node1 [node2, node3, node4] ]

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

    # first assert
    _assert_init_state(memory)
    description_1 = str(memory)

    # load from serialized file
    memory = None
    memory = StackMemory(serialize_path=serialize_path)
    _assert_init_state(memory)
    description_2 = str(memory)
    assert description_1 == description_2

    # test get node
    tmp_node = memory.get_node(3)
    assert tmp_node.content == 'node3'

    # get todo node
    todo_node = memory.get_todo_node()
    assert todo_node.node_id == 2

    # success node
    memory.success_node(todo_node)
    assert memory.get_todo_node().node_id == 3
    
    if os.path.exists(serialize_path):
        os.remove(serialize_path)

if __name__ == '__main__':
    test_memory()