from GeneralAgent.agent import Agent

# async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
#     agent = Agent.with_link_memory('./data/')
#     if file_path is not None:
#         input = f"""```read\n{file_path}\n```"""
#     await agent.run(input, output_callback=output_callback)

async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent.interpreter import RoleInterpreter, AsyncPythonInterpreter
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills

    workspace = './'
    functions = [
        skills.search_functions,
        skills.image_generation,
    ]
    role_interpreter = RoleInterpreter()
    role_interpreter.system_prompt_template = """
Now: {{now}}
You are GeneralAgent, a agent on the {{os_version}} computer to help the user solve the problem.
Remember, you can control the computer and access the internet.

In the Python environment, the skills library (from GeneralAgent import skills) has many powerful functions. You can search and use them through search_functions.
Please search for available pre-made functions before completing the user's task.
# For Example
```python
search_functions('scrape web page')
```
output: skills.scrape_web(url: str) Scrape web page, return (title: str, text: str, image_urls: [str], hyperlinks: [str]) when success, otherwise return None

Note: 
- Don’t make up functions that don’t exist
- Control the display length of the output text. Printing a string of unknown length requires a stage.

You can use the following skills to help you solve the problem directly without explain, without ask for permission: 
"""
    python_interpreter = AsyncPythonInterpreter(serialize_path=f'{workspace}/code.bin')
    python_interpreter.async_tools = functions
    output_interpreters = [role_interpreter, python_interpreter]
    agent = Agent(workspace, output_interpreters=output_interpreters, model_type='smart')

    input_content = input
    if file_path is not None and file_path != '':
        input_content = "user upload a file: " + file_path
    await agent.run(input_content, output_callback=output_callback)