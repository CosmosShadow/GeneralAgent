# GeneralAgent: From LLM to Agent

GeneralAgent是一个python原生的Agent框架，可以配置角色、工具(函数)、知识库来快速生成Agent，并通过agent.run来执行命令和输出结构化内容。

GeneralAgent有以下特性:

* GeneralAgent 不依赖大模型的 function call，通过python代码解释器来调用工具，可以直接传递python函数给Agent使用
* GeneralAgent 支持序列化，随用随启
* GeneralAgent 支持自我调用和堆栈记忆，用最少的大模型消耗，来完成复杂任务，请见[论文](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)
* GeneralAgent 开发的应用，可以通过 [AgentServer(开源准备中)](https://github.com/CosmosShadow/AgentServer) 进行部署，快速给大规模用户提供Agent服务


## 安装

```bash
pip install GeneralAgent
```



## 使用

### 函数调用

```python
# 函数调用
from GeneralAgent.agent import Agent
from GeneralAgent import skills

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

### 序列化

````python
# 序列化
from GeneralAgent.agent import Agent

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
# 写小说
from GeneralAgent.agent import Agent
from GeneralAgent import skills

agent = Agent('你是一个小说家')
# topic = skills.input('请输入小说的名称和主题: ')
topic = '小白兔吃糖不刷牙的故事'
summary = agent.run(f'小说的名称和主题是: {topic}，扩展和完善一下小说概要。要求具备文艺性、教育性、娱乐性。', return_type=str)
chapters = agent.run('输出小说的章节名称和每个章节的概要，返回列表 [(chapter_title, chapter_summary), ....]', return_type=list)
contents = []
for index, (chapter_title, chapter_summary) in enumerate(chapters):
    content = agent.run(f'对于章节: {chapter_title}\n{chapter_summary}. \n输出章节的详细内容，注意只返回内容，不要标题。', return_type=str)
    content = '\n'.join([x.strip() for x in content.split('\n')])
    contents.append(content)
with open('novel.md', 'w') as f:
    for index in range(len(chapters)):
        f.write(f'### {chapters[index][0]}\n')
        f.write(f'{contents[index]}\n\n')
skills.output('你的小说已经生成[novel.md](novel.md)\n')

# 删除Agent: 记忆文件 + python序列化状态
# agent.delete()
```

### 多Agent

```python
# 多Agent配合完成任务
from GeneralAgent.agent import Agent
story_writer = Agent('你是一个故事创作家，根据大纲要求或者故事梗概，返回一个更加详细的故事内容。')
humor_enhancer = Agent('你是一个润色作家，将一个故事进行诙谐润色，增加幽默元素。直接输出润色后的故事，不用python代码来实现。')

# topic = skills.input('请输入小说的大纲要求或者故事梗概: ')
topic = '写个小白兔吃糖不刷牙的故事，有教育意义。'
initial_story = story_writer.run(topic)
enhanced_story = humor_enhancer.run(initial_story)
print(enhanced_story)
```

更多例子请见[examples](./examples)



## 论文

[General Agent：自调用和堆栈内存](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)



## 加入我们

使用微信扫描下方二维码

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>