
async def main(chat_history, input, file_path, output_callback, file_callback, send_ui):
    # async def send_ui(component_name:str, js_path:str, data={}):
    from GeneralAgent.interpreter import RoleInterpreter, AsyncPythonInterpreter, UIInterpreter
    from GeneralAgent.agent import Agent
    workspace = './'
    python_interpreter = AsyncPythonInterpreter(serialize_path=f'{workspace}/code.bin')
    output_interpreters = [RoleInterpreter(), python_interpreter, UIInterpreter(send_ui)]
    agent = Agent(workspace, output_interpreters=output_interpreters, model_type='smart')
    await agent.run(input, output_callback=output_callback)