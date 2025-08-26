"""
Command line interface for AutomatriX
"""

import sys
import argparse
import logging
from typing import Optional

try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama for Windows compatibility
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

from automatrix import config, logger

# Import modules conditionally to handle missing dependencies
try:
    from automatrix.video.processor import VideoProcessor
    VIDEO_AVAILABLE = True
except ImportError as e:
    VIDEO_AVAILABLE = False
    VIDEO_ERROR = str(e)

try:
    from automatrix.youtube.downloader import YouTubeDownloader
    YOUTUBE_AVAILABLE = True
except ImportError as e:
    YOUTUBE_AVAILABLE = False
    YOUTUBE_ERROR = str(e)

try:
    from automatrix.image.downloader import ImageDownloader
    IMAGE_AVAILABLE = True
except ImportError as e:
    IMAGE_AVAILABLE = False
    IMAGE_ERROR = str(e)
from automatrix.core.utils import ValidationError, VideoProcessingError, DownloadError


def colored_print(message: str, color: str = '', style: str = ''):
    """Print colored message if colorama is available"""
    if COLORS_AVAILABLE:
        color_map = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'cyan': Fore.CYAN,
            'magenta': Fore.MAGENTA
        }
        style_map = {
            'bright': Style.BRIGHT,
            'dim': Style.DIM
        }
        
        prefix = color_map.get(color, '') + style_map.get(style, '')
        suffix = Style.RESET_ALL if prefix else ''
        print(f"{prefix}{message}{suffix}")
    else:
        print(message)


def setup_cli_logging(verbose: bool = False):
    """Setup logging for CLI"""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create console handler with custom format for CLI
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(log_level)


def cmd_video_watermark(args):
    """Handle video watermark command"""
    if not VIDEO_AVAILABLE:
        colored_print(f"Video processing not available: {VIDEO_ERROR}", 'red')
        colored_print("Install with: pip install moviepy", 'yellow')
        sys.exit(1)
        
    try:
        processor = VideoProcessor(config)
        
        if args.batch:
            # Batch processing
            colored_print(f"Processing videos in folder: {args.input}", 'blue')
            result = processor.batch_process_videos(
                input_folder=args.input,
                output_folder=args.output,
                text=args.text,
                position=(args.position_x, args.position_y),
                fontsize=args.fontsize,
                color=args.color,
                volume_factor=args.volume
            )
            
            colored_print(f"✓ Processed {result['total_processed']}/{result['total_files']} videos", 'green')
            
            if result['failed']:
                colored_print(f"⚠ {len(result['failed'])} videos failed", 'yellow')
                for failed in result['failed']:
                    colored_print(f"  - {failed['filename']}: {failed['error']}", 'red')
        else:
            # Single file processing
            colored_print(f"Processing video: {args.input}", 'blue')
            result = processor.add_text_watermark(
                input_path=args.input,
                output_path=args.output,
                text=args.text,
                position=(args.position_x, args.position_y),
                fontsize=args.fontsize,
                color=args.color,
                volume_factor=args.volume
            )
            
            colored_print(f"✓ Video processed successfully: {result['output_path']}", 'green')
            colored_print(f"  File size: {result['file_size_formatted']}", 'cyan')
            
    except (ValidationError, VideoProcessingError) as e:
        colored_print(f"Error: {e}", 'red')
        sys.exit(1)
    except Exception as e:
        colored_print(f"Unexpected error: {e}", 'red')
        sys.exit(1)


def cmd_youtube_download(args):
    """Handle YouTube download command"""
    if not YOUTUBE_AVAILABLE:
        colored_print(f"YouTube download not available: {YOUTUBE_ERROR}", 'red')
        colored_print("Install with: pip install yt-dlp", 'yellow')
        sys.exit(1)
        
    try:
        downloader = YouTubeDownloader(config)
        
        if args.search:
            # Search and download
            colored_print(f"Searching YouTube for: '{args.search}'", 'blue')
            result = downloader.search_and_download(
                query=args.search,
                num_videos=args.count,
                max_duration=args.max_duration,
                output_directory=args.output,
                quality=args.quality,
                audio_only=args.audio_only
            )
            
            colored_print(f"✓ Downloaded {result['total_downloaded']}/{result['requested_videos']} videos", 'green')
            
            if result['failed']:
                colored_print(f"⚠ {len(result['failed'])} downloads failed", 'yellow')
                for failed in result['failed']:
                    colored_print(f"  - {failed['url']}: {failed['error']}", 'red')
        else:
            # Single URL download
            colored_print(f"Downloading: {args.url}", 'blue')
            result = downloader.download_single_video(
                url=args.url,
                output_directory=args.output,
                quality=args.quality,
                audio_only=args.audio_only
            )
            
            colored_print(f"✓ Downloaded: {result['title']}", 'green')
            colored_print(f"  Output: {result['output_path']}", 'cyan')
            colored_print(f"  Size: {result['file_size_formatted']}", 'cyan')
            
    except (ValidationError, DownloadError) as e:
        colored_print(f"Error: {e}", 'red')
        sys.exit(1)
    except Exception as e:
        colored_print(f"Unexpected error: {e}", 'red')
        sys.exit(1)


