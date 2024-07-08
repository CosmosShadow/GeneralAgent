# 快速开始
from GeneralAgent import Agent

# 流式输出中间结果
def output_callback(token):
    token = token or '\n'
    print(token, end='', flush=True)

agent = Agent('你是AI助手，用中文回复。', output_callback=output_callback, temperature=0.5, frequency_penalty=2)
agent.clear()
agent.disable_python()
while True:
    query = input('请输入: ')
    agent.run(query)
    print('-'*50)