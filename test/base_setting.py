import logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(funcName)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# load env
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '/.env')
# check if exists
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print('Warning: .env file not found, please create one in the root directory of the project. you can copy .env.example to .env and modify it.')