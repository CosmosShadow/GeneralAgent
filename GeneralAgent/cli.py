import os
import asyncio
import datetime
import argparse
from GeneralAgent.agent import Agent
from GeneralAgent.utils import default_get_input, set_logging_level


def _main(args):
    if args.auto_run:
        os.environ['AUTO_RUN'] = 'y'
    else:
        os.environ['AUTO_RUN'] = 'n'
    set_logging_level(os.environ.get('LOG_LEVEL', 'ERROR'))
    workspace = args.workspace
    if args.new:
        if os.path.exists(workspace):
            workspace = workspace + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            print('New workspace: ', workspace)
    if not os.path.exists(workspace):
        os.mkdir(workspace)
    
    agent = Agent.default(workspace=workspace)
    print('You can input multi lines, enter twice to end')
    while True:
        input_content = default_get_input()
        print('[output]\n', end='', flush=True)
        agent.run(input_content)

def main():
    parser = argparse.ArgumentParser(description='GeneralAgent CLI')
    parser.add_argument('--workspace', default='./general_agent', help='Set workspace directory')
    parser.add_argument('--new', action='store_true', help='Enable new workspace')
    parser.add_argument('--auto_run', action='store_true', help='Auto run code without confirm')
    args = parser.parse_args()
    asyncio.run(_main(args))

if __name__ == '__main__':
    main()