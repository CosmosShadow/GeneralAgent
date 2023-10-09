import load_env

import asyncio
from GeneralAgent.tools import Tools
from GeneralAgent.agent import Agent
from GeneralAgent.interpreter import PythonInterpreter
from tool_get_weather import get_weather

import_code = """
import os, sys, math
from tool_get_weather import get_weather
"""

async def main():
    workspace = './'
    tools = Tools([get_weather])
    python_interpreter = PythonInterpreter(tools=tools, import_code=import_code)
    agent = Agent(workspace, input_interpreters=[], output_interpreters=[python_interpreter])
    while True:
        input_content = input('>>>')
        await agent.run(input_content)

if __name__ == '__main__':
    asyncio.run(main())

# [lichen@examples]$ python add_tools.py
# >>>what's the weather of chengdu?

# To get the weather of Chengdu, we can use the `get_weather` function provided in the prompt. Here's the code to get the weather of Chengdu:

# ```python
# weather = get_weather('Chengdu')
# print(weather)
# ```


# weather is good, sunny.

# Glad to hear that the weather in Chengdu is good and sunny! Is there anything else I can help you with?
# >>>Is there anything else I can help you with?
# >>>