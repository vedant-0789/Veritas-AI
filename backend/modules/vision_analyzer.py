"""
Veritas-AI Vision-Guard Module - Google Cloud Vision API Analysis
Uses Google Cloud Vision API to detect faces, emotions, and image properties
for additional authenticity verification.
"""

import os
from typing import List, Dict, Optional
import io

try:
    from google.cloud import vision
    from PIL import Image
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    print("Warning: google-cloud-vision not available. Vision API analysis will be disabled.")


class VisionAnalyzer:
    """
    Vision-Guard Module using Google Cloud Vision API
    Provides additional face detection and image quality analysis.
    """
    
    def __init__(self):
        """Initialize Vision API client"""
        self.client = None
        
        if VISION_AVAILABLE:
            try:
                # Try to initialize with credentials
                # Will use GOOGLE_APPLICATION_CREDENTIALS env var or default credentials
                self.client = vision.ImageAnnotatorClient()
                print("Google Cloud Vision API initialized successfully")
            except Exception as e:
                print(f"Vision API initialization failed: {e}")
                print("   Note: Vision API is optional. Set GOOGLE_APPLICATION_CREDENTIALS for full features.")
        else:
            print("Vision API SDK not installed (optional feature)")
    
    def analyze(self, frames: List[Dict]) -> Dict:
        """
        Analyze frames using Google Cloud Vision API.
        
        Args:
            frames: List of dicts with 'data' (bytes) and 'timestamp' (optional)
        
        Returns:
            Dict with vision-based analysis results
        """
        if not self.client:
            return {
                "available": False,
                "confidence": 0.5,
                "findings": ["Vision API not available"],
                "assessment": "Vision API not configured (optional feature)"
            }
        
        try:
            # Analyze first frame in detail (most representative)
            if not frames or len(frames) == 0:
                return {
                    "available": True,
                    "confidence": 0.0,
                    "findings": ["No frames provided"],
                    "assessment": "No frames to analyze"
                }
            
            frame_bytes = frames[0]["data"]
            image = vision.Image(content=frame_bytes)
            
            findings = []
            face_confidence = 0.0
            faces_detected = 0
            has_natural_features = False
            
            # Face detection with landmarks
            try:
                face_response = self.client.face_detection(image=image)
                faces = face_response.face_annotations
                
                if faces and len(faces) > 0:
                    faces_detected = len(faces)
                    face = faces[0]  # Analyze primary face
                    face_confidence = face.detection_confidence
                    
                    # Check for natural emotional expressions
                    if face.joy_likelihood > 2 or face.sorrow_likelihood > 2 or \
                       face.anger_likelihood > 2 or face.surprise_likelihood > 2:
                        has_natural_features = True
                        findings.append("Natural emotional expressions detected")
                    
                    # Check face quality
                    if face.detection_confidence > 0.8:
                        findings.append("High-quality face detection")
                    
                    # Check for natural landmarks
                    if face.landmarks:
                        findings.append(f"Facial landmarks detected ({len(face.landmarks)} points)")
                
            except Exception as e:
                findings.append(f"Face detection error: {str(e)[:100]}")
            
            # Image properties (compression, quality)
            try:
                properties_response = self.client.image_properties(image=image)
                
                if properties_response.image_properties_annotation:
                    colors = properties_response.image_properties_annotation.dominant_colors
                    if colors and len(colors.colors) > 10:
                        findings.append("Natural color distribution detected")
                        has_natural_features = True
            except Exception as e:
                # Image properties is optional
                pass
            
            # Safe search (for inappropriate content - not directly related but good to check)
            try:
                safe_response = self.client.safe_search_detection(image=image)
                # We don't use this for deepfake detection, but it's good to have
            except Exception:
                pass
            
            # Calculate confidence based on findings
            confidence = 0.5  # Neutral
            if face_confidence > 0.8:
                confidence = 0.7
            if has_natural_features:
                confidence = min(1.0, confidence + 0.2)
            if faces_detected == 0:
                confidence = 0.3  # Lower if no face detected
            
            assessment = "Vision API analysis complete"
            if faces_detected > 0 and face_confidence > 0.8:
                assessment = "High-quality face detected with natural features"
            elif faces_detected == 0:
                assessment = "No face detected in frame"
            
            return {
                "available": True,
                "faces_detected": faces_detected,
                "face_confidence": round(face_confidence, 3),
                "confidence": round(confidence, 3),
                "findings": findings,
                "has_natural_features": has_natural_features,
                "assessment": assessment,
                "details": {
                    "service": "google-cloud-vision",
                    "frames_analyzed": 1
                }
            }
            
        except Exception as e:
            return {
                "available": True,
                "confidence": 0.3,
                "error": str(e)[:200],
                "findings": [f"Vision API error: {str(e)[:100]}"],
                "assessment": "Error during Vision API analysis"
            }
    
    def test_connection(self) -> bool:
        """Test if Vision API is working"""
        if not self.client:
            return False
        
        try:
            # Create a simple test image
            from PIL import Image
            import io
            
            # Create a 1x1 pixel test image
            img = Image.new('RGB', (1, 1), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            image = vision.Image(content=img_bytes.read())
            # Just try to get image properties (lightweight test)
            self.client.image_properties(image=image)
            return True
        except Exception:
            return False








