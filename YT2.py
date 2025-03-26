import yt_dlp
import tkinter as tk
from tkinter import messagebox
import os
import requests

# Function to download images
def download_image(url, output_directory):
    ydl_opts = {'quiet': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            image_url = info_dict.get('thumbnail')
            title = info_dict.get('title', 'image').replace(" ", "_")
            
            if not image_url:
                print(f"No image found for {url}")
                return
            
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                file_path = os.path.join(output_directory, f"{title}.jpg")
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Downloaded image: {file_path}")
            else:
                print(f"Failed to download image for {url}")
    except Exception as e:
        print(f"Error fetching image: {e}")

# Function to start downloading images
def start_download():
    query = search_entry.get().strip()
    num_images = num_images_entry.get().strip()
    output_directory = output_entry.get().strip()

    if not query:
        messagebox.showwarning("Input Error", "Please enter a search query.")
        return

    try:
        num_images = int(num_images)
        if num_images < 1 or num_images > 100:
            raise ValueError("Number of images must be between 1 and 100.")
    except ValueError:
        messagebox.showwarning("Invalid Input", "Number of images must be a valid integer between 1 and 100.")
        return

    if not output_directory:
        output_directory = "."
    os.makedirs(output_directory, exist_ok=True)

    ydl_opts = {'extract_flat': True, 'quiet': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch{num_images}:{query}", download=False)
            image_urls = [entry['url'] for entry in search_results['entries']]

        if not image_urls:
            messagebox.showinfo("No Images Found", "No images found.")
            return

        for url in image_urls:
            download_image(url, output_directory)
    except Exception as e:
        messagebox.showerror("Search Error", f"An error occurred during search: {e}")

# Set up the GUI
root = tk.Tk()
root.title("Image Downloader")

# Search Query
tk.Label(root, text="Search Query:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
search_entry = tk.Entry(root, width=50)
search_entry.grid(row=0, column=1, padx=10, pady=5)

# Number of Images
tk.Label(root, text="Number of Images (1-100):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
num_images_entry = tk.Entry(root, width=50)
num_images_entry.grid(row=1, column=1, padx=10, pady=5)

# Output Directory
tk.Label(root, text="Output Directory:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=2, column=1, padx=10, pady=5)

# Download Button
download_button = tk.Button(root, text="Start Download", command=start_download)
download_button.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()