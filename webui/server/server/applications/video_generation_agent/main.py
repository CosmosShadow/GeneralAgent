async def main(messages, input, output_callback):
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills

    role_prompt = """
You are a video generator, write one piece of code which contains all steps to generate videos according to user requirements.
"""

    functions = [
        skills.image_generation,
        skills.stable_video_diffusion,
        skills.concatenate_videos,
        skills.text_to_speech,
        skills.generate_music,
        skills.merge_video_audio
    ]

    agent = Agent.with_functions(functions)
    agent.add_role_prompt(role_prompt)
    await agent.run(input, output_callback=output_callback)


