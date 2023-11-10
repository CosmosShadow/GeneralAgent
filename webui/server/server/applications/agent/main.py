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
You can use the following skills to help you solve the problem directly without explain, without ask for permission: 

Note: Before programming, you should search for available python functions through skills.search_functions and use them directly.
"""
    python_interpreter = AsyncPythonInterpreter(serialize_path=f'{workspace}/code.bin')
    python_interpreter.async_tools = functions
    output_interpreters = [role_interpreter, python_interpreter]
    agent = Agent(workspace, output_interpreters=output_interpreters, model_type='smart')

    input_content = input
    if file_path is not None and file_path != '':
        input_content = "user upload a file: " + file_path
    await agent.run(input_content, output_callback=output_callback)