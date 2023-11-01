
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    if file_path is None:
        await output_callback('Please upload a voice file')
        return
    text, language = skills.speech_to_text(file_path)
    await output_callback(text)
    