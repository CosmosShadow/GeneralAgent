import os
import shutil
from GeneralAgent.agent import Agent


workspace = './data/test_workspace'

result = ''

def get_output_callback():
    def _output_callback(token):
        if token is not None:
            global result
            result += token
            print(token, end='', flush=True)
    return _output_callback


def test_math():
    global result
    result = ''
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent.default(workspace=workspace)
    agent.run('calculate 0.99 ** 1000', output_callback=get_output_callback())
    count = 3
    while count > 0:
        if '3171' in result:
            break
        count -= 1
        agent.run('OK', output_callback=get_output_callback())
    assert '3171' in result

def test_write_file():
    global result
    result = ''
    target_path = './data/a.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent.default(workspace=workspace)
    agent.model_type = 'smart'
    agent.run('Write the description of Chengdu to the file ./data/a.txt. You shoud provide the description', output_callback=get_output_callback())
    for index in range(2):
        # print('-' * 100)
        # print(index)
        # print('-' * 100)
        if os.path.exists(target_path):
            break
        agent.run('OK', output_callback=get_output_callback())
    assert os.path.exists(target_path)
    with open(target_path, 'r') as f:
        content = f.read()
        assert 'Chengdu' in content
    if os.path.exists(target_path):
        os.remove(target_path)

def test_read_file():
    global result
    result = ''
    content = """Chengdu, the capital of China's southwest Sichuan Province, is famed for being the home of cute giant pandas. Apart from the Panda Research base, Chengdu has a lot of other attractions. It is known for its spicy Sichuan cuisine and ancient history, including the site of the ancient Jinsha civilization and the Three Kingdoms-era Wuhou Shrine. The city also features beautiful natural landscapes such as Mount Qingcheng and the Dujiangyan Irrigation System, both UNESCO World Heritage Sites."""
    target_path = './data/b.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    with open(target_path, 'w') as f:
        f.write(content)
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent.default(workspace=workspace)
    memory_node_id = agent.run('what is in ./data/b.txt', output_callback=get_output_callback())
    for _ in range(2):
        if 'Mount Qingcheng' in result:
            break
        agent.run('OK', output_callback=get_output_callback())
    assert 'Mount Qingcheng' in result
    assert memory_node_id == None
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
    global result
    result = ''
    if os.path.exists(workspace): shutil.rmtree(workspace)
    os.mkdir(workspace)
    agent = Agent.with_functions([get_weather], workspace=workspace)
    agent.hide_output_parse = False
    agent.run("what's the weather of Chengdu ?", output_callback=get_output_callback())
    for _ in range(2):
        if 'sunny' in result:
            break
        agent.run('OK', output_callback=get_output_callback())
    assert 'good, sunny' in result
    # assert os.path.exists(serialize_path)
    shutil.rmtree(workspace)



if __name__ == '__main__':
    test_math()
    test_write_file()
    test_read_file()
    test_functions()