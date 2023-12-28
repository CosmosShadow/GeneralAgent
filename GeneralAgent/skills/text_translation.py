def translate_text(text, language):
    """Translates the given text into the specified language, e.g. translate_text('I love china', 'chinese'). For efficiency, You Must translate larger text blocks at once."""
    """translate the text to language, like chinese, english, frech etc. like translate_text('I love china', 'chinese'). Try to translate more content at once, instead of calling multiple times"""
    from GeneralAgent import skills
    segments = skills.split_text(text, 1800)
    translated = []
    # system_prompt = [{"role": "system", "content": f"You are a translator, translate the following text to {language}."}]
    for x in segments:
        # messages = system_prompt + [{"role": "user", "content": x}]
        messages = [
            {"role": "system", "content": 'You are a helpful assistant that translates text.'},
            {"role": "user", "content": f'翻译下面被---------包围起来的文字成{language}。注意，返回翻译全文，不要任何解释和描述。: \n---------\n{x}\n---------\n'}
        ]
        translated += [skills.llm_inference(messages)]
    return '. '.join(translated)


def _translate_text(text, target_language):
    # This is write by Agent builder
    """
    Translate a given text into the specified language using the large language model.

    Parameters:
    text (str): The text to be translated.
    target_language (str): The language to which the text should be translated.

    Returns:
    str: The translated text.
    """
    # Importing necessary libraries
    import numpy as np
    from GeneralAgent import skills

    # Defining constants
    MAX_TOKENS = 8000

    # Splitting the text into chunks of suitable size
    text_chunks = []
    while len(text) > 0:
        if len(text) > MAX_TOKENS:
            chunk, text = text[:MAX_TOKENS], text[MAX_TOKENS:]
        else:
            chunk, text = text, ""
        text_chunks.append(chunk)

    # Translating each chunk
    translated_text = ""
    for chunk in text_chunks:
        # Preparing the messages for the LLM
        messages = [
            {"role": "system", "content": 'You are a helpful assistant that translates text.'},
            {"role": "user", "content": f'Translate the following text to {target_language}: "{chunk}"'}
        ]

        # Defining the JSON schema for the return dictionary
        json_schema = {
            "type": "object",
            "properties": {
                "translated_text": {"type": "string"}
            }
        }

        # Running the LLM inference
        result = skills.llm_inference_to_json(messages, json_schema)

        # Adding the translated chunk to the final translated text
        translated_text += result["translated_text"]

    return translated_text