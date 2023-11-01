
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from skills import skills
    while skills.messages_token_count(chat_history) > 15*1000:
        chat_history.pop(0)
    messages = [{"role": "system", "content": "You are a helpful assistant."}] + chat_history
    response = skills.llm_inference(messages, model_type='long')
    for token in response:
        await output_callback(token)
    await output_callback(None)