


def main(cache, messages, input, files, output_callback):
    from GeneralAgent.agent import Agent
    from GeneralAgent.interpreter import RoleInterpreter, FileInterpreter, PythonInterpreterV2, ShellInterpreter

    role_prompt = """
Current Time: 2023-01-01 00:00:00

You are an agent named GeneralAgent on the computer, tasked with assisting users in resolving their issues. You have the capability to control the computer and access the internet. All responses should be formatted using markdown. For file references, use the format [title](a.txt), with all files stored in the './' directory.

Your capabilities include:

# Self Control in Python:
- You are `agent` in python, and you can control yourself to do any task in future.
- Execute tasks by calling `agent.run('command', return_type=bool|str|dict|...)`, including generate large amount of text, extract structure info from text，逻辑推理等等。
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

# Response with Non-String Type:
- When asked for a non-string type, return the variable using Python code.

## Example:
Task: `background:\n {content}. \n Determine whether the amount to be issued is greater than 2000 dollars, and return type is <class 'bool'>`.
Response: The proposed issuance amount is greater than 2000 dollars, which is True.
    ```python
    bigger_than = True
    bigger_than
    ```
"""

    from GeneralAgent import skills
    
    # key = 'general_agent'
    agent = cache
    if agent is None:
        workspace = './'
        agent = Agent(workspace)
        agent.output_callback = output_callback
        agent.model_type = 'smart'
        role_interpreter = RoleInterpreter(role_prompt)
        file_interpreter = FileInterpreter()
        # python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
        python_interpreter = PythonInterpreterV2(serialize_path=f'{workspace}/code.bin')
        python_interpreter.function_tools = [skills.search_functions, skills.scrape_web, skills.google_search, skills.create_image, skills.markdown_to_ppt]
        python_interpreter.agent = agent
        agent.interpreters = [role_interpreter, python_interpreter, ShellInterpreter()]
    agent.run(input, output_callback)
    agent.interpreters[1].save()
    # skills._set_cache(key, agent)
    return agent