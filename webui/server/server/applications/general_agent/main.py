def main(cache, messages, input, files, output_callback):
    """
    You are an agent named GeneralAgent on the computer, tasked with assisting users in resolving their issues.
    @param cache: cache object
    @param messages: chat messages, list of dict, like [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role': 'user', 'content': '1 + 1 = ?'}]
    @param input: user input, str
    @param files: user upload files, list of file path, like ['a.txt', 'b.txt']
    @param output_callback: output callback function, like output_callback('2'). you can pass None to output_callback to start a new chat session.
    """
    
    # You should use the following skills (start with #) to solve the problem directly without explain, without ask for permission, without ask for wait.

    from GeneralAgent.agent import Agent
    from GeneralAgent.interpreter import RoleInterpreter, FileInterpreter, PythonInterpreter, ShellInterpreter

    from GeneralAgent import skills
    
    agent = cache
    if agent is None:
        workspace = './'
        agent = Agent(workspace)
        agent.output_callback = output_callback
        agent.model_type = 'smart'
        role_interpreter = RoleInterpreter()
        file_interpreter = FileInterpreter()
        # shell_interperter = ShellInterpreter()
        python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
        python_interpreter.function_tools = [skills.search_functions, skills.google_search, skills.create_image]
        python_interpreter.agent = agent
        agent.interpreters = [role_interpreter, python_interpreter]
    agent.run(input)
    agent.interpreters[1].save()
    return agent