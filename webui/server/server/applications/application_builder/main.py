
# async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
#     from GeneralAgent import skills
#     from GeneralAgent.tools import Tools
#     from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter
#     from GeneralAgent.agent import Agent
#     workspace = './'
#     system_prompt = """
# 你是一个应用构建机器人。
# 你通过编写python代码调用 # Run python 中预定义好的函数，来构建应用。
# """
#     role_interpreter = RoleInterpreter(system_prompt=system_prompt)
#     tools = Tools([
#         skills.create_function,
#         skills.delete_function,
#         skills.list_functions,
#         skills.show_function,
#         skills.update_function,
#         skills.create_application_icon,
#         skills.create_application,
#         skills.update_application,
#         skills.delete_application,
#         skills.install_application,
#         ])
#     import_code = """
# from GeneralAgent import skills
# create_function = skills.create_function
# delete_function = skills.delete_function
# list_functions = skills.list_functions
# show_function = skills.show_function
# update_function = skills.update_function
# create_application_icon = skills.create_application_icon
# create_application = skills.create_application
# update_application = skills.update_application
# delete_application = skills.delete_application
# install_application = skills.install_application
# """
#     # libs = skills.get_current_env_python_libs()
#     libs = ''
#     python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin', tools=tools, libs=libs, import_code=import_code)
#     output_interpreters = [role_interpreter, python_interpreter]
#     agent = Agent(workspace, output_interpreters=output_interpreters, model_type='smart')
#     await agent.run(input, output_callback=output_callback)

async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent.agent import Agent
    role_prompt = """
你是一个应用构建机器人。
你通过编写python代码调用 # Run python 中预定义好的函数，来构建应用。
"""
    function_names = [
        'create_function',
        'delete_function',
        'list_functions'
        'show_function',
        'update_function',
        'create_application_icon',
        'create_application',
        'update_application',
        'delete_application',
        'install_application'
    ]
    agent = Agent.agent_with_skills(function_names, role_prompt)
    await agent.run(input, output_callback=output_callback)