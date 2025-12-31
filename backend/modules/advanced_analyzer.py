"""
Veritas-AI Advanced Detection Module
Additional deepfake detection techniques including lip-sync analysis,
breathing detection, and micro-expression analysis.
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from scipy.spatial.distance import euclidean
from scipy import signal


class AdvancedAnalyzer:
    """
    Advanced Detection Analyzer
    Implements additional detection techniques for more accurate deepfake detection.
    """
    
    def __init__(self):
        """Initialize advanced analyzer"""
        self.lip_landmarks = None
        self.face_cascade = None
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except:
            pass
    
    def analyze(self, frames: List[Dict]) -> Dict:
        """
        Run advanced analysis on video frames.
        
        Args:
            frames: List of dicts with 'data' (bytes) and 'timestamp' (optional)
        
        Returns:
            Dict with advanced analysis results
        """
        if len(frames) < 10:
            return {
                "available": False,
                "confidence": 0.5,
                "findings": ["Insufficient frames for advanced analysis"],
                "assessment": "Cannot perform advanced analysis"
            }
        
        try:
            # Decode frames
            decoded_frames = []
            for frame_data in frames:
                img = self._decode_frame(frame_data["data"])
                if img is not None:
                    decoded_frames.append(img)
            
            if len(decoded_frames) < 10:
                return {
                    "available": False,
                    "confidence": 0.5,
                    "findings": ["Could not decode enough frames"],
                    "assessment": "Frame decoding error"
                }
            
            findings = []
            scores = []
            
            # 1. Lip-sync analysis
            lip_sync_result = self._analyze_lip_sync(decoded_frames)
            if lip_sync_result:
                scores.append(lip_sync_result.get("score", 0.5))
                findings.extend(lip_sync_result.get("findings", []))
            
            # 2. Breathing detection
            breathing_result = self._analyze_breathing(decoded_frames)
            if breathing_result:
                scores.append(breathing_result.get("score", 0.5))
                findings.extend(breathing_result.get("findings", []))
            
            # 3. Micro-expression analysis
            micro_expr_result = self._analyze_micro_expressions(decoded_frames)
            if micro_expr_result:
                scores.append(micro_expr_result.get("score", 0.5))
                findings.extend(micro_expr_result.get("findings", []))
            
            # 4. Head movement analysis
            head_movement_result = self._analyze_head_movement(decoded_frames)
            if head_movement_result:
                scores.append(head_movement_result.get("score", 0.5))
                findings.extend(head_movement_result.get("findings", []))
            
            # Calculate overall score
            if scores:
                overall_score = np.mean(scores)
            else:
                overall_score = 0.5
            
            # Determine confidence and assessment
            if overall_score > 0.75:
                assessment = "Advanced analysis indicates authentic video"
                confidence = min(0.95, 0.6 + overall_score * 0.35)
            elif overall_score > 0.5:
                assessment = "Advanced analysis shows moderate authenticity"
                confidence = 0.5 + (overall_score - 0.5) * 0.5
            elif overall_score > 0.3:
                assessment = "Advanced analysis shows possible manipulation"
                confidence = 0.3 + (overall_score - 0.3) * 0.5
            else:
                assessment = "Advanced analysis indicates likely deepfake"
                confidence = max(0.1, overall_score * 0.5)
            
            return {
                "available": True,
                "advanced_score": round(overall_score, 3),
                "confidence": round(confidence, 3),
                "findings": findings,
                "assessment": assessment,
                "details": {
                    "lip_sync": lip_sync_result,
                    "breathing": breathing_result,
                    "micro_expressions": micro_expr_result,
                    "head_movement": head_movement_result,
                    "frames_analyzed": len(decoded_frames)
                }
            }
            
        except Exception as e:
            return {
                "available": True,
                "confidence": 0.3,
                "error": str(e)[:200],
                "findings": [f"Advanced analysis error: {str(e)[:100]}"],
                "assessment": "Error during advanced analysis"
            }
    
    def _decode_frame(self, frame_bytes: bytes) -> Optional[np.ndarray]:
        """Decode frame bytes to numpy array"""
        try:
            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return None
        except Exception:
            return None
    
    def _analyze_lip_sync(self, frames: List[np.ndarray]) -> Optional[Dict]:
        """Analyze lip movement and synchronization"""
        try:
            # Extract mouth region from each frame
            mouth_regions = []
            for frame in frames:
                mouth_region = self._extract_mouth_region(frame)
                if mouth_region is not None:
                    # Calculate mouth openness (simple: height/width ratio)
                    h, w = mouth_region.shape[:2]
                    if w > 0:
                        openness = h / w
                        mouth_regions.append(openness)
            
            if len(mouth_regions) < 5:
                return None
            
            # Analyze mouth movement patterns
            mouth_variance = np.var(mouth_regions)
            mouth_mean = np.mean(mouth_regions)
            
            # Real videos have natural mouth movement variation
            if 0.1 < mouth_variance < 0.5:
                score = 0.85
                findings = ["✅ Natural lip movement detected"]
            elif mouth_variance < 0.05:
                score = 0.3
                findings = ["❌ Static or unnatural lip movement"]
            elif mouth_variance > 1.0:
                score = 0.4
                findings = ["⚠️ Erratic lip movement (possible manipulation)"]
            else:
                score = 0.6
                findings = ["⚠️ Moderate lip movement"]
            
            return {
                "score": score,
                "variance": round(mouth_variance, 3),
                "findings": findings
            }
            
        except Exception:
            return None
    
    def _analyze_breathing(self, frames: List[np.ndarray]) -> Optional[Dict]:
        """Detect breathing patterns (subtle chest/neck movement)"""
        try:
            # Extract upper body region (chest/neck area)
            breathing_signals = []
            for frame in frames:
                breathing_region = self._extract_breathing_region(frame)
                if breathing_region is not None:
                    # Calculate average intensity (breathing causes subtle intensity changes)
                    mean_intensity = np.mean(breathing_region)
                    breathing_signals.append(mean_intensity)
            
            if len(breathing_signals) < 10:
                return None
            
            # Analyze breathing pattern (should have periodic variation)
            breathing_array = np.array(breathing_signals)
            
            # Apply FFT to detect breathing frequency (0.2-0.5 Hz = 12-30 breaths/min)
            fps = 30  # Assume 30 fps
            fft_result = np.fft.fft(breathing_array - np.mean(breathing_array))
            freqs = np.fft.fftfreq(len(breathing_array), 1/fps)
            
            # Look for breathing frequency
            breathing_mask = (freqs > 0.2) & (freqs < 0.5)
            breathing_power = np.abs(fft_result[breathing_mask])
            
            if len(breathing_power) > 0 and np.max(breathing_power) > np.mean(breathing_power) * 1.5:
                score = 0.8
                findings = ["✅ Natural breathing pattern detected"]
            else:
                score = 0.5
                findings = ["⚠️ Breathing pattern not clearly detected"]
            
            return {
                "score": score,
                "breathing_detected": len(breathing_power) > 0 and np.max(breathing_power) > np.mean(breathing_power) * 1.5,
                "findings": findings
            }
            
        except Exception:
            return None
    
    def _analyze_micro_expressions(self, frames: List[np.ndarray]) -> Optional[Dict]:
        """Analyze micro-expressions (subtle facial muscle movements)"""
        try:
            # Extract facial region and analyze texture changes
            face_textures = []
            for frame in frames:
                face_region = self._extract_face_region(frame)
                if face_region is not None:
                    # Calculate texture variance (micro-expressions cause texture changes)
                    gray = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY) if len(face_region.shape) == 3 else face_region
                    # Use Laplacian variance as texture measure
                    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                    texture_variance = laplacian.var()
                    face_textures.append(texture_variance)
            
            if len(face_textures) < 5:
                return None
            
            # Real faces have natural texture variation
            texture_variance = np.var(face_textures)
            texture_mean = np.mean(face_textures)
            
            # Moderate variation indicates natural micro-expressions
            if 50 < texture_variance < 500:
                score = 0.85
                findings = ["✅ Natural micro-expressions detected"]
            elif texture_variance < 20:
                score = 0.3
                findings = ["❌ Very static face (possible deepfake)"]
            else:
                score = 0.6
                findings = ["⚠️ Moderate facial texture variation"]
            
            return {
                "score": score,
                "texture_variance": round(texture_variance, 2),
                "findings": findings
            }
            
        except Exception:
            return None
    
    def _analyze_head_movement(self, frames: List[np.ndarray]) -> Optional[Dict]:
        """Analyze head movement patterns"""
        try:
            # Track head position across frames
            head_positions = []
            for frame in frames:
                face_region = self._extract_face_region(frame)
                if face_region is not None:
                    # Get center of face region
                    h, w = frame.shape[:2]
                    # Simple: use center of frame as approximation
                    center_x, center_y = w // 2, h // 2
                    head_positions.append([center_x, center_y])
            
            if len(head_positions) < 5:
                return None
            
            head_positions = np.array(head_positions)
            
            # Calculate head movement smoothness
            movements = []
            for i in range(len(head_positions) - 1):
                dist = euclidean(head_positions[i], head_positions[i + 1])
                movements.append(dist)
            
            if len(movements) == 0:
                return None
            
            movement_variance = np.var(movements)
            avg_movement = np.mean(movements)
            
            # Real head movement is smooth and gradual
            if 0 < avg_movement < 50 and movement_variance < 100:
                score = 0.85
                findings = ["✅ Natural, smooth head movement"]
            elif avg_movement == 0:
                score = 0.4
                findings = ["❌ No head movement (static deepfake)"]
            elif movement_variance > 500:
                score = 0.3
                findings = ["❌ Jerky or unnatural head movement"]
            else:
                score = 0.6
                findings = ["⚠️ Moderate head movement"]
            
            return {
                "score": score,
                "movement_variance": round(movement_variance, 2),
                "avg_movement": round(avg_movement, 2),
                "findings": findings
            }
            
        except Exception:
            return None
    
    def _extract_face_region(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Extract face region from frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if len(frame.shape) == 3 else frame
            
            if self.face_cascade is not None:
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    return frame[y:y+h, x:x+w]
            
            # Fallback: center region
            h, w = frame.shape[:2]
            return frame[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
        except Exception:
            return None
    
    def _extract_mouth_region(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Extract mouth region from face"""
        try:
            face_region = self._extract_face_region(frame)
            if face_region is None:
                return None
            
            # Mouth is typically in lower 1/3 of face
            h, w = face_region.shape[:2]
            mouth_y = int(h * 0.6)
            mouth_h = int(h * 0.4)
            return face_region[mouth_y:mouth_y+mouth_h, :]
        except Exception:
            return None
    
    def _extract_breathing_region(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Extract chest/neck region for breathing detection"""
        try:
            face_region = self._extract_face_region(frame)
            if face_region is None:
                return None
            
            # Breathing region is below face
            h, w = frame.shape[:2]
            # Assume face is in upper portion, breathing region is below
            breathing_y = int(h * 0.3)
            breathing_h = int(h * 0.2)
            return frame[breathing_y:breathing_y+breathing_h, int(w*0.3):int(w*0.7)]
        except Exception:
            return None

