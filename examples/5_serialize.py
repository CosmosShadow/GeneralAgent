# 序列化
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

# agent序列化位置，运行过程中会自动保存LLM的messages和python解析器的状态
workspace='./5_serialize'

role = 'You are a helpful agent.'
agent = Agent(role, workspace=workspace)
agent.user_input('My name is Shadow.')

agent = None
agent = Agent(role, workspace=workspace)
agent.user_input('What is my name?')

# Output: Your name is Shadow. How can I help you today, Shadow?

# agent: 清除记忆 + python序列化状态
agent.clear()

agent.user_input('What is my name?')
# I'm sorry, but I don't have access to your personal information, including your name. How can I assist you today?

import shutil
shutil.rmtree(workspace)