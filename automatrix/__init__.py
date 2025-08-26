"""
AutomatriX - Professional automation tools for business activities
"""

__version__ = "1.0.0"
__author__ = "AutomatriX Team"
__email__ = "contact@automatrix.dev"
__description__ = "Professional automation tools for business activities"

from .core.config import Config
from .core.logger import Logger

# Initialize global configuration and logger
config = Config()
logger = Logger().get_logger(__name__)

__all__ = ["config", "logger", "__version__"]