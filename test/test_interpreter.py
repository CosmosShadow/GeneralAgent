from base_setting import *
from GeneralAgent.interpreter import BashInterperter, AppleScriptInterpreter, PythonInterpreter
from GeneralAgent.interpreter import FileInterpreter, PlanInterpreter, AskInterpreter
from GeneralAgent.memory import Memory, MemoryNode

def test_bash_interperter():
    interpreter = BashInterperter()
    output, is_stop = interpreter.parse("""```shell\npython ./data/hello.py\n```""")
    assert 'hello world' in output
    assert is_stop is False


def test_python_interpreter():
    # test add print
    code = """
a = 1
a
    c
try:
"""
    code = PythonInterpreter.add_print(code)
    assert code == """
a = 1
print(a)
    print(c)
try:
"""
    # test run
    serialize_path = './data/test_interpreter.bin'
    if os.path.exists(serialize_path): os.remove(serialize_path)

    interpreter = PythonInterpreter(serialize_path)
    sys_stdout, is_stop = interpreter.parse('```python\nprint("hello world")\n```')
    assert sys_stdout.strip() == 'hello world'
    assert is_stop is False

    interpreter.set_variable('a', 10)
    sys_stdout, is_stop = interpreter.parse('```python\na += 1\n```')
    a = interpreter.get_variable('a')
    assert a == 11

    sys_stdout, is_stop = interpreter.parse('```python\na += 1\n```')
    a = interpreter.get_variable('a')
    assert a == 12

    code = """
```python
url = 'https://tongtianta.ai'
result = scrape_web(url)
title = result[0]
```
"""
    sys_stdout, is_stop = interpreter.parse(code)
    title = interpreter.get_variable('title')
    assert title == '通天塔AI'

def test_applescript_interpreter():
    interpreter = AppleScriptInterpreter()
    content = """```applescript
tell application "Safari"
    activate
    open location "https://www.google.com"
end tell
```"""
    output, is_stop = interpreter.parse(content)
    assert is_stop is False
    assert output.strip() == 'run successfully'

def test_file_interpreter():
    interpreter = FileInterpreter('./')
    content = """
###file write 0 -1 ./data/a.py
print('a')
###endfile
"""
    output, is_stop = interpreter.parse(content)
    assert is_stop is False
    assert output.strip() == 'write successfully'

    content = """
###file read 0 1 ./data/a.py
###endfile
"""
    output, is_stop = interpreter.parse(content)
    assert is_stop is False
    assert output.strip() == "[0]print('a')"

    content = """
###file delete 0 1 ./data/a.py
###endfile
"""
    output, is_stop = interpreter.parse(content)
    assert is_stop is False
    assert output.strip() == 'delete successfully'

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
- [ ] 任务1
- [ ] 任务2
```
"""
    output, is_stop = interpreter.parse(content)
    assert output == ''
    assert is_stop is False
    assert memory.node_count() == 3




if __name__ == '__main__':
    test_python_interpreter()
    test_bash_interperter()
    test_applescript_interpreter()
    test_file_interpreter()
    test_plan_interpreter()