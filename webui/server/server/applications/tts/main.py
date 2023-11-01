
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    text = input
    if file_path is not None:
        text = skills.read_file_content(file_path)
    save_path = skills.unique_name() + '.mp3'
    await skills.text_to_speech(text, save_path)
    await file_callback(save_path)
    