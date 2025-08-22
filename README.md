# AutomatriX
Automatic tools for business activity

## Overview
AutomatriX is a collection of Python automation scripts for various tasks including:
- YouTube video and audio downloading (YT.py, YT2.py, YT3.py, YouTube_3.0.py)
- YouTube Shorts downloading with different quality options (YT_short_list*.py)
- Image downloading from various search engines (image*.py)
- Video processing and watermarking (VO1.py, VO2.py)

## Installation

### Prerequisites
- Python 3.12+ 
- For GUI applications: tkinter (usually included with Python, may need separate installation on some Linux systems)

### Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install yt-dlp moviepy requests Pillow beautifulsoup4
```

### Linux Users (Ubuntu/Debian)
For GUI applications, you may need to install tkinter:
```bash
sudo apt update
sudo apt install python3-tk
```

## Usage

### YouTube Downloaders
- **YT.py**: Download audio from YouTube with format conversion to MP3
- **YT2.py**: Download images from search results  
- **YT3.py**: Download videos with quality selection and duration limits
- **YouTube_3.0.py**: Advanced video downloader with progress tracking
- **YT_short_list*.py**: Various YouTube Shorts downloaders with different features

Run any of these with:
```bash
python YT.py  # or any other YT script
```

### Image Downloaders
- **image.py**: Basic image downloader
- **image_04.py**: Advanced image downloader with search engine support
- **image2.py** through **image_07.py**: Various image downloading implementations

Run with:
```bash
python image_04.py  # or any other image script
```

### Video Processing
- **VO1.py**: Add text overlays to videos
- **VO2.py**: Add watermarks and adjust audio volume

Run with:
```bash
python VO1.py
```

## Recent Updates

### Compatibility Fixes
- **MoviePy**: Updated imports from deprecated `moviepy.editor` to direct `moviepy` imports
- **MoviePy**: Fixed deprecated `volumex()` method, replaced with `with_volume_scaled()`
- **MoviePy**: Updated TextClip parameters (`fontsize` → `font_size`) and parameter order
- **Font handling**: Removed specific font requirements for better cross-platform compatibility
- **Syntax**: Fixed missing parentheses in image2.py

### Dependencies
- All dependencies are now properly specified in `requirements.txt`
- Scripts are compatible with latest library versions as of 2025

## Notes
- GUI applications require a display environment (may not work in headless environments)
- Some scripts require internet connectivity for downloading content
- Downloaded content will be saved to local directories created by the scripts
