#!/usr/bin/env python3
"""
AUTO_video_generate_chunked.py

Merged low-CPU pipeline:
- Generates scenes via OpenAI, images via DALL·E (as in original).
- Builds **per-scene short MP4 chunks** (default 3s) with OpenCV (light).
- Concatenates chunks using **ffmpeg concat demuxer** with `-c copy` (near-zero CPU).
- Muxes final audio track with **ffmpeg** (no full re-encode of video).

Optional:
- Pass --no-chunk to revert to legacy single-pass encoder.
- Control FPS, size, zoom, and duration per scene.

Requirements:
  - Python 3.x
  - pip install opencv-python pillow python-dotenv openai moviepy requests numpy
  - ffmpeg installed and on PATH
"""

import os
import json
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
from typing import List, Dict, Any, Tuple
import tempfile
import shutil
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip
import subprocess
import sys

# --- tame CPU spikes on low-core machines ---
os.environ.setdefault("OMP_NUM_THREADS", "1")
try:
    cv2.setNumThreads(1)
except Exception:
    pass

# Load environment variables from .env file
load_dotenv()

def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)

def extract_filename_from_prompt(prompt: str) -> str:
    import re
    clean_prompt = re.sub(r'[^\w\s]', '', prompt.lower())
    stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'}
    words = [word for word in clean_prompt.split() if word not in stop_words and len(word) > 2]
    if len(words) >= 3:
        conclusion_words = words[-3:] if len(words) >= 3 else words[-2:]
        filename = '_'.join(conclusion_words)
    elif len(words) >= 1:
        filename = words[-1]
    else:
        filename = 'video'
    filename = re.sub(r'[^\w\-_]', '', filename)
    filename = filename[:30]
    return filename if filename else 'video'

def generate_scenes(client: OpenAI, prompt: str, num_scenes: int = 5) -> List[Dict[str, str]]:
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
        import re
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            scenes = json.loads(json_match.group())
            return scenes
        else:
            raise ValueError("Failed to parse scenes from LLM response")

def generate_audio(client: OpenAI, text: str, output_file: str, voice: str = "alloy") -> None:
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
    import requests
    img_response = requests.get(image_url)
    if img_response.status_code != 200:
        raise Exception("Failed to download image")
    temp_dir = tempfile.mkdtemp()
    image_path = os.path.join(temp_dir, f"scene_{len(os.listdir(temp_dir))}.png")
    with open(image_path, 'wb') as f:
        f.write(img_response.content)
    return image_path

