# 🚀 Setup Guide - Face Attendance System

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 2GB+ free disk space
- Webcam (for face recognition features)

## Installation Steps

### 1. Install Python Dependencies

```bash
cd /Users/rokon/Desktop/face_
pip install -r requirements.txt
```

**Note:** This may take 5-10 minutes as it downloads ML models.

### 2. Environment Configuration

The `.env` file is already created with default settings. You can customize it:

```bash
# View current configuration
cat .env

# Edit if needed (optional)
nano .env
```

### 3. Verify Installation

```bash
# Test imports
python -c "
import streamlit
import cv2
import insightface
import database
print('✓ All dependencies installed successfully!')
"
```

### 4. Run the Application

```bash
streamlit run app.py
```

The app will start at: `http://localhost:8502`

## Configuration Options

### Face Recognition Model

Edit `.env` to change the face detection model:

```env
# Recommended for real-time (requires GPU or good CPU)
FACE_DETECTION_MODEL=insightface

# Alternative: Balanced performance
FACE_DETECTION_MODEL=mediapipe

# Alternative: Fastest (CPU-friendly)
FACE_DETECTION_MODEL=opencv
```

### AI Integration

To enable AI insights, add your OpenRouter API key:

1. Get API key from https://openrouter.ai
2. Edit `.env`:
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
ENABLE_AI_INSIGHTS=True
```

### Application Settings

```env
# Debug mode (shows detailed errors)
APP_DEBUG=False

# Port (change if 8502 is in use)
APP_PORT=8502

# Logging level
LOG_LEVEL=INFO
```

## First Time Setup

### 1. Start the Application
```bash
streamlit run app.py
```

### 2. Login with Demo Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Student Account:**
- Username: `student_STU001`
- Password: `password123`

**Instructor Account:**
- Username: `instructor_inst001`
- Password: `password123`

### 3. Register Your Face (Optional)

1. Go to Student Portal → Face Setup
2. Upload a clear photo of your face
3. Click "Register Face"
4. Use face recognition for attendance

### 4. Test Quick Kiosk

1. Select "📷 Quick Attendance Kiosk" from sidebar
2. Select a student and course
3. Register face or take photo
4. Mark attendance

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
pip install streamlit==1.28.1
```

### Issue: "No module named 'insightface'"

**Solution:**
```bash
pip install insightface onnxruntime
```

### Issue: "Camera not working"

**Solution:**
- Check camera permissions in system settings
- Try different face detection model in `.env`
- Restart the application

### Issue: "Database locked"

**Solution:**
```bash
# Remove old database
rm data/attendance.db

# Restart application
streamlit run app.py
```

### Issue: Port 8502 already in use

**Solution:**
Edit `.env`:
```env
APP_PORT=8503  # Use different port
```

Then run:
```bash
streamlit run app.py --server.port 8503
```

## Project Structure

```
face_/
├── app.py                      # Main application
├── config.py                   # Configuration
├── database.py                 # Database operations
├── face_recognition_module.py  # Face detection
├── ai_integration.py           # AI features
├── utils.py                    # Utilities
├── requirements.txt            # Dependencies
├── .env                        # Configuration file
├── README.md                   # Documentation
├── SETUP.md                    # This file
│
├── data/                       # Data directory
│   ├── attendance.db           # Database
│   ├── face_encodings/         # Face data
│   ├── face_images/            # Photos
│   └── backups/                # Backups
│
└── logs/                       # Logs
    └── app.log                 # Application log
```

## Next Steps

1. **Explore the UI** - Familiarize yourself with all features
2. **Add Users** - Create student and instructor accounts
3. **Create Courses** - Set up courses and sections
4. **Enroll Students** - Add students to courses
5. **Test Face Recognition** - Register faces and test attendance

## Performance Tips

### For Slow Computers

1. Use OpenCV model instead of InsightFace:
```env
FACE_DETECTION_MODEL=opencv
```

2. Disable AI insights:
```env
ENABLE_AI_INSIGHTS=False
```

3. Reduce image quality in camera input

### For Better Accuracy

1. Use InsightFace model:
```env
FACE_DETECTION_MODEL=insightface
```

2. Increase similarity threshold:
```env
FACE_SIMILARITY_THRESHOLD=0.7
```

3. Ensure good lighting when registering faces

## Updating the System

To update dependencies:

```bash
pip install --upgrade -r requirements.txt
```

## Backup and Recovery

### Backup Database

```bash
cp data/attendance.db data/backups/attendance_backup_$(date +%Y%m%d).db
```

### Restore Database

```bash
cp data/backups/attendance_backup_YYYYMMDD.db data/attendance.db
```

## Support

For issues:
1. Check logs: `tail -f logs/app.log`
2. Review `.env` configuration
3. Verify all dependencies are installed
4. Check internet connection (for AI features)

---

**Happy using Face Attendance System! 👤**
