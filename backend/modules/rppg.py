"""
Veritas-AI Bio-Guard Module - rPPG (Remote Photoplethysmography) Analysis
Detects biological pulse signals from video frames to verify human authenticity.

This module uses the POS (Plane-Orthogonal-to-Skin) algorithm which is
robust across different skin tones and lighting conditions.
"""

import cv2
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import List, Dict, Optional, Tuple
import io

try:
    import mediapipe as mp
    # Test if solutions attribute exists (compatibility check)
    if hasattr(mp, 'solutions'):
        MEDIAPIPE_AVAILABLE = True
    else:
        raise ImportError("MediaPipe solutions not available")
except (ImportError, AttributeError) as e:
    MEDIAPIPE_AVAILABLE = False
    print(f"Warning: MediaPipe not fully available ({e}). Using fallback face detection.")


class RPPGAnalyzer:
    """
    Remote Photoplethysmography (rPPG) Analyzer
    Detects pulse signals from video frames using the POS algorithm.
    """
    
    def __init__(self):
        """Initialize the rPPG analyzer with MediaPipe face mesh"""
        self.fps = 30  # Assumed frame rate
        self.min_bpm = 40
        self.max_bpm = 240
        self.min_freq = self.min_bpm / 60.0  # 0.67 Hz
        self.max_freq = self.max_bpm / 60.0  # 4.0 Hz
        
        # Initialize MediaPipe Face Mesh
        if MEDIAPIPE_AVAILABLE:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        else:
            self.face_mesh = None
        
        # ROI landmark indices for MediaPipe Face Mesh
        # Forehead region
        self.forehead_landmarks = [10, 67, 69, 104, 108, 109, 151, 297, 299, 333, 337, 338]
        # Left cheek region
        self.left_cheek_landmarks = [117, 118, 119, 120, 121, 128, 129, 130, 131]
        # Right cheek region
        self.right_cheek_landmarks = [346, 347, 348, 349, 350, 357, 358, 359, 360]
    
    def analyze(self, frames: List[Dict]) -> Dict:
        """
        Analyze video frames to detect pulse signals.
        
        Args:
            frames: List of dicts with 'data' (bytes) and 'timestamp' (optional)
        
        Returns:
            Dict with pulse detection results
        """
        if len(frames) < 5:
            return {
                "pulse_detected": False,
                "confidence": 0.0,
                "error": "Insufficient frames for analysis (need at least 5)"
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
                    "pulse_detected": False,
                    "confidence": 0.0,
                    "error": "Could not decode enough valid frames"
                }
            
            # Extract ROI signals from each frame
            rgb_signals = self._extract_roi_signals(decoded_frames)
            
            if rgb_signals is None or len(rgb_signals) < 5:
                return {
                    "pulse_detected": False,
                    "confidence": 0.0,
                    "bpm": None,
                    "snr": 0.0,
                    "assessment": "No face detected in video frames",
                    "details": "Could not extract facial ROI signals"
                }
            
            # Apply POS algorithm to extract pulse signal
            pulse_signal = self._apply_pos_algorithm(rgb_signals)
            
            # Apply bandpass filter
            filtered_signal = self._bandpass_filter(pulse_signal)
            
            # Analyze frequency content with FFT
            bpm, snr, confidence = self._analyze_frequency(filtered_signal)
            
            # Determine if pulse is detected
            # Increased threshold to 4.0 to reduce false positives from noise/compression
            pulse_detected = confidence > 0.5 and snr > 4.0
            
            # Generate assessment
            if pulse_detected:
                assessment = f"Likely Real - Biological pulse detected ({int(bpm)} BPM)"
                if snr > 10:
                    assessment = f"Highly Likely Real - Strong biological signals ({int(bpm)} BPM, SNR: {snr:.1f})"
            else:
                if snr < 1:
                    assessment = "Likely Fake - No biological pulse signal detected"
                else:
                    assessment = "Uncertain - Weak biological signals (may be compressed video)"
            
            return {
                "pulse_detected": pulse_detected,
                "bpm": round(bpm, 1) if bpm else None,
                "confidence": round(confidence, 3),
                "snr": round(snr, 2),
                "assessment": assessment,
                "details": {
                    "frames_analyzed": len(decoded_frames),
                    "signal_quality": "good" if snr > 5 else "fair" if snr > 2 else "poor",
                    "algorithm": "POS (Plane-Orthogonal-to-Skin)"
                }
            }
            
        except Exception as e:
            return {
                "pulse_detected": False,
                "confidence": 0.0,
                "error": f"Analysis error: {str(e)}"
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
    
    def _extract_roi_signals(self, frames: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        Extract RGB signals from facial ROIs across all frames.
        
        Returns:
            numpy array of shape (num_frames, 3) with mean RGB values
        """
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None:
            # Fallback: use center of frame as ROI
            return self._extract_center_roi(frames)
        
        rgb_signals = []
        
        for frame in frames:
            # Process with MediaPipe
            results = self.face_mesh.process(frame)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                h, w = frame.shape[:2]
                
                # Extract ROI from forehead, left cheek, and right cheek
                roi_values = []
                
                for roi_landmarks in [self.forehead_landmarks, self.left_cheek_landmarks, self.right_cheek_landmarks]:
                    roi_mean = self._get_roi_mean(frame, landmarks, roi_landmarks, w, h)
                    if roi_mean is not None:
                        roi_values.append(roi_mean)
                
                if roi_values:
                    # Average across all ROIs
                    mean_rgb = np.mean(roi_values, axis=0)
                    rgb_signals.append(mean_rgb)
                else:
                    # Use previous value or skip
                    if rgb_signals:
                        rgb_signals.append(rgb_signals[-1])
            else:
                # No face detected - use previous value or skip
                if rgb_signals:
                    rgb_signals.append(rgb_signals[-1])
        
        if len(rgb_signals) < 5:
            return None
        
        return np.array(rgb_signals)
    
    def _get_roi_mean(self, frame: np.ndarray, landmarks, indices: List[int], w: int, h: int) -> Optional[np.ndarray]:
        """Get mean RGB values from a region defined by landmark indices"""
        try:
            points = []
            for idx in indices:
                lm = landmarks.landmark[idx]
                x, y = int(lm.x * w), int(lm.y * h)
                if 0 <= x < w and 0 <= y < h:
                    points.append((x, y))
            
            if len(points) < 3:
                return None
            
            # Create mask for the ROI polygon
            points_array = np.array(points, dtype=np.int32)
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillConvexPoly(mask, points_array, 255)
            
            # Extract mean RGB
            mean_rgb = cv2.mean(frame, mask=mask)[:3]
            return np.array(mean_rgb)
            
        except Exception:
            return None
    
    def _extract_center_roi(self, frames: List[np.ndarray]) -> np.ndarray:
        """Fallback: extract RGB from center region of frame"""
        rgb_signals = []
        
        for frame in frames:
            h, w = frame.shape[:2]
            # Use center 20% of frame
            y1, y2 = int(h * 0.3), int(h * 0.5)
            x1, x2 = int(w * 0.4), int(w * 0.6)
            
            roi = frame[y1:y2, x1:x2]
            mean_rgb = np.mean(roi, axis=(0, 1))
            rgb_signals.append(mean_rgb)
        
        return np.array(rgb_signals)
    
    def _apply_pos_algorithm(self, rgb_signals: np.ndarray) -> np.ndarray:
        """
        Apply POS (Plane-Orthogonal-to-Skin) algorithm to extract pulse signal.
        
        The POS algorithm is designed to be robust across different skin tones
        by projecting RGB signals onto a plane orthogonal to skin tone variations.
        
        Reference: Wang et al., "Algorithmic Principles of Remote PPG"
        """
        # Normalize RGB signals
        mean_rgb = np.mean(rgb_signals, axis=0)
        normalized = rgb_signals / (mean_rgb + 1e-8)
        
        # Temporal normalization
        l = 32  # Window length
        pulse_signal = np.zeros(len(normalized))
        
        for i in range(len(normalized)):
            # Get window
            start = max(0, i - l // 2)
            end = min(len(normalized), i + l // 2)
            window = normalized[start:end]
            
            if len(window) < 5:
                continue
            
            # Normalize window
            window_mean = np.mean(window, axis=0)
            Cn = window / (window_mean + 1e-8)
            
            # POS projection
            # S = Xs - alpha * Ys where alpha = std(Xs) / std(Ys)
            Xs = Cn[:, 1] - Cn[:, 2]  # G - B
            Ys = Cn[:, 1] + Cn[:, 2] - 2 * Cn[:, 0]  # G + B - 2R
            
            alpha = np.std(Xs) / (np.std(Ys) + 1e-8)
            S = Xs - alpha * Ys
            
            # Use the center value of the window
            center_idx = len(S) // 2
            if center_idx < len(S):
                pulse_signal[i] = S[center_idx]
        
        return pulse_signal
    
    def _bandpass_filter(self, signal_data: np.ndarray) -> np.ndarray:
        """Apply bandpass filter to isolate pulse frequencies"""
        try:
            # Design Butterworth bandpass filter
            nyq = self.fps / 2
            low = self.min_freq / nyq
            high = min(self.max_freq / nyq, 0.99)  # Ensure < 1
            
            b, a = signal.butter(2, [low, high], btype='band')
            filtered = signal.filtfilt(b, a, signal_data)
            
            return filtered
        except Exception:
            # Return original if filtering fails
            return signal_data
    
    def _analyze_frequency(self, signal_data: np.ndarray) -> Tuple[float, float, float]:
        """
        Analyze frequency content to find dominant pulse frequency.
        
        Returns:
            Tuple of (bpm, snr, confidence)
        """
        try:
            n = len(signal_data)
            
            # Apply FFT
            fft_result = fft(signal_data)
            freqs = fftfreq(n, 1 / self.fps)
            
            # Only consider positive frequencies in pulse range
            positive_mask = (freqs > self.min_freq) & (freqs < self.max_freq)
            positive_freqs = freqs[positive_mask]
            positive_magnitudes = np.abs(fft_result)[positive_mask]
            
            if len(positive_magnitudes) == 0:
                return 0, 0, 0
            
            # Find dominant frequency
            peak_idx = np.argmax(positive_magnitudes)
            dominant_freq = positive_freqs[peak_idx]
            peak_magnitude = positive_magnitudes[peak_idx]
            
            # Calculate BPM
            bpm = dominant_freq * 60
            
            # Calculate SNR (Signal-to-Noise Ratio)
            noise_magnitudes = np.delete(positive_magnitudes, peak_idx)
            noise_power = np.mean(noise_magnitudes ** 2) if len(noise_magnitudes) > 0 else 1e-8
            signal_power = peak_magnitude ** 2
            snr = 10 * np.log10(signal_power / (noise_power + 1e-8))
            
            # Calculate confidence based on SNR and peak prominence
            if snr > 10:
                confidence = 0.95
            elif snr > 5:
                confidence = 0.75 + (snr - 5) * 0.04
            elif snr > 2:
                confidence = 0.5 + (snr - 2) * 0.083
            else:
                confidence = max(0.1, snr * 0.25)
            
            # Adjust confidence if BPM is in normal human range
            if 50 <= bpm <= 120:
                confidence = min(1.0, confidence * 1.1)
            elif bpm < 40 or bpm > 200:
                confidence *= 0.5
            
            return bpm, max(0, snr), min(1.0, confidence)
            
        except Exception as e:
            return 0, 0, 0
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'face_mesh') and self.face_mesh:
            self.face_mesh.close()
