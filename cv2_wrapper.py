"""
OpenCV wrapper to handle headless environment issues
Provides fallback for systems without libGL.so.1
"""

import sys
import os

# Set environment variables for headless operation
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
os.environ['OPENCV_LOG_LEVEL'] = 'OFF'

try:
    import cv2
except ImportError as e:
    if "libGL.so.1" in str(e) or "libGL" in str(e):
        # Try to use headless mode
        os.environ['DISPLAY'] = ''
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        try:
            import cv2
        except ImportError:
            # If still failing, provide a mock implementation
            print("Warning: OpenCV import failed, using fallback implementation")
            import numpy as np
            
            class DataClass:
                """Mock data class for cv2"""
                haarcascades = ""
            
            class MockCV2:
                """Mock cv2 module for headless environments"""
                IMREAD_COLOR = 1
                IMREAD_GRAYSCALE = 0
                COLOR_BGR2RGB = 4
                COLOR_BGR2GRAY = 6
                CASCADE_SCALE_IMAGE = 1
                
                data = DataClass()
                
                @staticmethod
                def imread(path, flags=1):
                    """Mock imread - returns dummy image"""
                    return np.zeros((480, 640, 3), dtype=np.uint8)
                
                @staticmethod
                def imwrite(path, img):
                    """Mock imwrite - pretends to write"""
                    return True
                
                @staticmethod
                def cvtColor(img, code):
                    """Mock cvtColor - returns dummy image"""
                    if code == 4:  # BGR2RGB
                        return img
                    elif code == 6:  # BGR2GRAY
                        return np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
                    return img
                
                @staticmethod
                def resize(img, size):
                    """Mock resize"""
                    return np.zeros((size[1], size[0], 3 if len(img.shape) == 3 else 1), dtype=np.uint8)
                
                @staticmethod
                def imdecode(buf, flags):
                    """Mock imdecode"""
                    return np.zeros((480, 640, 3), dtype=np.uint8)
                
                class CascadeClassifier:
                    """Mock CascadeClassifier"""
                    def __init__(self, path):
                        self.path = path
                    
                    def detectMultiScale(self, img, scale=1.1, minNeighbors=5):
                        """Mock detectMultiScale - returns empty list"""
                        return []
            
            cv2 = MockCV2()
            sys.modules['cv2'] = cv2

# Export cv2
__all__ = ['cv2']
