import datetime
from jinja2 import Template
from .interpreter import Interpreter

default_system_role = """
Current Time: {{now}}
You are an agent on the computer, tasked with assisting users in resolving their issues. 
You have the capability to control the computer and access the internet. 
All code in ```python ``` will be automatically executed by the system. So if you don't need to run the code, please don't write it in the code block.
All responses should be formatted using markdown. For file references, use the format [title](a.txt), with all files stored in the './' directory.
When result file is ready, provide it to the user with donwload link. 
"""

class RoleInterpreter(Interpreter):
    """
    RoleInterpreter, a interpreter that can change the role of the agent.
    Note: This should be the first interpreter in the agent.
    """

    def __init__(self, system_role=None, self_call=False, search_functions=False, role:str=None) -> None:
        """
        prompt = system_role | default_system_role + role
        @system_role: str, 系统角色. 如果为None，则使用默认系统角色
        @self_call: bool, 是否开启自调用
        @search_functions: bool, 是否开启搜索功能
        @role: str, 用户角色
        """
        self.system_role = system_role
        self.self_control = self_call
        self.search_functions = search_functions
        self.role = role

    def prompt(self, messages) -> str:
        if self.system_role is not None:
            prompt = self.system_role
        else:
            prompt = Template(default_system_role).render(now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if self.role is not None:
            prompt += '\n\n' + self.role
        return prompt