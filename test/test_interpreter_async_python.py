import os
import pytest
import asyncio
from GeneralAgent.interpreter import AsyncPythonInterpreter

code1 = """
a = 1
await asyncio.sleep(0.5)
"""

code2 = """
a += 1
"""

@pytest.mark.asyncio
async def test_async_python_interpreter():
    serialize_path = './data/serialized.bin'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    python_interpreter = AsyncPythonInterpreter(serialize_path=serialize_path)
    await python_interpreter.run_code(code1)
    value = python_interpreter.get_variable('a')
    assert value == 1

    python_interpreter = None
    python_interpreter = AsyncPythonInterpreter(serialize_path=serialize_path)
    await  python_interpreter.run_code(code2)
    value = python_interpreter.get_variable('a')
    assert value == 2

    if os.path.exists(serialize_path):
        os.remove(serialize_path)

if __name__ == '__main__':
    asyncio.run(test_async_python_interpreter())