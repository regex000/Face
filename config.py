"""
Configuration management for Face Attendance System
Loads settings from .env file with sensible defaults
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================== PROJECT PATHS ====================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ==================== DATABASE CONFIGURATION ====================
DATABASE_PATH = os.getenv('DATABASE_PATH', './data/attendance.db')
DATABASE_BACKUP_PATH = os.getenv('DATABASE_BACKUP_PATH', './data/backups')

# ==================== FACE RECOGNITION CONFIGURATION ====================
FACE_DETECTION_MODEL = os.getenv('FACE_DETECTION_MODEL', 'insightface')
FACE_CONFIDENCE_THRESHOLD = float(os.getenv('FACE_CONFIDENCE_THRESHOLD', '0.5'))
FACE_SIMILARITY_THRESHOLD = float(os.getenv('FACE_SIMILARITY_THRESHOLD', '0.6'))
FACE_ENCODINGS_DIR = './data/face_encodings'
FACE_IMAGES_DIR = './data/face_images'

# ==================== AI CONFIGURATION ====================
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_BASE_URL = 'https://api.openrouter.ai/api/v1'
AI_MODEL = os.getenv('AI_MODEL', 'mistralai/mistral-7b-instruct:free')
AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', '500'))
AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.7'))

# ==================== APPLICATION CONFIGURATION ====================
APP_DEBUG = os.getenv('APP_DEBUG', 'False').lower() == 'true'
APP_PORT = int(os.getenv('APP_PORT', '8502'))
APP_HOST = os.getenv('APP_HOST', 'localhost')
APP_TITLE = os.getenv('APP_TITLE', 'Face Attendance System')
APP_ICON = '👤'

# ==================== LOGGING CONFIGURATION ====================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')

# ==================== SECURITY CONFIGURATION ====================
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour
MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
LOCKOUT_DURATION = int(os.getenv('LOCKOUT_DURATION', '900'))  # 15 minutes

# ==================== ATTENDANCE CONFIGURATION ====================
ATTENDANCE_CONFIDENCE_MIN = float(os.getenv('ATTENDANCE_CONFIDENCE_MIN', '0.7'))
ATTENDANCE_LATE_THRESHOLD = int(os.getenv('ATTENDANCE_LATE_THRESHOLD', '15'))  # minutes
ATTENDANCE_RETENTION_DAYS = int(os.getenv('ATTENDANCE_RETENTION_DAYS', '365'))

# ==================== FEATURE FLAGS ====================
ENABLE_FACE_RECOGNITION = os.getenv('ENABLE_FACE_RECOGNITION', 'True').lower() == 'true'
ENABLE_AI_INSIGHTS = os.getenv('ENABLE_AI_INSIGHTS', 'True').lower() == 'true'
ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'False').lower() == 'true'
ENABLE_SMS_NOTIFICATIONS = os.getenv('ENABLE_SMS_NOTIFICATIONS', 'False').lower() == 'true'
DEMO_ENABLED = os.getenv('DEMO_ENABLED', 'True').lower() == 'true'

# ==================== STREAMLIT CONFIGURATION ====================
STREAMLIT_CONFIG = {
    'theme': {
        'primaryColor': '#667eea',
        'backgroundColor': '#ffffff',
        'secondaryBackgroundColor': '#f0f2f6',
        'textColor': '#262730',
        'font': 'sans serif'
    },
    'client': {
        'showErrorDetails': APP_DEBUG,
        'toolbarMode': 'developer' if APP_DEBUG else 'minimal'
    },
    'logger': {
        'level': LOG_LEVEL
    }
}

# ==================== FACE DETECTION MODELS ====================
AVAILABLE_MODELS = {
    'insightface': {
        'name': 'InsightFace (SCRFD)',
        'speed': 'Very Fast',
        'accuracy': 'High',
        'best_for': 'Real-time live camera',
        'requires': ['insightface', 'onnxruntime']
    },
    'mediapipe': {
        'name': 'MediaPipe',
        'speed': 'Fast',
        'accuracy': 'Medium-High',
        'best_for': 'Balanced performance',
        'requires': ['mediapipe']
    },
    'opencv': {
        'name': 'OpenCV Haar Cascade',
        'speed': 'Super Fast',
        'accuracy': 'Medium',
        'best_for': 'CPU laptops',
        'requires': ['opencv-python']
    }
}

# ==================== AI MODELS ====================
AVAILABLE_AI_MODELS = [
    'mistralai/mistral-7b-instruct:free',
    'meta-llama/llama-3.3-8b-instruct:free',
    'qwen/qwen3-4b:free',
    'google/gemma-3-4b-it:free',
    'deepseek/deepseek-chat-v3.1:free',
]

# ==================== DEMO CREDENTIALS ====================
DEMO_CREDENTIALS = {
    'admin': {
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin'
    },
    'instructor': {
        'username': 'instructor_inst001',
        'password': 'password123',
        'role': 'instructor'
    },
    'student': {
        'username': 'student_STU001',
        'password': 'password123',
        'role': 'student'
    }
}

# ==================== INITIALIZATION ====================
def initialize_directories():
    """Create all required directories"""
    directories = [
        DATA_DIR,
        LOGS_DIR,
        Path(DATABASE_BACKUP_PATH),
        Path(FACE_ENCODINGS_DIR),
        Path(FACE_IMAGES_DIR),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def validate_config():
    """Validate configuration and create necessary directories"""
    initialize_directories()
    
    errors = []
    
    # Validate database path
    db_dir = Path(DATABASE_PATH).parent
    if not db_dir.exists():
        try:
            db_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Failed to create database directory: {e}")
    
    # Validate AI configuration
    if ENABLE_AI_INSIGHTS and not OPENROUTER_API_KEY:
        errors.append("AI_INSIGHTS enabled but OPENROUTER_API_KEY not set in .env")
    
    return errors

# Validate configuration on import
_config_errors = validate_config()
if _config_errors:
    import warnings
    for error in _config_errors:
        warnings.warn(f"Config Warning: {error}")

# ==================== HELPER FUNCTIONS ====================
def get_model_info(model_name):
    """Get information about a face detection model"""
    return AVAILABLE_MODELS.get(model_name, {})

def is_model_available(model_name):
    """Check if a face detection model is available"""
    return model_name in AVAILABLE_MODELS

def get_all_models():
    """Get all available face detection models"""
    return AVAILABLE_MODELS

def get_config_summary():
    """Get a summary of current configuration"""
    return {
        'database': DATABASE_PATH,
        'face_model': FACE_DETECTION_MODEL,
        'ai_model': AI_MODEL,
        'debug': APP_DEBUG,
        'features': {
            'face_recognition': ENABLE_FACE_RECOGNITION,
            'ai_insights': ENABLE_AI_INSIGHTS,
            'email_notifications': ENABLE_EMAIL_NOTIFICATIONS,
            'sms_notifications': ENABLE_SMS_NOTIFICATIONS,
            'demo': DEMO_ENABLED
        }
    }

def get_paths_summary():
    """Get a summary of all important paths"""
    return {
        'project_root': str(PROJECT_ROOT),
        'data_dir': str(DATA_DIR),
        'logs_dir': str(LOGS_DIR),
        'database': DATABASE_PATH,
        'face_encodings': FACE_ENCODINGS_DIR,
        'face_images': FACE_IMAGES_DIR,
        'backups': DATABASE_BACKUP_PATH,
    }
