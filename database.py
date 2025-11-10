import sqlite3
from datetime import datetime
from pathlib import Path
import json
import sys
import os

# Ensure we import from the local config, not cv2's config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATABASE_PATH

DB_PATH = Path(DATABASE_PATH)

def init_db():
    """Initialize database with all required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            face_encoding BLOB,
            face_image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Instructors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            instructor_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE NOT NULL,
            course_name TEXT NOT NULL,
            description TEXT,
            instructor_id INTEGER NOT NULL,
            credits INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (instructor_id) REFERENCES instructors(id)
        )
    ''')
    
    # Sections table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            section_number TEXT NOT NULL,
            schedule TEXT,
            room TEXT,
            capacity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            UNIQUE(course_id, section_number)
        )
    ''')
    
    # Enrollments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            section_id INTEGER NOT NULL,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (section_id) REFERENCES sections(id),
            UNIQUE(student_id, section_id)
        )
    ''')
    
    # Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            section_id INTEGER NOT NULL,
            attendance_date DATE NOT NULL,
            check_in_time TIMESTAMP,
            check_out_time TIMESTAMP,
            status TEXT DEFAULT 'present',
            confidence REAL,
            face_match_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (section_id) REFERENCES sections(id),
            UNIQUE(student_id, section_id, attendance_date)
        )
    ''')
    
    # Face encodings cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_encodings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            encoding BLOB NOT NULL,
            encoding_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def execute_query(query, params=None):
    """Execute a query and return results"""
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def execute_update(query, params=None):
    """Execute an update/insert/delete query"""
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    conn.commit()
    conn.close()

# User operations
def create_user(username, password, email, role):
    """Create a new user"""
    try:
        execute_update(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
            (username, password, email, role)
        )
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(username):
    """Get user by username"""
    results = execute_query('SELECT * FROM users WHERE username = ?', (username,))
    return results[0] if results else None

def verify_user(username, password):
    """Verify user credentials"""
    user = get_user(username)
    return user if user and user[2] == password else None

# Student operations
def create_student(user_id, student_id, first_name, last_name, email, phone=None):
    """Create a new student"""
    try:
        execute_update(
            '''INSERT INTO students (user_id, student_id, first_name, last_name, email, phone)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, student_id, first_name, last_name, email, phone)
        )
        return True
    except sqlite3.IntegrityError:
        return False

def get_student(student_id):
    """Get student by student_id"""
    results = execute_query('SELECT * FROM students WHERE student_id = ?', (student_id,))
    return results[0] if results else None

def get_student_by_user_id(user_id):
    """Get student by user_id"""
    results = execute_query('SELECT * FROM students WHERE user_id = ?', (user_id,))
    return results[0] if results else None

def get_all_students():
    """Get all students"""
    return execute_query('SELECT * FROM students')

def update_student_face(student_id, face_image_path):
    """Update student face image path"""
    execute_update(
        'UPDATE students SET face_image_path = ? WHERE id = ?',
        (face_image_path, student_id)
    )

# Instructor operations
def create_instructor(user_id, instructor_id, first_name, last_name, email, phone=None, department=None):
    """Create a new instructor"""
    try:
        execute_update(
            '''INSERT INTO instructors (user_id, instructor_id, first_name, last_name, email, phone, department)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (user_id, instructor_id, first_name, last_name, email, phone, department)
        )
        return True
    except sqlite3.IntegrityError:
        return False

def get_instructor(instructor_id):
    """Get instructor by instructor_id"""
    results = execute_query('SELECT * FROM instructors WHERE instructor_id = ?', (instructor_id,))
    return results[0] if results else None

def get_instructor_by_user_id(user_id):
    """Get instructor by user_id"""
    results = execute_query('SELECT * FROM instructors WHERE user_id = ?', (user_id,))
    return results[0] if results else None

def get_all_instructors():
    """Get all instructors"""
    return execute_query('SELECT * FROM instructors')

# Course operations
def create_course(course_code, course_name, instructor_id, description=None, credits=3):
    """Create a new course"""
    try:
        execute_update(
            '''INSERT INTO courses (course_code, course_name, instructor_id, description, credits)
               VALUES (?, ?, ?, ?, ?)''',
            (course_code, course_name, instructor_id, description, credits)
        )
        return True
    except sqlite3.IntegrityError:
        return False

def get_course(course_code):
    """Get course by course_code or id"""
    # Try by course_code first (string)
    results = execute_query('SELECT * FROM courses WHERE course_code = ?', (course_code,))
    if results:
        return results[0]
    # Try by id (integer)
    try:
        results = execute_query('SELECT * FROM courses WHERE id = ?', (int(course_code),))
        return results[0] if results else None
    except (ValueError, TypeError):
        return None

def get_courses_by_instructor(instructor_id):
    """Get all courses by instructor"""
    return execute_query('SELECT * FROM courses WHERE instructor_id = ?', (instructor_id,))

def get_all_courses():
    """Get all courses"""
    return execute_query('SELECT * FROM courses')

# Section operations
def create_section(course_id, section_number, schedule=None, room=None, capacity=50):
    """Create a new section"""
    try:
        execute_update(
            '''INSERT INTO sections (course_id, section_number, schedule, room, capacity)
               VALUES (?, ?, ?, ?, ?)''',
            (course_id, section_number, schedule, room, capacity)
        )
        return True
    except sqlite3.IntegrityError:
        return False

def get_section(section_id):
    """Get section by id"""
    results = execute_query('SELECT * FROM sections WHERE id = ?', (section_id,))
    return results[0] if results else None

def get_sections_by_course(course_id):
    """Get all sections for a course"""
    return execute_query('SELECT * FROM sections WHERE course_id = ?', (course_id,))

def get_all_sections():
    """Get all sections"""
    return execute_query('SELECT * FROM sections')

# Enrollment operations
def enroll_student(student_id, section_id):
    """Enroll a student in a section"""
    try:
        execute_update(
            'INSERT INTO enrollments (student_id, section_id) VALUES (?, ?)',
            (student_id, section_id)
        )
        return True
    except sqlite3.IntegrityError:
        return False

def get_enrollments_by_student(student_id):
    """Get all enrollments for a student"""
    return execute_query('SELECT * FROM enrollments WHERE student_id = ?', (student_id,))

def get_enrollments_by_section(section_id):
    """Get all enrollments for a section"""
    return execute_query('SELECT * FROM enrollments WHERE section_id = ?', (section_id,))

# Attendance operations
def mark_attendance(student_id, section_id, status='present', confidence=0.0):
    """Mark attendance for a student"""
    from datetime import date
    today = date.today()
    try:
        execute_update(
            '''INSERT INTO attendance (student_id, section_id, attendance_date, check_in_time, status, confidence)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (student_id, section_id, today, datetime.now(), status, confidence)
        )
        return True
    except sqlite3.IntegrityError:
        # Update existing record
        execute_update(
            '''UPDATE attendance SET check_in_time = ?, status = ?, confidence = ?
               WHERE student_id = ? AND section_id = ? AND attendance_date = ?''',
            (datetime.now(), status, confidence, student_id, section_id, today)
        )
        return True

def get_attendance_by_date(section_id, attendance_date):
    """Get attendance records for a section on a specific date"""
    return execute_query(
        'SELECT * FROM attendance WHERE section_id = ? AND attendance_date = ?',
        (section_id, attendance_date)
    )

def get_attendance_by_student(student_id):
    """Get all attendance records for a student"""
    return execute_query('SELECT * FROM attendance WHERE student_id = ?', (student_id,))

def get_attendance_stats(section_id):
    """Get attendance statistics for a section"""
    return execute_query(
        '''SELECT student_id, COUNT(*) as total_classes, 
           SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count
           FROM attendance WHERE section_id = ? GROUP BY student_id''',
        (section_id,)
    )

# Initialize database on import
init_db()
