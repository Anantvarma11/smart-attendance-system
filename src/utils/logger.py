"""
Logging configuration for the Smart Attendance System
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Set up handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized with level: {log_level}")
    if log_file:
        logger.info(f"Log file: {log_file}")


class AttendanceLogger:
    """Custom logger for attendance system events."""
    
    def __init__(self, name: str = "attendance"):
        self.logger = logging.getLogger(name)
    
    def log_attendance_marked(self, student_name: str, timestamp: str):
        """Log when attendance is marked for a student."""
        self.logger.info(f"Attendance marked for {student_name} at {timestamp}")
    
    def log_unknown_face(self, timestamp: str = None):
        """Log when an unknown face is detected."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.warning(f"Unknown face detected at {timestamp}")
    
    def log_system_error(self, error: str, context: str = ""):
        """Log system errors."""
        self.logger.error(f"System error in {context}: {error}")
    
    def log_attendance_session_start(self, student_count: int):
        """Log when attendance session starts."""
        self.logger.info(f"Attendance session started with {student_count} registered students")
    
    def log_attendance_session_end(self, present_count: int, total_count: int):
        """Log when attendance session ends."""
        self.logger.info(f"Attendance session ended: {present_count}/{total_count} students present")


class ChatbotLogger:
    """Custom logger for chatbot events."""
    
    def __init__(self, name: str = "chatbot"):
        self.logger = logging.getLogger(name)
    
    def log_query(self, query: str, response: str, response_time: float = None):
        """Log chatbot queries and responses."""
        message = f"Query: '{query}' -> Response: '{response}'"
        if response_time:
            message += f" (Response time: {response_time:.2f}s)"
        self.logger.info(message)
    
    def log_unknown_query(self, query: str):
        """Log unknown queries."""
        self.logger.warning(f"Unknown query received: '{query}'")
    
    def log_faq_loaded(self, faq_count: int):
        """Log when FAQ data is loaded."""
        self.logger.info(f"FAQ data loaded with {faq_count} entries")
