def text_translation(text, language):
    """Translates the given text into the specified language, e.g. text_translation('I love china', 'chinese'). For efficiency, You Must translate larger text blocks at once."""
    """translate the text to language, like chinese, english, frech etc. like text_translation('I love china', 'chinese'). Try to translate more content at once, instead of calling multiple times"""
    from skills import skills
    segments = skills.split_text(text, 1800)
    translated = []
    system_prompt = [{"role": "system", "content": f"You are a translator, translate the following text to {language}."}]
    for x in segments:
        messages = system_prompt + [{"role": "user", "content": x}]
        translated += [skills.sync_llm_inference(messages)]
    return '. '.join(translated)