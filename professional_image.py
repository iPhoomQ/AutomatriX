#!/usr/bin/env python3
"""
Professional replacement for image_04.py using AutomatriX framework
This demonstrates how the original image downloader can be upgraded
to use the professional AutomatriX architecture.
"""

import sys
import os

# Add the current directory to Python path for development
sys.path.insert(0, os.path.abspath('.'))

from automatrix import config, logger
from automatrix.image.downloader import ImageDownloader
from automatrix.core.utils import ValidationError, DownloadError

def progress_callback(info):
    """Progress callback for image downloads"""
    if info['status'] == 'downloaded':
        print(f"✅ Downloaded: {info['filename']} ({info['file_size']} bytes) - Total: {info['total_downloaded']}")
    elif info['status'] == 'failed':
        print(f"❌ Failed: {info['url'][:50]}... - {info['error']}")

def main():
    """Professional image downloader with AutomatriX"""
    # Initialize logger
    main_logger = logger.get_logger(__name__)
    main_logger.info("Starting professional image downloader")
    
    try:
        # Initialize image downloader with progress callback
        downloader = ImageDownloader(config, progress_callback)
        
        print("🖼️  AutomatriX Professional Image Downloader")
        print("=" * 50)
        
        # Interactive input (like original image_04.py)
        print("Enter your preferences:")
        
        query = input("🔎 Search term: ").strip() or "nature photography"
        
        try:
            min_size_mb = float(input("📏 Minimum image size in MB (e.g., 0.5, 1, 2): ").strip() or "0.5")
        except ValueError:
            min_size_mb = 0.5
            print(f"⚠️  Invalid input, using default: {min_size_mb}MB")
        
        try:
            max_images = int(input("🔢 Maximum images to download: ").strip() or "10")
        except ValueError:
            max_images = 10
            print(f"⚠️  Invalid input, using default: {max_images} images")
        
        # Output directory
        output_directory = f"./downloaded_images"
        
        print(f"\n📋 Download Configuration:")
        print(f"🔎 Search query: {query}")
        print(f"📏 Minimum size: {min_size_mb}MB")
        print(f"🔢 Max images: {max_images}")
        print(f"📂 Output directory: {output_directory}")
        print(f"🔧 Max concurrent downloads: {config.getint('image_download', 'max_concurrent_downloads')}")
        print(f"⏱️  Request delay: {config.getfloat('image_download', 'request_delay_min')}-{config.getfloat('image_download', 'request_delay_max')}s")
        print()
        
        # Perform image download
        print(f"🚀 Starting image download...")
        result = downloader.download_images(
            query=query,
            max_images=max_images,
            min_size_mb=min_size_mb,
            output_directory=output_directory
        )
        
        # Display results
        print(f"\n📊 Download Results:")
        print("=" * 25)
        
        if result.get('success', True):
            print(f"✅ Successfully downloaded: {result['total_downloaded']} images")
            print(f"📂 Images saved to: {os.path.abspath(result['output_folder'])}")
            print(f"🔍 URLs found: {result['found_urls']}")
            print(f"📥 Requested: {result['requested_images']}")
            
            if result['total_failed'] > 0:
                print(f"❌ Failed downloads: {result['total_failed']}")
            
            if result['downloaded']:
                print(f"\n🎉 Downloaded files:")
                for i, download in enumerate(result['downloaded'][:5], 1):  # Show first 5
                    print(f"   {i}. {download['filename']} ({download['file_size_formatted']})")
                
                if len(result['downloaded']) > 5:
                    print(f"   ... and {len(result['downloaded']) - 5} more files")
            
            # Show some statistics
            total_size = sum(d['file_size'] for d in result['downloaded'])
            avg_size = total_size / len(result['downloaded']) if result['downloaded'] else 0
            
            print(f"\n📈 Statistics:")
            print(f"   📊 Total size: {downloader.format_file_size(total_size) if hasattr(downloader, 'format_file_size') else f'{total_size} bytes'}")
            print(f"   📊 Average size: {downloader.format_file_size(avg_size) if hasattr(downloader, 'format_file_size') else f'{avg_size:.0f} bytes'}")
            
        else:
            print(f"❌ Download failed: {result.get('error', 'Unknown error')}")
        
        main_logger.info(f"Image download completed: {result.get('total_downloaded', 0)} successful")
        
        # Configuration showcase
        print(f"\n⚙️  Configuration Settings:")
        print("-" * 25)
        print(f"Default min size: {config.getfloat('image_download', 'default_min_size_mb')}MB")
        print(f"Max concurrent: {config.getint('image_download', 'max_concurrent_downloads')}")
        print(f"Default output: {config.get('image_download', 'default_output_directory')}")
        print(f"Request delays: {config.getfloat('image_download', 'request_delay_min')}-{config.getfloat('image_download', 'request_delay_max')}s")
        
        print(f"\n🏗️  Architecture Benefits:")
        print("   ✓ Multi-engine search (DuckDuckGo, Bing)")
        print("   ✓ Concurrent downloads with threading")
        print("   ✓ Image validation and integrity checks")
        print("   ✓ Professional error handling")
        print("   ✓ Progress callbacks and reporting")
        print("   ✓ Configurable request delays")
        print("   ✓ Automatic file size filtering")
        print("   ✓ Safe filename sanitization")
        
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
    print("🚀 Professional AutomatriX Image Downloader")
    print("📄 This replaces the original image_04.py with professional features:")
    print("   - Multi-engine search capabilities")
    print("   - Concurrent downloading with thread pools")
    print("   - Image validation and integrity checks")
    print("   - Progress callbacks and real-time reporting")
    print("   - Professional error handling and logging")
    print("   - Configurable request delays to avoid blocking")
    print("   - Automatic file size filtering")
    print("   - Safe filename sanitization")
    print("   - Centralized configuration management")
    print("   - Type safety and validation")
    print()
    
    try:
        main()
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install beautifulsoup4 Pillow requests")
        sys.exit(1)