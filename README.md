# GeneralAgent: From LLM to Agent
<p align="center">简单、通用、统一、兼容基础 LLM 的 Agent</p>

<p align="center">
<a href="docs/README_CN.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a>
<a href="README.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
</p>

## Architecture

![Architecture](docs/images/Architecture.png)

## Features

  - Agent with GPT-3.5 is stable
  - Use GeneralAgent simply as use ChatGPT
  - Stacked Memory and Plan
  - Input Interpreter
  - Retrieve Interpreter
  - Output Interpreter
      - File Operation at line level: read、write、delete
      - Python: write python code to 解决数学、访问网络、本地文件操作等工作
      - AppleScript: Control your Mac computer
      - Shell: Control your computer

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

安装后，你可以在命令行中直接使用:

```bash
GeneralAgent
```

或者在你的python项目中使用: 

```python
from GeneralAgent.agent import Agent
workspace = './test'
agent = Agent.default_agent(workspace=workspace)

```
