
# https://platform.openai.com/docs/guides/text-to-speech/

def text_to_speech(text, voice='onyx'):
    """
    Convert text to speech, retrun the audio file path.
    @param text: text to convert
    @param voice: voice name, default is 'onyx' (male), other options are: 'nova' (female)
    @return: audio file path
    """
    from openai import OpenAI
    import os
    client = OpenAI(base_url=os.environ['OPENAI_API_BASE'])
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )
    from GeneralAgent import skills
    file_path = skills.unique_name() + '.mp3'
    response.stream_to_file(file_path)
    return file_path


def create_image(prompt) -> str:
    """draw image given a prompt, returns the image path. Note: limit to generate violent, adult, or hateful content"""
    import os
    from openai import OpenAI
    from GeneralAgent import skills

    client = OpenAI(base_url=os.environ['OPENAI_API_BASE'])
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    image_path = skills.try_download_file(image_url)
    return image_path


def edit_image(image_path:str, prompt:str) -> str:
    """Edit image given a prompt, returns the image path"""
    import os
    from openai import OpenAI
    from GeneralAgent import skills
    from pathlib import Path

    client = OpenAI(base_url=os.environ['OPENAI_API_BASE'])
    response = client.images.edit(
        image = Path(image_path),
        prompt = prompt,
        n=1,
    )
    image_url = response.data[0].url
    image_path = skills.try_download_file(image_url)
    return image_path


if __name__ == '__main__':

    image_path  = create_image('a picture of a dog')