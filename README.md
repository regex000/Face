# 👤 Face Attendance System

A modern, intelligent attendance management system using face recognition and AI-powered insights.

## ✨ Features

- **📷 Face Recognition Attendance** - Mark attendance using face recognition
- **🎯 Quick Kiosk Mode** - No login required, instant attendance marking
- **🤖 AI-Powered Insights** - Get personalized recommendations and analytics
- **📊 Comprehensive Dashboard** - View attendance statistics and reports
- **👨‍🎓 Student Portal** - Manage courses and view attendance history
- **👨‍🏫 Instructor Portal** - Manage courses and track student attendance
- **🔧 Admin Panel** - System administration and user management
- **🔐 Secure Authentication** - Role-based access control

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. **Clone or download the project**
```bash
cd /Users/rokon/Desktop/face_
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Copy .env file (already created)
# Edit .env if needed for custom settings
```

4. **Run the application**
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8502`

## 📁 Project Structure

```
face_/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration management
├── database.py                 # Database operations
├── face_recognition_module.py  # Face detection & recognition
├── ai_integration.py           # AI assistant integration
├── utils.py                    # Utility functions
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── .gitignore                  # Git ignore rules
│
├── data/                       # Data directory
│   ├── attendance.db           # SQLite database
│   ├── face_encodings/         # Face encoding files
│   ├── face_images/            # Student face images
│   └── backups/                # Database backups
│
└── logs/                       # Application logs
    └── app.log                 # Log file
```

## 🔐 Demo Credentials

### Admin
- **Username:** admin
- **Password:** admin123

### Instructor
- **Username:** instructor_inst001
- **Password:** password123

### Student
- **Username:** student_STU001
- **Password:** password123

## ⚙️ Configuration

Edit `.env` file to customize settings:

```env
# Face Recognition
FACE_DETECTION_MODEL=insightface  # Options: insightface, mediapipe, opencv
FACE_SIMILARITY_THRESHOLD=0.6

# AI Configuration
OPENROUTER_API_KEY=your_api_key_here
AI_MODEL=mistralai/mistral-7b-instruct:free

# Application
APP_DEBUG=False
APP_PORT=8502

# Features
ENABLE_FACE_RECOGNITION=True
ENABLE_AI_INSIGHTS=True
```

## 🎯 Usage

### Quick Attendance Kiosk (No Login)
1. Select "📷 Quick Attendance Kiosk" from sidebar
2. Select your name and course
3. Register your face (first time only)
4. Take a photo to mark attendance

### Student Portal
1. Login with student credentials
2. View enrolled courses
3. Check attendance history
4. Use face recognition to mark attendance

### Instructor Portal
1. Login with instructor credentials
2. Manage courses and sections
3. View student attendance
4. Generate reports

### Admin Panel
1. Login with admin credentials
2. Manage users and courses
3. View system statistics
4. Generate system reports

## 🔧 Face Recognition Models

The system supports three face detection models:

| Model | Speed | Accuracy | Best For |
|-------|-------|----------|----------|
| **InsightFace** | Very Fast | High | Real-time camera |
| **MediaPipe** | Fast | Medium-High | Balanced |
| **OpenCV** | Super Fast | Medium | CPU laptops |

Change model in `.env`:
```env
FACE_DETECTION_MODEL=insightface
```

## 🤖 AI Integration

The system uses OpenRouter API for AI insights. Get your API key from [openrouter.ai](https://openrouter.ai)

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
AI_MODEL=mistralai/mistral-7b-instruct:free
```

## 📊 Database

SQLite database with the following tables:
- **users** - User accounts
- **students** - Student information
- **instructors** - Instructor information
- **courses** - Course details
- **sections** - Course sections
- **enrollments** - Student enrollments
- **attendance** - Attendance records
- **face_encodings** - Face encoding cache

## 🛠️ Development

### Project Structure
- `app.py` - Main Streamlit UI
- `config.py` - Configuration management
- `database.py` - Database operations
- `face_recognition_module.py` - Face detection engine
- `ai_integration.py` - AI assistant
- `utils.py` - Utility functions

### Adding New Features
1. Update `config.py` for new settings
2. Add database operations to `database.py`
3. Update UI in `app.py`
4. Test thoroughly

## 📝 Logging

Logs are stored in `logs/app.log`. Configure logging level in `.env`:

```env
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🔒 Security

- Passwords stored in database (consider hashing in production)
- Role-based access control
- Session timeout configuration
- Login attempt limiting

## 🐛 Troubleshooting

### Face Recognition Not Working
- Check camera permissions
- Ensure good lighting
- Try different face detection model in `.env`
- Verify face is registered

### Database Issues
- Check `data/` directory exists
- Verify database file permissions
- Check logs for errors

### AI Insights Not Working
- Verify `OPENROUTER_API_KEY` in `.env`
- Check internet connection
- Verify API key is valid

## 📦 Dependencies

Key dependencies:
- **streamlit** - Web UI framework
- **opencv-python** - Computer vision
- **insightface** - Face detection
- **mediapipe** - Alternative face detection
- **sqlite3** - Database
- **numpy** - Numerical computing
- **pandas** - Data analysis

See `requirements.txt` for complete list.

## 📄 License

This project is provided as-is for educational purposes.

## 🤝 Support

For issues or questions, check the logs and configuration settings.

---

**Version:** 1.0.0  
**Last Updated:** November 2024
