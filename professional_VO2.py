#!/usr/bin/env python3
"""
Professional replacement for VO2.py using AutomatriX framework
This demonstrates how the original simple video processing code 
can be upgraded to use the professional AutomatriX architecture.
"""

import sys
import os

# Add the current directory to Python path for development
sys.path.insert(0, os.path.abspath('.'))

from automatrix import config, logger
from automatrix.video.processor import VideoProcessor
from automatrix.core.utils import ValidationError, VideoProcessingError

def main():
    """Professional video watermarking with AutomatriX"""
    # Initialize logger
    main_logger = logger.get_logger(__name__)
    main_logger.info("Starting professional video watermarking")
    
    try:
        # Initialize video processor
        processor = VideoProcessor(config)
        
        # Configuration from config.ini or use defaults
        folder_path = "./videos"  # Change this to your folder containing MP4 files
        
        if not os.path.exists(folder_path):
            main_logger.warning(f"Folder {folder_path} does not exist. Creating demo folder structure...")
            os.makedirs(folder_path, exist_ok=True)
            print(f"✓ Created folder: {folder_path}")
            print(f"📁 Place your MP4 files in {folder_path} and run this script again")
            return
        
        # Output folder
        output_folder = "./watermarked_videos"
        os.makedirs(output_folder, exist_ok=True)
        
        print("🎬 AutomatriX Professional Video Watermarking")
        print("=" * 50)
        print(f"📂 Input folder: {folder_path}")
        print(f"📂 Output folder: {output_folder}")
        print(f"🏷️  Watermark text: Hello World")
        print(f"📍 Position: center, bottom")
        print(f"🎨 Font size: {config.getint('video_processing', 'default_fontsize')}")
        print(f"🎨 Color: {config.get('video_processing', 'default_text_color')}")
        print()
        
        # Batch process videos
        result = processor.batch_process_videos(
            input_folder=folder_path,
            output_folder=output_folder,
            text="Hello World",
            position=('center', 'bottom'),
            volume_factor=0.8  # Reduce volume by 20% like original VO2.py
        )
        
        # Display results
        print("📊 Processing Results:")
        print(f"✅ Successfully processed: {result['total_processed']}/{result['total_files']} videos")
        
        if result['success']:
            print("\n🎉 Successful videos:")
            for success in result['success']:
                print(f"   ✓ {success['filename']} -> {success['file_size']}")
        
        if result['failed']:
            print(f"\n❌ Failed videos: {len(result['failed'])}")
            for failed in result['failed']:
                print(f"   ✗ {failed['filename']}: {failed['error']}")
        
        main_logger.info(f"Batch processing completed: {result['total_processed']} successful")
        
    except ValidationError as e:
        main_logger.error(f"Validation error: {e}")
        print(f"❌ Input validation failed: {e}")
        sys.exit(1)
        
    except VideoProcessingError as e:
        main_logger.error(f"Video processing error: {e}")
        print(f"❌ Video processing failed: {e}")
        sys.exit(1)
        
    except Exception as e:
        main_logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Professional AutomatriX Video Processor")
    print("📄 This replaces the original VO2.py with professional features:")
    print("   - Centralized configuration")
    print("   - Professional logging")
    print("   - Robust error handling")
    print("   - Progress reporting")
    print("   - Type safety")
    print("   - Modular architecture")
    print()
    
    main()