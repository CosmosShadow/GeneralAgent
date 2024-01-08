import os
import shutil
from GeneralAgent.agent import Agent
from GeneralAgent.utils import default_output_callback

workspace = './data/test_workspace'

def test_math():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent.default(workspace=workspace)
    result = agent.run('calculate 0.99 ** 1000')
    # print(result)
    # 4.317124741065786e-05
    assert '3171' in result

def test_write_file():
    target_path = './data/a.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent.default(workspace=workspace)
    result = agent.run('Write the description of Chengdu to the file ./data/a.txt. You shoud provide the description')
    assert os.path.exists(target_path)
    with open(target_path, 'r') as f:
        content = f.read()
        assert 'Chengdu' in content
    if os.path.exists(target_path):
        os.remove(target_path)

def test_read_file():
    content = """Chengdu, the capital of China's southwest Sichuan Province, is famed for being the home of cute giant pandas. Apart from the Panda Research base, Chengdu has a lot of other attractions. It is known for its spicy Sichuan cuisine and ancient history, including the site of the ancient Jinsha civilization and the Three Kingdoms-era Wuhou Shrine. The city also features beautiful natural landscapes such as Mount Qingcheng and the Dujiangyan Irrigation System, both UNESCO World Heritage Sites."""
    target_path = './data/b.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    with open(target_path, 'w') as f:
        f.write(content)
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent.default(workspace=workspace)
    result = agent.run('what is in ./data/b.txt')
    assert 'Mount Qingcheng' in result
    if os.path.exists(target_path):
        os.remove(target_path)


def get_weather(city:str):
    """
    get weather from city
    """
    state = 'weather is good, sunny.'
    print(state)
    return state

def test_functions():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    os.mkdir(workspace)
    agent = Agent.with_functions([get_weather], workspace=workspace)
    result = agent.run("what's the weather of Chengdu ?")
    assert 'good, sunny' in result
    # assert os.path.exists(serialize_path)
    shutil.rmtree(workspace)



if __name__ == '__main__':
    # test_math()
    # test_write_file()
    # test_read_file()
    test_functions()