def main(cache, messages, input, files, output_callback):
    """
    You are an agent named GeneralAgent on the computer, tasked with assisting users in resolving their issues.
    @param cache: cache object
    @param messages: chat messages, list of dict, like [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role': 'user', 'content': '1 + 1 = ?'}]
    @param input: user input, str
    @param files: user upload files, list of file path, like ['a.txt', 'b.txt']
    @param output_callback: output callback function, like output_callback('2'). you can pass None to output_callback to start a new chat session.
    """
    
    # You should use the following skills (start with #) to solve the problem directly without explain, without ask for permission, without ask for wait.

    from GeneralAgent.agent import Agent
    from GeneralAgent.interpreter import RoleInterpreter, FileInterpreter, PythonInterpreter, ShellInterpreter

    role_prompt = """
Current Time: 2023-01-01 00:00:00

You are an agent named GeneralAgent on the computer, tasked with assisting users in resolving their issues. 
You have the capability to control the computer and access the internet. 
All responses should be formatted using markdown. For file references, use the format [title](a.txt), with all files stored in the './' directory.
When result file is ready, provide it to the user with donwload link.

You should use the following skills (start with #) to solve the problem directly without explain, without ask for permission, without ask for wait:

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

# Reponse with non-string type:
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

# Pay attention to numbers and units
Be consistent wherever you use numbers and units. And in agent.run, it is necessary to explain the numbers and units clearly.

"""

    from GeneralAgent import skills
    
    agent = cache
    if agent is None:
        workspace = './'
        agent = Agent(workspace)
        agent.output_callback = output_callback
        agent.model_type = 'smart'
        role_interpreter = RoleInterpreter(role_prompt)
        file_interpreter = FileInterpreter()
        shell_interperter = ShellInterpreter()
        python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
        python_interpreter.function_tools = [skills.search_functions, skills.scrape_web, skills.google_search, skills.create_image, skills.markdown_to_ppt]
        python_interpreter.agent = agent
        agent.interpreters = [role_interpreter, python_interpreter, shell_interperter]
    agent.run(input)
    agent.interpreters[1].save()
    return agent