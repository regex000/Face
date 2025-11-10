import requests
import json
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://api.openrouter.ai/api/v1"

# Fallback model (free tier)
FALLBACK_MODEL = "mistralai/mistral-7b-instruct:free"

# List of free models to try
FREE_MODELS = [
    "mistralai/mistral-7b-instruct:free",
    "meta-llama/llama-3.3-8b-instruct:free",
    "qwen/qwen3-4b:free",
    "google/gemma-3-4b-it:free",
]

class AIAssistant:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.model = FALLBACK_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://face-attendance-app.local",
            "X-Title": "Face Attendance System",
            "Content-Type": "application/json"
        }
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate response from AI model"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": max_tokens,
                "top_p": 0.9
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
            
            return self._get_fallback_response(prompt)
        
        except Exception as e:
            print(f"AI API Error: {e}")
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Get fallback response when API fails"""
        # Simple rule-based responses for common queries
        prompt_lower = prompt.lower()
        
        if "attendance" in prompt_lower:
            return "Attendance tracking is essential for academic success. Regular attendance helps students stay engaged with course material and improves learning outcomes."
        elif "face recognition" in prompt_lower:
            return "Face recognition technology uses advanced AI to identify individuals based on facial features. It's secure, fast, and improves attendance accuracy."
        elif "course" in prompt_lower:
            return "Courses are structured learning programs designed to teach specific subjects. Each course has instructors, sections, and enrolled students."
        elif "student" in prompt_lower:
            return "Students are individuals enrolled in courses. They attend classes, participate in activities, and are tracked for attendance."
        else:
            return "I'm here to help with your attendance and course management questions. Please ask about attendance, courses, students, or instructors."
    
    def analyze_attendance_pattern(self, attendance_data: Dict) -> str:
        """Analyze attendance patterns using AI"""
        prompt = f"""Analyze the following attendance data and provide insights:
        
Attendance Data:
- Total Classes: {attendance_data.get('total_classes', 0)}
- Present: {attendance_data.get('present_count', 0)}
- Absent: {attendance_data.get('total_classes', 0) - attendance_data.get('present_count', 0)}
- Attendance Rate: {attendance_data.get('attendance_rate', 0):.1f}%

Provide a brief analysis with recommendations."""
        
        return self.generate_response(prompt, max_tokens=300)
    
    def generate_attendance_report(self, section_data: Dict) -> str:
        """Generate attendance report summary"""
        prompt = f"""Generate a brief attendance report summary for:
        
Section: {section_data.get('section_name', 'Unknown')}
Course: {section_data.get('course_name', 'Unknown')}
Total Students: {section_data.get('total_students', 0)}
Average Attendance: {section_data.get('avg_attendance', 0):.1f}%

Provide actionable insights."""
        
        return self.generate_response(prompt, max_tokens=250)
    
    def get_student_recommendations(self, student_data: Dict) -> str:
        """Get AI recommendations for a student"""
        prompt = f"""Based on the following student data, provide personalized recommendations:
        
Student: {student_data.get('name', 'Unknown')}
Attendance Rate: {student_data.get('attendance_rate', 0):.1f}%
Enrolled Courses: {student_data.get('course_count', 0)}
Recent Absences: {student_data.get('recent_absences', 0)}

Provide 2-3 specific recommendations."""
        
        return self.generate_response(prompt, max_tokens=200)
    
    def generate_course_summary(self, course_data: Dict) -> str:
        """Generate course summary"""
        prompt = f"""Create a brief summary for the following course:
        
Course Code: {course_data.get('course_code', 'Unknown')}
Course Name: {course_data.get('course_name', 'Unknown')}
Instructor: {course_data.get('instructor_name', 'Unknown')}
Credits: {course_data.get('credits', 3)}
Sections: {course_data.get('section_count', 1)}

Provide a concise overview."""
        
        return self.generate_response(prompt, max_tokens=200)

# Global AI instance
_ai_assistant = None

def get_ai_assistant(api_key: Optional[str] = None) -> AIAssistant:
    """Get or create AI assistant instance"""
    global _ai_assistant
    if _ai_assistant is None:
        _ai_assistant = AIAssistant(api_key)
    return _ai_assistant

def generate_ai_insight(query: str) -> str:
    """Generate AI insight for a query"""
    assistant = get_ai_assistant()
    return assistant.generate_response(query)
