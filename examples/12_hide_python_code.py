# 快速开始
from GeneralAgent import Agent

agent = Agent('You are a helpful assistant.', hide_python_code=True)
result = agent.run('caculate 0.999 ** 1000')
print(result)