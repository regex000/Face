#!/usr/bin/env python3
"""
Utility functions for Face Attendance System
"""

import sqlite3
import csv
from datetime import datetime, date, timedelta
from pathlib import Path
import json
import database as db

def export_attendance_to_csv(section_id, output_file=None):
    """Export attendance records to CSV"""
    if output_file is None:
        output_file = f"attendance_export_{date.today()}.csv"
    
    attendance_stats = db.get_attendance_stats(section_id)
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Student ID', 'Name', 'Total Classes', 'Present', 'Absent', 'Attendance Rate'])
        
        for stat in attendance_stats:
            student_id = stat[0]
            total = stat[1]
            present = stat[2]
            absent = total - present
            rate = (present / total * 100) if total > 0 else 0
            
            student = db.execute_query('SELECT * FROM students WHERE id = ?', (student_id,))
            if student:
                s = student[0]
                writer.writerow([s[2], f"{s[3]} {s[4]}", total, present, absent, f"{rate:.1f}%"])
    
    return output_file

def generate_attendance_report(section_id):
    """Generate detailed attendance report"""
    section = db.get_section(section_id)
    if not section:
        return None
    
    course = db.get_course(section[1])
    enrollments = db.get_enrollments_by_section(section_id)
    attendance_stats = db.get_attendance_stats(section_id)
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'course': {
            'code': course[0],
            'name': course[1],
            'credits': course[4]
        },
        'section': {
            'number': section[2],
            'schedule': section[3],
            'room': section[4],
            'capacity': section[5]
        },
        'statistics': {
            'total_students': len(enrollments),
            'total_classes': max([s[1] for s in attendance_stats]) if attendance_stats else 0,
            'average_attendance': sum([s[2]/s[1]*100 for s in attendance_stats if s[1] > 0]) / len(attendance_stats) if attendance_stats else 0
        },
        'student_records': []
    }
    
    for stat in attendance_stats:
        student_id = stat[0]
        total = stat[1]
        present = stat[2]
        
        student = db.execute_query('SELECT * FROM students WHERE id = ?', (student_id,))
        if student:
            s = student[0]
            report['student_records'].append({
                'student_id': s[2],
                'name': f"{s[3]} {s[4]}",
                'total_classes': total,
                'present': present,
                'absent': total - present,
                'attendance_rate': (present / total * 100) if total > 0 else 0
            })
    
    return report

def backup_database(backup_dir=None):
    """Backup database"""
    if backup_dir is None:
        backup_dir = Path("backups")
    
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(exist_ok=True)
    
    db_path = Path("attendance.db")
    if db_path.exists():
        backup_file = backup_dir / f"attendance_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy(db_path, backup_file)
        return str(backup_file)
    
    return None

def get_system_stats():
    """Get system statistics"""
    students = db.get_all_students()
    instructors = db.get_all_instructors()
    courses = db.get_all_courses()
    sections = db.get_all_sections()
    
    # Calculate total attendance records
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]
    conn.close()
    
    return {
        'total_students': len(students),
        'total_instructors': len(instructors),
        'total_courses': len(courses),
        'total_sections': len(sections),
        'total_attendance_records': total_attendance,
        'timestamp': datetime.now().isoformat()
    }

def get_course_statistics(course_id):
    """Get detailed course statistics"""
    course = db.get_course(course_id)
    if not course:
        return None
    
    sections = db.get_sections_by_course(course_id)
    
    stats = {
        'course': {
            'code': course[0],
            'name': course[1],
            'instructor_id': course[2],
            'credits': course[4]
        },
        'sections': []
    }
    
    for section in sections:
        enrollments = db.get_enrollments_by_section(section[0])
        attendance_stats = db.get_attendance_stats(section[0])
        
        avg_attendance = sum([s[2]/s[1]*100 for s in attendance_stats if s[1] > 0]) / len(attendance_stats) if attendance_stats else 0
        
        stats['sections'].append({
            'section_number': section[2],
            'schedule': section[3],
            'room': section[4],
            'capacity': section[5],
            'enrolled_students': len(enrollments),
            'average_attendance': avg_attendance
        })
    
    return stats

def get_student_statistics(student_id):
    """Get detailed student statistics"""
    student = db.execute_query('SELECT * FROM students WHERE id = ?', (student_id,))
    if not student:
        return None
    
    s = student[0]
    enrollments = db.get_enrollments_by_student(student_id)
    attendance_records = db.get_attendance_by_student(student_id)
    
    stats = {
        'student': {
            'id': s[2],
            'name': f"{s[3]} {s[4]}",
            'email': s[5],
            'phone': s[6]
        },
        'enrollment': {
            'total_courses': len(enrollments),
            'courses': []
        },
        'attendance': {
            'total_records': len(attendance_records),
            'present': sum(1 for r in attendance_records if r[7] == 'present'),
            'absent': sum(1 for r in attendance_records if r[7] == 'absent'),
            'late': sum(1 for r in attendance_records if r[7] == 'late'),
            'attendance_rate': (sum(1 for r in attendance_records if r[7] == 'present') / len(attendance_records) * 100) if attendance_records else 0
        }
    }
    
    for enrollment in enrollments:
        section = db.get_section(enrollment[2])
        if section:
            course = db.get_course(section[1])
            if course:
                stats['enrollment']['courses'].append({
                    'code': course[0],
                    'name': course[1],
                    'section': section[2],
                    'enrollment_date': enrollment[3]
                })
    
    return stats

def cleanup_old_records(days=90):
    """Delete attendance records older than specified days"""
    cutoff_date = date.today() - timedelta(days=days)
    
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE attendance_date < ?", (cutoff_date,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted

def export_all_data(output_dir=None):
    """Export all data to JSON"""
    if output_dir is None:
        output_dir = Path("exports")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Export students
    students = db.get_all_students()
    with open(output_dir / "students.json", 'w') as f:
        json.dump([{
            'id': s[0],
            'student_id': s[2],
            'name': f"{s[3]} {s[4]}",
            'email': s[5],
            'phone': s[6]
        } for s in students], f, indent=2)
    
    # Export instructors
    instructors = db.get_all_instructors()
    with open(output_dir / "instructors.json", 'w') as f:
        json.dump([{
            'id': i[0],
            'instructor_id': i[2],
            'name': f"{i[3]} {i[4]}",
            'email': i[5],
            'department': i[7]
        } for i in instructors], f, indent=2)
    
    # Export courses
    courses = db.get_all_courses()
    with open(output_dir / "courses.json", 'w') as f:
        json.dump([{
            'id': c[0],
            'code': c[1],
            'name': c[2],
            'credits': c[4]
        } for c in courses], f, indent=2)
    
    return str(output_dir)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "stats":
            print(json.dumps(get_system_stats(), indent=2))
        elif command == "backup":
            backup_file = backup_database()
            print(f"Database backed up to: {backup_file}")
        elif command == "export":
            export_dir = export_all_data()
            print(f"Data exported to: {export_dir}")
        elif command == "cleanup":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
            deleted = cleanup_old_records(days)
            print(f"Deleted {deleted} records older than {days} days")
        else:
            print("Usage: python utils.py [stats|backup|export|cleanup]")
    else:
        print("Face Attendance System Utilities")
        print("Usage: python utils.py [command]")
        print("\nCommands:")
        print("  stats    - Show system statistics")
        print("  backup   - Backup database")
        print("  export   - Export all data to JSON")
        print("  cleanup  - Delete old attendance records")
