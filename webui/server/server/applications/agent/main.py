from GeneralAgent.agent import Agent

async def main(chat_history, input, file_path, output_callback, file_callback, send_ui):
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills
    from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, AppleScriptInterpreter, ShellInterpreter, UIInterpreter
    functions = [
        skills.search_functions,
        skills.image_generation,
        skills.scrape_web,
        skills.text_to_speech,
        skills.text_to_speech,
        skills.translate_text
    ]
    workspace = './'
    agent = Agent(workspace)
    python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
    python_interpreter.function_tools = functions
    agent.output_interpreters = [RoleInterpreter(), python_interpreter, AppleScriptInterpreter(), ShellInterpreter(), UIInterpreter(send_ui)]
    agent.model_type = 'smart'

    input_content = input
    if file_path is not None and file_path != '':
        input_content = "user upload a file: " + file_path
    await agent.run(input_content, output_callback=output_callback)