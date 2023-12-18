import os
import pytest
import asyncio
from GeneralAgent.interpreter import SyncPythonInterpreter


@pytest.mark.asyncio
def test_python_interpreter():
    # test add print
    code = """
x = a + b
x"""
    code = SyncPythonInterpreter.add_print(code)
    print(code)
    assert code.strip() == """
x = a + b
print(x)""".strip()
    # test run
    serialize_path = './data/test_interpreter.bin'
    if os.path.exists(serialize_path): os.remove(serialize_path)

    interpreter = SyncPythonInterpreter(serialize_path)
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