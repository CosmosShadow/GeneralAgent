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
    # now: 432 tokens

async def terminal_interactive_agent():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace)
    async def _output_recall(result):
        # print('-----<output>------')
        # print(result)
        # print('-----</output>------')
        pass
    for_node_id = None
    while True:
        input_conent = input('[input]\n')
        for_node_id = await agent.run(input_conent, for_node_id=for_node_id, output_recall=_output_recall)
        # >>>写个详细的python版本带GUI的俄罗斯方块游戏到本地文件。不用询问我细节，你自由发挥。
        # >>>运行它呢

if __name__ == '__main__':
    # system_prompt_token_count()
    asyncio.run(terminal_interactive_agent())