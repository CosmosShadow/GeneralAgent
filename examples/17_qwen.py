# 测试阿里千问
api_key = 'sk-xxxx'
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
model  = 'qwen-vl-max'

from GeneralAgent import Agent

agent = Agent('You are a helpful assistant.', model=model, api_key=api_key, base_url=base_url, temperature=0.5, max_tokens=1000, top_p=0.9, frequency_penalty=1)
agent.run(['what is in the image?', {'image': '../docs/images/self_call.png'}], display=True)