# GeneralAgent: From LLM to Agent

GeneralAgent是一个Python原生的Agent框架，旨在将大型语言模型 与 Python 无缝集成。



**主要特性**

* **工具调用**：GeneralAgent 不依赖大模型的 function call，通过python代码解释器来调用工具。
* **序列化**：GeneralAgent 支持序列化，包括记忆和python执行状态，随用随启
* **自我调用**：GeneralAgent通过自我调用和堆栈记忆，最小化大模型的调用次数，来高效处理复杂任务。更多详情请见我们的 [论文](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)
* **部署服务**：使用 [AgentServer(即将开源)](https://github.com/CosmosShadow/AgentServer) 部署 Agent，快速为大规模用户提供服务。



使用GeneralAgent，您可以：

* 快速配置角色、函数和知识库，创建Agent。
* 执行稳定的复杂业务流程，协调多个Agent完成任务。
* 使用 `agent.run` 函数执行命令并产生结构化输出，超越简单的文本响应。
* 使用 `agent.user_input` 函数与用户进行动态交互。



## 安装

```bash
pip install GeneralAgent
```



## 配置

参考 [.env.example](./.env.example) 文件，配置大模型的Key或者其他参数

```bash
export OPENAI_API_KEY=your_openai_api_key
```



或者在代码中配置

```python
from GeneralAgent import Agent
agent = Agent('You are a helpful agent.', api_key='sk-xxx')
```



## 使用

### 基础应用

```python
# 基础应用
from GeneralAgent import Agent

# 流式输出中间结果
def output_callback(token):
    token = token or '\n'
    print(token, end='', flush=True)

agent = Agent('你是AI助手，用中文回复。', output_callback=output_callback)
while True:
    query = input('请输入或者回车结束：')
    agent.user_input(query)
    print('-'*50)
```



### 函数调用

```python
# 函数调用
from GeneralAgent import Agent

# 函数: 获取天气信息
def get_weather(city: str) -> str:
    """
    get weather information
    @city: str, city name
    @return: str, weather information
    """
    return f"{city} weather: sunny"


agent = Agent('你是一个天气小助手', functions=[get_weather])
agent.user_input('成都天气怎么样？')

# 输出
# ```python
# city = "成都"
# weather_info = get_weather(city)
# weather_info
# ```
# 成都的天气是晴天。
# 请问还有什么我可以帮忙的吗？
```



### 知识库

```python
# 知识库
from GeneralAgent import Agent

knowledge_files = ['../docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf']
agent = Agent('你是AI助手，用中文回复。', workspace='9_knowledge_files', knowledge_files=knowledge_files)
agent.user_input('Self call 是什么意思？')
```

知识库默认使用 GeneralAgent.skills 中 embedding_texts 函数来对文本进行 embedding (默认是OpenAI的text-embedding-3-small模型)

你可以重写 embedding_texts 函数，使用其他厂商 或者 本地的 embedding 方法，具体如下:

```python
def new_embedding_texts(texts) -> [[float]]:
    """
    对文本数组进行embedding
    """
    # 你的embedding方法
    return result
from GeneralAgent import skills
skills.embedding_texts = new_embedding_texts
```



### 序列化

```python
# 序列化
from GeneralAgent import Agent

# agent序列化位置，运行过程中会自动保存LLM的messages和python解析器的状态
workspace='./5_serialize'

role = 'You are a helpful agent.'
agent = Agent(workspace=workspace)
agent.user_input('My name is Shadow.')

agent = None
agent = Agent(role, workspace=workspace)
agent.user_input('What is my name?')

# Ooutput: Your name is Shadow. How can I help you today, Shadow?

# 删除agent: 记忆 + python序列化状态
agent.delete()
```



### 工作流

```python
# 工作流: 写小说
from GeneralAgent import Agent
from GeneralAgent import skills

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
with open('novel.md', 'w') as f:
    for index in range(len(chapters)):
        f.write(f'### {chapters[index][0]}\n')
        f.write(f'{contents[index]}\n\n')

# 步骤6(可选): 将markdown文件转换为pdf文件

# 步骤7: 输出小说文件给用户
skills.output('你的小说已经生成[novel.md](novel.md)\n')
```



### 多Agent

```python
# 多Agent配合完成任务
from GeneralAgent import Agent
story_writer = Agent('你是一个故事创作家，根据大纲要求或者故事梗概，返回一个更加详细的故事内容。')
humor_enhancer = Agent('你是一个润色作家，将一个故事进行诙谐润色，增加幽默元素。直接输出润色后的故事')

# 禁用Python运行
story_writer.disable_python_run = True
humor_enhancer.disable_python_run = True

# topic = skills.input('请输入小说的大纲要求或者故事梗概: ')
topic = '写个小白兔吃糖不刷牙的故事，有教育意义。'
initial_story = story_writer.run(topic)
enhanced_story = humor_enhancer.run(initial_story)
print(enhanced_story)
```



### 大模型切换

GeneralAgent框架使用OpenAI Python SDK 来支持其他大模型。

如果其他大模型不支持OpenAI SDK，则需要通过 https://github.com/songquanpeng/one-api 来支持。

得益于GeneralAgent框架不依赖大模型厂商的 function call 能力实现了函数调用，可以无缝切换不同的大模型实现相同的能力。

```python
from GeneralAgent import Agent

agent = Agent('You are a helpful agent.', model='deepseek-chat', token_limit=32000, api_key='sk-xxx', base_url='https://api.deepseek.com/v1')
agent.user_input('介绍一下成都')
```

详情见: [examples/8_multi_model.py](./examples/8_multi_model.py)



### 禁用Python运行

默认 GeneralAgent 自动运行 LLM 输出的python代码。

某些场景下，如果不希望自动运行，设置 `disable_python_run` 为 `True` 即可。

```python
from GeneralAgent import Agent

agent = Agent('你是一个python专家，辅助用户解决python问题。')
agent.disable_python_run = True
agent.user_input('用python实现一个读取文件的函数')
```



### 更多

更多例子请见 [examples](./examples)





## 论文

[General Agent：Self Call and Stack Memory](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)





## 加入我们👏🏻

使用微信扫描下方二维码，加入微信群聊，或参与贡献。

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>