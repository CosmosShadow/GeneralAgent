from GeneralAgent.agent import Agent
import sys, os
# sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../'))
from server import task_to_ui_js

async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    result = task_to_ui_js(input)
    if result is not None:
        js_path, lib_name = result
        data = {}
        await ui_callback(lib_name, js_path, data)
        # name, js_path, data={}
    else:
        # ui_callback('Something wrong')
        output_callback('Something wrong')
        output_callback(None)