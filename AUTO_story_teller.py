#!/usr/bin/env python3
"""
auto_story_teller.py

Automatic story teller from video.
Takes a video file, extracts frames, analyzes them with LLM,
generates a story, chooses voice based on mood, and adds narration.
"""

import asyncio
import base64
import json
import logging
import os
import shutil
import tempfile
import time
from typing import List, Optional

import cv2
import numpy as np
from dotenv import load_dotenv
from openai import AsyncOpenAI
from PIL import Image
from tqdm.asyncio import tqdm
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, VideoFileClip, concatenate_audioclips, CompositeAudioClip

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)

async def extract_frames(video_path: str, max_frames: int = 10) -> List[str]:
    """
    Extract frames from video, distributing them evenly.
    Returns list of frame image paths.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if total_frames <= max_frames:
        frame_indices = list(range(total_frames))
    else:
        frame_indices = [int(i * total_frames / max_frames) for i in range(max_frames)]

    frames = []
    temp_dir = tempfile.mkdtemp()

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            frame_path = os.path.join(temp_dir, f"frame_{len(frames):04d}.png")
            img.save(frame_path)
            frames.append(frame_path)

    cap.release()
    return frames

async def analyze_frame(client: AsyncOpenAI, frame_path: str) -> str:
    """
    Analyze a frame using OpenAI vision API.
    """
    with open(frame_path, "rb") as f:
        image_data = f.read()

    base64_image = base64.b64encode(image_data).decode('utf-8')

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Create fun adventure story from image details, make sound like news reporter. Focus on people, objects, actions, setting, and mood."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    }
                ]
            }
        ],
        max_tokens=3000
    )

    return response.choices[0].message.content.strip()

async def generate_story(client: AsyncOpenAI, frame_descriptions: List[str]) -> str:
    """
    Generate a cohesive story from frame descriptions.
    """
    descriptions_text = "\n".join(f"Frame {i+1}: {desc}" for i, desc in enumerate(frame_descriptions))

    system = "You are a creative storyteller. Create an engaging narrative story based on the sequence of image descriptions."
    user = f"""
Based on these sequential frame descriptions from a video, create a cohesive and engaging story.
Make it narrative and flowing, connecting the scenes naturally.
Keep the story concise but complete.

Frame descriptions:
{descriptions_text}

Write the story:
"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()

