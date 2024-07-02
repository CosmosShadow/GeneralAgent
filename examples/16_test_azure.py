# 测试Azure Open AI
import os
from GeneralAgent import Agent

# api_key = os.getenv("OPENAI_API_KEY")
# base_url = os.getenv("OPENAI_API_BASE")
api_key = '8ef0b4df45e444079cd5xxx' # Azure API Key
base_url = 'https://xxxx.openai.azure.com/' # Azure API Base URL
model = 'azure_cpgpt4' # azure_ with model name, e.g. azure_cpgpt4

agent = Agent('You are a helpful assistant', api_key=api_key, base_url=base_url, model=model)
while True:
    query = input('Please input your query:')
    agent.user_input(query)
    print('-'*50)
