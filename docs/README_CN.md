# GeneralAgent: From LLM to Agent
<p align="center">一个简单、通用的Agent框架</p>

<p align="center">
<a href="docs/README_CN.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a>
<a href="README.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
</p>
## 架构

![架构](./images/Architecture.png)



## 特性

* 以LLM为中心来构建Agent
    * 尽量让Agent知道所有事情，做所有决定
    * 让Agent心想事成: 所想即所得
    * GPT3.5也能稳定运行
  * 支持序列化，包括python执行环境

* 内置Interpreter
    * File Interperter: 按行进行 读取、写入、删除，能够支持比如代码编写等
    * Plan Interpreter: 通过堆栈记忆和计划，完成多个步骤的复杂任务，比如完成一份商业计划书
    * Retrieve Interpreter: 对文档进行embedding后进行检索
    * Python Interpreter
        * 可以完成数学计算、访问网络、文件操作(PDF转图片、写PPT、图片格式批量转换...)等
        * python代码片段间共享同一个命名空间，即可以互相访问变量、函数等所有可以序列化的内容
        * 工具使用: 能够调用各种工具API、模型API等
  * AppleScript Interpreter: 操作Mac操作系统，实现Dark模式切换、网站打开、发送邮件等任务
  * Shell Interpreter: 操作电脑，实现安装docker、node.js、python库，设置定时任务等任务




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



## 环境变量

参考 [test/.env.example](test/.env.example)

必须

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

命令行中使用:

```bash
GeneralAgent
```

在python中使用 [./examples/basic.py](./examples/basic.py)

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

或者定制你自己的agent



## 加入我们

微信扫码

<p align="center">
<img src="./images/wechat.jpg" alt="wechat" width=400/>
</p>