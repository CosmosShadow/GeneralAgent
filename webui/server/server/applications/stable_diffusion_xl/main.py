
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    prompt = input
    if not skills.text_is_english(prompt):
        prompt = skills.translate_text(prompt, 'english')
    image_url = skills.image_generation(prompt)
    await file_callback(image_url)