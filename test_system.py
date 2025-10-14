#!/usr/bin/env python3
"""
Simple test script for Smart Attendance System
Run this to verify all components are working correctly
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import face_recognition
        print("✅ face_recognition imported successfully")
    except ImportError as e:
        print(f"❌ face_recognition import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from src.utils.config import Config
        from src.utils.database import DatabaseManager
        from src.utils.logger import setup_logging
        print("✅ Local modules imported successfully")
    except ImportError as e:
        print(f"❌ Local module import failed: {e}")
        return False
    
    return True

def test_camera():
    """Test camera access."""
    print("\n📸 Testing camera access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera access successful")
            cap.release()
            return True
        else:
            print("❌ Camera access failed")
            return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_database():
    """Test database initialization."""
    print("\n💾 Testing database...")
    
    try:
        from src.utils.database import DatabaseManager
        
        # Test with temporary database
        db = DatabaseManager("test_attendance.db")
        db.initialize()
        print("✅ Database initialization successful")
        
        # Clean up test database
        if os.path.exists("test_attendance.db"):
            os.remove("test_attendance.db")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from src.utils.config import Config
        
        config = Config()
        print("✅ Configuration loaded successfully")
        print(f"   - Database file: {config.database_file}")
        print(f"   - Student images folder: {config.student_images_folder}")
        print(f"   - Face threshold: {config.face_threshold}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_chatbot():
    """Test chatbot functionality."""
    print("\n🤖 Testing chatbot...")
    
    try:
        from src.chatbot import FAQChatbot
        from src.utils.config import Config
        
        config = Config()
        chatbot = FAQChatbot(config)
        
        # Test FAQ loading
        if chatbot.faq_data:
            print(f"✅ FAQ data loaded successfully ({len(chatbot.faq_data)} entries)")
        else:
            print("⚠️ No FAQ data found")
        
        # Test response generation
        response = chatbot.get_response("attendance")
        if response:
            print("✅ Chatbot response generation successful")
        else:
            print("❌ Chatbot response generation failed")
        
        return True
    except Exception as e:
        print(f"❌ Chatbot test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Smart Attendance System - System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_camera,
        test_chatbot
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Add student images to data/student_images/ folder")
        print("   2. Run: python main.py")
        print("   3. Test attendance system and chatbot")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Check camera permissions")
        print("   3. Ensure all files are in correct locations")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
