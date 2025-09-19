#!/usr/bin/env python3
"""
auto_video_generate.py

Automatic video generator using LLM and DALL-E.
Takes a text prompt and generates a video with scenes.
"""

import os
import json
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
from typing import List, Dict, Any
import tempfile
import shutil
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip

# Load environment variables from .env file
load_dotenv()

def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)

def extract_filename_from_prompt(prompt: str) -> str:
    """
    Extract a meaningful filename from the prompt.
    Uses the last significant noun or key concept as the base name.
    """
    import re

    # Clean the prompt
    clean_prompt = re.sub(r'[^\w\s]', '', prompt.lower())

    # Common words to ignore
    stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'}

    # Split into words and filter
    words = [word for word in clean_prompt.split() if word not in stop_words and len(word) > 2]

    # Priority: look for nouns that might represent the conclusion/main concept
    # Try to find the last meaningful word, or combine 2-3 words for better naming
    if len(words) >= 3:
        # Use last 2-3 words for a more descriptive name
        conclusion_words = words[-3:] if len(words) >= 3 else words[-2:]
        filename = '_'.join(conclusion_words)
    elif len(words) >= 1:
        filename = words[-1]  # Last word as fallback
    else:
        filename = 'video'  # Ultimate fallback

    # Clean up the filename (remove special chars, limit length)
    filename = re.sub(r'[^\w\-_]', '', filename)
    filename = filename[:30]  # Limit length

    return filename if filename else 'video'

