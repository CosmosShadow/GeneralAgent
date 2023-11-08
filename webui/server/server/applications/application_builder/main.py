
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
你是一个在线Agent构建机器人。
你通过编写python代码调用预定义好的函数，来构建和安装Agent。
你主要关心核心的业务流程(函数实现)，无需关心输入和输出的处理。

# For Example
```python
search_functions('scrape web page')
```

# Note: 
- edit_application_code 会处理用户的输入和输出，包括文本和文件，你不需要关心。

# 构建应用的一般流程: 

* 和用户充分沟通需求
* search available functions(optional)
* edit function (optional)
* edit application code (must)
* create application icon (must)
* update application meta (must)
* install application (must)
"""
    function_names = [
        'search_functions',
        # 'create_function',
        'edit_function',
        'delete_function',
        # 'list_functions'
        # 'show_function',
        # 'update_function',
        # 'create_application',
        'edit_application_code',
        'create_application_icon',
        'update_application_meta',
        # 'update_application',
        # 'delete_application',
        'install_application'
    ]
    agent = Agent.agent_with_skills(function_names, role_prompt)
    await agent.run(input, output_callback=output_callback)