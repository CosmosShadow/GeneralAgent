from GeneralAgent.agent import Agent
from GeneralAgent.agent import LinkAgent

async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    agent = LinkAgent('./data/')
    if file_path is not None:
        await output_callback(f'Start to read file {file_path}.')
        context = skills.read_file_content(file_path)
        await agent.read_content(context)
        await output_callback('\nRead finish.')
    else:
        await agent.run(input, output_callback=output_callback)


# async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
#     agent = Agent.with_link_memory('./data/')
#     if file_path is not None:
#         input = f"""```read\n{file_path}\n```"""
#     await agent.run(input, output_callback=output_callback)