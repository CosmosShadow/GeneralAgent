from base_setting import *
from GeneralAgent.llm import num_tokens_from_string
import os
import shutil
import asyncio
from GeneralAgent.agent import Agent

workspace = './data/test_workspace'

def system_prompt_token_count():
    count = num_tokens_from_string('')
    print(count)

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

async def terminal_interactive_agent():
    if os.path.exists(workspace): shutil.rmtree(workspace)
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
    asyncio.run(terminal_interactive_agent())