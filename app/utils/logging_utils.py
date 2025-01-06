"""Logging utilities for the Library of Alexandria."""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
from functools import wraps
import time
import traceback

# Configure logging formats
DETAILED_FORMAT = '''
Time: %(asctime)s
Level: %(levelname)s
Module: %(module)s
Function: %(funcName)s
Line: %(lineno)d
Message: %(message)s
'''

CONSOLE_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
            
        return json.dumps(log_data)

def setup_logging(
    log_dir: str = 'logs',
    level: int = logging.INFO,
    enable_json: bool = True,
    retention_days: int = 30
) -> None:
    """Set up application-wide logging configuration.
    
    Args:
        log_dir: Directory to store log files
        level: Logging level
        enable_json: Whether to enable JSON structured logging
        retention_days: Number of days to retain log files
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT))
    handlers.append(console_handler)
    
    # File handlers
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Detailed log file
    detailed_handler = logging.FileHandler(
        log_path / f'detailed_{current_time}.log'
    )
    detailed_handler.setFormatter(logging.Formatter(DETAILED_FORMAT))
    handlers.append(detailed_handler)
    
    # JSON structured log file
    if enable_json:
        json_handler = logging.FileHandler(
            log_path / f'structured_{current_time}.json'
        )
        json_handler.setFormatter(JsonFormatter())
        handlers.append(json_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True
    )
    
    # Clean old logs
    clean_old_logs(log_path, retention_days)

def get_logger(
    name: str,
    extra: Optional[Dict[str, Any]] = None
) -> logging.Logger:
    """Get a logger with optional extra context data.
    
    Args:
        name: Logger name
        extra: Additional context data to include in logs
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if extra:
        logger = logging.LoggerAdapter(logger, extra)
    
    return logger

def clean_old_logs(log_dir: Path, retention_days: int) -> None:
    """Remove log files older than retention_days.
    
    Args:
        log_dir: Directory containing log files
        retention_days: Number of days to retain logs
    """
    current_time = datetime.now().timestamp()
    retention_seconds = retention_days * 24 * 60 * 60
    
    for log_file in log_dir.glob('*.log'):
        if current_time - log_file.stat().st_mtime > retention_seconds:
            log_file.unlink()
            
    for log_file in log_dir.glob('*.json'):
        if current_time - log_file.stat().st_mtime > retention_seconds:
            log_file.unlink()

def log_execution_time(logger: logging.Logger):
    """Decorator to log function execution time.
    
    Args:
        logger: Logger instance to use
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f'Function {func.__name__} completed in {execution_time:.2f} seconds'
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f'Function {func.__name__} failed after {execution_time:.2f} seconds',
                    exc_info=True
                )
                raise
        return wrapper
    return decorator 