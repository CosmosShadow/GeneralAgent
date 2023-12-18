
def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    chat_history = skills.cut_messages(chat_history, 15*1000)
    messages = [{"role": "system", "content": "You are a helpful assistant."}] + chat_history
    response = skills.llm_inference(messages, model_type='long', stream=True)
    for token in response:
        output_callback(token)
    output_callback(None)