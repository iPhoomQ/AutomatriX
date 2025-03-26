import yt_dlp
import tkinter as tk
from tkinter import messagebox

def download_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a video URL")
        return

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Best video + audio or best available
        'merge_output_format': 'mp4',  # Force output to be MP4
        'outtmpl': '%(title)s.%(ext)s',  # Output filename template
        'logger': MyLogger(),  # Use custom logger to capture yt-dlp output
        'progress_hooks': [my_hook],  # Hook for progress updates
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", "Download completed!")
    except Exception as e:
        messagebox.showerror("Download Error", f"An error occurred: {e}")

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

# Set up the GUI
root = tk.Tk()
root.title("Video Downloader")

tk.Label(root, text="Enter Video URL:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

download_button = tk.Button(root, text="Download", command=download_video)
download_button.grid(row=1, column=0, columnspan=2, pady=10)

# Start the GUI loop
root.mainloop()
