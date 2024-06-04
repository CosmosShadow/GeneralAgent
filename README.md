# GeneralAgent: From LLM to Agent



## 功能

* GeneralAgent 支持序列化
* 自我调用和堆栈内存：GeneralAgent可以自我控制并具有堆栈内存。更多细节请见[论文](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)
* 函数搜索和使用：从数千个函数中搜索并使用它们。
* [AthenaAgent](https://github.com/sigworld/AthenaAgent) 是 GeneralAgent 的 TypeScript 版本。



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