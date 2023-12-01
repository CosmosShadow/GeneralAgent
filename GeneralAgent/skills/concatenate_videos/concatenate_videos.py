
def concatenate_videos(video_list: list) -> str:
    """
    Concatenate a list of videos into one video.
    @param video_list: A list of video file paths.
    @return: The file path of the concatenated video.
    """
    import uuid
    from moviepy.editor import concatenate_videoclips, VideoFileClip
    clips = [VideoFileClip(video) for video in video_list]
    final_clip = concatenate_videoclips(clips)
    output_path = f"{uuid.uuid4().hex}.mp4"  # Generate a unique output file name
    final_clip.write_videofile(output_path)
    return output_path

def test_concatenate_videos():
    """
    Test the concatenate_videos function.
    """
    import os
    file_path = os.path.join(os.path.dirname(__file__), "f63bfaae7b0e.mp4")
    video_list = [file_path, file_path, file_path]  # Use the provided video file for testing
    output_path = concatenate_videos(video_list)
    assert os.path.exists(output_path)

if __name__ == '__main__':
    test_concatenate_videos()