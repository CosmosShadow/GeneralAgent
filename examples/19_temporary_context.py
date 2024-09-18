from GeneralAgent import Agent


agent = Agent('You are a helpful assistant.', hide_python_code=True)
with agent.temporary_context():
    agent.user_input('My name is Henry.')
agent.user_input("What's my name?")
