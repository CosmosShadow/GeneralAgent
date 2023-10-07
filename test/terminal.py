from base_setting import *
import os
import shutil
import asyncio
from GeneralAgent.agent import Agent

workspace = './data/test_workspace'

# input multi lines, enter twice to end
def get_input():
    print('[input]')
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    text = '\n'.join(lines)
    return text

async def main(new=False):
    if new and os.path.exists(workspace):
        print('renew workspace ' + workspace)
        shutil.rmtree(workspace)
    agent = Agent.default_agent(workspace=workspace)
    async def _output_recall(token):
        if token is not None:
            print(token, end='', flush=True)
        else:
            print()
    for_node_id = None
    print('Enter twice to input end | 两次回车结束输入')
    while True:
        input_conent = get_input()
        print('[output]\n', end='', flush=True)
        for_node_id = await agent.run(input_conent, for_node_id=for_node_id, output_recall=_output_recall)


if __name__ == '__main__':
    # 读取参数，如果有new，就传入
    new = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'new':
            new = True
    asyncio.run(main(new=new))