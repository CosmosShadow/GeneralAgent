import os
from GeneralAgent.interpreter import PythonInterpreter


def test_python_interpreter():
    # test add print
    code = """
x = a + b
x"""
    code = PythonInterpreter.add_print(code)
    print(code)
    assert code.strip() == """
x = a + b
print(x)""".strip()
    # test run
    serialize_path = './data/test_interpreter.bin'
    if os.path.exists(serialize_path): os.remove(serialize_path)

    interpreter = PythonInterpreter(serialize_path)
    sys_stdout, is_stop = interpreter.output_parse('```python\nprint("hello world")\n```')
    assert 'hello world' in sys_stdout.strip()
    assert is_stop is False

    interpreter.set_variable('a', 10)
    sys_stdout, is_stop = interpreter.output_parse('```python\na += 1\n```')
    a = interpreter.get_variable('a')
    assert a == 11

    sys_stdout, is_stop = interpreter.output_parse('```python\na += 1\n```')
    a = interpreter.get_variable('a')
    assert a == 12


def test_stack_code():
    serialize_path = './data/test_interpreter.bin'
    if os.path.exists(serialize_path): os.remove(serialize_path)
    interpreter = PythonInterpreter(serialize_path)
    code = """
```python
a = 10
code = "```python\\na += 1\\n```"
interpreter.output_parse(code)
print(a)
```
"""
    interpreter.set_variable('interpreter', interpreter)
    sys_stdout, is_stop = interpreter.output_parse(code)
    print(sys_stdout)

# output:
# 11
# python runs result:
# run successfully


if __name__ == '__main__':
    test_stack_code()
