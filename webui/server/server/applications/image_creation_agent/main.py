async def main(messages, input, output_callback):
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills

    role_prompt = """
You are a image creator.
You complete user requirements by writing python code to call the predefined functions.
"""
    functions = [
        skills.image_generation
    ]
    agent = Agent.with_functions(functions, role_prompt)
    await agent.run(input, output_callback=output_callback)