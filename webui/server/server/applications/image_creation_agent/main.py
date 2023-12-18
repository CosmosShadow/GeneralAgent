def main(messages, input, output_callback):
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills

    role_prompt = """
You are a image creator.
You complete user requirements by writing python code to call the predefined functions.
You should convert the user's needs into the description of the image's content and then pass it to image_generation.
response markdown format text to user.
"""
    functions = [
        skills.image_generation
    ]
    agent = Agent.with_functions(functions, role_prompt)
    agent.run(input, output_callback=output_callback)