"""
Comprehensive Logging System with Dual-Tag Architecture

This logging system provides structured logging with dual-tag architecture:
- Feature tags: Indicate user-facing functionality
- Module tags: Specify internal code modules

Key Features:
- Dual-tag filtering system
- Multiple storage backends (memory, file, archived)
- Configurable formatters (JSON, Pretty)
- Comprehensive log analysis
- Security-focused parameter sanitization
- Context tracking (user, session, request)
"""

from .logger import logger
from .config import config_manager
from .analyzer import LogAnalyzer
from .types import LogLevel, LogEntry, LogContext, LoggingConfig
from .constants import FEATURE_TAGS, MODULE_TAGS, COMMON_TAG_COMBINATIONS
from .storage import MemoryLogStorage, FileLogStorage, ArchivedFileLogStorage
from .formatters import JsonFormatter, PrettyFormatter, ConsoleFormatter, FileFormatter

__version__ = "1.0.0"

__all__ = [
    # Core components
    'logger',
    'config_manager',
    'LogAnalyzer',
    
    # Types
    'LogLevel',
    'LogEntry',
    'LogContext',
    'LoggingConfig',
    
    # Constants
    'FEATURE_TAGS',
    'MODULE_TAGS',
    'COMMON_TAG_COMBINATIONS',
    
    # Storage backends
    'MemoryLogStorage',
    'FileLogStorage',
    'ArchivedFileLogStorage',
    
    # Formatters
    'JsonFormatter',
    'PrettyFormatter',
    'ConsoleFormatter',
    'FileFormatter',
]


def setup_logging(config_file: str = "logging.json",
                 use_console: bool = True,
                 use_file: bool = True,
                 use_memory: bool = True,
                 log_directory: str = "./logs",
                 max_memory_entries: int = 10000,
                 max_file_size: int = 10 * 1024 * 1024,
                 max_files: int = 5) -> None:
    """
    Quick setup function for the logging system
    
    Args:
        config_file: Path to the logging configuration file
        use_console: Whether to add console formatter
        use_file: Whether to add file storage
        use_memory: Whether to add memory storage
        log_directory: Directory for log files
        max_memory_entries: Maximum entries in memory storage
        max_file_size: Maximum size per log file
        max_files: Maximum number of rotated log files
    """
    
    # Reload configuration
    config_manager.config_file = config_file
    config_manager.reload_config()
    
    # Add storage backends
    if use_memory:
        memory_storage = MemoryLogStorage(max_entries=max_memory_entries)
        logger.add_storage(memory_storage)
    
    if use_file:
        file_storage = ArchivedFileLogStorage(
            base_directory=log_directory,
            max_file_size=max_file_size,
            max_files=max_files
        )
        logger.add_storage(file_storage)
    
    # Add formatters
    if use_console:
        console_formatter = ConsoleFormatter()
        logger.add_formatter(console_formatter)


def create_sample_config() -> None:
    """Create a sample logging configuration file"""
    config_manager.create_sample_config()


def get_logger_for_feature_module(feature_tag: str, module_tag: str):
    """
    Get a logger instance pre-configured for a specific feature and module
    
    Args:
        feature_tag: The feature tag to use
        module_tag: The module tag to use
        
    Returns:
        A configured logger instance
    """
    class FeatureModuleLogger:
        def __init__(self, feature: str, module: str):
            self.feature = feature
            self.module = module
        
        def debug(self, function_name: str, message: str, parameters: dict = None):
            logger.debug(self.feature, self.module, function_name, message, parameters)
        
        def info(self, function_name: str, message: str, parameters: dict = None):
            logger.info(self.feature, self.module, function_name, message, parameters)
        
        def warn(self, function_name: str, message: str, parameters: dict = None):
            logger.warn(self.feature, self.module, function_name, message, parameters)
        
        def error(self, function_name: str, message: str, exception: Exception = None, parameters: dict = None):
            logger.error(self.feature, self.module, function_name, message, exception, parameters)
        
        def fatal(self, function_name: str, message: str, exception: Exception = None, parameters: dict = None):
            logger.fatal(self.feature, self.module, function_name, message, exception, parameters)
    
    return FeatureModuleLogger(feature_tag, module_tag)


# Quick access to common logger instances
browser_logger = get_logger_for_feature_module(FEATURE_TAGS.BROWSER_AUTOMATION, MODULE_TAGS.BROWSER_MANAGER)
element_logger = get_logger_for_feature_module(FEATURE_TAGS.ELEMENT_INTERACTION, MODULE_TAGS.ELEMENT_PROCESSORS)
vision_logger = get_logger_for_feature_module(FEATURE_TAGS.VISION_PROCESSING, MODULE_TAGS.VISION_PROCESSORS)
network_logger = get_logger_for_feature_module(FEATURE_TAGS.NETWORK_MONITORING, MODULE_TAGS.NETWORK_ANALYZERS)
file_logger = get_logger_for_feature_module(FEATURE_TAGS.FILE_OPERATIONS, MODULE_TAGS.UTILS)
system_logger = get_logger_for_feature_module(FEATURE_TAGS.SYSTEM_INTEGRATION, MODULE_TAGS.SERVICES)