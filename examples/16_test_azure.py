# 测试Azure Open AI
import os
from GeneralAgent import Agent

# api_key = os.getenv("OPENAI_API_KEY")
# base_url = os.getenv("OPENAI_API_BASE")
api_key = '8ef0b4df45e444079cd5xxx' # Azure API Key or use OPENAI_API_KEY environment variable
base_url = 'https://xxxx.openai.azure.com/' # Azure API Base URL or use OPENAI_API_BASE environment variable
model = 'azure_cpgpt4' # azure_ with model name, e.g. azure_cpgpt4
# azure api_version is default to '2024-05-01-preview'. You can set by environment variable AZURE_API_VERSION

agent = Agent('You are a helpful assistant', api_key=api_key, base_url=base_url, model=model)
while True:
    query = input('Please input your query:')
    agent.user_input(query)
    print('-'*50)
