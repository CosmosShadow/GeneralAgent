import os
import asyncio
import argparse
from GeneralAgent.agent import Agent
from GeneralAgent.utils import default_get_input, set_logging_level


async def _main(args):
    set_logging_level(os.environ.get('LOG_LEVEL', 'ERROR'))
    workspace = args.workspace
    if args.new:
        if os.path.exists(workspace):
            workspace = workspace + '_new'
            print('New workspace: ', workspace)
    if not os.path.exists(workspace):
        os.mkdir(workspace)
    
    agent = Agent.default(workspace=workspace)
    print('Enter twice to input end | 两次回车结束输入')
    while True:
        input_conent = default_get_input()
        print('[output]\n', end='', flush=True)
        await agent.run(input_conent)

def main():
    parser = argparse.ArgumentParser(description='GeneralAgent CLI')
    parser.add_argument('--workspace', default='./general_agent_data', help='Set workspace directory')
    parser.add_argument('--new', action='store_true', help='Enable new workspace')
    args = parser.parse_args()
    asyncio.run(_main(args))

if __name__ == '__main__':
    main()