import os
import pytest
import shutil
import asyncio
from GeneralAgent.agent import StackAgent
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter
from GeneralAgent.utils import set_logging_level
set_logging_level()


workspace = './data/test_workspace'

result = ''

def get_output_callback():
    global result
    result = ''
    async def _output_callback(token):
        if token is not None:
            global result
            result += token
            print(token, end='', flush=True)
    return _output_callback


@pytest.mark.asyncio
async def test_math():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = StackAgent.default(workspace=workspace)
    memory_node_id = await agent.run('calculate 0.99 ** 1000', output_callback=get_output_callback())
    assert '4.31712474' in result
    assert memory_node_id == None

@pytest.mark.asyncio
async def test_write_file():
    target_path = './data/a.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = StackAgent.default(workspace=workspace)
    memory_node_id = await agent.run('Write the description of Chengdu to the file ./data/a.txt', output_callback=get_output_callback())
    assert memory_node_id == None
    assert os.path.exists(target_path)
    with open(target_path, 'r') as f:
        content = f.read()
        assert 'Chengdu' in content
    if os.path.exists(target_path):
        os.remove(target_path)

@pytest.mark.asyncio
async def test_read_file():
    content = """Chengdu, the capital of China's southwest Sichuan Province, is famed for being the home of cute giant pandas. Apart from the Panda Research base, Chengdu has a lot of other attractions. It is known for its spicy Sichuan cuisine and ancient history, including the site of the ancient Jinsha civilization and the Three Kingdoms-era Wuhou Shrine. The city also features beautiful natural landscapes such as Mount Qingcheng and the Dujiangyan Irrigation System, both UNESCO World Heritage Sites."""
    target_path = './data/b.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    with open(target_path, 'w') as f:
        f.write(content)
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = StackAgent.default(workspace=workspace)
    memory_node_id = await agent.run('what is in ./data/b.txt', output_callback=get_output_callback())
    global result
    assert 'Mount Qingcheng' in result
    assert memory_node_id == None
    if os.path.exists(target_path):
        os.remove(target_path)

@pytest.mark.asyncio
async def test_functions():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    os.mkdir(workspace)
    serialize_path = f'{workspace}/code.bin'
    python_interpreter = PythonInterpreter(serialize_path=serialize_path)
    from GeneralAgent import skills
    python_interpreter.function_tools = [skills.scrape_web]
    agent = StackAgent(workspace=workspace, output_interpreters=[RoleInterpreter(), python_interpreter])
    memory_node_id = await agent.run("what's the tiltle of web page https://tongtianta.ai ?", output_callback=get_output_callback())
    global result
    assert 'AI' in result
    assert memory_node_id == None
    assert os.path.exists(serialize_path)
    shutil.rmtree(workspace)



if __name__ == '__main__':
    # asyncio.run(test_math())
    # asyncio.run(test_write_file())
    # asyncio.run(test_read_file())
    asyncio.run(test_functions())