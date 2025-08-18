"""
Logging Infrastructure.

Moved from utils/logging.py to infrastructure layer.
"""

import logging
import os
import datetime


def get_logger(name: str = "newtone_translate"):
    """
    Get configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger with file and console handlers
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Console handler
        handler = logging.StreamHandler()
        fmt = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)

        # File handler with timestamp - updated path for new structure
        log_dir = os.path.join(os.path.dirname(__file__), '../../../logs')
        log_dir = os.path.abspath(log_dir)
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

        level = os.getenv("NEWTT_LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, level, logging.INFO))
    return logger
