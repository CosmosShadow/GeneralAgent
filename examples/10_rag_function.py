# RAG function

# 设置日志级别
import os
os.environ['AGENT_LOG'] = 'debug'

from GeneralAgent import Agent

def rag_function(messages):
    input = messages[-1]['content']
    print('user input:', input)
    # TODO: 根据input或者messages更多信息，返回相关的背景知识
    return 'Background: GeneralAgent is a Python library for building AI assistants. It provides a simple API for building conversational agents.'

agent = Agent('You are a helpful assistant', rag_function=rag_function)
agent.user_input('What is GeneralAgent?')