async def main(messages, input, output_callback):
    from GeneralAgent import skills
    import json

    data = json.loads(input)['data']
    file_path = data['file']
    language = data.get('language', 'chinese')

    content = skills.read_file_content(file_path)
    translated_content = skills.translate_text(content, language)

    output_file_path = './translated_file.txt'
    skills.write_file_content(output_file_path, translated_content)

    await output_callback(f'Translated file: [translated_file.txt](sandbox:{output_file_path})')