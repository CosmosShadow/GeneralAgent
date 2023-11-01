
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from skills import skills
    system_prompt = "Please edit the following passage using the Emoji style, which is characterized by captivating headlines, the inclusion of emoticons in each paragraph, and the addition of relevant tags at the end. Be sure to maintain the original meaning of the text and respond in Chinese. Please begin by editing the following text: " + input
    messages = [{"role": "system", "content": system_prompt}]
    response = skills.llm_inference(messages)
    for token in response:
        await output_callback(token)
    await output_callback(None)