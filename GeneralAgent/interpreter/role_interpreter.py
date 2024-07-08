import os
import datetime
import platform
from jinja2 import Template
from .interpreter import Interpreter

def get_os_version() -> str:
    import platform
    system = platform.system()
    if system == 'Windows':
        version = platform.version()
        return f"Windows version: {version}"
    elif system == 'Darwin':
        version = platform.mac_ver()[0]
        return f"macOS version: {version}"
    elif system == 'Linux':
        version = platform.platform()
        return f"Linux version: {version}"
    else:
        return "Unknown system"

default_system_role = """
Current Time: {{now}}
You are an agent on the {{os_version}} computer, tasked with assisting users in resolving their issues. 
You have the capability to control the computer and access the internet. 
All code in ```python ``` will be automatically executed by the system. So if you don't need to run the code, please don't write it in the code block.
All responses should be formatted using markdown. For file references, use the format [title](a.txt), with all files stored in the './' directory.
When result file is ready, provide it to the user with donwload link. 
"""

self_call_prompt = """
# Self Control in Python:
- You are `agent` in python, and you can control yourself to do any task in future.
- Execute tasks by calling `agent.run('command', return_type=bool|str|dict|...)`.
- Ensure the 'command' string within `agent.run` does not exceed 5000 characters.
- Handle a wide range of tasks, not limited to text-based operations, by breaking down complex tasks into subtasks and executing them through self-calls.
- Use `agent.run` to complete parts of a task, not the entire task.
- Provide direct results when possible, without the need for additional calls to `agent.run('command', return_type=...)`.
- Complete highly complex tasks in one step through multi self-call, delivering the final result without requiring the user to wait or providing unnecessary explanations.

## Example:
To introduce Chengdu and Beijing into a file:
```python
cities = ['Chengdu', 'Beijing']
contents = []
for city in cities:
    contents.append(agent.run(f'Introduce {city}', return_type=str))
with open('a.md', 'w') as f:
    f.writelines(contents)
```

## Reponse with non-string type:
- when ask for a non-string type, you should return the variable by python code.

## DEMO 1: give me the web (url: xxx) page content if amount to be issued is greater than 2000 dollar, return type should be <class 'str'>
```python
content = agent.run('Scrape web page content of xxx', return_type=str)
bigger_than = agent.run(f'background: {content}\nDetermine whether the amount to be issued is greater than 2000 dollar?', return_type=bool)
result = content if bigger_than else "Content not displayed"
result
```

## DEMO 2: To return a boolean value, return type should be <class 'bool'>
user task: background:\n {content}. \nDetermine whether the amount to be issued is greater than 2000 dollar, and return a bool value
reposne:
\"\"\"
According to the background, the proposed issuance amount is greater than 2000 dollar, so it is True.
```python
bigger_than = True
bigger_than
```
"""

function_search_prompt = """
# Search for functions
- When you cannot directly meet user needs, you can use the skills.search_functions function in python code to search for available functions, and then execute the functions to complete user needs.
## DEMO: draw a image about Beijing
```python
skills.search_functions('draw image')
```
Result:
```
skills.create_image(prompt):
    Draw image given a prompt, returns the image path
    @prompt: A text description of the desired image. The maximum length is 4000 characters.
    @return: image path
```
Then Draw a image
```python
image_path = skills.create_image('image description')
image_path
```
"""


class RoleInterpreter(Interpreter):
    """
    RoleInterpreter, a interpreter that can change the role of the agent.
    Note: This should be the first interpreter in the agent.
    """

    def __init__(self, system_role=None, self_call=False, search_functions=False, role:str=None) -> None:
        """
        prompt = system_role | default_system_role + self_call_prompt + function_search_prompt + role
        @system_role: str, 系统角色. 如果为None，则使用默认系统角色
        @self_call: bool, 是否开启自调用
        @search_functions: bool, 是否开启搜索功能
        @role: str, 用户角色
        """
        self.os_version = get_os_version()
        self.system_role = system_role
        self.self_control = self_call
        self.search_functions = search_functions
        self.role = role

    def prompt(self, messages) -> str:
        if self.system_role is not None:
            prompt = self.system_role
        else:
            prompt = Template(default_system_role).render(os_version=self.os_version, now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if self.self_control:
            prompt += '\n\n' + self_call_prompt
        if self.search_functions:
            prompt += '\n\n' + function_search_prompt
        if self.role is not None:
            prompt += '\n\n' + self.role
        return prompt