from GeneralAgent.agent import Agent

async def main(chat_history, input, file_path, output_callback, file_callback, send_ui):
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills
    from GeneralAgent.interpreter import RoleInterpreter, AsyncPythonInterpreter, AppleScriptInterpreter, ShellInterpreter, UIInterpreter
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
    output_interpreters = [role_interpreter, python_interpreter, AppleScriptInterpreter(), ShellInterpreter(), UIInterpreter(send_ui)]
    agent = Agent(workspace, output_interpreters=output_interpreters, model_type='smart', hide_output_parse=True)
    input_content = input
    if file_path is not None and file_path != '':
        input_content = "user upload a file: " + file_path
    await agent.run(input_content, output_callback=output_callback)