import os
import datetime
import platform
from jinja2 import Template
from .interpreter import Interpreter

system_role_prompt = \
"""
Now: {{now}}
You are GeneralAgent, a agent on the {{os_version}} computer to help the user solve the problem.
Remember, you can control the computer and access the internet.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first simply and clearly.
You can use the following skills to help you solve the problem directly without explain and ask for permission: 
"""

# system prompt role
class RoleInterpreter(Interpreter):
    def __init__(self, system_prompt=None) -> None:
        self.os_version = self.get_os_version()
        self.system_prompt = system_prompt

    @classmethod
    def get_os_version(cls):
        system = platform.system()
        if system == 'Windows':
            version = platform.version()
            return f"Windows version: {version}"
        elif system == 'Darwin':
            version = platform.mac_ver()[0]
            return f"macOS version: {version}"
        elif system == 'Linux':
            dist = platform.linux_distribution()
            if dist[0] == 'CentOS':
                version = dist[1]
                return f"CentOS version: {version}"
            elif dist[0] == 'Ubuntu':
                version = dist[1]
                return f"Ubuntu version: {version}"
        else:
            return "Unknown system"

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
        the_prompt = Template(system_role_prompt).render(**data)
        return the_prompt

    @property
    def match_template(self):
        return ''
    
    def match(self, string):
        return False
    
    def parse(self, string):
        return '', False