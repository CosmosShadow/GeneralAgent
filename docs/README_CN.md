# GeneralAgent: From LLM to Agent
<p align="center">简单、通用、统一、兼容基础 LLM 的 Agent</p>

<p align="center">
<a href="docs/README_CN.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a>
<a href="README.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
</p>
## 架构

![架构](./images/Architecture.png)



## 特性

* 以LLM为中心来构建Agent
    * 增强单一Agent本身的能力，而非通过多个Agent来完成一个简单的任务
    * 单一Agent知道所有发生的事情、决定所有的事情
    * 让Agent心想事成: 所想即所行
    * 兼容比较基础的LLM，GPT3.5也能稳定运行，当然GPT-4更好
  * 支持序列化: 包括记忆、python执行环境、文档阅读等等

* 内置各种Interpreter
    * File Interperter: 按行进行 读取、写入、删除，能够支持比如代码编写等
    * Plan Interpreter: 通过堆栈记忆和计划，完成多个步骤的复杂任务，比如完成一份商业计划书
    * Retrieve Interpreter: 对文档进行embedding后进行检索
    * Python Interpreter
        * 可以完成数学计算、访问网络、文件操作(PDF转图片、写PPT、图片格式批量转换...)等
        * python代码片段间共享同一个命名空间，即可以互相访问变量、函数等所有可以序列化的内容
        * 工具使用: 能够调用各种工具API、模型API等
  * AppleScript Interpreter: 操作Mac电脑完成各种任务，比如Dark模式切换、网站打开、发送邮件等
  * Shell Interpreter: 执行命令行



## 警告!

默认情况下，GeneralAgent可能会由用户触发或者自动执行一些比较危险的操作，比如文件删除等。




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

命令行中使用:

```bash
GeneralAgent
```

python项目中使用

```python
from GeneralAgent.agent import Agent
agent = Agent.default(workspace='./test')
while True:
  question = input()
	agent.run(question)
```



## 加入我们

微信扫码

