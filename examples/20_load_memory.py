# load messages
from GeneralAgent import Agent


messages = [
        {"role": "user", "content": "My name is Yummy."},
        {"role": "assistant", "content": "Hello, Yummy! How can I assist you today?"},
    ]
agent = Agent('You are a helpful assistant.', messages=messages)
response = agent.user_input("What's my name?")

# Expect: Yummy in response