def generate_scenes(client: OpenAI, prompt: str, num_scenes: int = 5) -> List[Dict[str, str]]:
    """
    Use LLM to generate scenes from the prompt.
    """
    system = "You are a video script writer. Create a complete, cohesive story that fully covers the user's prompt without revision or shortening."
    user = f"""
Create a complete story that fully covers this prompt: "{prompt}"

Then break this complete story into exactly {num_scenes} sequential scenes for a video.

For each scene, provide:
- description: A detailed visual description for image generation that shows this part of the complete story
- text: The narration text for this scene (part of the complete story, not shortened)
- duration: Number of seconds this scene should last (between 3-5)

IMPORTANT: The story must be complete and cover the entire prompt. Do not revise, shorten, or change the original prompt - just break it into scenes.

Return ONLY valid JSON array of objects with keys: description, text, duration
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.7,
        max_tokens=2000
    )

    content = response.choices[0].message.content.strip()
    try:
        scenes = json.loads(content)
        return scenes
    except json.JSONDecodeError:
        # Fallback: try to extract JSON
        import re
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            scenes = json.loads(json_match.group())
            return scenes
        else:
            raise ValueError("Failed to parse scenes from LLM response")

def generate_audio(client: OpenAI, text: str, output_file: str, voice: str = "alloy") -> None:
    """
    Generate audio from text using OpenAI TTS.
    """
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )

    response.stream_to_file(output_file)

def generate_image(client: OpenAI, description: str, size: str = "1024x1024") -> str:
    response = client.images.generate(
        model="dall-e-3",
        prompt=description,
        size=size,
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url

    # Download and save image
    import requests
    img_response = requests.get(image_url)
    if img_response.status_code != 200:
        raise Exception("Failed to download image")

    # Save to temp file
    temp_dir = tempfile.mkdtemp()
    image_path = os.path.join(temp_dir, f"scene_{len(os.listdir(temp_dir))}.png")
    with open(image_path, 'wb') as f:
        f.write(img_response.content)

    return image_path

def add_text_overlay(image_path: str, text: str, output_path: str) -> None:
    """
    Add text overlay to image.
    """
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fallback to default
    try:
        # Try common font paths
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf"
        ]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 40)
                break
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Get text bbox
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Position text at bottom center
    x = (img.width - text_width) // 2
    y = img.height - text_height - 50

    # Draw semi-transparent background
    padding = 20
    bg_bbox = [x - padding, y - padding, x + text_width + padding, y + text_height + padding]
    draw.rectangle(bg_bbox, fill=(0, 0, 0, 128))

    # Draw text
    draw.text((x, y), text, font=font, fill=(255, 255, 255))

    img.save(output_path)

def create_video(image_paths: List[str], durations: List[int], output_file: str, fps: int = 30, zoom_effect: bool = True) -> None:
    """
    Create video from images with specified durations and optional zoom effects.
    """
    if not image_paths:
        raise ValueError("No images provided")

    # Read first image to get dimensions
    first_img = cv2.imread(image_paths[0])
    height, width, _ = first_img.shape

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    for img_path, duration in zip(image_paths, durations):
        img = cv2.imread(img_path)
        frames = duration * fps

        if zoom_effect:
            # Create zoom animation: start at 100% and zoom to 120% over the duration
            for i in range(frames):
                zoom_factor = 1.0 + (0.2 * i / (frames - 1))  # Gradually zoom from 1.0 to 1.2

                # Calculate new dimensions
                new_width = int(width * zoom_factor)
                new_height = int(height * zoom_factor)

                # Resize image with zoom
                zoomed_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

                # Crop to original size (center crop)
                start_x = (new_width - width) // 2
                start_y = (new_height - height) // 2
                cropped_img = zoomed_img[start_y:start_y + height, start_x:start_x + width]

                out.write(cropped_img)
        else:
            # Static image (original behavior)
            for _ in range(frames):
                out.write(img)

    out.release()

def add_audio_to_video(video_file: str, audio_file: str, output_file: str) -> None:
    """
    Add audio to video using moviepy.
    """
    video_clip = VideoFileClip(video_file)
    audio_clip = AudioFileClip(audio_file)

    # If audio is longer than video, trim it; if shorter, loop it
    if audio_clip.duration > video_clip.duration:
        audio_clip = audio_clip.subclip(0, video_clip.duration)
    elif audio_clip.duration < video_clip.duration:
        # Loop audio to match video duration by concatenating
        from moviepy.editor import concatenate_audioclips
        clips = []
        remaining_duration = video_clip.duration
        while remaining_duration > 0:
            clip_duration = min(remaining_duration, audio_clip.duration)
            clips.append(audio_clip.subclip(0, clip_duration))
            remaining_duration -= clip_duration
        audio_clip = concatenate_audioclips(clips)

    # Combine video and audio
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=30, verbose=False, logger=None)

def analyze_mood(description: str, text: str) -> str:
    """
    Simple mood analysis based on keywords. You can replace this with LLM if needed.
    """
    keywords = {
        "happy": ["happy", "joy", "smile", "bright", "cheerful", "upbeat"],
        "sad": ["sad", "gloomy", "dark", "tear", "lonely"],
        "epic": ["epic", "hero", "battle", "adventure", "grand"],
        "peaceful": ["peaceful", "calm", "serene", "quiet", "gentle"],
        "mysterious": ["mysterious", "mystery", "secret", "unknown", "shadow"],
        "dramatic": ["dramatic", "intense", "shock", "surprise", "powerful"]
    }
    desc = (description + " " + text).lower()
    for mood, words in keywords.items():
        if any(word in desc for word in words):
            return mood
    return "peaceful"  # default mood

def mood_to_voice(mood: str) -> str:
    """
    Map mood to OpenAI TTS voice.
    """
    mapping = {
        "happy": "nova",
        "sad": "echo",
        "epic": "onyx",
        "peaceful": "fable",
        "mysterious": "shimmer",
        "dramatic": "alloy"
    }
    return mapping.get(mood, "fable")

def mood_to_music(mood: str) -> str:
    """
    Map mood to music file in music/ folder.
    """
    base = os.path.join(os.path.dirname(__file__), "music")
    mapping = {
        "happy": os.path.join(base, "upbeat.mp3"),
        "sad": os.path.join(base, "calm.mp3"),
        "epic": os.path.join(base, "epic.mp3"),
        "peaceful": os.path.join(base, "peaceful.mp3"),
        "mysterious": os.path.join(base, "mysterious.mp3"),
        "dramatic": os.path.join(base, "dramatic.mp3")
    }
    return mapping.get(mood, os.path.join(base, "peaceful.mp3"))

def generate_unique_filename(base_name: str) -> str:
    """
    Generate a unique filename with two-digit numbering.
    """
    base_name = base_name.replace('.mp4', '')  # Remove extension if present

    # Find the next available number
    counter = 1
    while True:
        filename = f"{base_name}_{counter:02d}.mp4"
        if not os.path.exists(filename):
            return filename
        counter += 1
        if counter > 99:  # Prevent infinite loop
            # If we reach 99, start over from 01 (shouldn't happen in normal use)
            counter = 1
            break

def mix_audio_with_music(voice_file: str, music_file: str, output_file: str, voice_volume: float = 1.0, music_volume: float = 0.3):
    """
    Mix voice and background music with volume control.
    """
    from moviepy.editor import AudioFileClip, CompositeAudioClip
    voice = AudioFileClip(voice_file).volumex(voice_volume)
    music = AudioFileClip(music_file).volumex(music_volume)
    # Loop music if shorter than voice
    if music.duration < voice.duration:
        loops = int(voice.duration // music.duration) + 1
        music = CompositeAudioClip([music] * loops).subclip(0, voice.duration)
    else:
        music = music.subclip(0, voice.duration)
    mixed = CompositeAudioClip([music, voice])
    # Set fps for audio output to prevent AttributeError
    mixed.fps = 44100
    mixed.write_audiofile(output_file, codec="mp3", verbose=False, logger=None)
    """
    Mix voice and background music with volume control.
    """
    from moviepy.editor import AudioFileClip, CompositeAudioClip
    voice = AudioFileClip(voice_file).volumex(voice_volume)
    music = AudioFileClip(music_file).volumex(music_volume)
    # Loop music if shorter than voice
    if music.duration < voice.duration:
        loops = int(voice.duration // music.duration) + 1
        music = CompositeAudioClip([music] * loops).subclip(0, voice.duration)
    else:
        music = music.subclip(0, voice.duration)
    mixed = CompositeAudioClip([music, voice])
    # Set fps for audio output to prevent AttributeError
    mixed.fps = 44100
    mixed.write_audiofile(output_file, codec="mp3", verbose=False, logger=None)

def main():
    parser = argparse.ArgumentParser(description="Generate video from text prompt")
    parser.add_argument("prompt", help="Text prompt for video generation")
    parser.add_argument("--output", "-o", default="generated_video.mp4", help="Output video file")
    parser.add_argument("--scenes", "-n", type=int, default=5, help="Number of scenes")
    parser.add_argument("--fps", type=int, default=30, help="Video FPS")
    parser.add_argument("--size", default="1024x1024", choices=["1024x1024", "1792x1024", "1024x1792"], help="Image size")
    parser.add_argument("--voice", help="Text to speak as voiceover (uses OpenAI TTS)")
    parser.add_argument("--voice-model", default="alloy", choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"], help="OpenAI TTS voice")
    parser.add_argument("--no-zoom", action="store_true", help="Disable zoom effect on images")

    args = parser.parse_args()

    # Initialize OpenAI client
    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    client = OpenAI(api_key=api_key)

    print(f"Generating video for prompt: {args.prompt}")

    # Generate unique output filename
    if not args.output or args.output == "generated_video.mp4":
        base_name = "generated_video"
    else:
        base_name = args.output.replace('.mp4', '')

    args.output = generate_unique_filename(base_name)
    print(f"Output filename: {args.output}")
    print("Generating scenes...")
    scenes = generate_scenes(client, args.prompt, args.scenes)
    print(f"Generated {len(scenes)} scenes")

    # Generate images
    image_paths = []
    temp_dir = tempfile.mkdtemp()
    try:
        mood_list = []
        for i, scene in enumerate(scenes):
            print(f"Generating image for scene {i+1}...")
            img_path = generate_image(client, scene['description'], args.size)
            # Add text overlay
            overlay_path = os.path.join(temp_dir, f"scene_{i}_overlay.png")
            add_text_overlay(img_path, scene['text'], overlay_path)
            image_paths.append(overlay_path)
            # Analyze mood for each scene
            mood = analyze_mood(scene['description'], scene['text'])
            mood_list.append(mood)

        # Get durations
        durations = [scene.get('duration', 30) for scene in scenes]

        # Display scene information
        print("\n=== SCENE DETAILS ===")
        total_duration = 0
        for i, (scene, duration) in enumerate(zip(scenes, durations), 1):
            print(f"Scene {i}: {duration} seconds")
            print(f"  Text: {scene['text'][:50]}...")
            total_duration += duration

        zoom_status = "ENABLED (slow zoom from 100% to 120%)" if not args.no_zoom else "DISABLED (static images)"
        print(f"\nImage Movement: {zoom_status}")
        print(f"Total Video Duration: {total_duration} seconds")
        print("=" * 30)

        # Create initial video without audio
        temp_video = os.path.join(temp_dir, "temp_video.mp4")
        print("Creating video without audio...")
        create_video(image_paths, durations, temp_video, args.fps, zoom_effect=not args.no_zoom)

        # Output the video without sound
        silent_base = args.output.replace('.mp4', '_silent')
        silent_video = generate_unique_filename(silent_base)
        shutil.copy(temp_video, silent_video)
        print(f"Video without sound generated: {silent_video}")

        # Ask user if they want to add voice and music
        add_audio = input("Do you want to add mood-based voice narration and background music? (y/n): ").strip().lower()
        if add_audio == 'y':
            # Get overall mood
            from collections import Counter
            overall_mood = Counter(mood_list).most_common(1)[0][0] if mood_list else "neutral"
            print(f"Detected overall mood: {overall_mood}")

            # Select voice and music based on mood
            voice_model = mood_to_voice(overall_mood)
            music_file = mood_to_music(overall_mood)
            print(f"Selected voice: {voice_model}, music: {music_file}")

            # Generate narration text - use the complete story from all scenes
            narration_text = " ".join([scene['text'] for scene in scenes])
            print(f"Complete story narration: {narration_text}")

            # Generate voice audio
            print("Generating voice audio...")
            audio_file = os.path.join(temp_dir, "voice.mp3")
            generate_audio(client, narration_text, audio_file, voice_model)

            # Mix with background music
            print("Mixing audio with background music...")
            mixed_audio_file = os.path.join(temp_dir, "mixed_audio.mp3")
            mix_audio_with_music(audio_file, music_file, mixed_audio_file)

            # Add mixed audio to video
            print("Adding audio to video...")
            add_audio_to_video(temp_video, mixed_audio_file, args.output)

            print(f"Final video with audio generated: {args.output}")
        else:
            print("Video generation complete without audio. Final video is the silent version.")

    finally:
        # Cleanup temp files
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()