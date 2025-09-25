import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_dir: str = None) -> None:
    """
    Set up centralized logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files. Defaults to logs/ in project root.
    """
    if log_dir is None:
        base_dir = Path(__file__).parent.parent.resolve()
        log_dir = base_dir / "logs"
    
    # Ensure log directory exists
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for general application logs
    app_log_file = log_dir / "app.log"
    file_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Separate file handler for API logs
    api_log_file = log_dir / "api.log"
    api_handler = logging.handlers.RotatingFileHandler(
        api_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    api_handler.setLevel(numeric_level)
    api_handler.setFormatter(detailed_formatter)
    
    # Create API logger
    api_logger = logging.getLogger('api')
    api_logger.addHandler(api_handler)
    api_logger.setLevel(numeric_level)
    api_logger.propagate = False  # Don't propagate to root logger
    
    # Separate file handler for RAG engine logs
    rag_log_file = log_dir / "rag.log"
    rag_handler = logging.handlers.RotatingFileHandler(
        rag_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    rag_handler.setLevel(numeric_level)
    rag_handler.setFormatter(detailed_formatter)
    
    # Create RAG logger
    rag_logger = logging.getLogger('rag')
    rag_logger.addHandler(rag_handler)
    rag_logger.setLevel(numeric_level)
    rag_logger.propagate = False  # Don't propagate to root logger
    
    # Separate file handler for server logs
    server_log_file = log_dir / "server.log"
    server_handler = logging.handlers.RotatingFileHandler(
        server_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    server_handler.setLevel(numeric_level)
    server_handler.setFormatter(detailed_formatter)
    
    # Create server logger
    server_logger = logging.getLogger('server')
    server_logger.addHandler(server_handler)
    server_logger.setLevel(numeric_level)
    server_logger.propagate = False  # Don't propagate to root logger
    
    # Error log file for all ERROR and CRITICAL messages
    error_log_file = log_dir / "error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Log the setup completion
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured successfully. Log directory: {log_dir}")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log files: app.log, api.log, rag.log, server.log, error.log")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def get_api_logger() -> logging.Logger:
    """Get the API-specific logger."""
    return logging.getLogger('api')


def get_rag_logger() -> logging.Logger:
    """Get the RAG engine-specific logger."""
    return logging.getLogger('rag')


def get_server_logger() -> logging.Logger:
    """Get the server-specific logger."""
    return logging.getLogger('server')
