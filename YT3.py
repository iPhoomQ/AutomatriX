import yt_dlp
import tkinter as tk
from tkinter import messagebox
import os
import re
from typing import Optional

# Global variables
download_all = False  # Flag to determine if all videos should be downloaded without stopping

def download_video(url: str, quality: str = 'best', output_directory: str = '.') -> None:
    """
    Download a video from the given URL.
    
    Args:
        url: Video URL to download
        quality: Video quality setting (default: 'best')
        output_directory: Directory to save the video (default: current directory)
    """
    ydl_opts = {
        'format': quality,  # Set video quality
        'merge_output_format': 'mp4',  # Force output to be MP4
        'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s'),  # Output filename template
        'logger': MyLogger(),  # Use custom logger to capture yt-dlp output
        'progress_hooks': [my_hook],  # Hook for progress updates
        'format_sort': ['res:1440', 'res:1080'],  # Fallback to lower resolutions
        'quiet': True,  # Suppress yt-dlp output
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Download completed: {url}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

class MyLogger:
    """Custom logger class for yt-dlp output."""
    
    def debug(self, msg: str) -> None:
        """Log debug messages."""
        print(msg)
        
    def warning(self, msg: str) -> None:
        """Log warning messages."""
        print(msg)
        
    def error(self, msg: str) -> None:
        """Log error messages."""
        print(msg)

def my_hook(d: dict) -> None:
    """Progress hook for yt-dlp downloads."""
    if d['status'] == 'finished':
        print(f"Done downloading, now converting ...")
    elif d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} at {d['_speed_str']} ETA: {d['_eta_str']}")

def parse_duration(duration_str: str) -> int:
    """
    Parse a duration string like '1m', '2h', '30s' into seconds.
    
    Args:
        duration_str: Duration string with format like '1m', '2h', '30s'
        
    Returns:
        Duration in seconds as integer
        
    Raises:
        ValueError: If duration format is invalid
    """
    # Regex to match patterns like '1m', '2h', '30s', etc.
    match = re.match(r'^(\d+)([hms])$', duration_str.lower())
    if not match:
        raise ValueError("Invalid duration format. Use formats like '1m', '2h', '30s'.")

    value, unit = match.groups()
    value = int(value)

    if unit == 'h':
        return value * 3600  # Convert hours to seconds
    elif unit == 'm':
        return value * 60  # Convert minutes to seconds
    elif unit == 's':
        return value  # Seconds
    else:
        raise ValueError("Invalid unit. Use 'h', 'm', or 's'.")

def start_download() -> None:
    """Start the download process with values from GUI."""
    global download_all

    # Get values from the GUI
    query = search_entry.get().strip()
    quality = quality_var.get()
    duration_str = duration_entry.get().strip()
    num_videos = num_videos_entry.get().strip()
    output_directory = output_entry.get().strip()

    # Validate inputs
    if not query:
        messagebox.showwarning("Input Error", "Please enter a search query.")
        return

    try:
        max_duration = parse_duration(duration_str)
    except ValueError as e:
        messagebox.showwarning("Invalid Duration", str(e))
        return

    try:
        num_videos = int(num_videos)
        if num_videos < 1 or num_videos > 100:
            raise ValueError("Number of videos must be between 1 and 100.")
    except ValueError:
        messagebox.showwarning("Invalid Input", "Number of videos must be a valid integer between 1 and 50.")
        return

    if not output_directory:
        output_directory = "."

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Search for videos using yt-dlp
    ydl_opts = {
        'extract_flat': True,  # Extract metadata without downloading
        'quiet': True,  # Suppress output
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch{num_videos}:{query}", download=False)
            video_urls = []
            for entry in search_results['entries']:
                if entry.get('duration', float('inf')) <= max_duration:
                    video_urls.append(entry['url'])
                    if len(video_urls) >= num_videos:
                        break

        if not video_urls:
            messagebox.showinfo("No Videos Found", "No videos found within the specified duration.")
            return

        # Reset the download_all flag
        download_all = False

        for i, url in enumerate(video_urls):
            print(f"Downloading video {i + 1}/{len(video_urls)}: {url}")
            download_video(url, quality, output_directory)

       
            
            

    except Exception as e:
        messagebox.showerror("Search Error", f"An error occurred during search: {e}")

# Set up the GUI
root = tk.Tk()
root.title("Video Downloader")

# Search Query
tk.Label(root, text="Search Query:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
search_entry = tk.Entry(root, width=50)
search_entry.grid(row=0, column=1, padx=10, pady=5)

# Video Quality
tk.Label(root, text="Video Quality:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
quality_var = tk.StringVar(value="best")
quality_options = ["best", "4K", "1080p", "720p", "480p", "360p"]
quality_menu = tk.OptionMenu(root, quality_var, *quality_options)
quality_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# Maximum Duration
tk.Label(root, text="Max Duration (e.g., 1m, 2h, 30s):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
duration_entry = tk.Entry(root, width=50)
duration_entry.grid(row=2, column=1, padx=10, pady=5)

# Number of Videos
tk.Label(root, text="Number of Videos (1-100):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
num_videos_entry = tk.Entry(root, width=50)
num_videos_entry.grid(row=3, column=1, padx=10, pady=5)

# Output Directory
tk.Label(root, text="Output Directory:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=4, column=1, padx=10, pady=5)

# Download Button
download_button = tk.Button(root, text="Start Download", command=start_download)
download_button.grid(row=5, column=0, columnspan=2, pady=10)

# Start the GUI loop
root.mainloop()