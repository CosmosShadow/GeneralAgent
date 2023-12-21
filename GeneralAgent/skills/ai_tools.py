
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
    # print(f'audio file created: [{file_path}]({file_path})')
    return file_path


def create_image(prompt):
    """
    Draw image given a prompt, returns the image path
    @prompt: A text description of the desired image. The maximum length is 4000 characters.
    @return: image path
    """
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
    # print(f'image created at ![{image_path}]({image_path})')
    return image_path


if __name__ == '__main__':
    # file_path = text_to_speech('hello world')
    # print(file_path)

    image_path  = create_image('a picture of a dog')
    print(image_path)