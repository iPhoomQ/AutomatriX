import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox
import os
import re
from tkinter.scrolledtext import ScrolledText

# Global variables
download_all = False
video_list = []

def get_video_info(url):
    """Get video information including title, duration, and size"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'simulate': True,  # Don't actually download
        'format': 'best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'url': url,
                'size': info.get('filesize_approx', 0) or info.get('filesize', 0)
            }
    except Exception as e:
        print(f"Error getting info for {url}: {e}")
        return None

def format_duration(seconds):
    """Convert duration in seconds to HH:MM:SS format"""
    if not seconds:
        return "00:00"
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def format_size(bytes):
    """Convert file size to human-readable format"""
    if not bytes:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"

def download_video(url, quality='best', output_directory='.'):
    ydl_opts = {
        'format': quality,
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s'),
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'format_sort': ['res:1440', 'res:1080'],
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Download completed: {url}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

class MyLogger(object):
    def debug(self, msg):
        print(msg)
    def warning(self, msg):
        print(msg)
    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'finished':
        print(f"Done downloading, now converting ...")
    elif d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} at {d['_speed_str']} ETA: {d['_eta_str']}")

def parse_duration(duration_str):
    match = re.match(r'^(\d+)([hms])$', duration_str.lower())
    if not match:
        raise ValueError("Invalid duration format. Use formats like '1m', '2h', '30s'.")

    value, unit = match.groups()
    value = int(value)

    if unit == 'h':
        return value * 3600
    elif unit == 'm':
        return value * 60
    elif unit == 's':
        return value
    else:
        raise ValueError("Invalid unit. Use 'h', 'm', or 's'.")

def is_shorts_url(url):
    return '/shorts/' in url.lower()

def search_videos():
    global video_list
    video_list = []
    
    # Get values from the GUI
    query = search_entry.get().strip()
    duration_str = duration_entry.get().strip()
    num_videos = num_videos_entry.get().strip()

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
        messagebox.showwarning("Invalid Input", "Number of videos must be a valid integer between 1 and 100.")
        return

    # Clear previous results
    for row in preview_tree.get_children():
        preview_tree.delete(row)
    preview_text.delete('1.0', tk.END)

    # Search for videos using yt-dlp
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch{num_videos*2}:{query}", download=False)
            for entry in search_results['entries']:
                if entry and is_shorts_url(entry['url']):
                    if entry.get('duration', float('inf')) <= max_duration:
                        video_info = get_video_info(entry['url'])
                        if video_info:
                            video_list.append(video_info)
                            preview_tree.insert("", tk.END, values=(
                                video_info['title'],
                                format_duration(video_info['duration']),
                                format_size(video_info['size']),
                                video_info['url']
                            ))
                            if len(video_list) >= num_videos:
                                break

        if not video_list:
            messagebox.showinfo("No Videos Found", "No Shorts videos found within the specified duration.")
            return

        # Update preview text
        preview_text.insert(tk.END, f"Found {len(video_list)} Shorts videos:\n\n")
        for idx, video in enumerate(video_list, 1):
            preview_text.insert(tk.END, 
                f"{idx}. {video['title']}\n"
                f"   Duration: {format_duration(video['duration'])} | "
                f"Size: {format_size(video['size'])}\n"
                f"   URL: {video['url']}\n\n"
            )

    except Exception as e:
        messagebox.showerror("Search Error", f"An error occurred during search: {e}")

def start_download():
    global download_all

    if not video_list:
        messagebox.showwarning("No Videos", "Please search for videos first.")
        return

    output_directory = output_entry.get().strip()
    if not output_directory:
        output_directory = "shorts_downloads"

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    quality = quality_var.get()

    # Reset the download_all flag
    download_all = False

    for i, video in enumerate(video_list):
        print(f"Downloading Shorts video {i + 1}/{len(video_list)}: {video['title']}")
        download_video(video['url'], quality, output_directory)

# Set up the GUI
root = tk.Tk()
root.title("YouTube Shorts Downloader")
root.geometry("900x700")

# Search Frame
search_frame = tk.LabelFrame(root, text="Search Parameters", padx=10, pady=10)
search_frame.pack(fill=tk.X, padx=10, pady=5)

# Search Query
tk.Label(search_frame, text="Search Query:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
search_entry = tk.Entry(search_frame, width=50)
search_entry.grid(row=0, column=1, padx=5, pady=5)

# Video Quality
tk.Label(search_frame, text="Video Quality:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
quality_var = tk.StringVar(value="best")
quality_options = ["best", "1080p", "720p"]
quality_menu = tk.OptionMenu(search_frame, quality_var, *quality_options)
quality_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Maximum Duration
tk.Label(search_frame, text="Max Duration (e.g., 60s):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
duration_entry = tk.Entry(search_frame, width=50)
duration_entry.insert(0, "60s")
duration_entry.grid(row=2, column=1, padx=5, pady=5)

# Number of Videos
tk.Label(search_frame, text="Number of Shorts Videos (1-100):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
num_videos_entry = tk.Entry(search_frame, width=50)
num_videos_entry.insert(0, "10")
num_videos_entry.grid(row=3, column=1, padx=5, pady=5)

# Output Directory
tk.Label(search_frame, text="Output Directory:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
output_entry = tk.Entry(search_frame, width=50)
output_entry.insert(0, "shorts_downloads")
output_entry.grid(row=4, column=1, padx=5, pady=5)

# Buttons Frame
buttons_frame = tk.Frame(root)
buttons_frame.pack(fill=tk.X, padx=10, pady=5)

search_button = tk.Button(buttons_frame, text="Search Shorts", command=search_videos)
search_button.pack(side=tk.LEFT, padx=5)

download_button = tk.Button(buttons_frame, text="Download Selected", command=start_download)
download_button.pack(side=tk.LEFT, padx=5)

# Preview Frame
preview_frame = tk.LabelFrame(root, text="Video Preview", padx=10, pady=10)
preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Treeview for tabular preview
preview_tree = ttk.Treeview(preview_frame, columns=("Title", "Duration", "Size", "URL"), show="headings", height=5)
preview_tree.heading("Title", text="Title")
preview_tree.heading("Duration", text="Duration")
preview_tree.heading("Size", text="Size")
preview_tree.heading("URL", text="URL")
preview_tree.column("Title", width=250)
preview_tree.column("Duration", width=80)
preview_tree.column("Size", width=80)
preview_tree.column("URL", width=300)
preview_tree.pack(fill=tk.X, pady=5)

# Scrollable text for detailed preview
preview_text = ScrolledText(preview_frame, wrap=tk.WORD, height=15)
preview_text.pack(fill=tk.BOTH, expand=True)

# Start the GUI loop
root.mainloop()
