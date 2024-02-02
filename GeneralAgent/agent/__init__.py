# import 
from .normal_agent import NormalAgent
# from .stack_agent import StackAgent

class Agent(NormalAgent):
    pass

import os
# LLM_SOURCE = os.environ.get('LLM_SOURCE', None)
# if LLM_SOURCE is None:
#     print('enviroment variable LLM_SOURCE not available.')

from GeneralAgent.utils import set_logging_level
set_logging_level()