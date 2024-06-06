# 隐藏输出流，不显示给用户
from GeneralAgent.agent import Agent

agent = Agent('You are a helpful agent.')
chengdu_description = agent.run('介绍一下成都', show_stream=False)
print(chengdu_description)