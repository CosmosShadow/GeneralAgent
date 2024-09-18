from GeneralAgent import Agent
from GeneralAgent import skills

def test_math():
    """数学计算测试. 使用run直接返回python表达式的值"""
    agent = Agent()
    result = agent.run('calculate 0.99 ** 1000', return_type=float)
    assert 4.317124741065786e-05 == result

def test_function():
    """函数调用测试"""
    def get_weather(city: str) -> str:
        """
        get weather information
        @city: str, city name
        @return: str, weather information
        """
        return f"{city} weather: sunny"
    agent = Agent('你是一个天气小助手', functions=[get_weather])
    result = agent.user_input('成都天气怎么样？')
    assert '晴' in result or 'sunny' in result

def test_write_novel():
    # 工作流: 写小说
    novel_path = 'novel.md'
    # 清理掉已经有的小说
    import os
    if os.path.exists(novel_path):
        os.remove(novel_path)
    try:

        # 步骤0: 定义Agent
        agent = Agent('你是一个小说家')

        # 步骤1: 从用户处获取小说的名称和主题
        # topic = skills.input('请输入小说的名称和主题: ')
        topic = '小白兔吃糖不刷牙的故事'

        # 步骤2: 小说的概要
        summary = agent.run(f'小说的名称和主题是: {topic}，扩展和完善一下小说概要。要求具备文艺性、教育性、娱乐性。')

        # 步骤3: 小说的章节名称和概要列表
        chapters = agent.run('输出小说的章节名称和每个章节的概要，返回列表 [(chapter_title, chapter_summary), ....]', return_type=list)

        # 步骤4: 生成小说每一章节的详细内容
        contents = []
        for index, (chapter_title, chapter_summary) in enumerate(chapters):
            content = agent.run(f'对于章节: {chapter_title}\n{chapter_summary}. \n输出章节的详细内容，注意只返回内容，不要标题。')
            content = '\n'.join([x.strip() for x in content.split('\n')])
            contents.append(content)

        # 步骤5: 将小说格式化写入文件
        with open(novel_path, 'w') as f:
            for index in range(len(chapters)):
                f.write(f'### {chapters[index][0]}\n')
                f.write(f'{contents[index]}\n\n')

    except Exception as e:
        pass
    finally:
        # 验证小说存在，而且内容不为空
        assert os.path.exists(novel_path)
        with open(novel_path, 'r') as f:
            content = f.read()
            assert content != ''
            assert '### ' in content
        # 清理掉
        if os.path.exists(novel_path):
            os.remove(novel_path)

def test_knowledge():
    # 知识库
    workspace = '9_knowledge_files'
    try:
        files = ['../docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf']
        agent = Agent('你是AI助手，用中文回复。', workspace=workspace, knowledge_files=files)
        result = agent.user_input('Self call 是什么意思？')
        assert 'LLM' in result
    except Exception as e:
        raise e
    finally:
        # 清理掉
        import shutil
        shutil.rmtree(workspace)


def test_with_query_clear_data_0():
    workspace = 'test_with_query_clear_data_0'
    import os
    if os.path.exists(workspace):
        import shutil
        shutil.rmtree(workspace)
    agent = Agent('You are a helpful assistant.', workspace=workspace)
    with agent.temporary_context():
        agent.user_input('My name is Henry.')
    import json
    with open(f'{workspace}/memory.json', 'r') as f:
        memory = json.load(f)
        assert len(memory) == 0


def test_with_query_clear_data_1():
    agent = Agent('You are a helpful assistant.', hide_python_code=True)
    with agent.temporary_context():
        agent.user_input('My name is Henry.')
    response = agent.user_input("What's my name?")
    assert 'Henry' not in response


def test_with_query_save_data():
    workspace = 'test_with_query_save_data'
    import os
    if os.path.exists(workspace):
        import shutil
        shutil.rmtree(workspace)
    agent = Agent('You are a helpful assistant.', workspace=workspace)
    agent.user_input('My name is Henry.')
    with agent.temporary_context():
        agent.user_input('My name is Jimmy.')
    agent.user_input('My name is Yummy.')
    import json
    with open(f'{workspace}/memory.json', 'r') as f:
        memory = json.load(f)
        assert len(memory) == 4


def test_with_query_clear_data_with_exception_0():
    workspace = 'test_with_query_clear_data_with_exception_0'
    import os
    if os.path.exists(workspace):
        import shutil
        shutil.rmtree(workspace)
    try:
        agent = Agent('You are a helpful assistant.', workspace=workspace)
        with agent.temporary_context():
            agent.user_input('My name is Henry.')
            raise Exception('test exception')
    except Exception:
        ...
    finally:
        import json
        with open(f'{workspace}/memory.json', 'r') as f:
            memory = json.load(f)
            assert len(memory) == 0


def test_with_query_clear_data_with_exception_1():
    workspace = 'test_with_query_clear_data_with_exception_1'
    import os
    if os.path.exists(workspace):
        import shutil
        shutil.rmtree(workspace)
    try:
        agent = Agent('You are a helpful assistant.', workspace=workspace)
        agent.user_input('My name is Yummy.')
        with agent.temporary_context(): # no_memory()
            agent.user_input('My name is Henry.')
            raise Exception('test exception')
    except Exception:
        ...
    finally:
        import json
        with open(f'{workspace}/memory.json', 'r') as f:
            memory = json.load(f)
            assert len(memory) == 2


if __name__ == '__main__':
    test_math()
