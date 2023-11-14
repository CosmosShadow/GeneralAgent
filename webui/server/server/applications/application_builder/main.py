
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent.agent import Agent
    agent = Agent.agent_builder()
    await agent.run(input, output_callback=output_callback)