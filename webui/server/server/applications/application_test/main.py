from GeneralAgent.agent import Agent

async def main(chat_history, input, file_path, output_callback, file_callback, send_ui):
    message = 'I receive: ' + input
    await output_callback(message)