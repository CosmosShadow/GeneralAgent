# import 
from .agent import Agent
from .stack_agent import StackAgent
from .link_agent import LinkAgent

import os
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', None)
if OPENAI_API_KEY is None or len(OPENAI_API_KEY) < 10:
    print('enviroment variable OPENAI_API_KEY is not set correctly')
from GeneralAgent.utils import set_logging_level
set_logging_level()