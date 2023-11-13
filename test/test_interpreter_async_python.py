import os
import pytest
import asyncio
from GeneralAgent.interpreter import AsyncPythonInterpreter



@pytest.mark.asyncio
async def test_async_python_interpreter():
    serialize_path = './data/serialized.bin'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    code1 = """
a = 1
await asyncio.sleep(0.5)
"""
    code2 = """
a += 1
"""
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

# 
@pytest.mark.asyncio
async def test_with_async_tools():
    serialize_path = './data/serialized.bin'
    if os.path.exists(serialize_path):
        os.remove(serialize_path)
    code1 = """
a = 1
await asyncio.sleep(0.5)
"""
    code2 = """
a = await increase(a)
"""

    async def increase(x):
        await asyncio.sleep(0.5)
        print(f'increase called with parameter: x={x}')
        return x + 1
    
    python_interpreter = AsyncPythonInterpreter(serialize_path=serialize_path)
    python_interpreter.function_tools = [increase]
    await python_interpreter.run_code(code1)
    value = python_interpreter.get_variable('a')
    assert value == 1

    python_interpreter = None
    python_interpreter = AsyncPythonInterpreter(serialize_path=serialize_path)
    python_interpreter.function_tools = [increase]
    sys_out = await  python_interpreter.run_code(code2)
    value = python_interpreter.get_variable('a')
    assert value == 2
    assert 'increase called with parameter: x=' in sys_out

    if os.path.exists(serialize_path):
        os.remove(serialize_path)


if __name__ == '__main__':
    # asyncio.run(test_async_python_interpreter())
    asyncio.run(test_with_async_tools())