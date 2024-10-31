# 隐藏输出流，不显示给用户
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

agent = Agent('You are a helpful agent.', model='gpt-3.5-turbo')
chengdu_description = agent.run('介绍一下成都', display=True)
print(chengdu_description)