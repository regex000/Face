# Use wrapper to handle headless environment
from cv2_wrapper import cv2
import numpy as np
from pathlib import Path
import pickle
import os
from datetime import datetime
from config import FACE_ENCODINGS_DIR

# Try to import InsightFace (SCRFD - best for real-time)
try:
    import insightface
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

# Fallback to MediaPipe (not available on Python 3.13+)
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except (ImportError, RuntimeError):
    # MediaPipe not available (common on Python 3.13+)
    MEDIAPIPE_AVAILABLE = False
    mp = None

# Create face encodings directory
Path(FACE_ENCODINGS_DIR).mkdir(parents=True, exist_ok=True)

class FaceRecognitionEngine:
    def __init__(self, use_insightface=True):
        self.use_insightface = use_insightface and INSIGHTFACE_AVAILABLE
        self.use_mediapipe = MEDIAPIPE_AVAILABLE
        
        if self.use_insightface:
            try:
                # Use SCRFD for real-time detection
                self.detector = insightface.app.FaceAnalysis(
                    name='buffalo_l',
                    providers=['CPUProvider']
                )
                self.detector.prepare(ctx_id=-1, det_size=(640, 480))
                self.engine_type = "InsightFace (SCRFD)"
            except Exception as e:
                print(f"InsightFace initialization failed: {e}")
                self.use_insightface = False
                self._init_mediapipe()
        elif self.use_mediapipe:
            self._init_mediapipe()
        else:
            self._init_opencv()
    
    def _init_mediapipe(self):
        """Initialize MediaPipe face detection"""
        if mp is None or not MEDIAPIPE_AVAILABLE:
            self._init_opencv()
            return
        
        try:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1,
                min_detection_confidence=0.5
            )
            self.engine_type = "MediaPipe"
        except Exception as e:
            print(f"MediaPipe initialization failed: {e}")
            self._init_opencv()
    
    def _init_opencv(self):
        """Initialize OpenCV Haar Cascade"""
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.engine_type = "OpenCV Haar Cascade"
    
    def detect_faces(self, image):
        """Detect faces in image and return bounding boxes and encodings"""
        if self.use_insightface:
            return self._detect_insightface(image)
        elif self.use_mediapipe:
            return self._detect_mediapipe(image)
        else:
            return self._detect_opencv(image)
    
    def _detect_insightface(self, image):
        """Detect faces using InsightFace"""
        try:
            faces = self.detector.get(image)
            detections = []
            for face in faces:
                bbox = face.bbox.astype(int)
                embedding = face.embedding
                confidence = face.det_score
                detections.append({
                    'bbox': bbox,
                    'embedding': embedding,
                    'confidence': confidence,
                    'landmarks': face.kps if hasattr(face, 'kps') else None
                })
            return detections
        except Exception as e:
            print(f"InsightFace detection error: {e}")
            return []
    
    def _detect_mediapipe(self, image):
        """Detect faces using MediaPipe"""
        try:
            h, w, c = image.shape
            results = self.face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            detections = []
            
            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    x_min = int(bbox.xmin * w)
                    y_min = int(bbox.ymin * h)
                    width = int(bbox.width * w)
                    height = int(bbox.height * h)
                    
                    # Extract face region for encoding
                    face_region = image[y_min:y_min+height, x_min:x_min+width]
                    embedding = self._get_simple_embedding(face_region)
                    
                    detections.append({
                        'bbox': np.array([x_min, y_min, x_min+width, y_min+height]),
                        'embedding': embedding,
                        'confidence': detection.score[0],
                        'landmarks': None
                    })
            return detections
        except Exception as e:
            print(f"MediaPipe detection error: {e}")
            return []
    
    def _detect_opencv(self, image):
        """Detect faces using OpenCV Haar Cascade"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            detections = []
            
            for (x, y, w, h) in faces:
                face_region = image[y:y+h, x:x+w]
                embedding = self._get_simple_embedding(face_region)
                
                detections.append({
                    'bbox': np.array([x, y, x+w, y+h]),
                    'embedding': embedding,
                    'confidence': 0.8,
                    'landmarks': None
                })
            return detections
        except Exception as e:
            print(f"OpenCV detection error: {e}")
            return []
    
    def _get_simple_embedding(self, face_image):
        """Generate a simple embedding from face image"""
        # Resize to standard size
        face_resized = cv2.resize(face_image, (128, 128))
        # Normalize
        face_normalized = face_resized.astype(np.float32) / 255.0
        # Flatten and return as embedding
        embedding = face_normalized.flatten()
        return embedding
    
    def compare_faces(self, embedding1, embedding2, threshold=0.6):
        """Compare two face embeddings"""
        if embedding1 is None or embedding2 is None:
            return 0.0
        
        # Normalize embeddings
        emb1 = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        emb2 = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
        
        # Calculate cosine similarity
        similarity = np.dot(emb1, emb2)
        return float(similarity)
    
    def save_face_encoding(self, student_id, embedding):
        """Save face encoding to file"""
        encoding_path = Path(FACE_ENCODINGS_DIR) / f"{student_id}_encoding.pkl"
        with open(encoding_path, 'wb') as f:
            pickle.dump(embedding, f)
        return str(encoding_path)
    
    def load_face_encoding(self, student_id):
        """Load face encoding from file"""
        encoding_path = Path(FACE_ENCODINGS_DIR) / f"{student_id}_encoding.pkl"
        if encoding_path.exists():
            with open(encoding_path, 'rb') as f:
                return pickle.load(f)
        return None
    
    def get_engine_info(self):
        """Get information about the current engine"""
        return {
            'engine': self.engine_type,
            'insightface_available': INSIGHTFACE_AVAILABLE,
            'mediapipe_available': MEDIAPIPE_AVAILABLE
        }

# Global instance
_face_engine = None

def get_face_engine():
    """Get or create face recognition engine"""
    global _face_engine
    if _face_engine is None:
        _face_engine = FaceRecognitionEngine()
    return _face_engine

def detect_and_encode_face(image_path):
    """Detect and encode face from image file"""
    engine = get_face_engine()
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    detections = engine.detect_faces(image)
    if detections:
        return detections[0]['embedding']
    return None

def match_face_to_students(image, student_encodings, threshold=0.5):
    """Match detected face to student encodings"""
    engine = get_face_engine()
    detections = engine.detect_faces(image)
    
    if not detections:
        return []
    
    matches = []
    for detection in detections:
        face_embedding = detection['embedding']
        best_match = None
        best_similarity = 0
        
        for student_id, student_embedding in student_encodings.items():
            similarity = engine.compare_faces(face_embedding, student_embedding, threshold)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = student_id
        
        if best_similarity >= threshold:
            matches.append({
                'student_id': best_match,
                'similarity': best_similarity,
                'bbox': detection['bbox'],
                'confidence': detection['confidence']
            })
    
    return matches
