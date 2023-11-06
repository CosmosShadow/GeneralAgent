
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    result = skills.task_to_ui_js(input)
    if result is not None:
        lib_name, js_path = result
        data = {}
        await ui_callback(lib_name, js_path, data)
        # name, js_path, data={}
    else:
        # ui_callback('Something wrong')
        output_callback('Something wrong')
        output_callback(None)