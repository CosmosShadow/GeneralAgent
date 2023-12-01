def merge_video_audio(video_path:str, narration_path:str, music_path:str, base_element:str='video') -> str:
    """
    Merge video, narration, and background music into a final video based on the length of the base element.
    Parameters: video_path -- path of the video file, string
                narration_path -- path of the narration audio file, string
                music_path -- path of the background music file, string
                base_element -- which element's length to use as the base, string, default is 'video'
    Returns: the path of the final video file, string
    """
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

    # Load audio files
    narration = AudioFileClip(narration_path)
    music = AudioFileClip(music_path)

    # Load video file
    video = VideoFileClip(video_path)

    # Determine base length
    if base_element == 'video':
        base_length = video.duration
    elif base_element == 'narration':
        base_length = narration.duration
    elif base_element == 'music':
        base_length = music.duration

    # Adjust lengths of elements
    narration = narration.subclip(0, base_length)
    music = music.subclip(0, base_length)

    # Merge audio files
    final_audio = CompositeAudioClip([narration, music])

    # Set audio of video file to final audio
    final_video = video.set_audio(final_audio)

    # Save final video file
    from GeneralAgent import skills
    final_video_path = skills.unique_name() + ".mp4"
    final_video.write_videofile(final_video_path)

    return final_video_path


def test_merge_video_audio():
    """
    Test merge_video_audio function
    """
    import os
    video_path = os.path.join(os.path.dirname(__file__), "video.mp4")
    narration_path = os.path.join(os.path.dirname(__file__), "narration.mp3")
    music_path = os.path.join(os.path.dirname(__file__), "music.wav")
    final_video_path = merge_video_audio(video_path, narration_path, music_path)
    assert os.path.exists(final_video_path)
    os.remove(final_video_path)
    # os.remove("./final_audio.mp3")

if __name__ == '__main__':
    test_merge_video_audio()