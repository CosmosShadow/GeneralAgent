# import 
from .normal_agent import NormalAgent
from .stack_agent import StackAgent

class Agent(NormalAgent):
    pass

import os
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', None)
API_TYPE = os.environ.get('API_TYPE', None)
if API_TYPE is None or OPENAI_API_KEY is None or len(OPENAI_API_KEY) < 10:
    print('enviroment variable OPENAI_API_KEY or API_TYPE is not set correctly')
from GeneralAgent.utils import set_logging_level
set_logging_level()