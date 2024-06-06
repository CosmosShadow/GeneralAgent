# GeneralAgent: From LLM to Agent

GeneralAgent是一个原生Python框架，旨在将大型语言模型（LLM）与Python无缝集成，扩展LLM的文本输入输出能力到Python代码执行领域。这种集成允许创建结构化的工作流程，并协调多个Agent执行复杂任务。

使用GeneralAgent，您可以：
* 快速配置角色、功能和知识库，创建Agent。
* 执行稳定的复杂业务流程。
* 协调多个Agent共同完成任务。
* 使用 `agent.run` 函数执行命令并产生结构化输出，超越简单的文本响应。
* 使用 `agent.user_input` 函数与用户进行动态交互。

GeneralAgent的主要特性：
* **工具调用**：GeneralAgent 不依赖大模型的 function call，通过python代码解释器来调用工具。
* **序列化**：GeneralAgent 支持序列化，包括记忆和python执行状态，随用随启
* **自我调用**：GeneralAgent通过自我调用和堆栈记忆最小化大模型的调用次数使高效处理复杂任务。更多详情请见我们的[论文](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)
* **部署就绪**：使用GeneralAgent或者其他Agent框架开发的应用可以通过 [AgentServer(即将开源)](https://github.com/CosmosShadow/AgentServer)部署，快速为大规模用户提供Agent服务。

该框架赋予开发者在强大且多功能的Python环境中利用LLM的认知能力，增强基于Agent的应用的自动化和智能性。



## 安装

```bash
pip install GeneralAgent
```



## 使用

### 函数调用

```python
# 函数调用
from GeneralAgent.agent import Agent

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

```python
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



更多例子请见 [examples](./examples)



## 论文

[General Agent：自调用和堆栈内存](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)



## 加入我们

使用微信扫描下方二维码

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>