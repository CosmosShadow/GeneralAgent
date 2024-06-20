# 使用豆包大模型
# 使用豆包模型，需要先安装库: pip install 'volcengine-python-sdk[ark]'
# model设置为doubao，区分大模型链接库volcengine
# 豆包由于接口上模型是Endpoint。所以使用base_url来指定Endpoint(即哪种模型)

from GeneralAgent import Agent

api_key = 'your_api_key'
endpoint = 'your_endpoint_id'
agent = Agent('You are a helpful assistant', model='doubao', api_key=api_key, base_url=endpoint)
agent.user_input('介绍一下成都')