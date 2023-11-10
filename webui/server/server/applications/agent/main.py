from GeneralAgent.agent import Agent

# async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
#     agent = Agent.with_link_memory('./data/')
#     if file_path is not None:
#         input = f"""```read\n{file_path}\n```"""
#     await agent.run(input, output_callback=output_callback)

# async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
#     from GeneralAgent.interpreter import RoleInterpreter, AsyncPythonInterpreter
#     from GeneralAgent.agent import Agent
#     from GeneralAgent import skills

#     workspace = './'
#     functions = [
#         skills.search_functions,
#         skills.image_generation,
#     ]
#     role_interpreter = RoleInterpreter()
#     role_interpreter.system_prompt_template = """
# Now: {{now}}
# You are GeneralAgent, a agent on the {{os_version}} computer to help the user solve the problem.
# Remember, you can control the computer and access the internet.
# You should first use search_funtions to search for available functions and use them in subsequent code to solve the task
# You can use the following skills to help you solve the problem directly without explain, without ask for permission: 
# """
#     python_interpreter = AsyncPythonInterpreter(serialize_path=f'{workspace}/code.bin')
#     python_interpreter.python_prompt_template = """
# # Run python
# - Remember use print() to show or output, otherwise it will not be shown. code like below is wrong.
# ```python
# a = 10
# a
# ```
# code like below is right: 
# ```python
# a = 10
# print(a)
# ```
# - format is : ```python\\nthe_code\\n```
# - the code will be executed
# - python version is 3.9
# - Pickleable objects can be shared between different codes and variables
# - Available libraries: {{python_libs}}
# - The following functions can be used in code (already implemented and imported for you):
# ```
# {{python_funcs}}
# ```
# - You can search for available functions using search_funtions, like
# ```python
# search_functions('scrape web page')
# ```
# output: skills.scrape_web(url: str) Scrape web page, return (title: str, text: str, image_urls: [str], hyperlinks: [str]) when success, otherwise return None
# and Then use it:
# ```python
# conent = skills.scrape_web('https://xxx')
# ```
# """
#     python_interpreter.async_tools = functions
#     output_interpreters = [role_interpreter, python_interpreter]
#     agent = Agent(workspace, output_interpreters=output_interpreters, model_type='smart')

#     input_content = input
#     if file_path is not None and file_path != '':
#         input_content = "user upload a file: " + file_path
#     await agent.run(input_content, output_callback=output_callback)

# async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
#     from GeneralAgent.agent import Agent
#     from GeneralAgent import skills
#     functions = [
#         skills.search_functions,
#         skills.image_generation,
#         skills.scrape_web,
#         skills.text_to_speech,
#         skills.text_to_speech,
#         skills.translate_text
#     ]
#     agent = Agent.agent_with_functions(functions)
#     input_content = input
#     if file_path is not None and file_path != '':
#         input_content = "user upload a file: " + file_path
#     await agent.run(input_content, output_callback=output_callback)

async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills
    from GeneralAgent.interpreter import RoleInterpreter, AsyncPythonInterpreter, AppleScriptInterpreter, ShellInterpreter
    functions = [
        skills.search_functions,
        skills.image_generation,
        skills.scrape_web,
        skills.text_to_speech,
        skills.text_to_speech,
        skills.translate_text
    ]
    role_interpreter = RoleInterpreter()
    workspace = './'
    python_interpreter = AsyncPythonInterpreter(serialize_path=f'{workspace}/code.bin')
    python_interpreter.async_tools = functions
    output_interpreters = [role_interpreter, python_interpreter, AppleScriptInterpreter(), ShellInterpreter()]
    agent = Agent(workspace, output_interpreters=output_interpreters, model_type='smart')
    input_content = input
    if file_path is not None and file_path != '':
        input_content = "user upload a file: " + file_path
    await agent.run(input_content, output_callback=output_callback)

    