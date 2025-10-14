"""
Smart Attendance System with Rule-Based FAQ Chatbot
Main entry point for the application.
"""

import sys
import os
from src.attendance_system import AttendanceSystem
from src.chatbot import FAQChatbot
from src.utils.logger import setup_logging
from src.utils.database import DatabaseManager
from src.utils.config import Config

def main():
    """Main application entry point."""
    try:
        # Initialize configuration and logging
        config = Config()
        setup_logging(config.log_level, config.log_file)
        
        # Initialize database
        db_manager = DatabaseManager(config.database_file)
        db_manager.initialize()
        
        print("=" * 60)
        print("🎓 Smart Attendance System with FAQ Chatbot")
        print("=" * 60)
        print("1. 📸 Take Attendance (Face Recognition)")
        print("2. 🤖 Chat with FAQ Bot")
        print("3. 📊 View Attendance Reports")
        print("4. ⚙️  System Settings")
        print("5. ❌ Exit")
        print("=" * 60)
        
        while True:
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == '1':
                    attendance_system = AttendanceSystem(config)
                    attendance_system.start_attendance()
                    
                elif choice == '2':
                    chatbot = FAQChatbot(config)
                    chatbot.start_chat()
                    
                elif choice == '3':
                    db_manager.view_attendance_reports()
                    
                elif choice == '4':
                    show_settings(config)
                    
                elif choice == '5':
                    print("\n👋 Thank you for using Smart Attendance System!")
                    break
                    
                else:
                    print("❌ Invalid choice. Please enter 1-5.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        sys.exit(1)

def show_settings(config):
    """Display system settings and configuration."""
    print("\n" + "=" * 40)
    print("⚙️  SYSTEM SETTINGS")
    print("=" * 40)
    print(f"📁 Student Images Folder: {config.student_images_folder}")
    print(f"💾 Database File: {config.database_file}")
    print(f"📝 FAQ File: {config.faq_file}")
    print(f"📊 Log File: {config.log_file}")
    print(f"🎯 Face Recognition Threshold: {config.face_threshold}")
    print("=" * 40)

if __name__ == "__main__":
    main()
