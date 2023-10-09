import os
import sys
from dotenv import load_dotenv

# add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# load env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print('Warning: .env file not found, please create one in the root directory of the project. you can copy .env.example to .env and modify it.')

# set logging level
from GeneralAgent.utils import set_logging_level
set_logging_level(os.environ.get('LOG_LEVEL', 'ERROR'))