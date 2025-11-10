# 📁 Project Structure - Face Attendance System

## Directory Layout

```
face_/
│
├── 📄 Core Application Files
│   ├── app.py                      # Main Streamlit application (45KB)
│   ├── config.py                   # Configuration management
│   ├── database.py                 # SQLite database operations
│   ├── face_recognition_module.py  # Face detection & recognition engine
│   ├── ai_integration.py           # AI assistant integration
│   └── utils.py                    # Utility functions
│
├── 📦 Configuration & Dependencies
│   ├── .env                        # Environment variables (CONFIGURED)
│   ├── .env.example                # Example environment file
│   ├── requirements.txt            # Python dependencies
│   ├── requirements-minimal.txt    # Minimal dependencies
│   └── setup.py                    # Setup script
│
├── 📚 Documentation
│   ├── README.md                   # Main documentation
│   ├── SETUP.md                    # Setup & installation guide
│   ��── PROJECT_STRUCTURE.md        # This file
│
├── 📊 Data Directory (./data/)
│   ├── attendance.db               # SQLite database
│   ├── face_encodings/             # Face encoding files (.pkl)
│   │   ├── 1_encoding.pkl
│   │   ├── 11_encoding.pkl
│   │   └── ...
│   ├── face_images/                # Student face photos
│   │   ├── student_1.jpg
│   │   ├── student_11.jpg
│   │   └── ...
│   └── backups/                    # Database backups
│
├── 📝 Logs Directory (./logs/)
│   └── app.log                     # Application logs
│
├── 🔧 Git & Version Control
│   ├── .gitignore                  # Git ignore rules
│   └── .qodo/                      # Qodo AI configuration
│
└── 🐍 Python Cache
    └── __pycache__/                # Python bytecode cache
```

## File Descriptions

### Core Application Files

| File | Purpose | Size |
|------|---------|------|
| `app.py` | Main Streamlit UI with all portals | 45KB |
| `config.py` | Configuration management from .env | 7KB |
| `database.py` | SQLite database operations | 12KB |
| `face_recognition_module.py` | Face detection engine | 8KB |
| `ai_integration.py` | OpenRouter AI integration | 6KB |
| `utils.py` | Utility functions | 9KB |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | **ACTIVE** - Environment variables |
| `.env.example` | Template for .env file |
| `requirements.txt` | All Python dependencies |
| `setup.py` | Package setup configuration |

### Documentation

| File | Content |
|------|---------|
| `README.md` | Features, usage, troubleshooting |
| `SETUP.md` | Installation & configuration guide |
| `PROJECT_STRUCTURE.md` | This file - project organization |

### Data Storage

| Directory | Contents |
|-----------|----------|
| `data/attendance.db` | SQLite database with all records |
| `data/face_encodings/` | Face embedding files (pickle format) |
| `data/face_images/` | Student face photos (JPG) |
| `data/backups/` | Database backup files |
| `logs/app.log` | Application logs |

## Database Schema

### Tables

```
users
├── id (PK)
├── username (UNIQUE)
├── password
├── email (UNIQUE)
├── role (admin/instructor/student)
└── created_at

students
├── id (PK)
├── user_id (FK)
├── student_id (UNIQUE)
├── first_name
├── last_name
├── email (UNIQUE)
├── phone
├── face_image_path
└── created_at

instructors
├── id (PK)
├── user_id (FK)
├── instructor_id (UNIQUE)
├── first_name
├── last_name
├── email (UNIQUE)
├── phone
├── department
└── created_at

courses
├── id (PK)
├── course_code (UNIQUE)
├── course_name
├── description
├── instructor_id (FK)
├── credits
└── created_at

sections
├── id (PK)
├── course_id (FK)
├── section_number
├── schedule
├── room
├── capacity
└── created_at

enrollments
├── id (PK)
├── student_id (FK)
├── section_id (FK)
├── enrollment_date
├── status
└── UNIQUE(student_id, section_id)

attendance
├── id (PK)
├── student_id (FK)
├── section_id (FK)
├── attendance_date
├── check_in_time
├── check_out_time
├── status (present/absent/late)
├── confidence
├── face_match_id
├── created_at
└── UNIQUE(student_id, section_id, attendance_date)

face_encodings
├── id (PK)
├── student_id (FK)
├── encoding (BLOB)
└── encoding_date
```

