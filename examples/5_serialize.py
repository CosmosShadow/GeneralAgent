# 序列化
from GeneralAgent.agent import Agent

# agent序列化位置，运行过程中会自动保存LLM的messages和python解析器的状态
workspace='./5_serialize'

role = 'You are a helpful agent.'
agent = Agent(workspace=workspace)
agent.user_input('My name is Shadow.')

agent = None
agent = Agent(role, workspace=workspace)
agent.user_input('What is my name?')

# Ooutput: Your name is Shadow. How can I help you today, Shadow?

# 删除agent: 记忆 + python序列化状态
agent.delete()