import os
from GeneralAgent.interpreter import PythonInterpreter


def test_python_interpreter():
    # test run
    serialize_path = './data/test_interpreter.bin'
    if os.path.exists(serialize_path): os.remove(serialize_path)

    interpreter = PythonInterpreter(serialize_path=serialize_path)
    result, is_stop = interpreter.output_parse('```python\n"hello world"\n```')
    print(result)
    assert 'hello world' in result.strip()
    assert is_stop is False

    interpreter.set_variable('a', 10)
    result, is_stop = interpreter.output_parse('```python\na += 1\n```')
    a = interpreter.get_variable('a')
    assert a == 11

    result, is_stop = interpreter.output_parse('```python\na += 1\n```')
    a = interpreter.get_variable('a')
    assert a == 12


def test_stack_code():
    serialize_path = './data/test_interpreter.bin'
    if os.path.exists(serialize_path): os.remove(serialize_path)
    interpreter = PythonInterpreter(serialize_path=serialize_path)
    code = """
```python
a = 10
code = "```python\\na += 1\\n```"
interpreter.output_parse(code)
print(a)
```
"""
    interpreter.set_variable('interpreter', interpreter)
    result, is_stop = interpreter.output_parse(code)
    print(result)

# output:
# 11
# python runs result:
# run successfully


if __name__ == '__main__':
    test_python_interpreter()
    test_stack_code()
