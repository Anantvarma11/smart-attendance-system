# 🚀 Setup Guide - Smart Attendance System

This guide will help you set up the Smart Attendance System on your local machine.

## 📋 Prerequisites

Before installing the system, ensure you have:

- **Python 3.8 or higher** installed on your system
- **Webcam or camera device** connected and working
- **At least 4GB RAM** (8GB recommended for optimal performance)
- **Administrator/root access** for installing system dependencies

### Check Python Version

```bash
python --version
# or
python3 --version
```

If Python is not installed or you need a newer version, download it from [python.org](https://www.python.org/downloads/).

## 🔧 Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/smart-attendance-system.git
cd smart-attendance-system
```

### Step 2: Create Virtual Environment

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install System Dependencies

The face recognition library requires some system dependencies:

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
sudo apt-get install libboost-python-dev
```

**On macOS:**
```bash
brew install cmake
brew install boost
```

**On Windows:**
- Install Visual Studio Build Tools
- Install CMake from [cmake.org](https://cmake.org/download/)

### Step 5: Verify Installation

```bash
python -c "import cv2, face_recognition, numpy; print('All dependencies installed successfully!')"
```

## 📁 Directory Setup

The system will automatically create the following directory structure:

```
smart-attendance-system/
├── data/
│   ├── student_images/     # Place student photos here
│   ├── attendance.db       # Database file (auto-created)
│   └── faq.json           # FAQ data (auto-created)
├── logs/
│   └── system.log         # Application logs
└── reports/               # Attendance reports
```

## 👥 Setting Up Student Images

### Image Requirements

- **Format**: JPG, JPEG, PNG, BMP, or TIFF
- **Resolution**: Minimum 200x200 pixels, recommended 400x400 or higher
- **Quality**: Clear, well-lit photos with face clearly visible
- **Naming**: Use student names (e.g., `John_Doe.jpg`, `Jane_Smith.png`)

### Adding Student Images

1. Place student photos in `data/student_images/` folder
2. Ensure each photo shows only one person
3. Use clear, front-facing photos
4. Avoid photos with sunglasses, hats, or heavy makeup

### Example Student Images Structure

```
data/student_images/
├── John_Doe.jpg
├── Jane_Smith.png
├── Michael_Johnson.jpeg
└── Sarah_Wilson.jpg
```

## ⚙️ Configuration

### Basic Configuration

Edit `config.json` to customize system settings:

```json
{
    "face_threshold": 0.5,
    "camera_index": 0,
    "face_recognition_model": "hog",
    "log_level": "INFO"
}
```

### Camera Setup

1. **Test camera access:**
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   print("Camera working:", cap.isOpened())
   cap.release()
   ```

2. **Find correct camera index:**
   ```python
   import cv2
   for i in range(5):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f"Camera {i} is available")
           cap.release()
   ```

3. **Update config.json** with the correct camera index

## 🧪 Testing the System

### Test 1: Basic Functionality

```bash
python main.py
```

Select option 2 (FAQ Chatbot) to test basic functionality.

### Test 2: Camera Access

```bash
python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('✅ Camera access successful')
    cap.release()
else:
    print('❌ Camera access failed')
"
```

### Test 3: Face Recognition

1. Add at least one student image to `data/student_images/`
2. Run the system: `python main.py`
3. Select option 1 (Take Attendance)
4. Test with the student whose photo you added

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Issue: "No module named 'cv2'"
**Solution:**
```bash
pip uninstall opencv-python
pip install opencv-python==4.8.1.78
```

#### Issue: "No module named 'face_recognition'"
**Solution:**
```bash
pip install face_recognition==1.3.0
```

#### Issue: Camera not detected
**Solutions:**
1. Check camera permissions
2. Try different camera indices (0, 1, 2)
3. Ensure no other applications are using the camera
4. On Linux: `sudo usermod -a -G video $USER`

#### Issue: Poor face recognition accuracy
**Solutions:**
1. Improve lighting conditions
2. Use higher quality student images
3. Adjust `face_threshold` in config.json (try 0.4 or 0.6)
4. Ensure students face the camera directly

#### Issue: "Permission denied" errors
**Solutions:**
1. Check file permissions in data/ directory
2. Run with appropriate permissions
3. Ensure write access to logs/ directory

### Performance Optimization

#### For Large Student Databases (>100 students):

1. **Use HOG model:**
   ```json
   "face_recognition_model": "hog"
   ```

2. **Adjust processing frequency:**
   - Edit `attendance_system.py`
   - Change `process_every_n_frames = 3` for better performance

3. **Optimize camera settings:**
   ```python
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
   ```

## 🔒 Security Considerations

### Data Privacy

1. **Student Images:**
   - Store images securely
   - Use encrypted storage for sensitive environments
   - Implement access controls

2. **Database:**
   - Regular backups
   - Access restrictions
   - Consider encryption for sensitive data

3. **Logs:**
   - Regular log rotation
   - Secure log storage
   - Monitor for sensitive information

### Network Security (if deploying)

1. Use HTTPS for web interfaces
2. Implement authentication
3. Regular security updates
4. Firewall configuration

## 📊 System Monitoring

### Log Files

Monitor these log files for system health:

- `logs/system.log` - Main application logs
- Database logs (if enabled)
- System error logs

### Performance Metrics

Track these metrics for optimization:

- Face recognition accuracy rate
- Average processing time per frame
- Memory usage
- CPU utilization

## 🔄 Updates and Maintenance

### Regular Maintenance Tasks

1. **Weekly:**
   - Check log files for errors
   - Verify camera functionality
   - Test face recognition accuracy

2. **Monthly:**
   - Update student images if needed
   - Clean old attendance records
   - Backup database

3. **Quarterly:**
   - Update dependencies
   - Review and update FAQ data
   - Performance optimization review

### Updating the System

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## 📞 Getting Help

If you encounter issues not covered in this guide:

1. Check the [README.md](README.md) file
2. Review log files in `logs/` directory
3. Search existing issues on GitHub
4. Create a new issue with detailed information

### Support Information

When requesting help, include:

- Operating system and version
- Python version
- Error messages and logs
- Steps to reproduce the issue
- System specifications (RAM, CPU)

---

**🎉 Congratulations! Your Smart Attendance System is now ready to use!**
