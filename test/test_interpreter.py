from base_setting import *
from GeneralAgent.interpreter import BashInterperter, AppleScriptInterpreter, PythonInterpreter
from GeneralAgent.interpreter import FileInterpreter, PlanInterpreter, AskInterpreter


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
    serialize_path = './test_interpreter.bin'
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
    open location "https://tongtianta.ai"
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


if __name__ == '__main__':
    test_python_interpreter()
    test_bash_interperter()
    test_applescript_interpreter()
    test_file_interpreter()