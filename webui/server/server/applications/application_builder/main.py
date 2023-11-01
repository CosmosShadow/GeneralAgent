
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    code = skills.function_code_generation(input)
    await output_callback(code)
    await output_callback(None)
