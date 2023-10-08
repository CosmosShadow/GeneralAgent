<h1 align="center">GeneralAgent: From LLM to Agent</h1>
<p align="center">
<a href="README.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
<a href="README_CN.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a>
<img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white&style=flat" alt="License"/>
</p>
<p align='center'>
A simple, general, customizable Agent framework
</p>

![Architecture](./docs/images/Architecture.png)

* LLM serves as the brain, and Interpreters serve as sensors such as hands, feet, and eyes, forming a general agent.
* Let a single LLM understand the overall situation, thoughts become actions in nature, and GPT-3.5 can also run stably
* Support serialization, including memory, interpreter state (such as python), plan, recall content, etc.
* Customize the agent by customizing three parsers: input, output, and recall

## Demo

coming soon

## Installation

install from pip:

```bash
pip install GeneralAgent
```

install from source code:

```shell
git clone https://github.com/CosmosShadow/GeneralAgent
cd GeneralAgent
python setup.py install
```



## Configuration

Configure necessary environment variables ([test/.env.example](test/.env.example))

```shell
# Configure OpenAI API Key
export OPENAI_API_KEY='xx'
```

not necessary

```shell
# OpenAI Request URL
export OPENAI_API_BASE='https://api.openai.com/v1'
# MLL Model, defualt gpt-3.5-turbo
export OPENAI_API_MODEL='gpt-3.5-turbo'

# cache llm inference and embedding, useful when develop and debug
export LLM_CACHE='no' # otherwise yes
export LLM_CACHE_PATH='./llm_cache.json'

# google search tool at https://google.serper.dev
export SERPER_API_KEY='xxx'

# Whether to automatically run python, shell, applescript and other codes
# Default no: n
export AUTO_RUN='y' # y or n
```



## Usage

### Command Line

Use in command line

```bash
GeneralAgent
```

Optional parameters:

```shell
GeneralAgent --workspace ./test --logging DEBUG --auto_run --new --model gpt-4
# worksapce: Set workspace directory, default ./general_agent/data
# logging: set logging level: DEBUG, INFO, WARNING, ERROR, default ERROR
# auto_run: Enable auto run code like python、shell、applescript
# new: if workspace exists, create a new workspace
# model: OpenAI model, default gpt-3.5-turbo, you can use others
```



### Python

#### Basic LLM functions

[examples/act_as_llm.py](examples/act_as_llm.py)

```python
import asyncio
from GeneralAgent.agent import Agent

async def main():
    agent = Agent.act_as_llm()
    while True:
        input_conent = input('>>>')
        await agent.run(input_conent)

if __name__ == '__main__':
    asyncio.run(main())
```



#### Default Agent

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



#### Custom Interpreter
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



#### Custom output
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



#### Serialization

All the status of the agent is saved in the workspace directory in real time and only needs to be reloaded.

```python
agent = Agent.default(workspace='./test')
await agent.run('Hi, My Name is Chen Li').


agent = None
agent = Agent.default(workspace('./test'))
await agent.run('What is my Name?')
# expect to output Chen Li
```



### Built-in interpreter

* File Interperter: Read, write, delete by line, can support code writing, etc.
* Plan Interpreter: Complete multi-step complex tasks, such as completing a business plan, through stack memory and planning
* Retrieve Interpreter: Retrieve the document after embedding it
* Python Interpreter
  * Can complete mathematical calculations, access the network, file operations (PDF to pictures, write PPT, batch conversion of picture formats...), etc.
  * Python code snippets share the same namespace, that is, they can access each other's variables, functions, and all other serializable content.
  * Tool usage: Able to call various tool APIs, model APIs, etc.
* AppleScript Interpreter: Operate the Mac operating system to achieve tasks such as switching to Dark mode, opening websites, and sending emails.
* Shell Interpreter: Operate the computer to install docker, node.js, python libraries, set up scheduled tasks and other tasks