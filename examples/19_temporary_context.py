# 演示临时上下文的用法
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

agent = Agent('You are a helpful assistant.')
with agent.temporary_context():
    agent.user_input('My name is Henry.')
agent.user_input("What's my name?")

# Expect: I don't know your name. How can I help you today?