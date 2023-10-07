# GeneralAgent: From LLM to Agent
<p align="center">简单、通用、统一、兼容基础 LLM 的 Agent</p>

<p align="center">
<a href="docs/README_CN.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a>
<a href="README.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
</p>
## 架构

![架构](./images/Architecture.png)





## 特性

  - 从Agent本身的视角来构建Agent
  - 兼容GPT3.5，当然GPT-4更好
  - 像使用ChatGPT一样，使用GeneralAgent
  - 堆栈记忆和计划
  - Input Interpreter
  - Retrieve Interpreter
  - Output Interpreter
      - 文件行级别操作: 读取、写入、删除
      - python执行: 数学计算、访问网络、本地文件操作等
      - AppleScript执行: 操作Mac电脑完成各种任务，比如Dark模式切换、网站打开、发送邮件等
      - Shell: 




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
