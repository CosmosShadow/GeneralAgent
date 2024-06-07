# 知识库
from GeneralAgent import Agent

knowledge_files = ['../docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf']
agent = Agent('你是AI助手，用中文回复。', workspace='9_knowledge_files', knowledge_files=knowledge_files)
agent.user_input('Self call 是什么意思？')