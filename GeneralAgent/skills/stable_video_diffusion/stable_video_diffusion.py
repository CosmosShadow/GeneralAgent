def stable_video_diffusion(image_path:str, video_length='14_frames_with_svd', sizing_strategy='maintain_aspect_ratio', frames_per_second=6, motion_bucket_id=127, cond_aug=0.02, decoding_t=14, seed=0) -> str:
    """ 
    Generate Video. Convert an image to a video using the stability-ai/stable-video-diffusion model.
    
    Parameters:
    image_path (str): The path to the input image.
    video_length (str): Use svd to generate 14 frames or svd_xt for 25 frames. Default is '14_frames_with_svd'.
    sizing_strategy (str): Decide how to resize the input image. Default is 'maintain_aspect_ratio'.
    frames_per_second (int): Frames per second. Default is 6.
    motion_bucket_id (int): Increase overall motion in the generated video. Default is 127.
    cond_aug (float): Amount of noise to add to input image. Default is 0.02.
    decoding_t (int): Number of frames to decode at a time. Default is 14.
    seed (int): Random seed. Default is 0.

    Returns:
    str: The path of the generated video.
    """
    import replicate
    video_url = replicate.run(
        "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
        input={
            "input_image": open(image_path, "rb"),
            "video_length": video_length,
            "sizing_strategy": sizing_strategy,
            "frames_per_second": frames_per_second,
            "motion_bucket_id": motion_bucket_id,
            "cond_aug": cond_aug,
            "decoding_t": decoding_t,
            "seed": seed
        }
    )
    from GeneralAgent import skills
    video_path  = skills.try_download_file(video_url)
    print(f'video created at [{video_path}]({video_path})')
    return video_path

def test_stable_video_diffusion():
    import os
    image_path = os.path.join(os.path.dirname(__file__), 'dab774a452f3.jpg')
    video_path = stable_video_diffusion(image_path)
    assert os.path.exists(video_path)
    os.remove(video_path)