# 🎓 Smart Attendance System with FAQ Chatbot

A comprehensive solution that combines automated face recognition-based attendance marking with an intelligent rule-based FAQ chatbot for educational institutions.

##  Features

###  Smart Attendance System
- **Automated Face Recognition**: Uses advanced face recognition technology to automatically detect and mark student attendance
- **Real-time Processing**: Processes video feed in real-time with optimized performance
- **High Accuracy**: Configurable confidence thresholds for reliable face matching
- **Duplicate Prevention**: Prevents marking the same student multiple times in a session
- **Session Management**: Tracks attendance sessions with unique identifiers
- **Multiple Output Formats**: Generates reports in CSV and JSON formats

###  Intelligent FAQ Chatbot
- **Rule-based Matching**: Uses sophisticated keyword matching with synonyms
- **Contextual Responses**: Provides relevant answers based on query categories
- **Interactive Interface**: User-friendly command-line interface with helpful commands
- **Extensible Knowledge Base**: Easy to add new FAQ entries and categories
- **Response Analytics**: Tracks query patterns and response effectiveness
- **Fallback Handling**: Graceful handling of unknown queries with helpful suggestions

###  Data Management
- **SQLite Database**: Robust data storage with proper schema design
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Report Generation**: Automatic generation of attendance reports
- **Data Persistence**: Reliable data storage with backup capabilities
- **Statistics Tracking**: Detailed analytics on attendance and chatbot usage

##  Quick Start

### Prerequisites
- Python 3.8 or higher
- Webcam or camera device
- At least 4GB RAM (8GB recommended for better performance)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-attendance-system.git
   cd smart-attendance-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
smart-attendance-system/
├── main.py                 # Main application entry point
├── config.json            # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── LICENSE               # License file
├── .gitignore           # Git ignore rules
├── data/                # Data storage directory
│   ├── student_images/  # Student face images
│   ├── attendance.db    # SQLite database
│   └── faq.json         # FAQ data
├── logs/                # Log files
│   └── system.log       # Application logs
└── src/                 # Source code
    ├── __init__.py
    ├── attendance_system.py  # Face recognition module
    ├── chatbot.py           # FAQ chatbot module
    └── utils/               # Utility modules
        ├── __init__.py
        ├── config.py        # Configuration management
        ├── database.py      # Database operations
        └── logger.py        # Logging utilities
```

## ⚙️ Configuration

The system uses `config.json` for configuration. Key settings include:

```json
{
    "database_file": "data/attendance.db",
    "student_images_folder": "data/student_images",
    "faq_file": "data/faq.json",
    "log_file": "logs/system.log",
    "face_threshold": 0.5,
    "log_level": "INFO",
    "attendance_session_duration": 300,
    "camera_index": 0,
    "face_recognition_model": "hog",
    "save_reports_format": "csv"
}
```

### Configuration Options

- **face_threshold**: Confidence threshold for face recognition (0.0-1.0)
- **face_recognition_model**: "hog" for speed, "cnn" for accuracy
- **camera_index**: Camera device index (0 for default camera)
- **save_reports_format**: "csv", "json", or "both"
- **log_level**: "DEBUG", "INFO", "WARNING", "ERROR"

##  Usage Guide

### Setting Up Student Images

1. Create a `data/student_images/` directory
2. Add student photos with clear face visibility
3. Name files with student names (e.g., `John_Doe.jpg`, `Jane_Smith.png`)
4. Supported formats: JPG, JPEG, PNG, BMP, TIFF

### Taking Attendance

1. Run the application: `python main.py`
2. Select option 1: "Take Attendance"
3. Position students in front of the camera
4. The system will automatically detect and mark attendance
5. Press 'q' to quit and generate final report
6. Press 'r' to reset marked students
7. Press 's' to save current progress

### Using the FAQ Chatbot

1. Run the application: `python main.py`
2. Select option 2: "Chat with FAQ Bot"
3. Ask questions about:
   - Attendance procedures
   - Exam schedules
   - Leave policies
   - Campus facilities
   - General support

### Available Commands in Chatbot

- `help` - Show available commands
- `categories` - Display FAQ categories
- `stats` - Show chatbot statistics
- `exit` - Quit chatbot session

## 🔧 Advanced Features

### Custom FAQ Management

Add new FAQ entries programmatically:

```python
from src.chatbot import FAQChatbot
from src.utils.config import Config

config = Config()
chatbot = FAQChatbot(config)

chatbot.add_faq_entry(
    question="How to reset password?",
    answer="Visit the student portal and click 'Forgot Password'",
    keywords=["password", "reset", "forgot", "login"],
    category="support"
)
```

### Database Operations

Access database directly for custom queries:

```python
from src.utils.database import DatabaseManager

db = DatabaseManager("data/attendance.db")

# Get student attendance history
attendance = db.get_student_attendance("John_Doe", "2024-01-01", "2024-01-31")

# Get daily attendance report
daily_report = db.get_daily_attendance("2024-01-15")

# Get system statistics
stats = db.get_statistics()
```

### Performance Optimization

For better performance with large student databases:

1. Use "hog" model for face recognition (faster)
2. Enable encoding caching (automatic)
3. Process every nth frame instead of every frame
4. Use smaller image resolutions

##  Troubleshooting

### Common Issues

**Camera not working:**
- Check camera permissions
- Try different camera_index values (0, 1, 2)
- Ensure no other applications are using the camera

**Poor face recognition:**
- Improve lighting conditions
- Ensure students face the camera directly
- Use higher quality images in student_images folder
- Adjust face_threshold in config.json

**Database errors:**
- Check file permissions in data/ directory
- Ensure sufficient disk space
- Run database cleanup: `db.cleanup_old_records(90)`

**Import errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)
- Verify virtual environment is activated

### Performance Issues

**Slow face recognition:**
- Reduce camera resolution
- Use "hog" instead of "cnn" model
- Process fewer frames per second
- Upgrade hardware (more RAM, better CPU)

**Memory usage:**
- Limit number of concurrent students
- Clear face encodings cache periodically
- Monitor system resources

##  System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 1GB free disk space
- Webcam or USB camera
- Windows 10/macOS 10.14/Ubuntu 18.04+

### Recommended Requirements
- Python 3.9+
- 8GB RAM
- 5GB free disk space
- HD webcam (720p or higher)
- Modern multi-core processor

##  Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Development Setup

1. Clone the repository
2. Create virtual environment
3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8
   ```
4. Run tests: `pytest`
5. Format code: `black src/`
6. Lint code: `flake8 src/`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- [face_recognition](https://github.com/ageitgey/face_recognition) library by Adam Geitgey
- [OpenCV](https://opencv.org/) for computer vision capabilities
- [SQLite](https://sqlite.org/) for reliable data storage

##  Future Enhancements

- [ ] Web-based interface
- [ ] Mobile app integration
- [ ] Cloud database support
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Integration with LMS systems
- [ ] AI-powered chatbot improvements
- [ ] Real-time notifications
- [ ] Biometric authentication
- [ ] Advanced reporting features

---

**Made with ❤️ for better education management**
