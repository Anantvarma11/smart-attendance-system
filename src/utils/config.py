"""
Configuration management for the Smart Attendance System
"""

import os
import json
from typing import Dict, Any


class Config:
    """Configuration class to manage application settings."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize configuration with default values."""
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                self._apply_config(config_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file. Using defaults. Error: {e}")
                self._set_defaults()
        else:
            self._set_defaults()
            self._save_config()
    
    def _set_defaults(self):
        """Set default configuration values."""
        self.database_file = "data/attendance.db"
        self.student_images_folder = "data/student_images"
        self.faq_file = "data/faq.json"
        self.log_file = "logs/system.log"
        self.face_threshold = 0.5
        self.log_level = "INFO"
        self.attendance_session_duration = 300  # 5 minutes
        self.camera_index = 0
        self.face_recognition_model = "hog"  # or "cnn" for better accuracy but slower
        self.save_reports_format = "csv"  # csv, json, both
    
    def _apply_config(self, config_data: Dict[str, Any]):
        """Apply loaded configuration data."""
        self.database_file = config_data.get("database_file", "data/attendance.db")
        self.student_images_folder = config_data.get("student_images_folder", "data/student_images")
        self.faq_file = config_data.get("faq_file", "data/faq.json")
        self.log_file = config_data.get("log_file", "logs/system.log")
        self.face_threshold = config_data.get("face_threshold", 0.5)
        self.log_level = config_data.get("log_level", "INFO")
        self.attendance_session_duration = config_data.get("attendance_session_duration", 300)
        self.camera_index = config_data.get("camera_index", 0)
        self.face_recognition_model = config_data.get("face_recognition_model", "hog")
        self.save_reports_format = config_data.get("save_reports_format", "csv")
    
    def _save_config(self):
        """Save current configuration to file."""
        config_data = {
            "database_file": self.database_file,
            "student_images_folder": self.student_images_folder,
            "faq_file": self.faq_file,
            "log_file": self.log_file,
            "face_threshold": self.face_threshold,
            "log_level": self.log_level,
            "attendance_session_duration": self.attendance_session_duration,
            "camera_index": self.camera_index,
            "face_recognition_model": self.face_recognition_model,
            "save_reports_format": self.save_reports_format
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
        except IOError as e:
            print(f"Warning: Could not save config file. Error: {e}")
    
    def update_config(self, **kwargs):
        """Update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self._save_config()
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            "database_file": self.database_file,
            "student_images_folder": self.student_images_folder,
            "faq_file": self.faq_file,
            "log_file": self.log_file,
            "face_threshold": self.face_threshold,
            "log_level": self.log_level,
            "attendance_session_duration": self.attendance_session_duration,
            "camera_index": self.camera_index,
            "face_recognition_model": self.face_recognition_model,
            "save_reports_format": self.save_reports_format
        }