def add_text_overlay(image_path: str, text: str, output_path: str) -> None:
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
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

    # Wrap text to fit ~80% width
    max_width = int(img.width * 0.8)
    lines = []
    words = text.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)

    # Combine lines for bbox calc
    joined = "\n".join(lines)
    bbox = draw.textbbox((0, 0), joined, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (img.width - text_width) // 2
    y = img.height - text_height - 50

    padding = 20
    bg_bbox = [x - padding, y - padding, x + text_width + padding, y + text_height + padding]
    # semi-opaque black rectangle
    draw.rectangle(bg_bbox, fill=(0, 0, 0))

    draw.multiline_text((x, y), joined, font=font, fill=(255, 255, 255), align="center", spacing=6)

    img.save(output_path, format="PNG")

# --- Legacy single-pass video builder (kept for --no-chunk) ---
def create_video(image_paths: List[str], durations: List[int], output_file: str, fps: int = 30, zoom_effect: bool = True) -> None:
    if not image_paths:
        raise ValueError("No images provided")
    first_img = cv2.imread(image_paths[0])
    height, width = first_img.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
    for img_path, duration in zip(image_paths, durations):
        img = cv2.imread(img_path)
        frames = max(1, int(duration) * fps)
        if zoom_effect:
            for i in range(frames):
                z = 1.0 + (0.2 * i / max(1, frames - 1))
                new_w, new_h = int(width * z), int(height * z)
                zoomed = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                sx = max(0, (new_w - width) // 2)
                sy = max(0, (new_h - height) // 2)
                crop = zoomed[sy:sy + height, sx:sx + width]
                out.write(crop)
        else:
            for _ in range(frames):
                out.write(img)
    out.release()

# --- Low-CPU chunked helpers ---
def parse_size(size_str: str) -> Tuple[int, int]:
    if 'x' not in size_str:
        raise ValueError("Size must be formatted as WIDTHxHEIGHT")
    w, h = size_str.lower().split('x')
    return int(w), int(h)

def ensure_same_size(img, target_size: Tuple[int, int]):
    h, w = img.shape[:2]
    tw, th = target_size
    scale = min(tw / w, th / h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
    canvas = (0, 0, 0)
    frame = cv2.copyMakeBorder(
        resized,
        top=(th - nh) // 2,
        bottom=th - nh - (th - nh) // 2,
        left=(tw - nw) // 2,
        right=tw - nw - (tw - nw) // 2,
        borderType=cv2.BORDER_CONSTANT,
        value=canvas
    )
    return frame

def create_scene_video(image_path: str, duration_sec: int, out_file: str, fps: int = 24,
                       zoom_effect: bool = True, size: Tuple[int, int] = None) -> None:
    img = cv2.imread(image_path)
    if img is None:
        raise RuntimeError(f"Failed to read image: {image_path}")
    if size:
        img = ensure_same_size(img, size)
    height, width = img.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_file, fourcc, fps, (width, height))
    if not out.isOpened():
        raise RuntimeError("Failed to open VideoWriter. Check codec support.")
    total_frames = max(1, int(duration_sec * fps))
    if zoom_effect:
        for i in range(total_frames):
            z = 1.0 + (0.2 * i / max(1, total_frames - 1))
            new_w, new_h = int(width * z), int(height * z)
            zoomed = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            sx = max(0, (new_w - width) // 2)
            sy = max(0, (new_h - height) // 2)
            crop = zoomed[sy:sy + height, sx:sx + width]
            out.write(crop)
    else:
        for _ in range(total_frames):
            out.write(img)
    out.release()

def run_ffmpeg(cmd: List[str]) -> None:
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(e.stderr.decode('utf-8', errors='ignore'))
        raise RuntimeError("ffmpeg failed")
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found. Install ffmpeg and ensure it is on PATH.")

def ffmpeg_concat_mp4s(mp4_list: List[str], output_path: str) -> None:
    if not mp4_list:
        raise ValueError("No mp4 files provided for concatenation.")
    tmpdir = tempfile.mkdtemp(prefix="concat_")
    concat_file = os.path.join(tmpdir, "files.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for p in mp4_list:
            f.write(f"file '{p}'\n")
    cmd = [
        "ffmpeg", "-y", "-hide_banner",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_path
    ]
    run_ffmpeg(cmd)

def add_audio_to_video_ffmpeg(video_file: str, audio_file: str, output_file: str) -> None:
    cmd = [
        "ffmpeg", "-y", "-hide_banner",
        "-i", video_file,
        "-i", audio_file,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_file
    ]
    run_ffmpeg(cmd)

def add_audio_to_video_legacy(video_file: str, audio_file: str, output_file: str) -> None:
    """Legacy moviepy path (kept for --no-chunk)"""
    video_clip = VideoFileClip(video_file)
    audio_clip = AudioFileClip(audio_file)
    if audio_clip.duration > video_clip.duration:
        audio_clip = audio_clip.subclip(0, video_clip.duration)
    elif audio_clip.duration < video_clip.duration:
        from moviepy.editor import concatenate_audioclips
        clips = []
        remaining_duration = video_clip.duration
        while remaining_duration > 0:
            clip_duration = min(remaining_duration, audio_clip.duration)
            clips.append(audio_clip.subclip(0, clip_duration))
            remaining_duration -= clip_duration
        audio_clip = concatenate_audioclips(clips)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=30, verbose=False, logger=None)

def analyze_mood(description: str, text: str) -> str:
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
    return "peaceful"

def mood_to_voice(mood: str) -> str:
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
    base_name = base_name.replace('.mp4', '')
    counter = 1
    while True:
        filename = f"{base_name}_{counter:02d}.mp4"
        if not os.path.exists(filename):
            return filename
        counter += 1
        if counter > 999:
            raise RuntimeError("Too many files with similar name.")

def mix_audio_with_music(voice_file: str, music_file: str, output_file: str, voice_volume: float = 1.0, music_volume: float = 0.3):
    from moviepy.editor import AudioFileClip, CompositeAudioClip
    voice = AudioFileClip(voice_file).volumex(voice_volume)
    music = AudioFileClip(music_file).volumex(music_volume)
    if music.duration < voice.duration:
        loops = int(voice.duration // music.duration) + 1
        music = CompositeAudioClip([music] * loops).subclip(0, voice.duration)
    else:
        music = music.subclip(0, voice.duration)
    mixed = CompositeAudioClip([music, voice])
    mixed.fps = 44100
    mixed.write_audiofile(output_file, codec="mp3", verbose=False, logger=None)

def main():
    parser = argparse.ArgumentParser(description="Generate video from text prompt (low-CPU chunked pipeline)")
    parser.add_argument("prompt", help="Text prompt for video generation")
    parser.add_argument("--output", "-o", default="generated_video.mp4", help="Output video file")
    parser.add_argument("--scenes", "-n", type=int, default=5, help="Number of scenes")
    parser.add_argument("--fps", type=int, default=24, help="Video FPS (default: 24 for lower CPU)")
    parser.add_argument("--size", default="1024x1024", choices=["1024x1024", "1792x1024", "1024x1792"], help="Image size")
    parser.add_argument("--voice", help="Text to speak as voiceover (uses OpenAI TTS) — if omitted, will narrate the combined scene texts")
    parser.add_argument("--voice-model", default="alloy", choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"], help="OpenAI TTS voice")
    parser.add_argument("--no-zoom", action="store_true", help="Disable zoom effect on images")
    parser.add_argument("--no-chunk", action="store_true", help="Disable chunked pipeline and use legacy single-pass encoder")
    parser.add_argument("--duration-per-scene", type=int, default=3, help="Seconds per scene chunk (default: 3)")
    args = parser.parse_args()

    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    client = OpenAI(api_key=api_key)

    print(f"Generating video for prompt: {args.prompt}")
    base_name = "generated_video" if not args.output or args.output == "generated_video.mp4" else args.output.replace('.mp4', '')
    args.output = generate_unique_filename(base_name)
    print(f"Output filename: {args.output}")

    print("Generating scenes...")
    scenes = generate_scenes(client, args.prompt, args.scenes)
    print(f"Generated {len(scenes)} scenes")

    # Generate images + overlays
    image_paths: List[str] = []
    temp_dir = tempfile.mkdtemp()
    try:
        mood_list = []
        for i, scene in enumerate(scenes):
            print(f"Generating image for scene {i+1}...")
            img_path = generate_image(client, scene['description'], args.size)
            overlay_path = os.path.join(temp_dir, f"scene_{i}_overlay.png")
            add_text_overlay(img_path, scene['text'], overlay_path)
            image_paths.append(overlay_path)
            mood = analyze_mood(scene['description'], scene['text'])
            mood_list.append(mood)

        # Durations from scenes, but for chunked mode we enforce --duration-per-scene
        durations = [max(1, int(scene.get('duration', args.duration_per_scene))) for scene in scenes]

        print("\n=== SCENE DETAILS ===")
        total_duration = 0
        for i, (scene, duration) in enumerate(zip(scenes, durations), 1):
            print(f"Scene {i}: {duration} seconds")
            print(f"  Text: {scene['text'][:60]}...")
            total_duration += duration
        print(f"\nImage Movement: {'DISABLED' if args.no_zoom else 'ENABLED'}")
        print(f"Planned Total Duration (legacy mode): {total_duration} seconds")
        print("=" * 30)

        # ---- VIDEO BUILD ----
        if args.no_chunk:
            print("[legacy] Creating single-pass video (higher CPU)...")
            temp_video = os.path.join(temp_dir, "temp_video.mp4")
            create_video(image_paths, durations, temp_video, args.fps, zoom_effect=not args.no_zoom)
            silent_base = args.output.replace('.mp4', '_silent')
            silent_video = generate_unique_filename(silent_base)
            shutil.copy(temp_video, silent_video)
            final_silent = silent_video
        else:
            print("[chunked] Building 3-second chunks and concatenating with ffmpeg (low CPU)...")
            # Resolve output frame size for chunk builder
            size_map = {"1024x1024": (1024, 1024), "1792x1024": (1792, 1024), "1024x1792": (1024, 1792)}
            frame_size = size_map.get(args.size, (1024, 1024))

            chunk_paths: List[str] = []
            for idx, img in enumerate(image_paths, start=1):
                chunk_mp4 = os.path.join(temp_dir, f"scene_{idx:03d}.mp4")
                # Enforce 3-second chunks (or user-provided --duration-per-scene)
                create_scene_video(img, duration_sec=args.duration_per_scene, out_file=chunk_mp4,
                                   fps=args.fps, zoom_effect=not args.no_zoom, size=frame_size)
                chunk_paths.append(chunk_mp4)

            temp_concat = os.path.join(temp_dir, "concat.mp4")
            print("[chunked] Concatenating chunks (stream copy)...")
            ffmpeg_concat_mp4s(chunk_paths, temp_concat)

            silent_base = args.output.replace('.mp4', '_silent')
            final_silent = generate_unique_filename(silent_base)
            shutil.copy(temp_concat, final_silent)

        print(f"Video without sound generated: {final_silent}")

        # ---- AUDIO ----
        add_audio = input("Do you want to add mood-based voice narration and background music? (y/n): ").strip().lower()
        if add_audio == 'y':
            from collections import Counter
            overall_mood = Counter(mood_list).most_common(1)[0][0] if mood_list else "neutral"
            print(f"Detected overall mood: {overall_mood}")
            voice_model = mood_to_voice(overall_mood)
            music_file = mood_to_music(overall_mood)
            print(f"Selected voice: {voice_model}, music: {music_file}")

            narration_text = args.voice if args.voice else " ".join([scene['text'] for scene in scenes])
            print(f"Narration chars: {len(narration_text)}")

            print("Generating voice audio...")
            audio_file = os.path.join(temp_dir, "voice.mp3")
            generate_audio(client, narration_text, audio_file, voice_model if not args.voice_model else args.voice_model)

            print("Mixing audio with background music...")
            mixed_audio_file = os.path.join(temp_dir, "mixed_audio.mp3")
            mix_audio_with_music(audio_file, music_file, mixed_audio_file)

            print("Muxing audio to video (low CPU)...")
            # For legacy mode, we can still use low-CPU mux (copy video, encode audio)
            add_audio_to_video_ffmpeg(final_silent, mixed_audio_file, args.output)
            print(f"Final video with audio generated: {args.output}")
        else:
            print("Video generation complete without audio. Final video is the silent version.")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
