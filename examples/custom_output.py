
import asyncio
from GeneralAgent.agent import Agent

async def custom_output(token):
    if token is None:
        print('[output end]')
    else:
        print(token, end='', flush=True)

async def main():
    agent = Agent.default('./basic')
    while True:
        input_content = input('>>>')
        await agent.run(input_content, output_callback=custom_output)

if __name__ == '__main__':
    asyncio.run(main())