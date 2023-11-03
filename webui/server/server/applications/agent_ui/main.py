
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    from GeneralAgent.tools import Tools
    from GeneralAgent.interpreter import RoleInterpreter, AsyncPythonInterpreter
    from GeneralAgent.agent import Agent
    workspace = './'
    role_interpreter = RoleInterpreter()
    role_interpreter.system_prompt_template = """
Now: {{now}}
你是一个web后端的机器人，你正在通过网络，与web进行通信，和用户聊天。
你可以通过python代码调用下面预定义的函数，来创建和发送给用户UI元素。
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