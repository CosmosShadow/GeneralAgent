import os
from GeneralAgent.interpreter import SyncPythonInterpreter

def test_python_interpreter():
    # test add print
    code = """
x = a + b
x"""
    code = SyncPythonInterpreter.add_print(code)
    print(code)
    assert code == """
x = a + b
print(x)"""
    # test run
    serialize_path = './data/test_interpreter.bin'
    if os.path.exists(serialize_path): os.remove(serialize_path)

    interpreter = SyncPythonInterpreter(serialize_path)
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
url = 'https://www.google.com'
result = scrape_web(url)
title = result[0]
```
"""
    sys_stdout, is_stop = interpreter.parse(code)
    title = interpreter.get_variable('title')
    assert title == 'Google'

