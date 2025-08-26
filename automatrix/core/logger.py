"""
Professional logging system for AutomatriX
"""

import logging
import os
from typing import Optional
from .config import Config


class Logger:
    """Centralized logging management"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Get configuration values
        log_level = self.config.get('logging', 'level', 'INFO')
        log_format = self.config.get('logging', 'format', 
                                   '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_enabled = self.config.getboolean('logging', 'file_enabled', True)
        console_enabled = self.config.getboolean('logging', 'console_enabled', True)
        
        # Set log level
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        logging.basicConfig(level=numeric_level, format=log_format, handlers=[])
        
        # Create formatter
        formatter = logging.Formatter(log_format)
        
        # Setup file handler if enabled
        if file_enabled:
            try:
                os.makedirs('logs', exist_ok=True)
                file_handler = logging.FileHandler('logs/automatrix.log')
                file_handler.setLevel(numeric_level)
                file_handler.setFormatter(formatter)
                logging.getLogger().addHandler(file_handler)
            except Exception as e:
                print(f"Warning: Could not setup file logging: {e}")
        
        # Setup console handler if enabled
        if console_enabled:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(formatter)
            logging.getLogger().addHandler(console_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance"""
        return logging.getLogger(name)
    
    @staticmethod
    def log_function_call(func):
        """Decorator to log function calls"""
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Function {func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Function {func.__name__} failed with error: {e}")
                raise
        return wrapper