import pytest
import asyncio
from GeneralAgent.interpreter import ShellInterpreter

@pytest.mark.asyncio
async def test_bash_interperter():
    interpreter = ShellInterpreter()
    output, is_stop = await interpreter.output_parse("""```shell\npython ./data/hello.py\n```""")
    assert 'hello world' in output
    assert is_stop is False

if __name__ == '__main__':
    asyncio.run(test_bash_interperter())