# replicate api

def _replicate_image_generation(prompt):
    """generate a image with prompt (in english), return a image url"""

    # import replicate
    # output = replicate.run(
    #     "cjwbw/taiyi-stable-diffusion-1b-chinese-v0.1:36c580142e9fbbd52e5e678e30541c0da6f2021c9d2039a5c00be192a010e8c5",
    #     input={"prompt": prompt}
    # )
    # print(output)

    # 图片生成切换成为sdxl的version 1 版本
    import replicate

    output = replicate.run(
        # "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
        "stability-ai/sdxl:2f779eb9b23b34fe171f8eaa021b8261566f0d2c10cd2674063e7dbcd351509e",
        input={"prompt": prompt}
    )
    image_url = output[0]
    # print(image_url)

    return image_url


def image_generation(prompt) -> str:
    """
    Generate an image according to the prompt and return the image path. For example, when the prompt is "apple" you will get an image of an apple. Note: The prompt should describe objective things in detail, not abstract concepts. For example, if you want to draw a picture of Chengdu, the prompt should be "Picture of Chengdu, with giant pandas playing in the bamboo forest, people eating hot pot around, and a Jinsha Sunbird totem next to it" instead of "Draw a picture of Chengdu" "painting"
    @param prompt: The prompt should be detailed enough to describe the image. Tips can be in any type of language, but English is recommended.
    """
    from GeneralAgent import skills
    if not skills.text_is_english(prompt):
        prompt = skills.translate_text(prompt, 'english')
    image_url = _replicate_image_generation(prompt)
    image_path  = skills.try_download_file(image_url)
    print(f'image created at ![{image_path}]({image_path})')
    return image_path

def face_restoration(image_path):
    """ Practical face restoration algorithm for old photos or AI-generated faces. input image path, and return the new image path"""
    import replicate
    from GeneralAgent import skills
    image_url = replicate.run(
        "tencentarc/gfpgan:9283608cc6b7be6b65a8e44983db012355fde4132009bf99d976b2f0896856a3",
        input={"img": open(image_path, "rb")}
    )
    new_image_path  = skills.try_download_file(image_url)
    return new_image_path

def qrcode_stable_diffusion(prompt, qr_code_content):
    """generate a qrcode image with prompt, return a image url"""
    import replicate
    output = replicate.run(
        "nateraw/qrcode-stable-diffusion:9cdabf8f8a991351960c7ce2105de2909514b40bd27ac202dba57935b07d29d4",
        input={"prompt": prompt, 'qr_code_content': qr_code_content}
    )
    return output[0]

def speech_to_text(audio_file_path):
    """Convert speech in audio to text, return a text and the language of the text"""
    import replicate
    output = replicate.run(
        "openai/whisper:91ee9c0c3df30478510ff8c8a3a545add1ad0259ad3a9f78fba57fbc05ee64f7",
        input={"audio": open(audio_file_path, "rb")}
    )
    print(output)
    language = output['detected_language']
    text = output['transcription']

    return text, language


if __name__ == '__main__':
    image_generation('a cat')