def cmd_image_download(args):
    """Handle image download command"""
    if not IMAGE_AVAILABLE:
        colored_print(f"Image download not available: {IMAGE_ERROR}", 'red')
        colored_print("Install with: pip install beautifulsoup4 Pillow", 'yellow')
        sys.exit(1)
        
    try:
        downloader = ImageDownloader(config)
        
        colored_print(f"Searching for images: '{args.query}'", 'blue')
        result = downloader.download_images(
            query=args.query,
            max_images=args.count,
            min_size_mb=args.min_size,
            output_directory=args.output
        )
        
        if result.get('success', True):
            colored_print(f"✓ Downloaded {result['total_downloaded']} images", 'green')
            colored_print(f"  Output folder: {result['output_folder']}", 'cyan')
            
            if result['total_failed'] > 0:
                colored_print(f"⚠ {result['total_failed']} downloads failed", 'yellow')
        else:
            colored_print(f"Error: {result.get('error', 'Unknown error')}", 'red')
            sys.exit(1)
            
    except (ValidationError, DownloadError) as e:
        colored_print(f"Error: {e}", 'red')
        sys.exit(1)
    except Exception as e:
        colored_print(f"Unexpected error: {e}", 'red')
        sys.exit(1)


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog='automatrix',
        description='AutomatriX - Professional automation tools for business activities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add watermark to single video
  automatrix video-watermark input.mp4 output.mp4 --text "My Company"
  
  # Batch process videos
  automatrix video-watermark input_folder output_folder --text "Watermark" --batch
  
  # Download single YouTube video
  automatrix youtube-download --url "https://youtube.com/watch?v=..."
  
  # Search and download multiple YouTube videos
  automatrix youtube-download --search "funny cats" --count 5
  
  # Download images
  automatrix image-download "nature photography" --count 20 --min-size 1.0
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--config',
        help='Configuration file path'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Video watermark command
    video_parser = subparsers.add_parser('video-watermark', help='Add text watermark to videos')
    video_parser.add_argument('input', help='Input video file or folder')
    video_parser.add_argument('output', help='Output video file or folder')
    video_parser.add_argument('--text', default='Hello World', help='Watermark text')
    video_parser.add_argument('--batch', action='store_true', help='Batch process folder')
    video_parser.add_argument('--position-x', default='center', help='Horizontal position')
    video_parser.add_argument('--position-y', default='bottom', help='Vertical position')
    video_parser.add_argument('--fontsize', type=int, default=50, help='Font size')
    video_parser.add_argument('--color', default='white', help='Text color')
    video_parser.add_argument('--volume', type=float, default=1.0, help='Volume factor')
    
    # YouTube download command
    youtube_parser = subparsers.add_parser('youtube-download', help='Download YouTube videos')
    youtube_group = youtube_parser.add_mutually_exclusive_group(required=True)
    youtube_group.add_argument('--url', help='YouTube video URL')
    youtube_group.add_argument('--search', help='Search query')
    youtube_parser.add_argument('--count', type=int, default=5, help='Number of videos to download')
    youtube_parser.add_argument('--quality', default='best', help='Video quality')
    youtube_parser.add_argument('--max-duration', help='Maximum duration (e.g., 5m, 1h)')
    youtube_parser.add_argument('--audio-only', action='store_true', help='Download audio only')
    youtube_parser.add_argument('--output', default='./downloads', help='Output directory')
    
    # Image download command
    image_parser = subparsers.add_parser('image-download', help='Download images from search')
    image_parser.add_argument('query', help='Search query')
    image_parser.add_argument('--count', type=int, default=10, help='Number of images to download')
    image_parser.add_argument('--min-size', type=float, default=0.5, help='Minimum size in MB')
    image_parser.add_argument('--output', default='./downloaded_images', help='Output directory')
    
    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_cli_logging(args.verbose)
    
    # Load custom config if specified
    if args.config:
        global config
        from automatrix.core.config import Config
        config = Config(args.config)
    
    # Display header
    colored_print("AutomatriX - Professional Automation Tools", 'cyan', 'bright')
    colored_print("=" * 50, 'cyan')
    
    # Handle commands
    if args.command == 'video-watermark':
        cmd_video_watermark(args)
    elif args.command == 'youtube-download':
        cmd_youtube_download(args)
    elif args.command == 'image-download':
        cmd_image_download(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()