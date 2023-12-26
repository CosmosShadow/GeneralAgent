
def main(cache, messages, input, files, output_callback):
    from GeneralAgent import skills
    messages = skills.cut_messages(messages, 6000)
    messages = [{"role": "system", "content": "You are a helpful assistant."}] + messages
    response = skills.llm_inference(messages, model_type='smart', stream=True)
    for token in response:
        output_callback(token)
    output_callback(None)