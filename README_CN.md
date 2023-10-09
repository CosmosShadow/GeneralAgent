<h1 align="center">GeneralAgent: From LLM to Agent</h1>
<p align="center">
<a href="README.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
<a href="README_CN.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a>
<img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white&style=flat" alt="License"/>
</p>
<p align='center'>
一个简单、通用、可定制的Agent框架
</p>

![架构](./docs/images/Architecture.png)

* 从 LLM 到 Agent
    * 让单一LLM知道所有事情
    * 所思即所得，即时行动
    * 接收外部反馈，自助决策
* GPT-3.5也可以稳定运行
* 支持通过解释器、角色系统提示词和工具来定制化Agent
* 支持序列化
* 内置解释器: Python, AppleScript, Shell, File, Plan, Retrieve等
* 内置工具: google search, wikipedia_search, scrabe web

## Demo



https://github.com/CosmosShadow/GeneralAgent/assets/13933465/9d9b4d6b-0c9c-404d-87d8-7f8e03f3772b



## 安装

```bash
pip install GeneralAgent
```

或者

```shell
git clone https://github.com/CosmosShadow/GeneralAgent
cd GeneralAgent
python setup.py install
```



## 使用

### 命令行

在命令行中使用

```bash
GeneralAgent
```

可选参数:

```shell
GeneralAgent --workspace ./test --new
# worksapce: Set workspace directory, default ./general_agent_data
# new: if workspace exists, create a new workspace
```



### Python

#### 基础Agent

[examples/empty.py](examples/empty.py)

基础Agent，只包含角色解释器(RoleInterpreter)和记忆，像一个基础的LLM聊天机器人

```python
import asyncio
from GeneralAgent.agent import Agent

async def main():
    agent = Agent.empty()
    while True:
        input_conent = input('>>>')
        await agent.run(input_conent)

if __name__ == '__main__':
    asyncio.run(main())
```



#### 默认Agent

[examples/default_agent.py](examples/default_agent.py)

```python
import asyncio
from GeneralAgent.agent import Agent

async def main():
    agent = Agent.default()
    while True:
        input_conent = input()
        await agent.run(input_conent)

if __name__ == '__main__':
    asyncio.run(main())
```



#### 定制解析器

[examples/custom.py](examples/custom.py)

```python
import re
import asyncio
from GeneralAgent.agent import Agent
from GeneralAgent.interpreter import Interpreter
from GeneralAgent.utils import confirm_to_run

python_prompt = """
# Run python
* Remember use print() to output
* format is : ```python\\nthe_code\\n```
* the code will be executed
* python version is 3.9
"""

class BasicPythonInterpreter(Interpreter):
    @property
    def match_template(self) -> bool:
        return  r'```python\n([\s\S]*)\n```'

    def parse(self, string) -> (str, bool):
        pattern = re.compile(self.match_template, re.DOTALL)
        code = pattern.search(string).group(1)
        if confirm_to_run():
            exec(code)
        return '' , False

    def prompt(self, messages) -> str:
        return python_prompt

    def match(self, string) -> bool:
        super().match(string)


async def main():
    agent = Agent(output_interpreters=[BasicPythonInterpreter()])
    while True:
        input_conent = input('>>>')
        await agent.run(input_conent)

if __name__ == '__main__':
    asyncio.run(main())
```



#### 定制输出

[examples/custom_output.py](examples/custom_output.py)

```python
import asyncio
from GeneralAgent.agent import Agent

async def custom_output(token):
    if token is None:
        print('[output end]')
    else:
        print(token, end='', flush=True)

async def main():
    agent = Agent.default('./basic')
    while True:
        input_conent = input('>>>')
        await agent.run(input_conent, output_recall=custom_output)

if __name__ == '__main__':
    asyncio.run(main())
```

#### 定制系统提示词

默认系统提示词定义在 RoleInterpreter [GeneralAgent/interperters/role_interperter.py](GeneralAgent/interperters/role_interperter.py)

```python
"""
Now: {{now}}
You are GeneralAgent, a agent on the {{os_version}} computer to help the user solve the problem.
Remember, you can control the computer and access the internet.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first simply and clearly.
You can use the following skills to help you solve the problem directly without explain and ask for permission: 
"""
```

你可以设置自己的系统提示词:

```python
RoleInterpreter(system_prompt='xxxx')
```

或者通过继承RoleInterpreter来定制自己的系统提示词:



#### 给Agent添加工具

[examples/add_tools.py](examples/add_tools.py)

以下进行举例:
定义一个工具，获取城市的天气 [examples/tool_get_weather.py](examples/tool_get_weather.py)

```python
def get_weather(city:str):
    """
    get weather from city
    """
    return 'weather is good, sunny.'
```

然后，将工具添加到PythonInterperter中，Agent会自动使用PythonInterperter中的工具。
注意，PythonInterperter和当前程序不在同一个命名空间，所以需要在PythonInterperter中import对应的函数，即定义import_code。

```python
import asyncio
from GeneralAgent.tools import Tools
from GeneralAgent.agent import Agent
from GeneralAgent.interpreter import PythonInterpreter
from tool_get_weather import get_weather

import_code = """
import os, sys, math
from tool_get_weather import get_weather
"""

async def main():
    workspace = './'
    tools = Tools([get_weather])
    python_interpreter = PythonInterpreter(tools=tools, import_code=import_code)
    agent = Agent(workspace, input_interpreters=[], output_interpreters=[python_interpreter])
    while True:
        input_conent = input('>>>')
        await agent.run(input_conent)

if __name__ == '__main__':
    asyncio.run(main())
```

```
[lichen@examples]$ python add_tools.py
>>>what's the weather of chengdu?

To get the weather of Chengdu, we can use the `get_weather` function provided in the prompt. Here's the code to get the weather of Chengdu:

\`\`\`python
weather = get_weather('Chengdu')
print(weather)
\`\`\`


weather is good, sunny.

Glad to hear that the weather in Chengdu is good and sunny! Is there anything else I can help you with?
>>>Is there anything else I can help you with?
>>>
```



#### 序列化

agent的所有状态实时保存在workspace目录下，只需重新加载即可.

```python
agent = Agent.default(workspace='./test')
await agent.run('Hi, My Name is Chen Li').


agent = None
agent = Agent.default(workspace('./test'))
await agent.run('What is my Name?')
# expect to output Chen Li
```

## 配置

通过环境变量，配置Agent (参考: [.env.example](.env.example))

```shell
# 配置OpenAI的API Key
export OPENAI_API_KEY='xx'

# OpenAI Request URL
export OPENAI_API_BASE='https://api.openai.com/v1'
# MLL Model, defualt gpt-3.5-turbo
export OPENAI_API_MODEL='gpt-3.5-turbo'
# model temperature, default 0.5
TEMPERATURE=0.5

# cache llm inference and embedding, useful when develop and debug
export LLM_CACHE='no' # otherwise yes
export LLM_CACHE_PATH='./llm_cache.json'

# google search tool at https://google.serper.dev
export SERPER_API_KEY='xxx'

# 是否自动运行python、shell、applescript等代码
# 默认否: n
export AUTO_RUN='y' # y or n
```




## 加入我们

微信扫码

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>

discord is comming soon.