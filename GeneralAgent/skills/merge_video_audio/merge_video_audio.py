def merge_video_audio(video_path:str, narration_path:str=None, music_path:str=None) -> str:
    """
    Merge video, narration, and background music into a final video based on the shortest length among all elements.
    Parameters: video_path -- path of the video file, string
                narration_path -- path of the narration audio file, string, can be None
                music_path -- path of the background music file, string, can be None
    Returns: the path of the final video file, string
    """
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

    # Load video file
    video = VideoFileClip(video_path)

    # Load audio files if they exist
    audio_clips = []
    durations = [video.duration]
    if narration_path is not None:
        narration = AudioFileClip(narration_path)
        audio_clips.append(narration)
        durations.append(narration.duration)
    if music_path is not None:
        music = AudioFileClip(music_path)
        audio_clips.append(music)
        durations.append(music.duration)

    # Determine base length
    base_length = min(durations)

    # Adjust lengths of elements
    audio_clips = [clip.subclip(0, base_length) for clip in audio_clips]

    # Merge audio files
    if len(audio_clips) == 1:
        final_audio = audio_clips[0]
    elif audio_clips:
        final_audio = CompositeAudioClip(audio_clips)
    else:
        final_audio = None

    # Set audio of video file to final audio
    final_video = video.subclip(0, base_length)
    if final_audio is not None:
        final_video = final_video.set_audio(final_audio)

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