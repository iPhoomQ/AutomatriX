"""
Professional GUI interface for AutomatriX
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
from typing import Optional, Dict, Any, Callable
import os

from ..core.config import Config
from ..core.utils import ValidationError, VideoProcessingError, DownloadError

# Import modules conditionally
try:
    from ..video.processor import VideoProcessor
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False

try:
    from ..youtube.downloader import YouTubeDownloader
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False

try:
    from ..image.downloader import ImageDownloader
    IMAGE_AVAILABLE = True
except ImportError:
    IMAGE_AVAILABLE = False


class ProgressDialog:
    """Progress dialog for long-running operations"""
    
    def __init__(self, parent, title="Progress"):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.dialog, 
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(self.dialog, text="Starting...")
        self.status_label.pack(pady=10)
        
        # Log text
        self.log_text = scrolledtext.ScrolledText(
            self.dialog, 
            height=6, 
            width=50
        )
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Cancel button
        self.cancel_button = tk.Button(
            self.dialog, 
            text="Cancel",
            command=self.cancel
        )
        self.cancel_button.pack(pady=5)
        
        self.cancelled = False
        self.progress.start()
    
    def update_status(self, message: str):
        """Update status message"""
        self.status_label.config(text=message)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.dialog.update()
    
    def cancel(self):
        """Cancel operation"""
        self.cancelled = True
        self.close()
    
    def close(self):
        """Close dialog"""
        self.progress.stop()
        self.dialog.destroy()


class AutomatriXGUI:
    """Main GUI application for AutomatriX"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize processors
        self.video_processor = VideoProcessor(self.config) if VIDEO_AVAILABLE else None
        self.youtube_downloader = YouTubeDownloader(self.config) if YOUTUBE_AVAILABLE else None
        self.image_downloader = ImageDownloader(self.config) if IMAGE_AVAILABLE else None
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the main GUI"""
        # Configure main window
        self.root.title(self.config.get('ui', 'window_title', 'AutomatriX - Professional Automation Tools'))
        self.root.geometry(self.config.get('ui', 'window_geometry', '800x600'))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        if VIDEO_AVAILABLE:
            self.create_video_tab()
        
        if YOUTUBE_AVAILABLE:
            self.create_youtube_tab()
        
        if IMAGE_AVAILABLE:
            self.create_image_tab()
        
        # Create status bar
        self.create_status_bar()
        
        # Add missing dependencies warning
        self.show_missing_dependencies()
    
    def create_video_tab(self):
        """Create video processing tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Video Processing")
        
        # Input section
        input_frame = ttk.LabelFrame(tab, text="Input", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="Input File/Folder:").grid(row=0, column=0, sticky="w", padx=5)
        self.video_input_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.video_input_var, width=50).grid(row=0, column=1, padx=5)
        tk.Button(input_frame, text="Browse", command=self.browse_video_input).grid(row=0, column=2, padx=5)
        
        tk.Label(input_frame, text="Output File/Folder:").grid(row=1, column=0, sticky="w", padx=5)
        self.video_output_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.video_output_var, width=50).grid(row=1, column=1, padx=5)
        tk.Button(input_frame, text="Browse", command=self.browse_video_output).grid(row=1, column=2, padx=5)
        
        # Options section
        options_frame = ttk.LabelFrame(tab, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(options_frame, text="Watermark Text:").grid(row=0, column=0, sticky="w", padx=5)
        self.video_text_var = tk.StringVar(value="Hello World")
        tk.Entry(options_frame, textvariable=self.video_text_var, width=30).grid(row=0, column=1, padx=5)
        
        tk.Label(options_frame, text="Position:").grid(row=0, column=2, sticky="w", padx=5)
        self.video_position_var = tk.StringVar(value="center,bottom")
        tk.Entry(options_frame, textvariable=self.video_position_var, width=20).grid(row=0, column=3, padx=5)
        
        tk.Label(options_frame, text="Font Size:").grid(row=1, column=0, sticky="w", padx=5)
        self.video_fontsize_var = tk.IntVar(value=50)
        tk.Spinbox(options_frame, from_=10, to=100, textvariable=self.video_fontsize_var, width=10).grid(row=1, column=1, padx=5)
        
        tk.Label(options_frame, text="Color:").grid(row=1, column=2, sticky="w", padx=5)
        self.video_color_var = tk.StringVar(value="white")
        tk.Entry(options_frame, textvariable=self.video_color_var, width=20).grid(row=1, column=3, padx=5)
        
        self.video_batch_var = tk.BooleanVar()
        tk.Checkbutton(options_frame, text="Batch Processing", variable=self.video_batch_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Control buttons
        control_frame = tk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(control_frame, text="Process Video", command=self.process_video, bg="green", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear", command=self.clear_video_form).pack(side=tk.LEFT, padx=5)
    
    def create_youtube_tab(self):
        """Create YouTube download tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="YouTube Download")
        
        # Input section
        input_frame = ttk.LabelFrame(tab, text="Input", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Mode selection
        self.youtube_mode_var = tk.StringVar(value="url")
        tk.Radiobutton(input_frame, text="Single URL", variable=self.youtube_mode_var, value="url").grid(row=0, column=0, sticky="w")
        tk.Radiobutton(input_frame, text="Search", variable=self.youtube_mode_var, value="search").grid(row=0, column=1, sticky="w")
        
        tk.Label(input_frame, text="URL/Search Query:").grid(row=1, column=0, sticky="w", padx=5)
        self.youtube_query_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.youtube_query_var, width=60).grid(row=1, column=1, columnspan=3, padx=5, sticky="ew")
        
        # Options section
        options_frame = ttk.LabelFrame(tab, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(options_frame, text="Quality:").grid(row=0, column=0, sticky="w", padx=5)
        self.youtube_quality_var = tk.StringVar(value="best")
        quality_combo = ttk.Combobox(options_frame, textvariable=self.youtube_quality_var, values=["best", "1080p", "720p", "480p", "360p"], width=15)
        quality_combo.grid(row=0, column=1, padx=5)
        
        tk.Label(options_frame, text="Max Videos:").grid(row=0, column=2, sticky="w", padx=5)
        self.youtube_count_var = tk.IntVar(value=5)
        tk.Spinbox(options_frame, from_=1, to=50, textvariable=self.youtube_count_var, width=10).grid(row=0, column=3, padx=5)
        
        tk.Label(options_frame, text="Max Duration:").grid(row=1, column=0, sticky="w", padx=5)
        self.youtube_duration_var = tk.StringVar(value="10m")
        tk.Entry(options_frame, textvariable=self.youtube_duration_var, width=15).grid(row=1, column=1, padx=5)
        
        tk.Label(options_frame, text="Output Folder:").grid(row=1, column=2, sticky="w", padx=5)
        self.youtube_output_var = tk.StringVar(value="./downloads")
        tk.Entry(options_frame, textvariable=self.youtube_output_var, width=20).grid(row=1, column=3, padx=5)
        
        self.youtube_audio_var = tk.BooleanVar()
        tk.Checkbutton(options_frame, text="Audio Only", variable=self.youtube_audio_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Control buttons
        control_frame = tk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(control_frame, text="Download", command=self.download_youtube, bg="red", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear", command=self.clear_youtube_form).pack(side=tk.LEFT, padx=5)
    
    def create_image_tab(self):
        """Create image download tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Image Download")
        
        # Input section
        input_frame = ttk.LabelFrame(tab, text="Search", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="Search Query:").grid(row=0, column=0, sticky="w", padx=5)
        self.image_query_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.image_query_var, width=50).grid(row=0, column=1, padx=5)
        
        # Options section
        options_frame = ttk.LabelFrame(tab, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(options_frame, text="Max Images:").grid(row=0, column=0, sticky="w", padx=5)
        self.image_count_var = tk.IntVar(value=10)
        tk.Spinbox(options_frame, from_=1, to=100, textvariable=self.image_count_var, width=10).grid(row=0, column=1, padx=5)
        
        tk.Label(options_frame, text="Min Size (MB):").grid(row=0, column=2, sticky="w", padx=5)
        self.image_size_var = tk.DoubleVar(value=0.5)
        tk.Spinbox(options_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.image_size_var, width=10).grid(row=0, column=3, padx=5)
        
        tk.Label(options_frame, text="Output Folder:").grid(row=1, column=0, sticky="w", padx=5)
        self.image_output_var = tk.StringVar(value="./downloaded_images")
        tk.Entry(options_frame, textvariable=self.image_output_var, width=30).grid(row=1, column=1, columnspan=2, padx=5)
        tk.Button(options_frame, text="Browse", command=self.browse_image_output).grid(row=1, column=3, padx=5)
        
        # Control buttons
        control_frame = tk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(control_frame, text="Download Images", command=self.download_images, bg="blue", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear", command=self.clear_image_form).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = tk.Frame(self.root, relief=tk.SUNKEN, bd=1)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)
    
    def show_missing_dependencies(self):
        """Show warning for missing dependencies"""
        missing = []
        if not VIDEO_AVAILABLE:
            missing.append("Video Processing (moviepy)")
        if not YOUTUBE_AVAILABLE:
            missing.append("YouTube Download (yt-dlp)")
        if not IMAGE_AVAILABLE:
            missing.append("Image Download (beautifulsoup4, Pillow)")
        
        if missing:
            warning = f"Missing dependencies: {', '.join(missing)}\nSome features will not be available."
            messagebox.showwarning("Missing Dependencies", warning)
    
    def update_status(self, message: str):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update()
    
    # File browser methods
    def browse_video_input(self):
        if self.video_batch_var.get():
            folder = filedialog.askdirectory()
            if folder:
                self.video_input_var.set(folder)
        else:
            file = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
            if file:
                self.video_input_var.set(file)
    
    def browse_video_output(self):
        if self.video_batch_var.get():
            folder = filedialog.askdirectory()
            if folder:
                self.video_output_var.set(folder)
        else:
            file = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
            if file:
                self.video_output_var.set(file)
    
    def browse_image_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_output_var.set(folder)
    
    # Clear form methods
    def clear_video_form(self):
        self.video_input_var.set("")
        self.video_output_var.set("")
        self.video_text_var.set("Hello World")
        self.video_position_var.set("center,bottom")
        self.video_fontsize_var.set(50)
        self.video_color_var.set("white")
        self.video_batch_var.set(False)
    
    def clear_youtube_form(self):
        self.youtube_query_var.set("")
        self.youtube_quality_var.set("best")
        self.youtube_count_var.set(5)
        self.youtube_duration_var.set("10m")
        self.youtube_output_var.set("./downloads")
        self.youtube_audio_var.set(False)
    
    def clear_image_form(self):
        self.image_query_var.set("")
        self.image_count_var.set(10)
        self.image_size_var.set(0.5)
        self.image_output_var.set("./downloaded_images")
    
    # Processing methods
    def process_video(self):
        """Process video in background thread"""
        def worker():
            try:
                progress = ProgressDialog(self.root, "Processing Video")
                
                # Parse position
                pos_parts = self.video_position_var.get().split(',')
                position = (pos_parts[0].strip(), pos_parts[1].strip() if len(pos_parts) > 1 else 'center')
                
                if self.video_batch_var.get():
                    progress.update_status("Starting batch processing...")
                    result = self.video_processor.batch_process_videos(
                        input_folder=self.video_input_var.get(),
                        output_folder=self.video_output_var.get(),
                        text=self.video_text_var.get(),
                        position=position,
                        fontsize=self.video_fontsize_var.get(),
                        color=self.video_color_var.get()
                    )
                    progress.update_status(f"Completed: {result['total_processed']}/{result['total_files']} videos")
                else:
                    progress.update_status("Processing single video...")
                    result = self.video_processor.add_text_watermark(
                        input_path=self.video_input_var.get(),
                        output_path=self.video_output_var.get(),
                        text=self.video_text_var.get(),
                        position=position,
                        fontsize=self.video_fontsize_var.get(),
                        color=self.video_color_var.get()
                    )
                    progress.update_status(f"Completed: {result['output_path']}")
                
                progress.close()
                messagebox.showinfo("Success", "Video processing completed successfully!")
                
            except Exception as e:
                if 'progress' in locals():
                    progress.close()
                messagebox.showerror("Error", f"Video processing failed: {str(e)}")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def download_youtube(self):
        """Download YouTube videos in background thread"""
        def worker():
            try:
                progress = ProgressDialog(self.root, "Downloading YouTube Videos")
                
                if self.youtube_mode_var.get() == "search":
                    progress.update_status("Searching and downloading...")
                    result = self.youtube_downloader.search_and_download(
                        query=self.youtube_query_var.get(),
                        num_videos=self.youtube_count_var.get(),
                        max_duration=self.youtube_duration_var.get(),
                        output_directory=self.youtube_output_var.get(),
                        quality=self.youtube_quality_var.get(),
                        audio_only=self.youtube_audio_var.get()
                    )
                    progress.update_status(f"Downloaded: {result['total_downloaded']} videos")
                else:
                    progress.update_status("Downloading single video...")
                    result = self.youtube_downloader.download_single_video(
                        url=self.youtube_query_var.get(),
                        output_directory=self.youtube_output_var.get(),
                        quality=self.youtube_quality_var.get(),
                        audio_only=self.youtube_audio_var.get()
                    )
                    progress.update_status(f"Downloaded: {result['title']}")
                
                progress.close()
                messagebox.showinfo("Success", "YouTube download completed successfully!")
                
            except Exception as e:
                if 'progress' in locals():
                    progress.close()
                messagebox.showerror("Error", f"YouTube download failed: {str(e)}")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def download_images(self):
        """Download images in background thread"""
        def worker():
            try:
                progress = ProgressDialog(self.root, "Downloading Images")
                progress.update_status("Searching and downloading images...")
                
                result = self.image_downloader.download_images(
                    query=self.image_query_var.get(),
                    max_images=self.image_count_var.get(),
                    min_size_mb=self.image_size_var.get(),
                    output_directory=self.image_output_var.get()
                )
                
                progress.update_status(f"Downloaded: {result['total_downloaded']} images")
                progress.close()
                messagebox.showinfo("Success", f"Downloaded {result['total_downloaded']} images successfully!")
                
            except Exception as e:
                if 'progress' in locals():
                    progress.close()
                messagebox.showerror("Error", f"Image download failed: {str(e)}")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point for GUI"""
    app = AutomatriXGUI()
    app.run()


if __name__ == "__main__":
    main()