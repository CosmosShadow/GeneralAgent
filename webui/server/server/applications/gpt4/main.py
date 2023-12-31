
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    chat_history = skills.cut_messages(chat_history, 6000)
    messages = [{"role": "system", "content": "You are a helpful assistant."}] + chat_history
    response = skills.llm_inference(messages, model_type='smart', stream=True)
    for token in response:
        await output_callback(token)
    await output_callback(None)