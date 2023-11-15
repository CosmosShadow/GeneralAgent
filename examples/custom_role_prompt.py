import asyncio
from GeneralAgent.agent import Agent
from GeneralAgent.interpreter import RoleInterpreter

role_prompt = """
You are GeneralAgent, a agent on the computer to help the user solve the problem.
Remember, you can control the computer and access the internet.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first simply and clearly.
You can use the following skills to help you solve the problem directly without explain and ask for permission: 
"""

async def main():
    agent = Agent()
    agent.interpreters = [RoleInterpreter(system_prompt=role_prompt)]
    while True:
        input_content = input('>>>')
        await agent.run(input_content)

if __name__ == '__main__':
    asyncio.run(main())