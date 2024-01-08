def main(cache, messages, input, files, output_callback):
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills
    role_prompt = """You are a music creator."""
    functions = [
        skills.generate_music
    ]
    agent = Agent.with_functions(functions, role_prompt)
    agent.run(input, output_callback=output_callback)