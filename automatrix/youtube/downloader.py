"""
Professional YouTube downloader module for AutomatriX
"""

import os
import logging
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    raise ImportError("yt-dlp is required for YouTube downloads. Install with: pip install yt-dlp")

from ..core.config import Config
from ..core.utils import (
    DownloadError,
    ValidationError,
    parse_duration,
    validate_video_quality,
    validate_file_path,
    sanitize_filename,
    format_file_size
)


class YouTubeDownloader:
    """Professional YouTube downloader with advanced features"""
    
    def __init__(self, config: Optional[Config] = None, progress_callback: Optional[Callable] = None):
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        self.progress_callback = progress_callback
        
        # Load configuration defaults
        self.default_quality = self.config.get('youtube_download', 'default_quality', 'best')
        self.max_videos = self.config.getint('youtube_download', 'max_videos_per_search', 100)
        self.default_output_dir = self.config.get('youtube_download', 'default_output_directory', './downloads')
        self.timeout = self.config.getint('youtube_download', 'timeout', 300)
        
        # Setup yt-dlp logger
        self.ydl_logger = self._create_ydl_logger()
    
    def _create_ydl_logger(self):
        """Create a custom logger for yt-dlp"""
        class YDLLogger:
            def __init__(self, main_logger):
                self.main_logger = main_logger
            
            def debug(self, msg):
                self.main_logger.debug(f"yt-dlp: {msg}")
            
            def warning(self, msg):
                self.main_logger.warning(f"yt-dlp: {msg}")
            
            def error(self, msg):
                self.main_logger.error(f"yt-dlp: {msg}")
        
        return YDLLogger(self.logger)
    
    def _progress_hook(self, d):
        """Progress hook for yt-dlp downloads"""
        if d['status'] == 'finished':
            self.logger.info(f"Download completed: {d.get('filename', 'Unknown')}")
            if self.progress_callback:
                self.progress_callback({
                    'status': 'finished',
                    'filename': d.get('filename'),
                    'total_bytes': d.get('total_bytes', 0)
                })
        elif d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            
            self.logger.debug(f"Downloading: {percent} at {speed} ETA: {eta}")
            if self.progress_callback:
                self.progress_callback({
                    'status': 'downloading',
                    'percent': percent,
                    'speed': speed,
                    'eta': eta,
                    'downloaded_bytes': d.get('downloaded_bytes', 0),
                    'total_bytes': d.get('total_bytes', 0)
                })
        elif d['status'] == 'error':
            error_msg = f"Download error: {d.get('error', 'Unknown error')}"
            self.logger.error(error_msg)
            if self.progress_callback:
                self.progress_callback({
                    'status': 'error',
                    'error': error_msg
                })
    
    def download_single_video(
        self,
        url: str,
        output_directory: Optional[str] = None,
        quality: Optional[str] = None,
        audio_only: bool = False
    ) -> Dict[str, Any]:
        """
        Download a single video from YouTube.
        
        Args:
            url: YouTube video URL
            output_directory: Directory to save the video
            quality: Video quality preference
            audio_only: Download only audio
            
        Returns:
            Dictionary with download results
            
        Raises:
            DownloadError: If download fails
            ValidationError: If inputs are invalid
        """
        self.logger.info(f"Downloading video: {url}")
        
        # Validate inputs
        if not url:
            raise ValidationError("URL cannot be empty")
        
        output_directory = output_directory or self.default_output_dir
        quality = validate_video_quality(quality or self.default_quality)
        
        # Ensure output directory exists
        os.makedirs(output_directory, exist_ok=True)
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best' if audio_only else quality,
            'merge_output_format': 'mp3' if audio_only else 'mp4',
            'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s'),
            'logger': self.ydl_logger,
            'progress_hooks': [self._progress_hook],
            'format_sort': ['res:1440', 'res:1080', 'res:720'] if not audio_only else [],
            'quiet': False,
            'no_warnings': False,
            'extractaudio': audio_only,
            'audioformat': 'mp3' if audio_only else None,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info first
                info = ydl.extract_info(url, download=False)
                
                # Sanitize filename
                title = sanitize_filename(info.get('title', 'Unknown'))
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')
                view_count = info.get('view_count', 0)
                
                # Download the video
                ydl.download([url])
                
                # Determine output filename
                ext = 'mp3' if audio_only else 'mp4'
                output_filename = f"{title}.{ext}"
                output_path = os.path.join(output_directory, output_filename)
                
                # Get file size if exists
                file_size = 0
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                
                result = {
                    'success': True,
                    'url': url,
                    'title': title,
                    'duration': duration,
                    'uploader': uploader,
                    'view_count': view_count,
                    'output_path': output_path,
                    'file_size': file_size,
                    'file_size_formatted': format_file_size(file_size),
                    'audio_only': audio_only,
                    'quality': quality
                }
                
                self.logger.info(f"Successfully downloaded: {title}")
                return result
                
        except Exception as e:
            error_msg = f"Failed to download video {url}: {str(e)}"
            self.logger.error(error_msg)
            raise DownloadError(error_msg) from e
    
    def search_and_download(
        self,
        query: str,
        num_videos: int = 5,
        max_duration: Optional[str] = None,
        output_directory: Optional[str] = None,
        quality: Optional[str] = None,
        audio_only: bool = False
    ) -> Dict[str, Any]:
        """
        Search for videos and download them.
        
        Args:
            query: Search query
            num_videos: Number of videos to download
            max_duration: Maximum duration filter (e.g., '5m', '1h')
            output_directory: Directory to save videos
            quality: Video quality preference
            audio_only: Download only audio
            
        Returns:
            Dictionary with search and download results
        """
        self.logger.info(f"Searching and downloading: '{query}' ({num_videos} videos)")
        
        # Validate inputs
        if not query:
            raise ValidationError("Search query cannot be empty")
        
        if num_videos < 1 or num_videos > self.max_videos:
            raise ValidationError(f"Number of videos must be between 1 and {self.max_videos}")
        
        # Parse max duration if provided
        max_duration_seconds = None
        if max_duration:
            max_duration_seconds = parse_duration(max_duration)
        
        output_directory = output_directory or self.default_output_dir
        quality = validate_video_quality(quality or self.default_quality)
        
        # Ensure output directory exists
        os.makedirs(output_directory, exist_ok=True)
        
        # Configure yt-dlp for search
        ydl_opts = {
            'extract_flat': True,
            'quiet': True,
        }
        
        results = {
            'query': query,
            'requested_videos': num_videos,
            'downloaded': [],
            'failed': [],
            'skipped': [],
            'total_downloaded': 0
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for videos
                search_results = ydl.extract_info(
                    f"ytsearch{num_videos * 2}:{query}",  # Search for more to account for filtering
                    download=False
                )
                
                video_urls = []
                for entry in search_results.get('entries', []):
                    # Apply duration filter if specified
                    if max_duration_seconds and entry.get('duration', 0) > max_duration_seconds:
                        results['skipped'].append({
                            'title': entry.get('title', 'Unknown'),
                            'reason': f"Duration exceeds {max_duration}"
                        })
                        continue
                    
                    video_urls.append(entry['url'])
                    if len(video_urls) >= num_videos:
                        break
                
                # Download each video
                for i, url in enumerate(video_urls, 1):
                    try:
                        self.logger.info(f"Downloading video {i}/{len(video_urls)}")
                        download_result = self.download_single_video(
                            url=url,
                            output_directory=output_directory,
                            quality=quality,
                            audio_only=audio_only
                        )
                        
                        results['downloaded'].append(download_result)
                        results['total_downloaded'] += 1
                        
                    except Exception as e:
                        error_info = {
                            'url': url,
                            'error': str(e)
                        }
                        results['failed'].append(error_info)
                        self.logger.error(f"Failed to download video {i}: {e}")
                
                self.logger.info(
                    f"Search and download complete. "
                    f"Downloaded: {results['total_downloaded']}/{num_videos}"
                )
                
                return results
                
        except Exception as e:
            error_msg = f"Failed to search and download '{query}': {str(e)}"
            self.logger.error(error_msg)
            raise DownloadError(error_msg) from e
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Get information about a video without downloading it.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video information
        """
        self.logger.debug(f"Getting video info: {url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': len(info.get('formats', [])),
                    'url': url
                }
                
        except Exception as e:
            error_msg = f"Failed to get video info for {url}: {str(e)}"
            self.logger.error(error_msg)
            raise DownloadError(error_msg) from e