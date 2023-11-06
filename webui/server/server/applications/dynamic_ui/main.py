
async def main(chat_history, input, file_path, output_callback, file_callback, send_ui):
    from GeneralAgent import skills
    result = skills.create_ui(input)
    if result is not None:
        lib_name, js_path = result
        data = {}
        await send_ui(lib_name, js_path, data)
        # name, js_path, data={}
    else:
        # send_ui('Something wrong')
        output_callback('Something wrong')
        output_callback(None)