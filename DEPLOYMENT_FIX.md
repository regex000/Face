# Deployment Fix - Python 3.13 Compatibility

## Problem
The Streamlit deployment was failing with the following error:
```
ERROR: Could not find a version that satisfies the requirement mediapipe>=0.10.0
ERROR: No matching distribution found for mediapipe>=0.10.0
```

The deployment environment uses Python 3.13.9, but `mediapipe` and `insightface` don't have wheels compatible with Python 3.13.

## Root Cause
- `mediapipe` requires Python < 3.13 (last compatible version is for Python 3.12)
- `insightface` depends on `mediapipe`, making it incompatible with Python 3.13
- The requirements.txt was attempting to install these packages unconditionally

## Solution Implemented

### 1. Updated `requirements.txt`
- **Removed** the hard requirement for `insightface>=0.7.3` and `mediapipe>=0.10.0`
- Added comments explaining that these packages require Python < 3.13
- The app now uses OpenCV's Haar Cascade as the fallback face detection engine

### 2. Enhanced `face_recognition_module.py`
- Added better error handling for MediaPipe import failures
- Added `RuntimeError` to the exception handling for MediaPipe imports
- Updated `_init_mediapipe()` to gracefully fall back to OpenCV if MediaPipe is unavailable
- Set `mp = None` when MediaPipe import fails to prevent AttributeErrors

## Face Recognition Engine Hierarchy
The app now uses a three-tier fallback system:

1. **InsightFace (SCRFD)** - Best accuracy, requires Python < 3.13
   - Status: Optional, only used if available
   
2. **MediaPipe** - Good accuracy, requires Python < 3.13
   - Status: Optional, only used if available
   
3. **OpenCV Haar Cascade** - Reliable fallback, works on all Python versions
   - Status: Always available, used on Python 3.13+

## Deployment Status
✅ **Fixed** - The app will now deploy successfully on Python 3.13.9 using OpenCV Haar Cascade for face detection.

## Local Development (Optional Enhancement)
For local development on Python < 3.13, you can uncomment the optional dependencies in `requirements.txt`:
```bash
pip install insightface>=0.7.3 mediapipe>=0.10.0
```

This will enable the more accurate face recognition engines while maintaining compatibility with Python 3.13+ deployments.

## Testing
The app has been tested to ensure:
- ✅ Imports work without mediapipe/insightface
- ✅ Face detection works with OpenCV Haar Cascade
- ✅ Face encoding and comparison functions work correctly
- ✅ All Streamlit features remain functional
