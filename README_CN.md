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

* LLM作为大脑，Interpreters作为手脚、眼睛等传感器，构成一个通用的agent
* 让单一LLM了解全局、心想事成、GPT-3.5也能稳定运行
* 支持序列化，包括记忆、解释器状态(比如python)、计划、召回内容等
* 通过定制输入、输出、召回三种解析器，定制agent

## Demo

coming soon


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



## 配置

配置必须的环境变量 ([test/.env.example](test/.env.example))

```shell
# 配置OpenAI的API Key
export OPENAI_API_KEY='xx'
```

非必须

```shell
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



### 内置解析器

* File Interperter: 按行进行 读取、写入、删除，能够支持比如代码编写等
* Plan Interpreter: 通过堆栈记忆和计划，完成多个步骤的复杂任务，比如完成一份商业计划书
* Retrieve Interpreter: 对文档进行embedding后进行检索
* Python Interpreter
    * 可以完成数学计算、访问网络、文件操作(PDF转图片、写PPT、图片格式批量转换...)等
    * python代码片段间共享同一个命名空间，即可以互相访问变量、函数等所有可以序列化的内容
    * 工具使用: 能够调用各种工具API、模型API等
* AppleScript Interpreter: 操作Mac操作系统，实现Dark模式切换、网站打开、发送邮件等任务
* Shell Interpreter: 操作电脑，实现安装docker、node.js、python库，设置定时任务等任务



## 加入我们

微信扫码

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>