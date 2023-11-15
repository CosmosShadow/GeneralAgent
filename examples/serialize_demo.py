import asyncio
from GeneralAgent.agent import Agent

async def main():
    agent = Agent.default(workspace='./test')
    await agent.run('Hi, My Name is Chen Li')

    agent = None
    agent = Agent.default(workspace='./test')
    await agent.run('What is my Name?')
    # expect to output Chen Li

if __name__ == '__main__':
    asyncio.run(main())