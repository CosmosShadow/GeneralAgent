# 支持多模态: 图片输入
# 格式为自定最简模式，: ['text_content', {'image': 'path/to/image'}, ...]
from GeneralAgent import Agent

agent = Agent('You are a helpful assistant.')
agent.user_input(['what is in the image?', {'image': '../docs/images/self_call.png'}])