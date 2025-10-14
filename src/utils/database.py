"""
Database management for the Smart Attendance System
"""

import sqlite3
import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging


class DatabaseManager:
    """Manages database operations for the attendance system."""
    
    def __init__(self, db_file: str = "data/attendance.db"):
        """
        Initialize database manager.
        
        Args:
            db_file: Path to SQLite database file
        """
        self.db_file = db_file
        self.logger = logging.getLogger("database")
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        data_dir = os.path.dirname(self.db_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            self.logger.info(f"Created data directory: {data_dir}")
    
    def initialize(self):
        """Initialize database with required tables."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Create attendance table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_name TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        status TEXT NOT NULL,
                        session_id TEXT,
                        confidence REAL
                    )
                ''')
                
                # Create students table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        student_id TEXT UNIQUE,
                        image_path TEXT,
                        encoding_path TEXT,
                        date_added TEXT DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # Create sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        total_students INTEGER,
                        present_count INTEGER,
                        status TEXT DEFAULT 'active'
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def mark_attendance(self, student_name: str, status: str = "Present", 
                       session_id: str = None, confidence: float = None) -> bool:
        """
        Mark attendance for a student.
        
        Args:
            student_name: Name of the student
            status: Attendance status (Present/Absent)
            session_id: Session identifier
            confidence: Face recognition confidence score
            
        Returns:
            True if successful, False otherwise
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO attendance (student_name, timestamp, status, session_id, confidence)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_name, timestamp, status, session_id, confidence))
                conn.commit()
                
            self.logger.info(f"Attendance marked: {student_name} - {status} at {timestamp}")
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to mark attendance for {student_name}: {e}")
            return False
    
    def get_student_attendance(self, student_name: str, 
                              start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Get attendance records for a specific student.
        
        Args:
            student_name: Name of the student
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            
        Returns:
            List of attendance records
        """
        query = "SELECT * FROM attendance WHERE student_name = ?"
        params = [student_name]
        
        if start_date:
            query += " AND DATE(timestamp) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(timestamp) <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get attendance for {student_name}: {e}")
            return []
    
    def get_daily_attendance(self, date: str = None) -> Dict[str, List[Dict]]:
        """
        Get attendance records for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary with student names as keys and attendance records as values
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM attendance 
                    WHERE DATE(timestamp) = ? 
                    ORDER BY student_name, timestamp
                ''', (date,))
                rows = cursor.fetchall()
                
                attendance_dict = {}
                for row in rows:
                    student_name = row['student_name']
                    if student_name not in attendance_dict:
                        attendance_dict[student_name] = []
                    attendance_dict[student_name].append(dict(row))
                
                return attendance_dict
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get daily attendance for {date}: {e}")
            return {}
    
    def save_attendance_report(self, session_data: Dict, format_type: str = "csv") -> str:
        """
        Save attendance report to file.
        
        Args:
            session_data: Dictionary containing session information
            format_type: Output format (csv, json, both)
            
        Returns:
            Path to saved report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"attendance_report_{timestamp}"
        
        saved_files = []
        
        if format_type in ["csv", "both"]:
            csv_file = f"{base_filename}.csv"
            try:
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Student Name', 'Status', 'Timestamp', 'Confidence'])
                    
                    for student, data in session_data.get('students', {}).items():
                        writer.writerow([
                            student,
                            data.get('status', 'Unknown'),
                            data.get('timestamp', ''),
                            data.get('confidence', '')
                        ])
                
                saved_files.append(csv_file)
                self.logger.info(f"CSV report saved: {csv_file}")
                
            except IOError as e:
                self.logger.error(f"Failed to save CSV report: {e}")
        
        if format_type in ["json", "both"]:
            json_file = f"{base_filename}.json"
            try:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=4, ensure_ascii=False)
                
                saved_files.append(json_file)
                self.logger.info(f"JSON report saved: {json_file}")
                
            except IOError as e:
                self.logger.error(f"Failed to save JSON report: {e}")
        
        return saved_files[0] if saved_files else None
    
    def view_attendance_reports(self):
        """Display attendance reports in a user-friendly format."""
        print("\n" + "=" * 60)
        print("📊 ATTENDANCE REPORTS")
        print("=" * 60)
        
        # Get today's attendance
        today = datetime.now().strftime("%Y-%m-%d")
        daily_attendance = self.get_daily_attendance(today)
        
        if not daily_attendance:
            print(f"📅 No attendance records found for {today}")
            return
        
        print(f"📅 Attendance for {today}")
        print("-" * 40)
        
        total_students = len(daily_attendance)
        present_count = sum(1 for records in daily_attendance.values() 
                          if any(r['status'] == 'Present' for r in records))
        
        print(f"👥 Total Students: {total_students}")
        print(f"✅ Present: {present_count}")
        print(f"❌ Absent: {total_students - present_count}")
        print(f"📈 Attendance Rate: {(present_count/total_students)*100:.1f}%")
        
        print("\n📋 Student Details:")
        print("-" * 40)
        
        for student_name, records in daily_attendance.items():
            latest_record = max(records, key=lambda x: x['timestamp'])
            status_icon = "✅" if latest_record['status'] == 'Present' else "❌"
            print(f"{status_icon} {student_name} - {latest_record['status']} "
                  f"({latest_record['timestamp']})")
    
    def cleanup_old_records(self, days_to_keep: int = 90):
        """
        Clean up old attendance records.
        
        Args:
            days_to_keep: Number of days to keep records
        """
        cutoff_date = datetime.now().replace(day=datetime.now().day - days_to_keep)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM attendance WHERE DATE(timestamp) < ?",
                    (cutoff_str,)
                )
                deleted_count = cursor.rowcount
                conn.commit()
                
            self.logger.info(f"Cleaned up {deleted_count} old attendance records")
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to cleanup old records: {e}")
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Total records
                cursor.execute("SELECT COUNT(*) FROM attendance")
                total_records = cursor.fetchone()[0]
                
                # Unique students
                cursor.execute("SELECT COUNT(DISTINCT student_name) FROM attendance")
                unique_students = cursor.fetchone()[0]
                
                # Present records
                cursor.execute("SELECT COUNT(*) FROM attendance WHERE status = 'Present'")
                present_records = cursor.fetchone()[0]
                
                # Latest record
                cursor.execute("SELECT MAX(timestamp) FROM attendance")
                latest_record = cursor.fetchone()[0]
                
                return {
                    "total_records": total_records,
                    "unique_students": unique_students,
                    "present_records": present_records,
                    "attendance_rate": (present_records / total_records * 100) if total_records > 0 else 0,
                    "latest_record": latest_record
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
