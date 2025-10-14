"""
Face recognition-based attendance system module
"""

import cv2
import face_recognition
import numpy as np
import os
import pickle
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
import logging
from .utils.database import DatabaseManager
from .utils.logger import AttendanceLogger


class AttendanceSystem:
    """Face recognition-based attendance system."""
    
    def __init__(self, config):
        """
        Initialize attendance system.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = AttendanceLogger("attendance")
        self.db_manager = DatabaseManager(config.database_file)
        self.known_encodings = []
        self.known_names = []
        self.marked_students: Set[str] = set()
        self.session_id = None
        self.session_start_time = None
        
    def load_student_encodings(self) -> Tuple[List, List]:
        """
        Load face encodings for all registered students.
        
        Returns:
            Tuple of (encodings, names) lists
        """
        encodings = []
        names = []
        
        # Ensure student images directory exists
        if not os.path.exists(self.config.student_images_folder):
            os.makedirs(self.config.student_images_folder, exist_ok=True)
            self.logger.logger.warning(f"Created missing directory: {self.config.student_images_folder}")
        
        # Get all image files
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        image_files = [f for f in os.listdir(self.config.student_images_folder) 
                      if f.lower().endswith(image_extensions)]
        
        if not image_files:
            self.logger.logger.warning(f"No images found in {self.config.student_images_folder}")
            return encodings, names
        
        self.logger.logger.info(f"Loading {len(image_files)} student images...")
        
        for filename in image_files:
            image_path = os.path.join(self.config.student_images_folder, filename)
            student_name = os.path.splitext(filename)[0]
            
            try:
                # Load image
                image = face_recognition.load_image_file(image_path)
                
                # Get face encodings
                face_encodings = face_recognition.face_encodings(image)
                
                if face_encodings:
                    # Use the first (and usually only) face found
                    encodings.append(face_encodings[0])
                    names.append(student_name)
                    self.logger.logger.info(f"✅ Loaded encoding for: {student_name}")
                else:
                    self.logger.logger.warning(f"❌ No face found in: {filename}")
                    
            except Exception as e:
                self.logger.logger.error(f"❌ Error processing {filename}: {e}")
        
        # Cache encodings for faster loading next time
        self._cache_encodings(encodings, names)
        
        self.logger.logger.info(f"Successfully loaded {len(encodings)} student encodings")
        return encodings, names
    
    def _cache_encodings(self, encodings: List, names: List):
        """Cache face encodings to disk for faster loading."""
        cache_file = os.path.join(self.config.student_images_folder, "encodings_cache.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump((encodings, names), f)
            self.logger.logger.info(f"Encodings cached to: {cache_file}")
        except Exception as e:
            self.logger.logger.warning(f"Failed to cache encodings: {e}")
    
    def _load_cached_encodings(self) -> Tuple[List, List]:
        """Load cached face encodings if available."""
        cache_file = os.path.join(self.config.student_images_folder, "encodings_cache.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    encodings, names = pickle.load(f)
                self.logger.logger.info(f"Loaded cached encodings for {len(names)} students")
                return encodings, names
            except Exception as e:
                self.logger.logger.warning(f"Failed to load cached encodings: {e}")
        return [], []
    
    def _recognize_face(self, face_encoding: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Recognize a face using loaded encodings.
        
        Args:
            face_encoding: Face encoding to recognize
            
        Returns:
            Tuple of (student_name, confidence_score)
        """
        if not self.known_encodings:
            return None, 0.0
        
        # Calculate face distances
        distances = face_recognition.face_distance(self.known_encodings, face_encoding)
        
        # Find the best match
        best_match_index = distances.argmin()
        best_distance = distances[best_match_index]
        
        # Convert distance to confidence (lower distance = higher confidence)
        confidence = max(0, 1 - best_distance)
        
        # Check if match is above threshold
        if best_distance <= self.config.face_threshold:
            return self.known_names[best_match_index], confidence
        
        return None, confidence
    
    def _draw_face_info(self, frame: np.ndarray, face_location: Tuple, 
                       name: str, confidence: float, is_marked: bool = False):
        """
        Draw face recognition information on frame.
        
        Args:
            frame: Video frame
            face_location: Face location coordinates (top, right, bottom, left)
            name: Student name
            confidence: Recognition confidence
            is_marked: Whether attendance is already marked
        """
        top, right, bottom, left = face_location
        
        # Choose color based on status
        if is_marked:
            color = (0, 255, 0)  # Green for already marked
            status_text = "✓ Marked"
        else:
            color = (255, 0, 0)  # Blue for new detection
            status_text = "New"
        
        # Draw rectangle around face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw background for text
        cv2.rectangle(frame, (left, bottom - 40), (right, bottom), color, cv2.FILLED)
        
        # Draw name and status
        text = f"{name} ({confidence:.2f})"
        cv2.putText(frame, text, (left + 4, bottom - 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(frame, status_text, (left + 4, bottom - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    def _draw_stats(self, frame: np.ndarray, marked_count: int, total_count: int):
        """
        Draw attendance statistics on frame.
        
        Args:
            frame: Video frame
            marked_count: Number of students marked present
            total_count: Total number of registered students
        """
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw statistics
        cv2.putText(frame, f"Present: {marked_count}/{total_count}", (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if total_count > 0:
            percentage = (marked_count / total_count) * 100
            cv2.putText(frame, f"Attendance: {percentage:.1f}%", (20, 65), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, "Press 'q' to quit", (20, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def start_attendance(self):
        """Start the attendance marking process."""
        print("\n🎯 Starting Smart Attendance System...")
        
        # Try to load cached encodings first
        self.known_encodings, self.known_names = self._load_cached_encodings()
        
        # If no cached encodings, load from images
        if not self.known_encodings:
            self.known_encodings, self.known_names = self.load_student_encodings()
        
        if not self.known_encodings:
            print("❌ No student data found!")
            print(f"📁 Please add student face images to: {self.config.student_images_folder}")
            print("💡 Image files should be named with student names (e.g., 'John_Doe.jpg')")
            return
        
        # Initialize camera
        cap = cv2.VideoCapture(self.config.camera_index)
        if not cap.isOpened():
            print("❌ Error: Could not access camera!")
            self.logger.log_system_error("Camera access failed", "start_attendance")
            return
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Initialize session
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start_time = datetime.now()
        self.marked_students.clear()
        
        self.logger.log_attendance_session_start(len(self.known_names))
        
        print(f"📸 Camera initialized successfully!")
        print(f"👥 Found {len(self.known_names)} registered students")
        print(f"🎯 Face recognition threshold: {self.config.face_threshold}")
        print("\n📋 Instructions:")
        print("• Look at the camera to mark attendance")
        print("• Press 'q' to stop and generate report")
        print("• Press 'r' to reset marked students")
        print("• Press 's' to save current attendance")
        
        # Main attendance loop
        frame_count = 0
        process_every_n_frames = 2  # Process every 2nd frame for better performance
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    self.logger.log_system_error("Failed to read camera frame", "attendance_loop")
                    break
                
                frame_count += 1
                
                # Process frame for face recognition
                if frame_count % process_every_n_frames == 0:
                    # Convert BGR to RGB for face_recognition
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    rgb_frame = np.ascontiguousarray(rgb_frame)
                    
                    # Find face locations and encodings
                    face_locations = face_recognition.face_locations(
                        rgb_frame, model=self.config.face_recognition_model
                    )
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    
                    # Process each detected face
                    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                        name, confidence = self._recognize_face(face_encoding)
                        
                        if name:
                            is_already_marked = name in self.marked_students
                            
                            # Mark attendance if not already marked
                            if not is_already_marked:
                                success = self.db_manager.mark_attendance(
                                    name, "Present", self.session_id, confidence
                                )
                                if success:
                                    self.marked_students.add(name)
                                    print(f"✅ {name} marked present (confidence: {confidence:.2f})")
                                    self.logger.log_attendance_marked(name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            
                            # Draw face information
                            self._draw_face_info(frame, (top, right, bottom, left), 
                                               name, confidence, is_already_marked)
                        else:
                            # Unknown face
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                            cv2.putText(frame, "Unknown", (left, top - 10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                            self.logger.log_unknown_face()
                
                # Draw statistics
                self._draw_stats(frame, len(self.marked_students), len(self.known_names))
                
                # Display frame
                cv2.imshow('Smart Attendance System', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self._reset_attendance()
                elif key == ord('s'):
                    self._save_current_attendance()
                    
        except KeyboardInterrupt:
            print("\n⏹️  Attendance session interrupted by user")
        except Exception as e:
            self.logger.log_system_error(str(e), "attendance_loop")
            print(f"❌ An error occurred: {e}")
        finally:
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()
            self._finalize_session()
    
    def _reset_attendance(self):
        """Reset marked students for current session."""
        self.marked_students.clear()
        print("🔄 Attendance reset - all students can be marked again")
    
    def _save_current_attendance(self):
        """Save current attendance progress."""
        if not self.marked_students:
            print("📝 No attendance marked yet")
            return
        
        session_data = {
            "session_id": self.session_id,
            "start_time": self.session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_students": len(self.known_names),
            "present_count": len(self.marked_students),
            "students": {}
        }
        
        # Add present students
        for student in self.marked_students:
            session_data["students"][student] = {
                "status": "Present",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Add absent students
        for student in self.known_names:
            if student not in self.marked_students:
                session_data["students"][student] = {
                    "status": "Absent",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        
        # Save report
        report_file = self.db_manager.save_attendance_report(session_data, self.config.save_reports_format)
        if report_file:
            print(f"💾 Attendance saved to: {report_file}")
    
    def _finalize_session(self):
        """Finalize attendance session and generate reports."""
        if not self.marked_students:
            print("📝 No attendance was marked in this session")
            return
        
        # Create final session data
        session_data = {
            "session_id": self.session_id,
            "start_time": self.session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_students": len(self.known_names),
            "present_count": len(self.marked_students),
            "students": {}
        }
        
        # Mark all students (present and absent)
        for student in self.known_names:
            if student in self.marked_students:
                status = "Present"
            else:
                status = "Absent"
            
            session_data["students"][student] = {
                "status": status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to database
            self.db_manager.mark_attendance(student, status, self.session_id)
        
        # Save final report
        report_file = self.db_manager.save_attendance_report(session_data, self.config.save_reports_format)
        
        # Log session completion
        self.logger.log_attendance_session_end(len(self.marked_students), len(self.known_names))
        
        # Display summary
        print("\n" + "=" * 50)
        print("📊 ATTENDANCE SESSION COMPLETED")
        print("=" * 50)
        print(f"👥 Total Students: {len(self.known_names)}")
        print(f"✅ Present: {len(self.marked_students)}")
        print(f"❌ Absent: {len(self.known_names) - len(self.marked_students)}")
        print(f"📈 Attendance Rate: {(len(self.marked_students)/len(self.known_names))*100:.1f}%")
        print(f"⏱️  Session Duration: {datetime.now() - self.session_start_time}")
        
        if report_file:
            print(f"💾 Report saved: {report_file}")
        
        print("=" * 50)
