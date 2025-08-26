"""
Professional video processing module for AutomatriX
"""

import os
import logging
from typing import Optional, Tuple, Union, List, Dict, Any
from pathlib import Path

try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
except ImportError:
    raise ImportError("moviepy is required for video processing. Install with: pip install moviepy")

from ..core.config import Config
from ..core.utils import (
    VideoProcessingError, 
    ValidationError, 
    validate_file_path,
    sanitize_filename,
    format_file_size
)


class VideoProcessor:
    """Professional video processing with configurable options"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration defaults
        self.default_font = self.config.get('video_processing', 'default_font', 'Arial-Bold')
        self.default_fontsize = self.config.getint('video_processing', 'default_fontsize', 50)
        self.default_text_color = self.config.get('video_processing', 'default_text_color', 'white')
        self.default_stroke_color = self.config.get('video_processing', 'default_stroke_color', 'black')
        self.default_stroke_width = self.config.getint('video_processing', 'default_stroke_width', 2)
        self.default_codec = self.config.get('video_processing', 'default_codec', 'libx264')
        self.default_audio_codec = self.config.get('video_processing', 'default_audio_codec', 'aac')
    
    def add_text_watermark(
        self,
        input_path: str,
        output_path: str,
        text: str = "Hello World",
        position: Union[str, Tuple[str, str]] = ('center', 'bottom'),
        fontsize: Optional[int] = None,
        color: Optional[str] = None,
        font: Optional[str] = None,
        stroke_color: Optional[str] = None,
        stroke_width: Optional[int] = None,
        duration: Optional[float] = None,
        volume_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Add text watermark to a video file.
        
        Args:
            input_path: Path to input video file
            output_path: Path to output video file
            text: Text to overlay on video
            position: Position of text (tuple or string like 'center')
            fontsize: Font size for text
            color: Text color
            font: Font family
            stroke_color: Stroke color for text outline
            stroke_width: Stroke width for text outline
            duration: Duration for text display (None for full video)
            volume_factor: Volume adjustment factor (1.0 = no change, 0.5 = half volume)
            
        Returns:
            Dictionary with processing results
            
        Raises:
            VideoProcessingError: If processing fails
            ValidationError: If inputs are invalid
        """
        self.logger.info(f"Processing video: {input_path}")
        
        # Validate inputs
        validate_file_path(input_path, must_exist=True)
        if not input_path.lower().endswith('.mp4'):
            raise ValidationError("Input file must be an MP4 video")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        # Use configured defaults if not specified
        fontsize = fontsize or self.default_fontsize
        color = color or self.default_text_color
        font = font or self.default_font
        stroke_color = stroke_color or self.default_stroke_color
        stroke_width = stroke_width or self.default_stroke_width
        
        try:
            # Load video file
            self.logger.debug(f"Loading video clip from {input_path}")
            clip = VideoFileClip(input_path)
            
            # Get video info
            video_info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,
                'original_file_size': os.path.getsize(input_path)
            }
            
            # Adjust audio volume if needed
            if volume_factor != 1.0:
                self.logger.debug(f"Adjusting volume by factor {volume_factor}")
                clip = clip.volumex(volume_factor)
            
            # Create text watermark
            self.logger.debug(f"Creating text watermark: '{text}'")
            txt_clip = TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font=font,
                stroke_color=stroke_color,
                stroke_width=stroke_width
            ).set_duration(duration or clip.duration).set_position(position)
            
            # Overlay text onto video
            self.logger.debug("Compositing video with text overlay")
            final_video = CompositeVideoClip([clip, txt_clip])
            
            # Export video
            self.logger.info(f"Exporting video to {output_path}")
            final_video.write_videofile(
                output_path, 
                codec=self.default_codec, 
                audio_codec=self.default_audio_codec,
                verbose=False,
                logger=None
            )
            
            # Get output file info
            output_file_size = os.path.getsize(output_path)
            
            # Clean up
            clip.close()
            final_video.close()
            
            result = {
                'success': True,
                'input_path': input_path,
                'output_path': output_path,
                'text': text,
                'video_info': video_info,
                'output_file_size': output_file_size,
                'file_size_formatted': format_file_size(output_file_size)
            }
            
            self.logger.info(f"Successfully processed video: {output_path}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to process video {input_path}: {str(e)}"
            self.logger.error(error_msg)
            raise VideoProcessingError(error_msg) from e
    
    def batch_process_videos(
        self,
        input_folder: str,
        output_folder: str,
        text: str = "Hello World",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Batch process multiple videos in a folder.
        
        Args:
            input_folder: Folder containing input videos
            output_folder: Folder to save processed videos
            text: Text to overlay on videos
            **kwargs: Additional arguments for add_text_watermark
            
        Returns:
            Dictionary with batch processing results
        """
        self.logger.info(f"Starting batch processing: {input_folder} -> {output_folder}")
        
        # Validate input folder
        validate_file_path(input_folder, must_exist=True)
        if not os.path.isdir(input_folder):
            raise ValidationError("Input path must be a directory")
        
        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        results = {
            'success': [],
            'failed': [],
            'total_processed': 0,
            'total_files': 0
        }
        
        # Process all MP4 files in the folder
        mp4_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.mp4')]
        results['total_files'] = len(mp4_files)
        
        for filename in mp4_files:
            input_path = os.path.join(input_folder, filename)
            output_filename = f"watermarked_{filename}"
            output_path = os.path.join(output_folder, output_filename)
            
            try:
                result = self.add_text_watermark(
                    input_path=input_path,
                    output_path=output_path,
                    text=text,
                    **kwargs
                )
                results['success'].append({
                    'filename': filename,
                    'output_path': output_path,
                    'file_size': result['file_size_formatted']
                })
                results['total_processed'] += 1
                
            except Exception as e:
                error_info = {
                    'filename': filename,
                    'error': str(e)
                }
                results['failed'].append(error_info)
                self.logger.error(f"Failed to process {filename}: {e}")
        
        self.logger.info(
            f"Batch processing complete. "
            f"Processed: {results['total_processed']}/{results['total_files']}"
        )
        
        return results