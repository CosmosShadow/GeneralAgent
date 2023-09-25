from base_setting import *
from GeneralAgent.llm import num_tokens_from_string
from GeneralAgent.prompts import general_agent_prompt
import os
import shutil
import asyncio
from GeneralAgent.agent import Agent

workspace = './data/test_workspace'

def system_prompt_token_count():
    count = num_tokens_from_string(general_agent_prompt)
    print(count)
    # 649 tokens, it's long

async def terminal_interactive_agent():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace)
    async def _output_recall(result):
        print('-----<output>------')
        print(result)
        print('-----</output>------')
    for_node_id = None
    while True:
        input_conent = input('>>>')
        for_node_id = await agent.run(input_conent, for_node_id=for_node_id, output_recall=_output_recall)
        # 不用做计划，写一个用python语言实现的带GUI界面的俄罗斯方块游戏，保存在当前目录下。不用询问我，直接做就行了。
        # 写一个带GUI界面的俄罗斯方块游戏，python实现，保存在当前目录下，并运行起来

if __name__ == '__main__':
    # system_prompt_token_count()
    asyncio.run(terminal_interactive_agent())