import os
from GeneralAgent.interpreter import PlanInterpreter
from GeneralAgent.memory import StackMemory, StackMemoryNode


def test_structure_plan():
    content = """
1.xxx
    1.1 xxx

2.xxx

"""
    plan_dict = PlanInterpreter._structure_plan(content)
    assert len(plan_dict) == 2
    key0 = list(plan_dict.keys())[0]
    key1 = list(plan_dict.keys())[1]
    assert key0 == '1.xxx'
    assert len(plan_dict[key0]) == 1
    assert len(plan_dict[key1]) == 0

def test_plan_interpreter():
    serialize_path = './data/plan_memory.json'
    if os.path.exists(serialize_path): os.remove(serialize_path)
    memory = StackMemory(serialize_path)
    node = StackMemoryNode('user', 'input', content='hello world')
    memory.add_node(node)
    memory.set_current_node(node)
    interpreter = PlanInterpreter(memory, max_plan_depth=4)
    content = """
```runplan
1.xxx
    1.1 xxx

2.xxx

```
"""
    output, is_stop = interpreter.input_parse(content)
    assert output == content
    assert is_stop is False
    assert memory.node_count() == 4




if __name__ == '__main__':
    # test_python_interpreter()
    # test_bash_interperter()
    # test_applescript_interpreter()
    # test_file_interpreter_old()
    # test_structure_plan()
    test_plan_interpreter()
    # test_ask_interpreter()