"""
Veritas-AI Temporal Consistency Analyzer
Analyzes frame-to-frame consistency to detect deepfake artifacts.
Deepfakes often have temporal inconsistencies that real videos don't.
"""

import cv2
import numpy as np
from typing import List, Dict, Optional
from scipy.spatial.distance import cosine
from scipy.stats import pearsonr


class TemporalAnalyzer:
    """
    Temporal Consistency Analyzer
    Detects frame-to-frame inconsistencies that indicate deepfake manipulation.
    """
    
    def __init__(self):
        """Initialize temporal analyzer"""
        self.face_cascade = None
        try:
            # Try to load OpenCV face cascade (fallback if MediaPipe fails)
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except:
            pass
    
    def analyze(self, frames: List[Dict]) -> Dict:
        """
        Analyze temporal consistency across frames.
        
        Args:
            frames: List of dicts with 'data' (bytes) and 'timestamp' (optional)
        
        Returns:
            Dict with temporal analysis results
        """
        if len(frames) < 5:
            return {
                "available": False,
                "confidence": 0.5,
                "temporal_consistency": 0.5,
                "findings": ["Insufficient frames for temporal analysis"],
                "assessment": "Cannot analyze temporal consistency"
            }
        
        try:
            # Decode frames
            decoded_frames = []
            for frame_data in frames:
                img = self._decode_frame(frame_data["data"])
                if img is not None:
                    decoded_frames.append(img)
            
            if len(decoded_frames) < 5:
                return {
                    "available": False,
                    "confidence": 0.5,
                    "temporal_consistency": 0.5,
                    "findings": ["Could not decode frames"],
                    "assessment": "Frame decoding error"
                }
            
            # Calculate temporal metrics
            consistency_score, findings = self._analyze_temporal_consistency(decoded_frames)
            
            # Calculate motion smoothness
            motion_score, motion_findings = self._analyze_motion_smoothness(decoded_frames)
            
            # Calculate color consistency
            color_score, color_findings = self._analyze_color_consistency(decoded_frames)
            
            # Combine scores
            overall_score = (consistency_score * 0.4 + motion_score * 0.3 + color_score * 0.3)
            
            # Determine confidence and assessment
            all_findings = findings + motion_findings + color_findings
            
            if overall_score > 0.75:
                assessment = "High temporal consistency - indicates authentic video"
                confidence = min(0.95, 0.6 + overall_score * 0.35)
            elif overall_score > 0.5:
                assessment = "Moderate temporal consistency"
                confidence = 0.5 + (overall_score - 0.5) * 0.5
            elif overall_score > 0.3:
                assessment = "Low temporal consistency - possible manipulation"
                confidence = 0.3 + (overall_score - 0.3) * 0.5
            else:
                assessment = "Very low temporal consistency - likely deepfake"
                confidence = max(0.1, overall_score * 0.5)
            
            return {
                "available": True,
                "temporal_consistency": round(overall_score, 3),
                "consistency_score": round(consistency_score, 3),
                "motion_score": round(motion_score, 3),
                "color_score": round(color_score, 3),
                "confidence": round(confidence, 3),
                "findings": all_findings,
                "assessment": assessment,
                "details": {
                    "frames_analyzed": len(decoded_frames),
                    "method": "temporal_consistency_analysis"
                }
            }
            
        except Exception as e:
            return {
                "available": True,
                "confidence": 0.3,
                "temporal_consistency": 0.3,
                "error": str(e)[:200],
                "findings": [f"Temporal analysis error: {str(e)[:100]}"],
                "assessment": "Error during temporal analysis"
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
    
    def _analyze_temporal_consistency(self, frames: List[np.ndarray]) -> tuple:
        """Analyze frame-to-frame consistency"""
        findings = []
        consistency_scores = []
        
        # Extract face regions for consistency check
        face_regions = []
        for frame in frames:
            face_region = self._extract_face_region(frame)
            if face_region is not None:
                face_regions.append(face_region)
        
        if len(face_regions) < 3:
            return 0.5, ["Could not extract consistent face regions"]
        
        # Calculate frame-to-frame similarity
        for i in range(len(face_regions) - 1):
            # Calculate structural similarity
            similarity = self._calculate_similarity(face_regions[i], face_regions[i + 1])
            consistency_scores.append(similarity)
        
        avg_consistency = np.mean(consistency_scores)
        std_consistency = np.std(consistency_scores)
        
        # High consistency = real video
        if avg_consistency > 0.85 and std_consistency < 0.1:
            findings.append("✅ Excellent frame-to-frame consistency")
            score = 0.9
        elif avg_consistency > 0.75 and std_consistency < 0.15:
            findings.append("✅ Good temporal consistency")
            score = 0.75
        elif avg_consistency > 0.6:
            findings.append("⚠️ Moderate temporal consistency")
            score = 0.6
        elif avg_consistency > 0.4:
            findings.append("❌ Low temporal consistency detected")
            score = 0.4
        else:
            findings.append("❌ Very low temporal consistency - possible deepfake")
            score = 0.2
        
        # High variance indicates flickering (deepfake artifact)
        if std_consistency > 0.2:
            findings.append("⚠️ High frame variance detected (possible flickering)")
            score *= 0.7
        
        return max(0.0, min(1.0, score)), findings
    
    def _analyze_motion_smoothness(self, frames: List[np.ndarray]) -> tuple:
        """Analyze motion smoothness between frames"""
        findings = []
        
        if len(frames) < 3:
            return 0.5, ["Insufficient frames for motion analysis"]
        
        # Convert to grayscale for optical flow
        gray_frames = [cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if len(frame.shape) == 3 else frame for frame in frames]
        
        # Calculate optical flow between consecutive frames
        flow_magnitudes = []
        for i in range(len(gray_frames) - 1):
            flow = cv2.calcOpticalFlowFarneback(
                gray_frames[i], gray_frames[i + 1],
                None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            flow_magnitudes.append(np.mean(magnitude))
        
        if len(flow_magnitudes) == 0:
            return 0.5, ["Could not calculate motion"]
        
        # Calculate motion smoothness (low variance = smooth motion)
        motion_variance = np.var(flow_magnitudes)
        avg_motion = np.mean(flow_magnitudes)
        
        # Real videos have smooth, gradual motion changes
        if motion_variance < 100 and avg_motion > 0:
            findings.append("✅ Smooth, natural motion detected")
            score = 0.85
        elif motion_variance < 500:
            findings.append("✅ Generally smooth motion")
            score = 0.7
        elif motion_variance < 2000:
            findings.append("⚠️ Some motion inconsistencies")
            score = 0.5
        else:
            findings.append("❌ Jerky or unnatural motion detected")
            score = 0.3
        
        # Very low motion might indicate static deepfake
        if avg_motion < 0.5:
            findings.append("⚠️ Very low motion detected")
            score *= 0.8
        
        return max(0.0, min(1.0, score)), findings
    
    def _analyze_color_consistency(self, frames: List[np.ndarray]) -> tuple:
        """Analyze color consistency across frames"""
        findings = []
        
        if len(frames) < 3:
            return 0.5, ["Insufficient frames for color analysis"]
        
        # Extract face regions and calculate mean colors
        face_colors = []
        for frame in frames:
            face_region = self._extract_face_region(frame)
            if face_region is not None:
                mean_color = np.mean(face_region, axis=(0, 1))
                face_colors.append(mean_color)
        
        if len(face_colors) < 3:
            return 0.5, ["Could not extract face colors"]
        
        # Calculate color variance
        face_colors = np.array(face_colors)
        color_variance = np.var(face_colors, axis=0)
        total_variance = np.mean(color_variance)
        
        # Real videos have consistent skin tones (with natural variations)
        if total_variance < 50:
            findings.append("✅ Consistent skin tone across frames")
            score = 0.85
        elif total_variance < 150:
            findings.append("✅ Generally consistent colors")
            score = 0.7
        elif total_variance < 300:
            findings.append("⚠️ Some color inconsistencies")
            score = 0.5
        else:
            findings.append("❌ Significant color flickering detected")
            score = 0.3
        
        return max(0.0, min(1.0, score)), findings
    
    def _extract_face_region(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Extract face region from frame"""
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if len(frame.shape) == 3 else frame
            
            # Try MediaPipe first (if available in main module)
            # For now, use OpenCV cascade
            if self.face_cascade is not None:
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    # Expand region slightly
                    x = max(0, x - w // 10)
                    y = max(0, y - h // 10)
                    w = min(frame.shape[1] - x, int(w * 1.2))
                    h = min(frame.shape[0] - y, int(h * 1.2))
                    return frame[y:y+h, x:x+w]
            
            # Fallback: use center region
            h, w = frame.shape[:2]
            return frame[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
            
        except Exception:
            return None
    
    def _calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate similarity between two images"""
        try:
            # Resize to same dimensions
            h, w = min(img1.shape[0], img2.shape[0]), min(img1.shape[1], img2.shape[1])
            img1_resized = cv2.resize(img1, (w, h))
            img2_resized = cv2.resize(img2, (w, h))
            
            # Calculate histogram correlation
            hist1 = cv2.calcHist([img1_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([img2_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            # Also calculate structural similarity
            # Simple version: normalized cross-correlation
            img1_norm = img1_resized.astype(np.float32) / 255.0
            img2_norm = img2_resized.astype(np.float32) / 255.0
            
            # Flatten and calculate cosine similarity
            flat1 = img1_norm.flatten()
            flat2 = img2_norm.flatten()
            
            cosine_sim = 1 - cosine(flat1, flat2)
            
            # Combine metrics
            similarity = (correlation + cosine_sim) / 2.0
            
            return max(0.0, min(1.0, similarity))
            
        except Exception:
            return 0.5

