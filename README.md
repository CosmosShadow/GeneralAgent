# GeneralAgent: From LLM to Agent

* GeneralAgent 是一个python库，可以快速搭建Agent应用，嵌入到你的业务中，或者通过 [AgentServer](https://github.com/CosmosShadow/AgentServer) 进行部署，快速给大规模用户提供Agent服务
* GeneralAgent 通过python代码解释器来调用工具，不依赖大模型的 function call
* GeneralAgent 支持序列化
* GeneralAgent 支持自我调用和堆栈记忆，请见[论文](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)



## 安装

```bash
pip install GeneralAgent
```



## 使用

```python
from GeneralAgent.agent import Agent
from GeneralAgent import skills
role_prompt = """您是音乐创作者。"""
functions = [skills.generate_music]
agent = Agent.with_functions(functions, role_prompt)
result = agent.run("柔和的钢琴声")
print(result)

#python代码执行完成，结果如下：
#ff4bc8c264cf.wav
#音乐已生成。您可以从以下链接下载音频文件：
# [下载音乐](./ff4bc8c264cf.wav)

```



## 论文

[General Agent：自调用和堆栈内存](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)



## 加入我们

使用微信扫描下方二维码

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>