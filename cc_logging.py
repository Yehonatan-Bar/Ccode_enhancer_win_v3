"""
Shared logging configuration for Claude Code enhancer scripts.
All logs are saved to cc_app.log with rotation support.
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logger(name='cc_enhancer', log_file='cc_app.log', max_bytes=10*1024*1024, backup_count=5):
    """
    Set up a logger with file rotation and consistent formatting.
    
    Args:
        name: Logger name
        log_file: Path to the log file
        max_bytes: Maximum size of each log file before rotation (default 10MB)
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file) or '.'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler for errors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


def log_session_start(logger, script_name, args=None):
    """Log the start of a session with context information."""
    logger.info("="*80)
    logger.info(f"SESSION START: {script_name}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Working directory: {os.getcwd()}")
    if args:
        logger.info(f"Arguments: {args}")
    logger.info("="*80)


def log_session_end(logger, script_name, return_code=0):
    """Log the end of a session with status."""
    logger.info("="*80)
    logger.info(f"SESSION END: {script_name}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Return code: {return_code}")
    logger.info("="*80)
    logger.info("")  # Add blank line for readability


def log_claude_invocation(logger, prompt, command=None):
    """Log Claude CLI invocation details."""
    logger.info("-"*60)
    logger.info("CLAUDE CLI INVOCATION")
    if command:
        logger.info(f"Command: {command}")
    logger.info(f"Prompt length: {len(prompt)} characters")
    logger.info("Prompt preview (first 500 chars):")
    logger.info(prompt[:500] + ("..." if len(prompt) > 500 else ""))
    logger.info("-"*60)


def log_claude_response(logger, response, return_code, error=None):
    """Log Claude CLI response details."""
    logger.info("-"*60)
    logger.info("CLAUDE CLI RESPONSE")
    logger.info(f"Return code: {return_code}")
    
    if return_code == 0:
        logger.info(f"Response length: {len(response)} characters")
        logger.info("Response preview (first 500 chars):")
        logger.info(response[:500] + ("..." if len(response) > 500 else ""))
    else:
        logger.error(f"Claude CLI failed with return code: {return_code}")
        if error:
            logger.error(f"Error details: {error}")
        if response:
            logger.error(f"Error output: {response}")
    
    logger.info("-"*60)


def log_exception(logger, exception, context=""):
    """Log exception details with context."""
    logger.error(f"EXCEPTION in {context}" if context else "EXCEPTION")
    logger.error(f"Type: {type(exception).__name__}")
    logger.error(f"Message: {str(exception)}")
    logger.exception("Full traceback:")