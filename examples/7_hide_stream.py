# 隐藏输出流，不显示给用户
from GeneralAgent.agent import Agent

agent = Agent('You are a helpful agent.', model='gpt-3.5-turbo')
chengdu_description = agent.run('介绍一下成都', show_stream=False)
print(chengdu_description)