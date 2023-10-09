import os
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../.env')
if os.path.exists(env_path):
    load_dotenv(env_path)