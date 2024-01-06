import os
import datetime
import platform
from jinja2 import Template
from .interpreter import Interpreter


class RoleInterpreter(Interpreter):
    """
    RoleInterpreter, a interpreter that can change the role of the agent.
    Note: This should be the first interpreter in the agent.
    """
    
    system_prompt_template = """
Current Time: 2023-01-01 00:00:00

You are an agent named GeneralAgent on the computer, tasked with assisting users in resolving their issues. 
You have the capability to control the computer and access the internet. 
All responses should be formatted using markdown. For file references, use the format [title](a.txt), with all files stored in the './' directory.
When result file is ready, provide it to the user with donwload link.
You should use the following skills (start with #) to solve the problem directly without explain, without ask for permission, without ask for wait.

"""

#     system_prompt_template = \
# """
# Now: {{now}}
# You are GeneralAgent, a agent on the {{os_version}} computer to help the user solve the problem.
# Remember, you can control the computer and access the internet.
# Reponse message in markdown format to user. for example file a.txt, you should reponse [title](a.txt)
# You can use the following skills (start with # ) to help you solve the problem directly without explain, without ask for permission.
# """

    def __init__(self, system_prompt=None) -> None:
        from GeneralAgent import skills
        self.os_version = skills.get_os_version()
        self.system_prompt = system_prompt

    def prompt(self, messages) -> str:
        if self.system_prompt is not None:
            return self.system_prompt
        if os.environ.get('LLM_CACHE', 'no') in ['yes', 'y', 'YES']:
            now = '2023-09-27 00:00:00'
        else:    
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = {
            'now': now,
            'os_version': self.os_version
        }
        the_prompt = Template(self.system_prompt_template).render(**data)
        return the_prompt