# GeneralAgent: From LLM to Agent

<p align="center">
<a href="README.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a>
<a href="README_EN.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
</p>

GeneralAgent是一个Python原生的Agent框架，旨在将大型语言模型 与 Python 无缝集成。



**主要特性**

* **工具调用**：GeneralAgent 不依赖大模型的 function call，通过python代码解释器来调用工具。
* **序列化**：GeneralAgent 支持序列化，包括记忆和python执行状态，随用随启
* **自我调用(探索)**：GeneralAgent通过自我调用和堆栈记忆，最小化大模型的调用次数，来高效处理复杂任务。更多详情请见我们的 [论文](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)
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
# export OPENAI_API_BASE=your_openai_base_url
# using with not openai official server or using other OpenAI API formate LLM server such as deepseek, zhipu(chatglm),qwen, etc.
```



或者在代码中配置

```python
from GeneralAgent import Agent
agent = Agent('You are a helpful agent.', api_key='sk-xxx')
```



## 使用

### 快速开始

```python
from GeneralAgent import Agent

agent = Agent('你是一个AI助手')
while True:
    query = input('请输入: ')
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
# Output: Your name is Shadow. How can I help you today, Shadow?

# agent: 清除记忆 + python序列化状态
agent.clear()

agent.user_input('What is my name?')
# Output: I'm sorry, but I don't have access to your personal information, including your name. How can I assist you today?

import shutil
shutil.rmtree(workspace)
```



### 写小说

```python
# 写小说
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




### 多模态输入

user_input 的 input 参数，和 run 的 command 参数，支持字符串或者数组。

数组时支持多模态，格式为最简模式: ['text_content', {'image': 'path/to/image'}, ...]

```python
# 支持多模态: 图片输入
from GeneralAgent import Agent

agent = Agent('You are a helpful assistant.')
agent.user_input(['what is in the image?', {'image': '../docs/images/self_call.png'}])
```



### 大模型切换

#### OpenAI SDK

得益于GeneralAgent框架不依赖大模型厂商的 function call 能力实现了函数调用，可以无缝切换不同的大模型实现相同的能力。

GeneralAgent框架使用OpenAI Python SDK 来支持其他大模型。

```python
from GeneralAgent import Agent

agent = Agent('You are a helpful agent.', model='deepseek-chat', token_limit=32000, api_key='sk-xxx', base_url='https://api.deepseek.com/v1')
agent.user_input('介绍一下成都')
```

详情见: [examples/8_multi_model.py](./examples/8_multi_model.py)


#### Azure OpenAI 

```python
from GeneralAgent import Agent

# api_key = os.getenv("OPENAI_API_KEY")
# base_url = os.getenv("OPENAI_API_BASE")
api_key = '8ef0b4df45e444079cd5xxx' # Azure API Key or use OPENAI_API_KEY environment variable
base_url = 'https://xxxx.openai.azure.com/' # Azure API Base URL or use OPENAI_API_BASE environment variable
model = 'azure_cpgpt4' # azure_ with model name, e.g. azure_cpgpt4
# azure api_version is default to '2024-05-01-preview'. You can set by environment variable AZURE_API_VERSION

agent = Agent('You are a helpful assistant', api_key=api_key, base_url=base_url, model=model)
while True:
    query = input('Please input your query:')
    agent.user_input(query)
    print('-'*50)
```


#### OneAPI

如果其他大模型不支持OpenAI SDK，可以通过 https://github.com/songquanpeng/one-api 来支持。


#### 自定义大模型

或者重写 GeneralAgent.skills 中 llm_inference 函数来使用其他大模型。

```python
from GeneralAgent import skills
def new_llm_inference(messages, model, stream=False, temperature=None, api_key=None, base_url=None):
    """
    使用大模型进行推理
    """
    pass
skills.llm_inference = new_llm_inference
```



### 禁用Python运行

默认 GeneralAgent 自动运行 LLM 输出的python代码。

某些场景下，如果不希望自动运行，设置 `disable_python_run` 为 `True` 即可。

```python
from GeneralAgent import Agent

agent = Agent('你是一个python专家，辅助用户解决python问题。')
agent.disable_python_run = True
agent.user_input('用python实现一个读取文件的函数')
```

### 隐藏python运行

在正式的业务场景中，不希望用户看到python代码的运行，而只是看到最终结果，可以设置 `hide_python_code` 为 `True`。

```python
from GeneralAgent import Agent
agent = Agent('You are a helpful assistant.', hide_python_code=True)
agent.user_input('caculate 0.999 ** 1000')
```



### AI搜索

```python
# AI搜索
# 运行前置条件: 
# 1. 请先配置环境变量 SERPER_API_KEY (https://serper.dev/ 的API KEY)；
# 2. 安装 selenium 库: pip install selenium

from GeneralAgent import Agent
from GeneralAgent import skills

google_results = []

# 步骤1: 第一次google搜索
question = input('请输入问题，进行 AI 搜索: ')
# question = '周鸿祎卖车'
content1 = skills.google_search(question)
google_results.append(content1)

# 步骤2: 第二次google搜索: 根据第一次搜索结构，获取继续搜索的问题
agent = Agent('你是一个AI搜索助手。')
querys = agent.run(f'用户问题: \n{question}\n\n搜索引擎结果: \n{content1}\n\n。请问可以帮助用户，需要继续搜索的关键短语有哪些(最多3个，且和问题本身不太重合)？返回关键短语列表变量([query1, query2])', return_type=list)
print(querys)
for query in querys:
    content = skills.google_search(query)
    google_results.append(content)

# 步骤3: 提取重点网页内容
agent.clear()
web_contents = []
google_result = '\n\n'.join(google_results)
urls = agent.run(f'用户问题: \n{question}\n\n搜索引擎结果: \n{google_result}\n\n。哪些网页对于用户问题比较有帮助？请返回最重要的不超过5个的网页url列表变量([url1, url2, ...])', return_type=list)
for url in urls:
    content = skills.web_get_text(url, wait_time=2)
    web_contents.append(content)

# 步骤4: 输出结果
agent.clear()
web_content = '\n\n'.join(web_contents)
agent.run(f'用户问题: \n{question}\n\n搜索引擎结果: \n{google_result}\n\n部分网页内容: \n{web_content}\n\n。请根据用户问题，搜索引擎结果，网页内容，给出用户详细的回答，要求按一定目录结构来输出，并且使用markdown格式。')
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