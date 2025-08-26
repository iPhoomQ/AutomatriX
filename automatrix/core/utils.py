"""
Core utilities and exceptions for AutomatriX
"""

import re
from typing import Union, Optional


class AutomatriXError(Exception):
    """Base exception for AutomatriX"""
    pass


class ConfigurationError(AutomatriXError):
    """Configuration related errors"""
    pass


class VideoProcessingError(AutomatriXError):
    """Video processing related errors"""
    pass


class DownloadError(AutomatriXError):
    """Download related errors"""
    pass


class ValidationError(AutomatriXError):
    """Input validation errors"""
    pass


def parse_duration(duration_str: str) -> int:
    """
    Parse a duration string like '1m', '2h', '30s' into seconds.
    
    Args:
        duration_str: Duration string in format like '1m', '2h', '30s'
        
    Returns:
        Duration in seconds
        
    Raises:
        ValidationError: If duration format is invalid
    """
    if not duration_str:
        raise ValidationError("Duration string cannot be empty")
    
    # Regex to match patterns like '1m', '2h', '30s', etc.
    match = re.match(r'^(\d+)([hms])$', duration_str.lower().strip())
    if not match:
        raise ValidationError(
            "Invalid duration format. Use formats like '1m', '2h', '30s'."
        )

    value, unit = match.groups()
    value = int(value)

    if unit == 'h':
        return value * 3600  # Convert hours to seconds
    elif unit == 'm':
        return value * 60  # Convert minutes to seconds
    elif unit == 's':
        return value  # Seconds
    else:
        raise ValidationError("Invalid unit. Use 'h', 'm', or 's'.")


def validate_video_quality(quality: str) -> str:
    """
    Validate video quality parameter.
    
    Args:
        quality: Video quality string
        
    Returns:
        Validated quality string
        
    Raises:
        ValidationError: If quality is invalid
    """
    valid_qualities = ['best', 'worst', '4K', '1080p', '720p', '480p', '360p', '144p']
    
    if quality not in valid_qualities:
        raise ValidationError(
            f"Invalid video quality '{quality}'. "
            f"Valid options: {', '.join(valid_qualities)}"
        )
    
    return quality


def validate_file_path(file_path: str, must_exist: bool = False) -> str:
    """
    Validate file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether the file must already exist
        
    Returns:
        Validated file path
        
    Raises:
        ValidationError: If path is invalid
    """
    import os
    
    if not file_path:
        raise ValidationError("File path cannot be empty")
    
    if must_exist and not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    # Check for invalid characters (basic check)
    invalid_chars = '<>:"|?*' if os.name == 'nt' else ''
    if any(char in file_path for char in invalid_chars):
        raise ValidationError(f"File path contains invalid characters: {file_path}")
    
    return file_path


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f}{size_names[i]}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Remove/replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename or "untitled"