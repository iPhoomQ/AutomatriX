#!/usr/bin/env python3
"""
Professional replacement for YouTube_3.0.py using AutomatriX framework
This demonstrates how the original YouTube downloader can be upgraded
to use the professional AutomatriX architecture.
"""

import sys
import os

# Add the current directory to Python path for development
sys.path.insert(0, os.path.abspath('.'))

from automatrix import config, logger
from automatrix.youtube.downloader import YouTubeDownloader
from automatrix.core.utils import ValidationError, DownloadError

def progress_callback(info):
    """Progress callback for downloads"""
    if info['status'] == 'downloading':
        print(f"📥 {info.get('percent', 'N/A')} - {info.get('speed', 'N/A')} - ETA: {info.get('eta', 'N/A')}")
    elif info['status'] == 'finished':
        print(f"✅ Download completed: {info.get('filename', 'Unknown')}")
    elif info['status'] == 'error':
        print(f"❌ Download error: {info.get('error', 'Unknown error')}")

def main():
    """Professional YouTube downloader with AutomatriX"""
    # Initialize logger
    main_logger = logger.get_logger(__name__)
    main_logger.info("Starting professional YouTube downloader")
    
    try:
        # Initialize YouTube downloader with progress callback
        downloader = YouTubeDownloader(config, progress_callback)
        
        print("📺 AutomatriX Professional YouTube Downloader")
        print("=" * 50)
        
        # Example 1: Search and download multiple videos
        print("\n🔍 Example 1: Search and Download")
        print("-" * 30)
        
        search_query = "python automation tutorial"
        num_videos = 3
        max_duration = "10m"
        quality = "720p"
        output_dir = "./downloads"
        
        print(f"🔎 Search query: {search_query}")
        print(f"📊 Max videos: {num_videos}")
        print(f"⏱️  Max duration: {max_duration}")
        print(f"🎬 Quality: {quality}")
        print(f"📂 Output: {output_dir}")
        print()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Perform search and download
        print("Starting search and download...")
        result = downloader.search_and_download(
            query=search_query,
            num_videos=num_videos,
            max_duration=max_duration,
            output_directory=output_dir,
            quality=quality,
            audio_only=False
        )
        
        # Display results
        print(f"\n📊 Download Results:")
        print(f"✅ Successfully downloaded: {result['total_downloaded']}/{result['requested_videos']} videos")
        
        if result['downloaded']:
            print("\n🎉 Downloaded videos:")
            for download in result['downloaded']:
                print(f"   ✓ {download['title']}")
                print(f"     📁 {download['output_path']}")
                print(f"     📏 {download['file_size_formatted']}")
                print(f"     ⏱️  {download['duration']} seconds")
        
        if result['failed']:
            print(f"\n❌ Failed downloads: {len(result['failed'])}")
            for failed in result['failed']:
                print(f"   ✗ {failed['url']}: {failed['error']}")
        
        if result['skipped']:
            print(f"\n⏭️  Skipped videos: {len(result['skipped'])}")
            for skipped in result['skipped']:
                print(f"   → {skipped['title']}: {skipped['reason']}")
        
        main_logger.info(f"Search and download completed: {result['total_downloaded']} successful")
        
        # Example 2: Single video download (commented out to avoid duplicate downloads)
        print(f"\n📺 Example 2: Single Video Download")
        print("-" * 35)
        print("# To download a single video, use:")
        print("# result = downloader.download_single_video(")
        print("#     url='https://youtube.com/watch?v=...',")
        print("#     output_directory='./downloads',")
        print("#     quality='720p',")
        print("#     audio_only=False")
        print("# )")
        
        # Example 3: Configuration showcase
        print(f"\n⚙️  Configuration Settings:")
        print("-" * 25)
        print(f"Default quality: {config.get('youtube_download', 'default_quality')}")
        print(f"Max videos per search: {config.getint('youtube_download', 'max_videos_per_search')}")
        print(f"Default output directory: {config.get('youtube_download', 'default_output_directory')}")
        print(f"Timeout: {config.getint('youtube_download', 'timeout')} seconds")
        
    except ValidationError as e:
        main_logger.error(f"Validation error: {e}")
        print(f"❌ Input validation failed: {e}")
        sys.exit(1)
        
    except DownloadError as e:
        main_logger.error(f"Download error: {e}")
        print(f"❌ Download failed: {e}")
        sys.exit(1)
        
    except Exception as e:
        main_logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Professional AutomatriX YouTube Downloader")
    print("📄 This replaces the original YouTube_3.0.py with professional features:")
    print("   - Advanced search and filtering")
    print("   - Progress callbacks and reporting")
    print("   - Robust error handling")
    print("   - Centralized configuration")
    print("   - Professional logging")
    print("   - Type safety and validation")
    print("   - Modular architecture")
    print()
    
    try:
        main()
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install yt-dlp")
        sys.exit(1)