from base_setting import *
import os
import asyncio
from GeneralAgent.agent import Agent
from GeneralAgent.utils import default_get_input

async def main(workspace):
    if not os.path.exists(workspace):
        os.mkdir(workspace)
    agent = Agent.default(workspace=workspace)
    for_node_id = None
    print('Enter twice to input end | 两次回车结束输入')
    while True:
        input_conent = default_get_input()
        print('[output]\n', end='', flush=True)
        for_node_id = await agent.run(input_conent, for_node_id=for_node_id)

if __name__ == '__main__':
    workspace = './data/test_workspace'
    if len(sys.argv) > 1:
        workspace = sys.argv[1]
    asyncio.run(main(workspace))