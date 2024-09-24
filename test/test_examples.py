import os
import shutil
from unittest.mock import patch
from GeneralAgent import Agent, skills


def test_base_usage():
    agent = Agent('You are a helpful assistant.')
    with patch('builtins.print') as mock_print:
        response = agent.user_input('Your name is "Tom". Who are you?')
        assert 'Tom' in response


def test_function_call():
    def get_weather(city: str) -> str:
        print(f"{city} weather: 晴天")
    agent = Agent('你是一个天气小助手', functions=[get_weather])
    response = agent.user_input('成都天气怎么样？')
    assert '晴天' in response


def test_write_novel():
    agent = Agent('你是一个小说家')
    topic = '小白兔吃糖不刷牙的故事'
    summary = agent.run(f'小说的名称和主题是: {topic}，扩展和完善一下小说概要。要求具备文艺性、教育性、娱乐性。')
    chapters = agent.run('输出小说的章节名称和每个章节的概要，返回列表 [(chapter_title, chapter_summary), ....]',
                         return_type=list)
    contents = []
    for index, (chapter_title, chapter_summary) in enumerate(chapters):
        content = agent.run(
            f'对于章节: {chapter_title}\n{chapter_summary}. \n输出章节的详细内容，注意只返回内容，不要标题。')
        content = '\n'.join([x.strip() for x in content.split('\n')])
        contents.append(content)
    with open('novel.md', 'w') as f:
        for index in range(len(chapters)):
            f.write(f'### {chapters[index][0]}\n')
            f.write(f'{contents[index]}\n\n')
    skills.output('你的小说已经生成[novel.md](novel.md)\n')
    # 判断文件是否存在
    assert os.path.exists('novel.md')
    # 判断文件字符数量是否大于 200
    with open('novel.md', 'r') as f:
        assert len(f.read()) > 200
    # 删除文件
    os.remove('novel.md')


def test_multi_agents():
    from GeneralAgent import Agent
    story_writer = Agent('你是一个故事创作家，根据大纲要求或者故事梗概，返回一个更加详细的故事内容。')
    humor_enhancer = Agent('你是一个润色作家，将一个故事进行诙谐润色，增加幽默元素。直接输出润色后的故事')
    story_writer.disable_python_run = True
    humor_enhancer.disable_python_run = True
    topic = '写个小白兔吃糖不刷牙的故事，有教育意义。'
    initial_story = story_writer.run(topic)
    assert '小白兔' in initial_story
    enhanced_story = humor_enhancer.run(initial_story)
    assert '小白兔' in enhanced_story


def test_serialize():
    workspace = './5_serialize'
    # 如果文件存在则删除
    if os.path.exists(workspace):
        shutil.rmtree(workspace)
    role = 'You are a helpful agent.'
    agent = Agent(role, workspace=workspace)
    agent.user_input('My name is Shadow.')
    agent = Agent(role, workspace=workspace)
    response = agent.user_input('What is my name?')
    assert 'Shadow' in response
    agent.clear()
    response = agent.user_input('What is my name?')
    assert 'Shadow' not in response
    shutil.rmtree(workspace)


def test_disable_python_run():
    # 在当前目录下创建 a.txt 并写入 “My name is Henry.”
    # 如果文件存在则删除
    if os.path.exists('a.txt'):
        os.remove('a.txt')
    with open('a.txt', 'w') as f:
        f.write('My name is Henry.')
    agent = Agent('You are a helpful assistant.')
    agent.disable_python_run = True
    response = agent.user_input('帮我读取 ./a.txt 中的内容')
    assert 'Henry' not in response


def test_enable_python_run():
    # 在当前目录下创建 a.txt 并写入 “My name is Henry.”
    # 如果文件存在则删除
    if os.path.exists('a.txt'):
        os.remove('a.txt')
    with open('a.txt', 'w') as f:
        f.write('My name is Henry.')
    agent = Agent('You are a helpful assistant.')
    agent.disable_python_run = False
    response = agent.user_input('帮我读取 ./a.txt 中的内容')
    assert 'Henry' in response


def test_hide_stream(capsys):
    agent = Agent('You are a helpful assistant.')
    agent.hide_stream = False
    agent.run('一句话介绍成都', display=False)
    captured = capsys.readouterr()
    assert len(captured.out) == 0


def test_show_stream(capsys):
    agent = Agent('You are a helpful assistant.')
    agent.hide_stream = False
    agent.run('一句话介绍成都', display=True)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_deepseek_chat():
    model = 'deepseek-chat'
    token_limit = 32000
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    base_url = 'https://api.deepseek.com/v1'
    agent = Agent('You are a helpful agent.', model=model, token_limit=token_limit, api_key=api_key, base_url=base_url)
    response = agent.run('一句话介绍成都', display=False)
    print(response)
    assert '成都' in response


def test_add_knowledge_files():
    workspace = './knowledge_files'
    if os.path.exists(workspace):
        shutil.rmtree(workspace)
    file_name = "test_knowledge_file.txt"
    with open(file_name, 'w') as f:
        f.write('My name is Henry')
    files = [file_name, ]
    agent = Agent('你是AI助手，用中文回复。', workspace=workspace, knowledge_files=files)
    response = agent.user_input(['我叫什么名字？'])
    shutil.rmtree(workspace)
    os.remove(file_name)
    assert 'Henry' in response


def test_rag_function():
    def rag_function(messages):
        input = messages[-1]['content']
        print('user input:', input)
        return 'Background: GeneralAgent is a Python library for building AI assistants. It provides a simple API for building conversational agents.'
    agent = Agent('You are a helpful assistant', rag_function=rag_function)
    response = agent.user_input('What is GeneralAgent?')
    assert "GeneralAgent is a Python library" in response


def test_collection_and_store():
    role = """
    你是一个专业的导游。
    你的主要工作: 和游客讲解城市的景点。

    # 1、旅游沟通例子
    用户: 我想去成都玩
    你: 成都是一所宜居的城市，安逸的很
    用户: 成都有什么好吃的？
    你: 火锅

    当城市确认，直接输出python代码，使用 save_travel_guide_record 函数保存旅游攻略。


    travel_guide_record = \"\"\"
    城市： 成都
    美食： 火锅
    \"\"\"
    save_travel_guide_record(travel_guide_record)

    """

    stop = False

    def save_travel_guide_record(medical_record):
        with open('test_collection.txt', 'a') as f:
            f.write(medical_record)
        global stop
        stop = True
        return "旅行攻略已保存"
    # 删除文件
    if os.path.exists('test_collection.txt'):
        os.remove('test_collection.txt')
    agent = Agent(role, functions=[save_travel_guide_record], hide_python_code=True)
    agent.user_input('你想去哪玩？')
    agent.user_input("成都")
    agent.user_input("")
    with open("test_collection.txt", "r") as f:
        content = f.read()
    assert "成都" in content


def test_image_input():
    agent = Agent('You are a helpful assistant.')
    response = agent.user_input(['What animal in the picture?', {'image': './data/test.jpeg'}])
    assert 'dog' in response


def test_temporary_context():
    agent = Agent('You are a helpful assistant.')
    with agent.temporary_context():
        agent.user_input('My name is Henry.')
    response = agent.user_input("What's my name?")
    assert 'Henry' not in response


def test_load_messages():
    messages = [
        {"role": "user", "content": "My name is Yummy."},
        {"role": "assistant", "content": "Hello, Yummy! How can I assist you today?"},
    ]
    agent = Agent('You are a helpful assistant.', messages=messages)
    response = agent.user_input("What's my name?")
    assert 'Yummy' in response
