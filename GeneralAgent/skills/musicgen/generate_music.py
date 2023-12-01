def generate_music(prompt: str, model_version: str = 'stereo-melody-large', duration: int = 8, output_format: str = 'wav') -> str:
    """
    Generate music according to the prompt and return the music file path. prompt should be english.
    @param prompt: A description of the music you want to generate.
    @param model_version: Model to use for generation. Default is 'stereo-melody-large'.
    @param duration: Duration of the generated audio in seconds. Default is 8.
    @param output_format: Output format for generated audio. Default is 'wav'.
    """
    import replicate
    from GeneralAgent import skills

    output = replicate.run(
        "meta/musicgen:7be0f12c54a8d033a0fbd14418c9af98962da9a86f5ff7811f9b3423a1f0b7d7",
        input={
            "model_version": model_version,
            "prompt": prompt,
            "duration": duration,
            "output_format": output_format
        }
    )
    music_url = output
    music_path = skills.try_download_file(music_url)
    print(f'Music created at {music_path}')
    return music_path

def test_generate_music():
    import os
    music_path = generate_music('Happy birthday song', 'stereo-melody-large', 10, 'mp3')
    assert os.path.exists(music_path), "Music file does not exist."

if __name__ == '__main__':
    test_generate_music()