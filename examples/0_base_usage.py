# 快速开始
from GeneralAgent import Agent

# 流式输出中间结果
def output_callback(token):
    token = token or '\n'
    print(token, end='', flush=True)

agent = Agent('你是AI助手，用中文回复。', output_callback=output_callback)
while True:
    query = input('请输入: ')
    agent.user_input(query)
    print('-'*50)