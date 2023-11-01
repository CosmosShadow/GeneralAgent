from GeneralAgent.agent import Agent

async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    agent = Agent.default('./data/')
    await agent.run(input, output_callback=output_callback)