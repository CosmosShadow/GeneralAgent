from base_setting import *
import os
import asyncio
import shutil
from GeneralAgent.agent import Agent
from GeneralAgent.utils import default_get_input
workspace = './multi_lines_input'

async def main():
    if os.path.exists(workspace):
        shutil.rmtree(workspace)
    os.mkdir(workspace)
    agent = Agent.default(workspace=workspace)
    print('Enter twice to input end | 两次回车结束输入')
    while True:
        input_content = default_get_input()
        print('[output]\n', end='', flush=True)
        await agent.run(input_content)

if __name__ == '__main__':
    asyncio.run(main())