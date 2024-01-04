def main(cache, messages, input, files, output_callback):
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills

    role_prompt = """
You are a image creator.
You complete user requirements by writing python code to call the predefined functions.
You should convert the user's needs into the description of the image's content and then pass it to create_image.
response markdown format text to user.
"""
    functions = [
        skills.create_image
    ]
    agent = Agent.with_functions(functions, role_prompt)
    agent.output_callback = output_callback
    agent.run(input)