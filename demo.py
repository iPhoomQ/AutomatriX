#!/usr/bin/env python3
"""
Example usage of AutomatriX professional modules
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

from automatrix.core.config import Config
from automatrix.core.logger import Logger
from automatrix.core.utils import parse_duration, validate_video_quality, format_file_size

def demo_core_functionality():
    """Demonstrate core functionality"""
    print("🚀 AutomatriX Professional Demo")
    print("=" * 50)
    
    # Configuration demo
    print("\n📋 Configuration Management:")
    config = Config()
    print(f"✓ Loaded configuration from: {config.config_file}")
    print(f"  - Video font size: {config.getint('video_processing', 'default_fontsize')}")
    print(f"  - YouTube quality: {config.get('youtube_download', 'default_quality')}")
    print(f"  - Image min size: {config.getfloat('image_download', 'default_min_size_mb')}MB")
    
    # Logging demo
    print("\n📊 Logging System:")
    logger = Logger(config)
    test_logger = logger.get_logger('demo')
    test_logger.info("Logging system initialized successfully")
    print("✓ Logger configured with file and console output")
    
    # Utilities demo
    print("\n🔧 Utility Functions:")
    
    # Duration parsing
    durations = ["5m", "1h", "30s", "2h"]
    for duration_str in durations:
        seconds = parse_duration(duration_str)
        print(f"  - {duration_str} = {seconds} seconds")
    
    # Quality validation
    qualities = ["best", "1080p", "720p", "480p"]
    print(f"  - Valid qualities: {', '.join(qualities)}")
    
    # File size formatting
    sizes = [1024, 1048576, 1073741824]
    for size in sizes:
        formatted = format_file_size(size)
        print(f"  - {size} bytes = {formatted}")
    
    print("\n✅ Core functionality working perfectly!")

def demo_api_usage():
    """Demonstrate API usage examples"""
    print("\n🔧 API Usage Examples:")
    print("-" * 25)
    
    print("""
# Video Processing Example:
from automatrix.video.processor import VideoProcessor
from automatrix import config

processor = VideoProcessor(config)
result = processor.add_text_watermark(
    input_path="input.mp4",
    output_path="output.mp4",
    text="Professional Watermark",
    position=("center", "bottom"),
    fontsize=60,
    color="white"
)

# YouTube Download Example:
from automatrix.youtube.downloader import YouTubeDownloader

downloader = YouTubeDownloader(config)
result = downloader.search_and_download(
    query="automation tutorial",
    num_videos=5,
    max_duration="10m",
    quality="720p"
)

# Image Download Example:
from automatrix.image.downloader import ImageDownloader

image_downloader = ImageDownloader(config)
result = image_downloader.download_images(
    query="business automation",
    max_images=20,
    min_size_mb=1.0
)
""")

def demo_cli_commands():
    """Show CLI command examples"""
    print("\n💻 Command Line Interface:")
    print("-" * 30)
    
    print("""
# Video Watermarking:
automatrix video-watermark input.mp4 output.mp4 --text "My Company"
automatrix video-watermark videos/ processed/ --text "Watermark" --batch

# YouTube Downloads:
automatrix youtube-download --url "https://youtube.com/watch?v=..."
automatrix youtube-download --search "python tutorial" --count 5

# Image Downloads:
automatrix image-download "nature photography" --count 20 --min-size 1.0
""")

def check_dependencies():
    """Check which dependencies are available"""
    print("\n📦 Dependency Status:")
    print("-" * 20)
    
    dependencies = [
        ("moviepy", "Video processing"),
        ("yt-dlp", "YouTube downloads"),
        ("beautifulsoup4", "Web scraping"),
        ("Pillow", "Image processing"),
        ("requests", "HTTP requests"),
        ("colorama", "Colored CLI output"),
    ]
    
    for module, description in dependencies:
        try:
            __import__(module.replace('-', '_'))
            status = "✅ Available"
        except ImportError:
            status = "❌ Missing"
        
        print(f"  {module:15} - {description:20} {status}")
    
    print(f"\nTo install missing dependencies:")
    print(f"pip install -r requirements.txt")

def main():
    """Main demo function"""
    try:
        demo_core_functionality()
        demo_api_usage()
        demo_cli_commands()
        check_dependencies()
        
        print("\n🎉 AutomatriX Professional is ready to use!")
        print("📚 For more information, see the README.md file")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()