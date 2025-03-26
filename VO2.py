import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def add_watermark_to_videos(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp4"):
            input_path = os.path.join(folder_path, filename)
            output_path = os.path.join(folder_path, f"watermarked_{filename}")
            
            try:
                # Load video file
                clip = VideoFileClip(input_path)
                
                # Reduce audio volume by 80%
                clip = clip.volumex(0.8)
                
                # Create text watermark
                txt_clip = TextClip(
                    "Hello World",
                    fontsize=50,
                    color='white',
                    font="Arial-Bold.ttf",  # Ensure this font is available
                    stroke_color='black',
                    stroke_width=2
                ).set_duration(clip.duration).set_position(('center', 'bottom'))
                
                # Overlay text onto video
                final_video = CompositeVideoClip([clip, txt_clip])
                
                # Export video
                final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
                
                print(f"Processed: {filename} -> {output_path}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    folder_path = "./videos"  # Change this to your folder containing MP4 files
    add_watermark_to_videos(folder_path)
