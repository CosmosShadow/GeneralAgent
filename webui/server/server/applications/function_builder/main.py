
def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    agent = skills.get_function_builder_agent()
    agent.run(input, output_callback=output_callback)