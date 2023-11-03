
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    from GeneralAgent.tools import Tools
    from GeneralAgent.interpreter import RoleInterpreter, AsyncPythonInterpreter
    from GeneralAgent.agent import Agent
    workspace = './'
    role_interpreter = RoleInterpreter()
    role_interpreter.system_prompt_template = """
Now: {{now}}
You are GeneralAgent, a agent on the {{os_version}} computer to help the user solve the problem.
Remember, you can control the computer and access the internet.
If a plan is not provided, explain your plan first simply and clearly. And then run the plan directty.
You can create UI components and send them to the user if nessary by using the python functions.
You can use the following skills to help you solve the problem directly without explain, without ask for permission.
"""
    tools = Tools([
        skills.task_to_ui_js,
        ])
    import_code = """
from GeneralAgent import skills
task_to_ui_js = skills.task_to_ui_js
"""
    # libs = skills.get_current_env_python_libs()
    libs = ''
    python_interpreter = AsyncPythonInterpreter(serialize_path=f'{workspace}/code.bin', libs=libs, import_code=import_code, tools=tools)
    python_interpreter.async_tools = [ui_callback]
    output_interpreters = [role_interpreter, python_interpreter]
    agent = Agent(workspace, output_interpreters=output_interpreters, model_type='smart')
    await agent.run(input, output_callback=output_callback)