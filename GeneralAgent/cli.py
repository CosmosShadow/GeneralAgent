import os
import asyncio
import logging
import argparse
from GeneralAgent.agent import Agent
from GeneralAgent.utils import default_get_input

def set_logging_level(args):
    args.debug = args.debug.upper()
    if args.debug == 'DEBUG':
        level = logging.DEBUG
    elif args.debug == 'INFO':
        level = logging.INFO
    elif args.debug == 'WARNING':
        level = logging.WARNING
    elif args.debug == 'ERROR':
        level = logging.ERROR
    else:
        level = logging.ERROR
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(funcName)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

async def _main(args):
    set_logging_level(args)
    workspace = args.workspace
    if args.new:
        if os.path.exists(workspace):
            workspace = workspace + '_new'
            print('New workspace: ', workspace)
    if not os.path.exists(workspace):
        os.mkdir(workspace)
    
    model = args.model
    os.environ['OPENAI_API_MODEL'] = model

    if args.auto_run:
        os.environ['AUTO_RUN'] = 'y'
    else:
        os.environ['AUTO_RUN'] = 'n'
    
    agent = Agent.default(workspace=workspace)
    print('Enter twice to input end | 两次回车结束输入')
    while True:
        input_conent = default_get_input()
        print('[output]\n', end='', flush=True)
        await agent.run(input_conent)

def main():
    parser = argparse.ArgumentParser(description='GeneralAgent CLI')
    # parser.add_argument('--help', action='help', help='Show this help message and exit')
    parser.add_argument('--auto_run', action='store_true', help='Enable auto run')
    parser.add_argument('--workspace', default='./general_agent_data', help='Set workspace directory')
    parser.add_argument('--new', action='store_true', help='Enable new workspace')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='Set model')
    parser.add_argument('--logging', default='ERROR', help='set logging level: DEBUG, INFO, WARNING, ERROR')
    args = parser.parse_args()
    asyncio.run(_main(args))

if __name__ == '__main__':
    main()