from GeneralAgent.agent import Agent

async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    agent = Agent.with_link_memory('./data/')
    if file_path is not None:
        input = f"""```read\n{file_path}\n```"""
    await agent.run(input, output_callback=output_callback)