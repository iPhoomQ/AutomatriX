"""
Configuration management for AutomatriX
"""

import configparser
import os
from typing import Any, Optional
from pathlib import Path


class Config:
    """Centralized configuration management"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = configparser.ConfigParser()
        self.config_file = config_file or self._find_config_file()
        self._load_config()
    
    def _find_config_file(self) -> str:
        """Find the configuration file in standard locations"""
        possible_paths = [
            "config.ini",
            os.path.expanduser("~/.automatrix/config.ini"),
            "/etc/automatrix/config.ini"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default path if none found
        return "config.ini"
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file)
            else:
                self._create_default_config()
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        self.config['logging'] = {
            'level': 'INFO',
            'format': '%%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s',
            'file_enabled': 'true',
            'console_enabled': 'true'
        }
        
        self.config['video_processing'] = {
            'default_font': 'Arial-Bold',
            'default_fontsize': '50',
            'default_text_color': 'white',
            'default_stroke_color': 'black',
            'default_stroke_width': '2',
            'default_codec': 'libx264',
            'default_audio_codec': 'aac'
        }
        
        self.config['youtube_download'] = {
            'default_quality': 'best',
            'max_videos_per_search': '100',
            'default_output_directory': './downloads',
            'timeout': '300'
        }
        
        self.config['image_download'] = {
            'default_min_size_mb': '0.5',
            'max_concurrent_downloads': '4',
            'default_output_directory': './downloaded_images',
            'request_delay_min': '1.0',
            'request_delay_max': '3.0'
        }
        
        self.config['ui'] = {
            'window_title': 'AutomatriX - Professional Automation Tools',
            'window_geometry': '800x600',
            'theme': 'default'
        }
    
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration value"""
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value"""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value"""
        try:
            return self.config.getfloat(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value"""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def set(self, section: str, key: str, value: str):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
    
    def save(self):
        """Save configuration to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")