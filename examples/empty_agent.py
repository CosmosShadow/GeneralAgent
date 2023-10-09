import load_env

import asyncio
from GeneralAgent.agent import Agent

async def main():
    agent = Agent.empty()
    while True:
        input_conent = input('>>>')
        await agent.run(input_conent)

if __name__ == '__main__':
    asyncio.run(main())