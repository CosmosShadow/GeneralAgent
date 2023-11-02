import os
from GeneralAgent.interpreter import ShellInterpreter, AppleScriptInterpreter, PythonInterpreter, PlanInterpreter, AskInterpreter
from GeneralAgent.memory import Memory, MemoryNode

def test_bash_interperter():
    interpreter = ShellInterpreter()
    output, is_stop = interpreter.parse("""```shell\npython ./data/hello.py\n```""")
    assert 'hello world' in output
    assert is_stop is False


def test_structure_plan():
    content = """
1.xxx
    1.1 xxx

2.xxx

"""
    plan_dict = PlanInterpreter.structure_plan(content)
    assert len(plan_dict) == 2
    key0 = list(plan_dict.keys())[0]
    key1 = list(plan_dict.keys())[1]
    assert key0 == '1.xxx'
    assert len(plan_dict[key0]) == 1
    assert len(plan_dict[key1]) == 0

def test_plan_interpreter():
    serialize_path = './data/plan_memory.json'
    if os.path.exists(serialize_path): os.remove(serialize_path)
    memory = Memory(serialize_path)
    node = MemoryNode('user', 'input', content='hello world')
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
    output, is_stop = interpreter.parse(content)
    assert output == content
    assert is_stop is False
    assert memory.node_count() == 4

def test_ask_interpreter():
    interpreter = AskInterpreter()
    content = """
```ask
who are your?
```
"""
    output, is_stop = interpreter.parse(content)
    assert output == ''
    assert is_stop is True


if __name__ == '__main__':
    # test_python_interpreter()
    # test_bash_interperter()
    # test_applescript_interpreter()
    # test_file_interpreter_old()
    # test_structure_plan()
    test_plan_interpreter()
    # test_ask_interpreter()