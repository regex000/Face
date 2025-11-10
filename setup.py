#!/usr/bin/env python3
"""
Setup script for Face Attendance System
Initializes database and creates demo data
"""

import database as db
from datetime import datetime, timedelta
import random

def setup_demo_data():
    """Create demo data for testing"""
    
    print("🔧 Setting up Face Attendance System...")
    
    # Create admin user
    print("📝 Creating admin user...")
    db.create_user("admin", "admin123", "admin@attendance.local", "admin")
    
    # Create demo instructors
    print("👨‍🏫 Creating instructors...")
    instructors_data = [
        ("inst001", "Dr. John", "Smith", "john.smith@university.edu", "Computer Science"),
        ("inst002", "Prof. Sarah", "Johnson", "sarah.johnson@university.edu", "Mathematics"),
        ("inst003", "Dr. Mike", "Williams", "mike.williams@university.edu", "Physics"),
    ]
    
    instructor_ids = []
    for inst_id, first, last, email, dept in instructors_data:
        username = f"instructor_{inst_id}"
        if db.create_user(username, "password123", email, "instructor"):
            user = db.get_user(username)
            if db.create_instructor(user[0], inst_id, first, last, email, None, dept):
                instructor_ids.append(user[0])
                print(f"  ✓ Created {first} {last}")
    
    # Create demo courses
    print("📚 Creating courses...")
    courses_data = [
        ("CS101", "Introduction to Programming", "Learn Python basics", 3),
        ("CS201", "Data Structures", "Advanced programming concepts", 4),
        ("MATH101", "Calculus I", "Differential calculus", 4),
        ("PHYS101", "Physics I", "Mechanics and motion", 4),
    ]
    
    course_ids = []
    for i, (code, name, desc, credits) in enumerate(courses_data):
        if db.create_course(code, name, instructor_ids[i % len(instructor_ids)], desc, credits):
            course = db.get_course(code)
            course_ids.append(course[0])
            print(f"  ✓ Created {code}")
    
    # Create sections
    print("📍 Creating sections...")
    for course_id in course_ids:
        for section_num in ["A", "B"]:
            db.create_section(
                course_id,
                section_num,
                f"MWF 10:00-11:00" if section_num == "A" else "TTh 14:00-15:30",
                f"Room {100 + course_id + ord(section_num)}",
                50
            )
    
    # Create demo students
    print("👨‍🎓 Creating students...")
    students_data = [
        ("STU001", "Alice", "Brown", "alice.brown@student.edu", "555-0001"),
        ("STU002", "Bob", "Davis", "bob.davis@student.edu", "555-0002"),
        ("STU003", "Charlie", "Evans", "charlie.evans@student.edu", "555-0003"),
        ("STU004", "Diana", "Frank", "diana.frank@student.edu", "555-0004"),
        ("STU005", "Eve", "Garcia", "eve.garcia@student.edu", "555-0005"),
        ("STU006", "Frank", "Harris", "frank.harris@student.edu", "555-0006"),
        ("STU007", "Grace", "Jones", "grace.jones@student.edu", "555-0007"),
        ("STU008", "Henry", "King", "henry.king@student.edu", "555-0008"),
    ]
    
    student_ids = []
    for stu_id, first, last, email, phone in students_data:
        username = f"student_{stu_id}"
        if db.create_user(username, "password123", email, "student"):
            user = db.get_user(username)
            if db.create_student(user[0], stu_id, first, last, email, phone):
                student_ids.append(user[0])
                print(f"  ✓ Created {first} {last}")
    
    # Enroll students in courses
    print("📋 Enrolling students...")
    sections = db.get_all_sections()
    for section in sections:
        # Enroll 5-7 random students per section
        num_students = random.randint(5, 7)
        selected_students = random.sample(student_ids, min(num_students, len(student_ids)))
        
        for user_id in selected_students:
            student = db.get_student_by_user_id(user_id)
            if student:
                db.enroll_student(student[0], section[0])
    
    # Create sample attendance records
    print("✅ Creating sample attendance records...")
    today = datetime.now().date()
    
    for i in range(10):  # Last 10 days
        attendance_date = today - timedelta(days=i)
        
        for section in sections[:2]:  # Only for first 2 sections
            enrollments = db.get_enrollments_by_section(section[0])
            
            for enrollment in enrollments:
                try:
                    status = random.choice(['present', 'present', 'present', 'absent', 'late'])
                    confidence = random.uniform(0.85, 0.99) if status == 'present' else random.uniform(0.5, 0.8)
                    
                    db.mark_attendance(enrollment[1], section[0], status, confidence)
                except Exception as e:
                    # Skip duplicate attendance records
                    pass
    
    print("\n✨ Setup complete!")
    print("\n📋 Demo Credentials:")
    print("  Admin: admin / admin123")
    print("  Instructor: instructor_inst001 / password123")
    print("  Student: student_STU001 / password123")
    print("\n🚀 Run the app with: streamlit run app.py")

if __name__ == "__main__":
    setup_demo_data()
