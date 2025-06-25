import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any
from .config import config


def setup_logging():
    """Setup logging based on configuration."""
    log_config = config.get_section("logging")
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_config.get("level", "INFO")))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Setup handlers based on configuration
    handlers = log_config.get("handlers", [])
    
    for handler_config in handlers:
        handler = _create_handler(handler_config, log_config.get("format"))
        if handler:
            root_logger.addHandler(handler)
    
    # If no handlers configured, add console handler as fallback
    if not handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(log_config.get("format", "%(levelname)s - %(message)s"))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)


def _create_handler(handler_config: Dict[str, Any], log_format: str) -> logging.Handler:
    """Create a logging handler based on configuration."""
    handler_type = handler_config.get("type")
    level = handler_config.get("level", "INFO")
    
    if handler_type == "console":
        handler = logging.StreamHandler()
    elif handler_type == "file":
        filename = handler_config.get("filename", "logs/app.log")
        max_bytes = handler_config.get("max_bytes", 10485760)  # 10MB default
        backup_count = handler_config.get("backup_count", 5)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=filename,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
    else:
        return None
    
    handler.setLevel(getattr(logging, level))
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    
    return handler


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)