## Configuration Files

### .env File Structure

```env
# API Keys
OPENROUTER_API_KEY=sk-or-v1-...

# Face Recognition
FACE_DETECTION_MODEL=insightface
FACE_CONFIDENCE_THRESHOLD=0.5
FACE_SIMILARITY_THRESHOLD=0.6

# Database
DATABASE_PATH=./data/attendance.db
DATABASE_BACKUP_PATH=./data/backups/

# Application
APP_DEBUG=False
APP_PORT=8502
APP_HOST=localhost

# AI
AI_MODEL=mistralai/mistral-7b-instruct:free
AI_MAX_TOKENS=500
AI_TEMPERATURE=0.7

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# Security
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900

# Features
ENABLE_FACE_RECOGNITION=True
ENABLE_AI_INSIGHTS=True
DEMO_ENABLED=True
```

## Dependencies

### Core Dependencies
- **streamlit** - Web UI framework
- **opencv-python** - Computer vision
- **insightface** - Face detection (primary)
- **mediapipe** - Face detection (fallback)
- **numpy** - Numerical computing
- **pandas** - Data analysis

### Database
- **sqlite3** - Database engine
- **sqlalchemy** - ORM

### Configuration
- **python-dotenv** - Environment variables

### Deep Learning
- **torch** - PyTorch
- **torchvision** - Vision models
- **onnxruntime** - ONNX runtime

See `requirements.txt` for complete list with versions.

## Key Features by File

### app.py
- 📷 Quick Attendance Kiosk (no login)
- 👨‍🎓 Student Portal
- 👨‍🏫 Instructor Portal
- 🔧 Admin Panel
- 🤖 AI Insights
- 📊 Attendance Tracking

### config.py
- Environment variable management
- Path configuration
- Feature flags
- Model selection
- Security settings

### database.py
- User management
- Student/Instructor operations
- Course management
- Enrollment tracking
- Attendance recording
- Statistics generation

### face_recognition_module.py
- Face detection (InsightFace/MediaPipe/OpenCV)
- Face encoding/embedding
- Face comparison
- Encoding persistence

### ai_integration.py
- OpenRouter API integration
- Student recommendations
- Attendance insights
- Personalized feedback

## Running the Application

```bash
# Start the app
streamlit run app.py

# Access at http://localhost:8502
```

## Customization

### Change Face Detection Model
Edit `.env`:
```env
FACE_DETECTION_MODEL=opencv  # or mediapipe
```

### Change Database Location
Edit `.env`:
```env
DATABASE_PATH=./data/attendance.db
```

### Enable/Disable Features
Edit `.env`:
```env
ENABLE_AI_INSIGHTS=False
ENABLE_FACE_RECOGNITION=True
```

## Backup & Recovery

### Backup Database
```bash
cp data/attendance.db data/backups/attendance_backup_$(date +%Y%m%d).db
```

### Restore Database
```bash
cp data/backups/attendance_backup_YYYYMMDD.db data/attendance.db
```

## Performance Considerations

### For Slow Computers
- Use OpenCV model instead of InsightFace
- Disable AI insights
- Reduce image quality

### For Better Accuracy
- Use InsightFace model
- Increase similarity threshold
- Ensure good lighting

## Security Notes

- Passwords stored in database (consider hashing in production)
- Role-based access control implemented
- Session timeout configurable
- Login attempt limiting available

## Version Information

- **Python:** 3.8+
- **Streamlit:** 1.28.1
- **OpenCV:** 4.8.1.78
- **InsightFace:** 0.7.3
- **Last Updated:** November 2024

---

**For setup instructions, see SETUP.md**  
**For usage guide, see README.md**
