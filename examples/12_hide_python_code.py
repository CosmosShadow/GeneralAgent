# 快速开始
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()
agent = Agent('You are a helpful assistant.', hide_python_code=True)
agent.user_input('caculate 0.999 ** 1000')