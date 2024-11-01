from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()
# agent = Agent('You are a helpful assistant.', temperature=0.5, frequency_penalty=2)
agent = Agent('You are a helpful assistant.')
while True:
    query = input('>: ')
    agent.user_input(query)
    print('-'*50)