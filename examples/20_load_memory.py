# load memory from history
from GeneralAgent import Agent


history = [
        {"role": "user", "content": "My name is Yummy."},
        {"role": "assistant", "content": "Hello, Yummy! How can I assist you today?"},
    ]
agent = Agent('You are a helpful assistant.', history=history)
response = agent.user_input("What's my name?")

# Expect: Yummy in response
