import asyncio
from GeneralAgent.agent import Agent

def get_weather(city:str):
    """
    get weather from city
    """
    state = 'weather is good, sunny.'
    print(state)
    return state

async def main():
    agent = Agent.with_functions([get_weather])
    while True:
        input_content = input('>>>')
        await agent.run(input_content)

if __name__ == '__main__':
    asyncio.run(main())