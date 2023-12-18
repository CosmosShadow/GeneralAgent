
def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    image_path = skills.image_generation(input)
    file_callback(image_path)