
def main(chat_history, input:str, file_path:str, output_callback, file_callback, send_ui):
    """
    input: for example, {"data":518102.454}
    """
    from GeneralAgent import skills
    file_path = skills.unique_name() + '.json'
    with open(file_path, 'w') as f:
        f.write(input)
    message = f'I receive: {input}, And write to file [{file_path}](sandbox:{file_path})'
    output_callback(message)