async def analyze_mood_and_choose_voice(client: AsyncOpenAI, story: str) -> tuple[str, str]:
    """
    Analyze the story mood and choose appropriate TTS voice and background music.
    Returns (voice, music_file)
    """
    system = "You are a voice casting director and music supervisor. Choose the most appropriate OpenAI TTS voice and background music style for narrating a story based on its mood and content."
    user = f"""
Analyze this story and choose the best OpenAI TTS voice and background music style.

Story:
{story}

Voice options: alloy, echo, fable, onyx, nova, shimmer
Music styles: calm, epic, mysterious, upbeat, dramatic, peaceful

Return only JSON with keys: voice, music_style
"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.3,
        max_tokens=50,
        response_format={"type": "json_object"}
    )

    try:
        result = json.loads(response.choices[0].message.content)
        voice = result.get("voice", "alloy")
        music_style = result.get("music_style", "calm")
    except Exception as e:
        logger.warning(f"Failed to parse mood analysis: {e}")
        voice = "alloy"
        music_style = "calm"

    valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    if voice not in valid_voices:
        voice = "alloy"

    return voice, music_style

def select_background_music(music_style: str, custom_music: Optional[str] = None) -> Optional[str]:
    """
    Select background music file based on style or custom file.
    Returns path to music file.
    """
    if custom_music and os.path.exists(custom_music):
        return custom_music

    music_dir = "music"
    if not os.path.exists(music_dir):
        logger.warning(f"Music directory '{music_dir}' not found. Skipping background music.")
        return None

    style_files = {
        "calm": ["calm.mp3", "peaceful.mp3", "relaxing.mp3"],
        "epic": ["epic.mp3", "heroic.mp3", "dramatic.mp3"],
        "mysterious": ["mysterious.mp3", "suspense.mp3", "dark.mp3"],
        "upbeat": ["upbeat.mp3", "happy.mp3", "energetic.mp3"],
        "dramatic": ["dramatic.mp3", "intense.mp3", "epic.mp3"],
        "peaceful": ["peaceful.mp3", "calm.mp3", "serene.mp3"]
    }

    candidates = style_files.get(music_style, ["calm.mp3"])
    for filename in candidates:
        filepath = os.path.join(music_dir, filename)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return filepath

    for file in os.listdir(music_dir):
        if file.endswith('.mp3'):
            filepath = os.path.join(music_dir, file)
            if os.path.getsize(filepath) > 0:
                return filepath

    logger.warning(f"No suitable music file found for style '{music_style}'. Skipping background music.")
    return None

def mix_audio_with_music(narration_file: str, music_file: str, output_file: str, narration_volume: float = 1.0, music_volume: float = 0.3) -> None:
    """
    Mix narration audio with background music with adjustable volume levels.
    """
    logger.info(f"Mixing audio - Voice: {narration_volume}, Music: {music_volume}")

    narration_clip = AudioFileClip(narration_file).volumex(narration_volume)
    music_clip = AudioFileClip(music_file).volumex(music_volume)

    # Ensure music loops to match narration duration
    if music_clip.duration < narration_clip.duration:
        clips = []
        remaining_duration = narration_clip.duration
        while remaining_duration > 0:
            clip_duration = min(remaining_duration, music_clip.duration)
            clips.append(music_clip.subclip(0, clip_duration))
            remaining_duration -= clip_duration
        music_clip = concatenate_audioclips(clips)
    else:
        music_clip = music_clip.subclip(0, narration_clip.duration)

    # Mix the audio tracks
    mixed_audio = CompositeAudioClip([narration_clip, music_clip])

    # Normalize audio to prevent clipping
    max_volume = max(narration_volume, music_volume)
    if max_volume > 1.0:
        mixed_audio = mixed_audio.volumex(1.0 / max_volume)

    final_audio = mixed_audio.set_fps(44100)  # Set a standard fps for audio
    final_audio.write_audiofile(output_file, verbose=False, logger=None)

async def generate_audio(client: AsyncOpenAI, text: str, output_file: str, voice: str = "alloy") -> None:
    """
    Generate audio from text using OpenAI TTS. Splits text into <=4096 char chunks and concatenates audio.
    """
    max_len = 4096
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    temp_files = []
    for idx, chunk in enumerate(chunks):
        temp_file = output_file + f".part{idx}.mp3"
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=chunk
        )
        response.write_to_file(temp_file)
        temp_files.append(temp_file)
    # Concatenate audio files
    clips = [AudioFileClip(f) for f in temp_files]
    final = concatenate_audioclips(clips)
    final.write_audiofile(output_file, verbose=False, logger=None)
    for f in temp_files:
        try:
            os.remove(f)
        except Exception:
            pass

def add_audio_to_video(video_file: str, audio_file: str, output_file: str) -> None:
    """
    Add audio to video using moviepy.
    """
    try:
        logger.info(f"Loading video: {video_file}")
        video_clip = VideoFileClip(video_file)
        logger.info(f"Video duration: {video_clip.duration}")

        logger.info(f"Loading audio: {audio_file}")
        audio_clip = AudioFileClip(audio_file)
        logger.info(f"Audio duration: {audio_clip.duration}")

        if audio_clip.duration > video_clip.duration:
            logger.info("Trimming audio to match video duration")
            audio_clip = audio_clip.subclip(0, video_clip.duration)
        elif audio_clip.duration < video_clip.duration:
            logger.info("Looping audio to match video duration")
            clips = []
            remaining_duration = video_clip.duration
            while remaining_duration > 0:
                clip_duration = min(remaining_duration, audio_clip.duration)
                clips.append(audio_clip.subclip(0, clip_duration))
                remaining_duration -= clip_duration
            audio_clip = concatenate_audioclips(clips)

        logger.info("Setting audio to video")
        final_clip = video_clip.set_audio(audio_clip)

        logger.info(f"Writing final video to: {output_file}")
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=30, verbose=False, logger=None)
        logger.info("Video creation completed")

    except Exception as e:
        logger.error(f"Error in add_audio_to_video: {e}")
        raise

# Initialize a pre-trained object detection model (e.g., MobileNet-SSD, YOLO, etc.)
# For simplicity, we use a placeholder function for object detection.
def detect_objects(frame):
    # Replace this with actual object detection logic
    # Example: Use a pre-trained model like YOLO or OpenCV's DNN module
    detected_objects = ["human", "drum"]  # Example detected objects
    return detected_objects

# Function to detect objects and log their detection time
def detect_objects_with_time(frame):
    detected_objects = []  # Replace with actual object detection logic
    current_time = time.time()  # Get the current timestamp

    for obj in detected_objects:
        print(f"Object detected: {obj} at time {current_time}")
        # Log or store the object and its detection time for future use
        # Example: detected_objects_with_time.append((obj, current_time))

    return detected_objects

# Function to process video frames and log detected objects with timestamps
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Unable to open video file.")
        return

    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process every frame
        current_time = frame_count / frame_rate
        detected_objects = detect_objects(frame)

        for obj in detected_objects:
            print(f"Detected {obj} at time {current_time:.2f} seconds")

        frame_count += 1

    cap.release()
    print("Video processing complete.")

def create_zoom_video(image_paths: List[str], durations: List[int], output_file: str, fps: int = 30, zoom_factor: float = 1.1) -> None:
    """
    Create video from images with slow zoom effect using moviepy.
    """
    clips = []
    for img_path, duration in zip(image_paths, durations):
        clip = ImageClip(img_path).set_duration(duration)
        # Apply slow zoom effect
        def zoom(t):
            factor = 1 + (zoom_factor - 1) * (t / duration)
            return factor, factor
        clip = clip.resize(zoom)
        clips.append(clip)
    video = concatenate_videoclips(clips, method="compose")
    video.write_videofile(output_file, fps=fps, codec='libx264', audio=False, verbose=False, logger=None)

def get_unique_output_path(base_path: str) -> str:
    """
    Generate a unique output path by appending a 2-digit number if the file already exists.
    """
    if not os.path.exists(base_path):
        return base_path
    
    base, ext = os.path.splitext(base_path)
    for i in range(1, 100):
        new_path = f"{base}{i:02d}{ext}"
        if not os.path.exists(new_path):
            return new_path
    
    # Fallback: append timestamp if all 99 numbers are taken
    timestamp = int(time.time())
    return f"{base}_{timestamp}{ext}"

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate story narration from video")
    parser.add_argument("video", help="Input video file")
    parser.add_argument("--output", "-o", default="story_video.mp4", help="Output video file")
    parser.add_argument("--max-frames", "-m", type=int, default=10, help="Maximum number of frames to analyze")
    parser.add_argument("--custom-music", help="Path to custom background music file")
    parser.add_argument("--voice-volume", type=float, default=1.0, help="Voice narration volume (0.0-2.0, default: 1.0)")
    parser.add_argument("--music-volume", type=float, default=0.3, help="Background music volume (0.0-1.0, default: 0.3)")
    parser.add_argument("--voice-mood", help="Override automatic mood detection. Options: happy, sad, calm, epic, mysterious, upbeat, dramatic, peaceful")
    args = parser.parse_args()

    if not os.path.exists(args.video):
        logger.error(f"Input video file '{args.video}' not found")
        return

    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return

    try:
        client = AsyncOpenAI(api_key=api_key)
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {e}")
        return

    logger.info(f"Processing video: {args.video}")

    # Ensure output file is in the same folder as input video
    input_dir = os.path.dirname(os.path.abspath(args.video))
    output_filename = os.path.basename(args.output)
    output_path = os.path.join(input_dir, output_filename)
    
    # Generate unique output path with 2-digit number if needed
    unique_output_path = get_unique_output_path(output_path)
    args.output = unique_output_path
    logger.info(f"Output will be saved to: {args.output}")

    temp_dir = None
    try:
        logger.info("Extracting frames...")
        frame_paths = await extract_frames(args.video, args.max_frames)
        if not frame_paths:
            logger.error("No frames extracted from video")
            return
        logger.info(f"Extracted {len(frame_paths)} frames")

        logger.info("Analyzing frames...")
        tasks = [analyze_frame(client, path) for path in frame_paths]
        frame_descriptions = []
        for desc in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Analyzing frames"):
            try:
                frame_descriptions.append(await desc)
            except Exception as e:
                logger.warning(f"Error analyzing frame: {e}")

        if not frame_descriptions:
            logger.error("No frame descriptions generated")
            return

        logger.info("Generating story...")
        story = await generate_story(client, frame_descriptions)
        logger.info(f"Story: {story[:200]}...")

        logger.info("Choosing voice and background music...")
        if args.voice_mood:
            # Manual override for mood
            mood_map = {
                "happy": ("nova", "upbeat"),
                "sad": ("echo", "calm"),
                "calm": ("alloy", "peaceful"),
                "epic": ("onyx", "epic"),
                "mysterious": ("shimmer", "mysterious"),
                "upbeat": ("nova", "upbeat"),
                "dramatic": ("fable", "dramatic"),
                "peaceful": ("alloy", "peaceful"),
            }
            voice, music_style = mood_map.get(args.voice_mood.lower(), ("alloy", "calm"))
            logger.info(f"Manual mood override: {args.voice_mood} -> Voice: {voice}, Music style: {music_style}")
        else:
            voice, music_style = await analyze_mood_and_choose_voice(client, story)
            logger.info(f"Selected voice: {voice}, Music style: {music_style}")

        logger.info("Generating narration audio...")
        temp_dir = tempfile.mkdtemp()
        narration_file = os.path.join(temp_dir, "narration.mp3")
        await generate_audio(client, story, narration_file, voice)

        music_file = select_background_music(music_style, args.custom_music)
        if music_file:
            logger.info(f"Using background music: {music_file}")
            mixed_audio_file = os.path.join(temp_dir, "mixed_audio.mp3")
            mix_audio_with_music(narration_file, music_file, mixed_audio_file, args.voice_volume, args.music_volume)
            final_audio_file = mixed_audio_file
        else:
            final_audio_file = narration_file

        logger.info("Adding audio to video...")
        add_audio_to_video(args.video, final_audio_file, args.output)
        logger.info(f"Story video created: {args.output}")

    except Exception as e:
        logger.error(f"Error processing video: {e}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(main())

