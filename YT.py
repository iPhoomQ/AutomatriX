import yt_dlp
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

def search_and_download_audio(query, num_results=10, max_duration=600, download_all=False, output_directory='.'):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'extract_flat': True,  # Extract metadata without downloading
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch{num_results}:{query}", download=False)
            if not search_results or 'entries' not in search_results or not search_results['entries']:
                messagebox.showinfo("No Results", "No audio found for the given search query.")
                return
            
            valid_entries = [entry for entry in search_results['entries'] if entry.get('duration', 0) <= max_duration]
            
            if not valid_entries:
                messagebox.showinfo("No Valid Results", "No audio found within the specified duration.")
                return
            
            if download_all:
                video_urls = [entry['url'] for entry in valid_entries]
            else:
                options = "\n".join([f"{i+1}. {entry['title']} ({entry['duration']}s)" for i, entry in enumerate(valid_entries)])
                choice = simpledialog.askinteger("Select Audio", f"Choose a file to download:\n{options}", minvalue=1, maxvalue=len(valid_entries))
                
                if choice is None or choice < 1 or choice > len(valid_entries):
                    messagebox.showwarning("Invalid Selection", "No valid selection made.")
                    return
                
                video_urls = [valid_entries[choice - 1]['url']]
            
            ydl_opts.pop('extract_flat')  # Remove search-only option to allow downloading
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(video_urls)
            
            messagebox.showinfo("Success", "Audio downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download: {e}")

def start_download():
    query = search_entry.get().strip()
    output_directory = output_entry.get().strip() or '.'
    num_results = int(num_results_entry.get().strip() or 10)
    max_duration = int(duration_entry.get().strip() or 600)
    download_all = download_all_var.get()
    
    if not query:
        messagebox.showwarning("Input Error", "Please enter a search query.")
        return
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    search_and_download_audio(query, num_results, max_duration, download_all, output_directory)

# Set up the GUI
root = tk.Tk()
root.title("Audio Downloader")

tk.Label(root, text="Search Query:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
search_entry = tk.Entry(root, width=50)
search_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Number of Results (1-100):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
num_results_entry = tk.Entry(root, width=50)
num_results_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Max Duration (seconds):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
duration_entry = tk.Entry(root, width=50)
duration_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Output Directory:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=3, column=1, padx=10, pady=5)

download_all_var = tk.BooleanVar()
download_all_check = tk.Checkbutton(root, text="Download All", variable=download_all_var)
download_all_check.grid(row=4, column=1, pady=5, sticky="w")

download_button = tk.Button(root, text="Start Download", command=start_download)
download_button.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()
