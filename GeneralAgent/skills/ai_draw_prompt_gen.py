
def ai_draw_prompt_gen(command):
    """The prompt word generator for AI painting inputs the user's needs and outputs a description word for a picture."""
    from GeneralAgent import skills
    system_prompt = "You are a prompt word engineer for AI painting. Your task is to describe the user's needs into descriptors for a picture, and require the content of the picture to meet the user's needs as much as possible. You can add some of your own creativity and understanding. Directly returns the description of the image without explanation or suffixes."
    messages = [
        {'role': 'system', 'content': system_prompt},
        {"role": "user", "content": command}
    ]
    image_prompt = skills.llm_inference(messages)
    return image_prompt