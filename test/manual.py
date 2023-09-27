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
    # 419 tokens
    # 432 tokens
    # now: 326 tokens

async def terminal_interactive_agent():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace)
    async def _output_recall(token):
        if token is not None:
            print(token, end='', flush=True)
        else:
            print()
    for_node_id = None
    while True:
        input_conent = input('[input]\n')
        print('[output]\n', end='', flush=True)
        for_node_id = await agent.run(input_conent, for_node_id=for_node_id, output_recall=_output_recall)
        # calculate 0.99 ** 1000
        # 不使用计划，直接帮我一次性写个俄罗斯方块游戏代码，保存在本地，要求python实现，带GUI界面。
        # plan
        # 帮我写一份AI画画产品的商业计划书框架，用于天使轮投资，不清晰的地方，你合理设计，不用询问我。
        # 将框架作为计划，运行它

if __name__ == '__main__':
    # system_prompt_token_count()
    asyncio.run(terminal_interactive_agent())