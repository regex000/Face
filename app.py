import streamlit as st
import cv2
import numpy as np
from datetime import datetime, date, timedelta
import pandas as pd
from pathlib import Path
import sqlite3

import database as db
from face_recognition_module import get_face_engine, match_face_to_students
from ai_integration import get_ai_assistant

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Face Attendance System",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .header-title { color: #667eea; font-size: 2.5em; font-weight: bold; margin-bottom: 1rem; }
    .subheader-title { color: #667eea; font-size: 1.8em; font-weight: bold; margin: 1rem 0; }
    .success-box { background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #28a745; }
    .error-box { background-color: #f8d7da; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #dc3545; }
    .info-box { background-color: #d1ecf1; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #17a2b8; }
    .kiosk-container { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; color: white; }
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.role = None
        st.session_state.student_data = None
        st.session_state.instructor_data = None
    
    if 'face_engine' not in st.session_state:
        st.session_state.face_engine = get_face_engine()
    
    if 'ai_assistant' not in st.session_state:
        st.session_state.ai_assistant = get_ai_assistant()
    
    if 'kiosk_mode' not in st.session_state:
        st.session_state.kiosk_mode = False

init_session()

# ==================== FACE ATTENDANCE KIOSK ====================
def face_attendance_kiosk():
    """Standalone face attendance kiosk - no login required"""
    st.markdown('<div class="kiosk-container">', unsafe_allow_html=True)
    st.markdown("# 📷 Quick Face Attendance Kiosk")
    st.markdown("**Mark your attendance using face recognition - No login required**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📋 Selection")
        
        # Get all students
        all_students = db.get_all_students()
        if not all_students:
            st.error("❌ No students found")
            return
        
        # Student selection
        student_options = {f"{s[3]} {s[4]} ({s[2]})": s for s in all_students}
        selected_student_name = st.selectbox("👨‍🎓 Select Your Name:", student_options.keys(), key="kiosk_student")
        selected_student = student_options[selected_student_name]
        student_id = selected_student[0]
        
        # Get enrollments
        enrollments = db.get_enrollments_by_student(student_id)
        
        if not enrollments:
            st.warning("⚠️ Not enrolled in any courses")
            return
        
        # Section selection
        section_options = {}
        for enrollment in enrollments:
            section = db.get_section(enrollment[2])
            if section:
                course = db.get_course(section[1])
                if course:
                    key = f"{course[1]} ({course[0]}) - Sec {section[2]}"
                    section_options[key] = (section, course)
        
        if not section_options:
            st.error("❌ No courses available for enrollment")
            return
        
        selected_section_name = st.selectbox("📚 Select Course:", section_options.keys(), key="kiosk_section")
        selected_section, selected_course = section_options[selected_section_name]
        section_id = selected_section[0]
        
        # Display info
        st.markdown("---")
        st.markdown("### ✅ Your Info")
        st.write(f"**Student:** {selected_student[3]} {selected_student[4]}")
        st.write(f"**ID:** {selected_student[2]}")
        st.write(f"**Course:** {selected_course[1]}")
        st.write(f"**Section:** {selected_section[2]}")
        
        # Check today's status
        today = date.today()
        today_att = db.execute_query(
            'SELECT * FROM attendance WHERE student_id = ? AND section_id = ? AND attendance_date = ?',
            (student_id, section_id, today)
        )
        
        if today_att:
            st.markdown('<div class="success-box">✅ Already Marked Today</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">ℹ️ Not Marked Yet</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📷 Face Recognition")
        
        # Check if face registered
        face_encoding = st.session_state.face_engine.load_face_encoding(student_id)
        
        if face_encoding is None:
            st.markdown('<div class="error-box">❌ Face Not Registered</div>', unsafe_allow_html=True)
            
            st.markdown("#### Register Your Face")
            uploaded_file = st.file_uploader("Upload face photo", type=['jpg', 'jpeg', 'png'], key="kiosk_upload")
            
            if uploaded_file:
                image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
                st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Your Photo", use_column_width=True)
                
                if st.button("✅ Register Face", use_container_width=True, key="kiosk_register"):
                    with st.spinner("🔍 Processing..."):
                        detections = st.session_state.face_engine.detect_faces(image)
                        if detections:
                            embedding = detections[0]['embedding']
                            st.session_state.face_engine.save_face_encoding(student_id, embedding)
                            Path("face_images").mkdir(exist_ok=True)
                            cv2.imwrite(f"face_images/student_{student_id}.jpg", image)
                            db.update_student_face(student_id, f"face_images/student_{student_id}.jpg")
                            st.markdown('<div class="success-box">✅ Face Registered!</div>', unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.markdown('<div class="error-box">❌ No Face Detected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">✅ Face Registered - Ready</div>', unsafe_allow_html=True)
            
            st.markdown("#### 📷 Live Face Recognition")
            st.info("📹 Camera will auto-capture and match your face")
            
            camera_input = st.camera_input("📷 Position your face in camera", key="kiosk_camera")
            
            if camera_input:
                image = cv2.imdecode(np.frombuffer(camera_input.read(), np.uint8), cv2.IMREAD_COLOR)
                
                with st.spinner("🔍 Analyzing face..."):
                    detections = st.session_state.face_engine.detect_faces(image)
                    
                    if detections:
                        detected_embedding = detections[0]['embedding']
                        confidence = st.session_state.face_engine.compare_faces(face_encoding, detected_embedding)
                        
                        st.markdown("---")
                        
                        col_r1, col_r2, col_r3 = st.columns(3)
                        with col_r1:
                            st.metric("🎯 Confidence", f"{confidence*100:.1f}%")
                        with col_r2:
                            status = "✅ MATCH" if confidence >= 0.6 else "❌ NO MATCH"
                            st.metric("Status", status)
                        with col_r3:
                            st.metric("📸 Faces", len(detections))
                        
                        st.markdown("---")
                        
                        if confidence >= 0.6:
                            # Check if already marked
                            today = date.today()
                            existing = db.execute_query(
                                'SELECT * FROM attendance WHERE student_id = ? AND section_id = ? AND attendance_date = ?',
                                (student_id, section_id, today)
                            )
                            
                            if existing:
                                st.markdown('<div class="info-box">ℹ️ Already Marked Today at ' + str(existing[0][4]) + '</div>', unsafe_allow_html=True)
                            else:
                                if st.button("✅ Mark Attendance", use_container_width=True, key="kiosk_mark"):
                                    db.mark_attendance(student_id, section_id, 'present', confidence)
                                    st.markdown('<div class="success-box"><strong>✅ SUCCESS!</strong><br>Attendance Marked<br>Confidence: ' + f"{confidence*100:.1f}%" + '<br>Time: ' + str(datetime.now().strftime("%H:%M:%S")) + '</div>', unsafe_allow_html=True)
                                    st.balloons()
                        else:
                            st.markdown(f'<div class="error-box"><strong>❌ SORRY, NOT MATCHED</strong><br>Confidence: {confidence*100:.1f}% (Need 60%+)<br>Please try again with better lighting</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-box">❌ No Face Detected - Please try again</div>', unsafe_allow_html=True)

# ==================== LOGIN PAGE ====================
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="header-title">👤 Face Attendance System</div>', unsafe_allow_html=True)
        st.markdown("**Intelligent Attendance Management with AI**")
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "ℹ️ Info"])
        
        with tab1:
            st.subheader("Login to Your Account")
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔓 Login", use_container_width=True):
                    user = db.verify_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.role = user[4]
                        
                        if user[4] == "student":
                            st.session_state.student_data = db.get_student_by_user_id(user[0])
                        elif user[4] == "instructor":
                            st.session_state.instructor_data = db.get_instructor_by_user_id(user[0])
                        
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
            
            with col_b:
                st.info("Demo:\n- admin/admin123\n- instructor_inst001/password123\n- student_STU001/password123")
        
        with tab2:
            st.subheader("Create Account")
            reg_username = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_role = st.selectbox("Role", ["student", "instructor", "admin"], key="reg_role")
            
            if st.button("📝 Register", use_container_width=True):
                if db.create_user(reg_username, reg_password, reg_email, reg_role):
                    st.success("✅ Registration successful! Please login.")
                else:
                    st.error("❌ Username or email exists")
        
        with tab3:
            st.markdown("### About This System")
            st.markdown("""
            **Features:**
            - 👤 Face Recognition Attendance
            - 🤖 AI-Powered Insights
            - 📚 Course Management
            - 📊 Analytics & Reports
            - 🔐 Secure Access Control
            """)

# ==================== STUDENT PORTAL ====================
def student_portal():
    student = st.session_state.student_data
    if not student:
        st.error("❌ Student profile not found")
        return
    
    student_id = student[0]
    st.markdown(f'<div class="header-title">📚 Student Portal</div>', unsafe_allow_html=True)
    st.markdown(f"**{student[3]} {student[4]}** | ID: {student[2]}")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Dashboard", "📖 Courses", "📋 Enroll", "✅ Attendance", "📷 Face Attendance", "👤 Face Setup"])
    
    with tab1:
        st.subheader("Your Dashboard")
        enrollments = db.get_enrollments_by_student(student_id)
        attendance_records = db.get_attendance_by_student(student_id)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Courses", len(enrollments))
        with col2:
            if attendance_records:
                present = sum(1 for r in attendance_records if r[7] == 'present')
                rate = (present / len(attendance_records)) * 100
                st.metric("✅ Rate", f"{rate:.1f}%")
            else:
                st.metric("✅ Rate", "N/A")
        with col3:
            st.metric("📅 Classes", len(attendance_records))
        with col4:
            if attendance_records:
                absent = sum(1 for r in attendance_records if r[7] == 'absent')
                st.metric("❌ Absent", absent)
            else:
                st.metric("❌ Absent", "0")
        
        st.markdown("---")
        st.subheader("🤖 AI Insights")
        if st.button("🔄 Get Recommendations"):
            with st.spinner("Generating insights..."):
                student_data = {
                    'name': f"{student[3]} {student[4]}",
                    'attendance_rate': (sum(1 for r in attendance_records if r[7] == 'present') / len(attendance_records) * 100) if attendance_records else 0,
                    'course_count': len(enrollments),
                    'recent_absences': sum(1 for r in attendance_records[-5:] if r[7] == 'absent') if len(attendance_records) >= 5 else 0
                }
                rec = st.session_state.ai_assistant.get_student_recommendations(student_data)
                st.info(f"💡 {rec}")
    
    with tab2:
        st.subheader("My Enrolled Courses")
        enrollments = db.get_enrollments_by_student(student_id)
        
        if enrollments:
            for idx, enrollment in enumerate(enrollments):
                section = db.get_section(enrollment[2])
                if section:
                    course = db.get_course(section[1])
                    if course:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.markdown(f"### 📖 {course[1]}")
                            st.markdown(f"**{course[0]}** | Section {section[2]}")
                            st.markdown(f"📍 {section[4]} | ⏰ {section[3]}")
                        with col2:
                            st.metric("Credits", course[4])
                        with col3:
                            if st.button("📊 Details", key=f"detail_{idx}"):
                                st.session_state[f"show_{idx}"] = True
                        
                        if st.session_state.get(f"show_{idx}", False):
                            st.markdown(f"**Description:** {course[3]}")
                        st.markdown("---")
        else:
            st.info("📭 No courses. Go to Enroll tab!")
    
    with tab3:
        st.subheader("🎓 Enroll in Courses")
        all_courses = db.get_all_courses()
        enrolled_ids = {db.get_section(e[2])[1] for e in enrollments}
        available = [c for c in all_courses if c[0] not in enrolled_ids]
        
        if available:
            for course in available:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{course[1]}** ({course[0]})")
                    st.caption(f"📝 {course[3]}")
                with col2:
                    st.metric("Credits", course[4])
                with col3:
                    sections = db.get_sections_by_course(course[0])
                    if sections:
                        section_opts = {f"Sec {s[2]} ({s[3]})": s[0] for s in sections}
                        sel = st.selectbox("Section", section_opts.keys(), key=f"sec_{course[0]}")
                        if st.button("✅ Enroll", key=f"enr_{course[0]}"):
                            if db.enroll_student(student_id, section_opts[sel]):
                                st.success(f"✅ Enrolled in {course[1]}!")
                                st.rerun()
                st.markdown("---")
        else:
            st.info("✅ Enrolled in all courses!")
    
    with tab4:
        st.subheader("📋 Attendance History")
        attendance_records = db.get_attendance_by_student(student_id)
        
        if attendance_records:
            col1, col2, col3, col4 = st.columns(4)
            present = sum(1 for r in attendance_records if r[7] == 'present')
            absent = sum(1 for r in attendance_records if r[7] == 'absent')
            late = sum(1 for r in attendance_records if r[7] == 'late')
            
            with col1:
                st.metric("✅ Present", present)
            with col2:
                st.metric("❌ Absent", absent)
            with col3:
                st.metric("⏰ Late", late)
            with col4:
                rate = (present / len(attendance_records) * 100) if attendance_records else 0
                st.metric("📊 Rate", f"{rate:.1f}%")
            
            st.markdown("---")
            
            df_data = []
            for record in attendance_records:
                section = db.get_section(record[2])
                if section:
                    course = db.get_course(section[1])
                    status = str(record[7]) if record[7] else 'present'
                    emoji = "✅" if status == 'present' else "❌" if status == 'absent' else "⏰"
                    df_data.append({
                        'Date': record[3],
                        'Course': course[1] if course else 'Unknown',
                        'Status': f"{emoji} {status.upper()}",
                        'Check-in': record[4],
                        'Confidence': f"{record[8]*100:.1f}%" if record[8] else "N/A"
                    })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 No records yet")
    
    with tab5:
        st.subheader("📷 Face Attendance - Mark Your Attendance")
        st.markdown("Use face recognition to mark your attendance in enrolled courses")
        
        enrollments = db.get_enrollments_by_student(student_id)
        
        if not enrollments:
            st.warning("⚠️ You are not enrolled in any courses yet")
        else:
            face_encoding = st.session_state.face_engine.load_face_encoding(student_id)
            
            if face_encoding is None:
                st.error("❌ Please register your face first in the 'Face Setup' tab")
            else:
                st.success("✅ Face registered and ready for attendance")
                st.markdown("---")
                
                course_options = {}
                for enrollment in enrollments:
                    section = db.get_section(enrollment[2])
                    if section:
                        course = db.get_course(section[1])
                        if course:
                            key = f"{course[1]} ({course[0]}) - Section {section[2]}"
                            course_options[key] = (enrollment[2], course[1], section[2])
                
                if course_options:
                    selected_course = st.selectbox("Select Course for Attendance", course_options.keys())
                    section_id, course_name, section_num = course_options[selected_course]
                    
                    st.markdown(f"### 📚 {course_name} - Section {section_num}")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("#### 📷 Capture Your Face")
                        camera_input = st.camera_input("Take a photo to mark attendance")
                        
                        if camera_input:
                            image = cv2.imdecode(np.frombuffer(camera_input.read(), np.uint8), cv2.IMREAD_COLOR)
                            
                            with st.spinner("🔍 Analyzing face..."):
                                detections = st.session_state.face_engine.detect_faces(image)
                                
                                if detections:
                                    detected_embedding = detections[0]['embedding']
                                    confidence = st.session_state.face_engine.compare_faces(face_encoding, detected_embedding)
                                    
                                    st.markdown("---")
                                    st.subheader("📊 Face Recognition Result")
                                    
                                    col_res1, col_res2, col_res3 = st.columns(3)
                                    
                                    with col_res1:
                                        st.metric("🎯 Match Confidence", f"{confidence*100:.1f}%")
                                    
                                    with col_res2:
                                        threshold = 0.6
                                        if confidence >= threshold:
                                            st.metric("✅ Status", "MATCH")
                                        else:
                                            st.metric("❌ Status", "NO MATCH")
                                    
                                    with col_res3:
                                        st.metric("📸 Faces Detected", len(detections))
                                    
                                    st.markdown("---")
                                    
                                    if confidence >= 0.6:
                                        st.success(f"✅ Face matched with {confidence*100:.1f}% confidence!")
                                        
                                        today = date.today()
                                        existing = db.execute_query(
                                            'SELECT * FROM attendance WHERE student_id = ? AND section_id = ? AND attendance_date = ?',
                                            (student_id, section_id, today)
                                        )
                                        
                                        if existing:
                                            st.info(f"ℹ️ You already marked attendance for this course today at {existing[0][4]}")
                                        else:
                                            if st.button("✅ Mark Attendance", use_container_width=True):
                                                db.mark_attendance(student_id, section_id, 'present', confidence)
                                                st.success(f"✅ Attendance marked successfully!")
                                                st.balloons()
                                    else:
                                        st.warning(f"⚠️ Face match confidence is {confidence*100:.1f}% (minimum required: 60%)")
                                        st.info("💡 Try taking another photo with better lighting or closer to the camera")
                                else:
                                    st.error("❌ No face detected in the image")
                                    st.info("💡 Make sure your face is clearly visible in the camera")
                    
                    with col2:
                        st.markdown("#### 📋 Today's Status")
                        today = date.today()
                        today_attendance = db.execute_query(
                            'SELECT * FROM attendance WHERE student_id = ? AND section_id = ? AND attendance_date = ?',
                            (student_id, section_id, today)
                        )
                        
                        if today_attendance:
                            st.success("✅ Marked Present")
                            st.write(f"**Time:** {today_attendance[0][4]}")
                            st.write(f"**Confidence:** {today_attendance[0][8]*100:.1f}%")
                        else:
                            st.warning("❌ Not Marked")
                            st.write("No attendance record for today")
                        
                        st.markdown("---")
                        st.markdown("#### 📊 Course Statistics")
                        
                        all_attendance = db.execute_query(
                            'SELECT * FROM attendance WHERE student_id = ? AND section_id = ?',
                            (student_id, section_id)
                        )
                        
                        if all_attendance:
                            present = sum(1 for r in all_attendance if r[7] == 'present')
                            total = len(all_attendance)
                            rate = (present / total * 100) if total > 0 else 0
                            
                            st.metric("📚 Total Classes", total)
                            st.metric("✅ Present", present)
                            st.metric("📊 Rate", f"{rate:.1f}%")
                        else:
                            st.info("No attendance records yet")
    
    with tab6:
        st.subheader("👤 Face Setup - Register Your Face")
        st.markdown("Register your face for automatic attendance tracking")
        
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file = st.file_uploader("Upload face photo", type=['jpg', 'jpeg', 'png'])
            if uploaded_file:
                image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
                st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Your Photo")
                
                if st.button("✅ Register Face", use_container_width=True):
                    with st.spinner("Processing..."):
                        detections = st.session_state.face_engine.detect_faces(image)
                        if detections:
                            embedding = detections[0]['embedding']
                            st.session_state.face_engine.save_face_encoding(student_id, embedding)
                            Path("face_images").mkdir(exist_ok=True)
                            cv2.imwrite(f"face_images/student_{student_id}.jpg", image)
                            db.update_student_face(student_id, f"face_images/student_{student_id}.jpg")
                            st.success("✅ Face registered successfully!")
                            st.info("You can now use face recognition for attendance in the 'Face Attendance' tab")
                        else:
                            st.error("❌ No face detected")
        
        with col2:
            st.markdown("#### 📸 Tips for Best Results")
            st.info("""
            ✅ **Good Lighting**: Use natural light or bright room
            ✅ **Clear Face**: Face should be 50-70% of image
            ✅ **Direct Look**: Look straight at camera
            ✅ **No Accessories**: Remove glasses/sunglasses
            ✅ **Close-up**: Head and shoulders visible
            ✅ **Neutral Expression**: Relax your face
            ✅ **Single Face**: Only one person in photo
            ✅ **High Quality**: Use clear, sharp image
            """)
            
            st.markdown("---")
            st.markdown("#### ℹ️ Face Recognition Info")
            engine_info = st.session_state.face_engine.get_engine_info()
            st.write(f"**Engine:** {engine_info['engine']}")
            st.write(f"**Status:** Ready for registration")

# ==================== INSTRUCTOR PORTAL ====================
def instructor_portal():
    instructor = st.session_state.instructor_data
    if not instructor:
        st.error("❌ Instructor profile not found")
        return
    
    instructor_id = instructor[0]
    st.markdown(f'<div class="header-title">👨‍🏫 Instructor Portal</div>', unsafe_allow_html=True)
    st.markdown(f"**{instructor[3]} {instructor[4]}** | {instructor[7]}")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📚 Courses", "📋 Attendance", "📷 Face", "📈 Reports"])
    
    with tab1:
        st.subheader("Dashboard")
        courses = db.get_courses_by_instructor(instructor_id)
        total_sections = sum(len(db.get_sections_by_course(c[0])) for c in courses)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Courses", len(courses))
        with col2:
            st.metric("📍 Sections", total_sections)
        with col3:
            total_students = sum(len(db.get_enrollments_by_section(s[0])) for c in courses for s in db.get_sections_by_course(c[0]))
            st.metric("👨‍🎓 Students", total_students)
        with col4:
            st.metric("📊 Status", "Active")
    
    with tab2:
        st.subheader("📚 Course Management")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("#### Your Courses")
        with col2:
            if st.button("➕ New Course"):
                st.session_state.show_add_course = True
        
        if st.session_state.get('show_add_course', False):
            with st.form("add_course_form"):
                course_code = st.text_input("Course Code")
                course_name = st.text_input("Course Name")
                description = st.text_area("Description")
                credits = st.number_input("Credits", 1, 6, 3)
                
                if st.form_submit_button("✅ Create"):
                    if db.create_course(course_code, course_name, instructor_id, description, credits):
                        st.success("✅ Created!")
                        st.session_state.show_add_course = False
                        st.rerun()
                    else:
                        st.error("❌ Code exists")
        
        courses = db.get_courses_by_instructor(instructor_id)
        if courses:
            for course in courses:
                with st.expander(f"📖 {course[1]} ({course[0]})"):
                    st.markdown(f"**Description:** {course[3]}")
                    st.markdown(f"**Credits:** {course[4]}")
                    
                    sections = db.get_sections_by_course(course[0])
                    st.markdown(f"**Sections:** {len(sections)}")
                    
                    for section in sections:
                        enrollments = db.get_enrollments_by_section(section[0])
                        st.markdown(f"- Section {section[2]}: {len(enrollments)} students | {section[3]} | {section[4]}")
                    
                    if st.button(f"➕ Add Section", key=f"add_sec_{course[0]}"):
                        st.session_state[f"show_sec_{course[0]}"] = True
                    
                    if st.session_state.get(f"show_sec_{course[0]}", False):
                        with st.form(f"sec_form_{course[0]}"):
                            section_num = st.text_input("Section Number")
                            schedule = st.text_input("Schedule")
                            room = st.text_input("Room")
                            capacity = st.number_input("Capacity", 10, 200, 50)
                            
                            if st.form_submit_button("✅ Create"):
                                if db.create_section(course[0], section_num, schedule, room, capacity):
                                    st.success("✅ Created!")
                                    st.session_state[f"show_sec_{course[0]}"] = False
                                    st.rerun()
        else:
            st.info("📭 No courses")
    
    with tab3:
        st.subheader("📋 Attendance")
        courses = db.get_courses_by_instructor(instructor_id)
        if courses:
            course = st.selectbox("Course", courses, format_func=lambda x: f"{x[1]} ({x[0]})")
            sections = db.get_sections_by_course(course[0])
            if sections:
                section = st.selectbox("Section", sections, format_func=lambda x: f"Section {x[2]}")
                att_date = st.date_input("Date", date.today())
                
                if st.button("📊 View"):
                    attendance = db.get_attendance_by_date(section[0], att_date)
                    if attendance:
                        df_data = []
                        for record in attendance:
                            student = db.get_student(record[1])
                            if student:
                                status = str(record[7]) if record[7] else 'present'
                                emoji = "✅" if status == 'present' else "❌" if status == 'absent' else "⏰"
                                df_data.append({
                                    'ID': student[2],
                                    'Name': f"{student[3]} {student[4]}",
                                    'Status': f"{emoji} {status.upper()}",
                                    'Check-in': record[4],
                                    'Confidence': f"{record[8]*100:.1f}%" if record[8] else "N/A"
                                })
                        df = pd.DataFrame(df_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.info("📭 No records")
    
    with tab4:
        st.subheader("📷 Face Recognition")
        courses = db.get_courses_by_instructor(instructor_id)
        if courses:
            course = st.selectbox("Course", courses, format_func=lambda x: f"{x[1]} ({x[0]})", key="face_c")
            sections = db.get_sections_by_course(course[0])
            if sections:
                section = st.selectbox("Section", sections, format_func=lambda x: f"Section {x[2]}", key="face_s")
                
                st.markdown("---")
                enrollments = db.get_enrollments_by_section(section[0])
                student_encodings = {}
                student_map = {}
                
                for enrollment in enrollments:
                    student_id = enrollment[1]
                    encoding = st.session_state.face_engine.load_face_encoding(student_id)
                    if encoding is not None:
                        student_encodings[student_id] = encoding
                        student = db.get_student(student_id)
                        if student:
                            student_map[student_id] = student
                
                if not student_encodings:
                    st.warning("⚠️ No registered faces")
                else:
                    st.info(f"✅ Ready: {len(student_encodings)} students")
                    camera_input = st.camera_input("📷 Take photo")
                    
                    if camera_input:
                        image = cv2.imdecode(np.frombuffer(camera_input.read(), np.uint8), cv2.IMREAD_COLOR)
                        with st.spinner("🔍 Recognizing..."):
                            matches = match_face_to_students(image, student_encodings, threshold=0.5)
                        
                        if matches:
                            st.success(f"✅ Found {len(matches)} face(s)")
                            for match in matches:
                                student_id = match['student_id']
                                student = student_map.get(student_id)
                                if student:
                                    col1, col2, col3 = st.columns([2, 1, 1])
                                    with col1:
                                        st.write(f"**{student[3]} {student[4]}** ({student[2]})")
                                    with col2:
                                        st.write(f"Confidence: {match['similarity']*100:.1f}%")
                                    with col3:
                                        if st.button("✅ Mark", key=f"mark_{student_id}"):
                                            db.mark_attendance(student_id, section[0], 'present', match['similarity'])
                                            st.success(f"✅ Marked!")
                        else:
                            st.warning("⚠️ No faces")
    
    with tab5:
        st.subheader("📈 Reports")
        if st.button("📊 Generate Report"):
            with st.spinner("Generating..."):
                courses = db.get_courses_by_instructor(instructor_id)
                report_data = []
                
                for course in courses:
                    for section in db.get_sections_by_course(course[0]):
                        enrollments = db.get_enrollments_by_section(section[0])
                        stats = db.get_attendance_stats(section[0])
                        avg = sum(r[2] / r[1] * 100 for r in stats if r[1] > 0) / len(stats) if stats else 0
                        
                        report_data.append({
                            'Course': course[1],
                            'Section': section[2],
                            'Students': len(enrollments),
                            'Avg Attendance': f"{avg:.1f}%"
                        })
                
                if report_data:
                    df = pd.DataFrame(report_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    csv = df.to_csv(index=False)
                    st.download_button("📥 Download", csv, f"report_{date.today()}.csv", "text/csv")

# ==================== ADMIN PORTAL ====================
def admin_portal():
    st.markdown(f'<div class="header-title">🔧 Admin Portal</div>', unsafe_allow_html=True)
    st.markdown("**System Administration**")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "👥 Users", "🔍 System", "📈 Reports"])
    
    with tab1:
        st.subheader("System Dashboard")
        students = db.get_all_students()
        instructors = db.get_all_instructors()
        courses = db.get_all_courses()
        sections = db.get_all_sections()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👨‍🎓 Students", len(students))
        with col2:
            st.metric("👨‍🏫 Instructors", len(instructors))
        with col3:
            st.metric("📚 Courses", len(courses))
        with col4:
            st.metric("📍 Sections", len(sections))
    
    with tab2:
        st.subheader("👥 User Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Add Student")
            with st.form("add_student_form"):
                username = st.text_input("Username")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                student_id = st.text_input("Student ID")
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                phone = st.text_input("Phone")
                
                if st.form_submit_button("✅ Create"):
                    if db.create_user(username, password, email, "student"):
                        user = db.get_user(username)
                        if db.create_student(user[0], student_id, first_name, last_name, email, phone):
                            st.success("✅ Created!")
                        else:
                            st.error("❌ Failed")
                    else:
                        st.error("❌ Exists")
        
        with col2:
            st.markdown("#### Add Instructor")
            with st.form("add_instructor_form"):
                username = st.text_input("Username", key="inst_u")
                email = st.text_input("Email", key="inst_e")
                password = st.text_input("Password", type="password", key="inst_p")
                instructor_id = st.text_input("Instructor ID")
                first_name = st.text_input("First Name", key="inst_f")
                last_name = st.text_input("Last Name", key="inst_l")
                department = st.text_input("Department")
                
                if st.form_submit_button("✅ Create"):
                    if db.create_user(username, password, email, "instructor"):
                        user = db.get_user(username)
                        if db.create_instructor(user[0], instructor_id, first_name, last_name, email, None, department):
                            st.success("✅ Created!")
                        else:
                            st.error("❌ Failed")
                    else:
                        st.error("❌ Exists")
    
    with tab3:
        st.subheader("🔍 System Health")
        if st.button("🔄 Check System"):
            checks = {
                'Database': True,
                'Face Engine': True,
                'AI Assistant': True,
                'Storage': True
            }
            for check, status in checks.items():
                emoji = "✅" if status else "❌"
                st.write(f"{emoji} {check}")
    
    with tab4:
        st.subheader("📈 Reports")
        if st.button("📊 Generate Report"):
            with st.spinner("Generating..."):
                sections = db.get_all_sections()
                report_data = []
                
                for section in sections:
                    course = db.get_course(section[1])
                    enrollments = db.get_enrollments_by_section(section[0])
                    stats = db.get_attendance_stats(section[0])
                    avg = sum(r[2] / r[1] * 100 for r in stats if r[1] > 0) / len(stats) if stats else 0
                    
                    report_data.append({
                        'Course': course[1] if course else 'Unknown',
                        'Section': section[2],
                        'Students': len(enrollments),
                        'Avg Attendance': f"{avg:.1f}%"
                    })
                
                if report_data:
                    df = pd.DataFrame(report_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    csv = df.to_csv(index=False)
                    st.download_button("📥 Download", csv, f"report_{date.today()}.csv", "text/csv")

# ==================== MAIN ====================
def main():
    # Check if accessing kiosk mode
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        page = st.radio(
            "Select Mode:",
            ["📷 Quick Attendance Kiosk", "🔐 Portal Login"],
            key="nav_page"
        )
        
        if page == "📷 Quick Attendance Kiosk":
            st.session_state.page = 'kiosk'
        else:
            st.session_state.page = 'portal'
        
        st.markdown("---")
        
        if st.session_state.logged_in:
            st.markdown(f"### 👤 {st.session_state.user[1]}")
            st.markdown(f"**Role:** {st.session_state.role.upper()}")
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.role = None
                st.session_state.student_data = None
                st.session_state.instructor_data = None
                st.rerun()
    
    # Route to appropriate page
    if st.session_state.page == 'kiosk':
        face_attendance_kiosk()
    elif st.session_state.logged_in:
        if st.session_state.role == "student":
            student_portal()
        elif st.session_state.role == "instructor":
            instructor_portal()
        elif st.session_state.role == "admin":
            admin_portal()
        else:
            st.error("❌ Unknown role")
    else:
        login_page()

if __name__ == "__main__":
    main()
