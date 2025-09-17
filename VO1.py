from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip # type: ignore
import os
from typing import List

def add_text_to_video(input_folder: str, output_folder: str) -> None:
    """
    Add "Hello World" text overlay to all MP4 videos in the input folder.
    
    Args:
        input_folder: Path to folder containing input MP4 files
        output_folder: Path to folder where modified videos will be saved
    """
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp4"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"modified_{filename}")

            # Load the video
            video = VideoFileClip(input_path)

            # Create a TextClip with "Hello World"
            txt_clip = TextClip(
                "Hello World",
                fontsize=50,
                color="white",
                font="Arial-Bold"  # Ensure this font is available
            ).set_position(("center", "top")).set_duration(video.duration)

            # Overlay the text on the video
            final_video = CompositeVideoClip([video, txt_clip])

            # Write the output video file
            final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

            print(f"Processed: {filename}")

    print("All videos processed successfully!")

# Example usage
input_folder = "input_videos"  # Folder containing .mp4 files
output_folder = "output_videos"  # Folder to save modified videos

add_text_to_video(input_folder, output_folder)
