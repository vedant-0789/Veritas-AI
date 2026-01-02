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
    # Check for old API (solutions) or new API (tasks)
    if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_mesh'):
        # Old API available
        try:
            test_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)
            test_mesh.close()
            MEDIAPIPE_AVAILABLE = True
            MEDIAPIPE_USE_OLD_API = True
            print("✅ MediaPipe (old API) initialized successfully")
        except Exception as e:
            raise ImportError(f"MediaPipe old API failed: {e}")
    else:
        # New API or not available - use fallback
        raise ImportError("MediaPipe solutions API not available (new API detected or not installed)")
except (ImportError, AttributeError, Exception) as e:
    MEDIAPIPE_AVAILABLE = False
    MEDIAPIPE_USE_OLD_API = False
    print(f"⚠️ Warning: MediaPipe not available ({e}). Using OpenCV fallback face detection.")
    print(f"   Note: Pulse detection will still work using center ROI method.")


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
        
        # Initialize MediaPipe Face Mesh or OpenCV fallback
        if MEDIAPIPE_AVAILABLE and MEDIAPIPE_USE_OLD_API:
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
            # Initialize OpenCV face detector as fallback
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                if self.face_cascade.empty():
                    self.face_cascade = None
                else:
                    print("✅ Using OpenCV face detection fallback")
            except:
                self.face_cascade = None
        
        # ROI landmark indices for MediaPipe Face Mesh
        # Forehead region
        self.forehead_landmarks = [10, 67, 69, 104, 108, 109, 151, 297, 299, 333, 337, 338]
        # Left cheek region
        self.left_cheek_landmarks = [117, 118, 119, 120, 121, 128, 129, 130, 131]
        # Right cheek region
        self.right_cheek_landmarks = [346, 347, 348, 349, 350, 357, 358, 359, 360]
    
    def analyze(self, frames: List[Dict], fps: Optional[float] = None) -> Dict:
        """
        Analyze video frames to detect pulse signals.
        
        Args:
            frames: List of dicts with 'data' (bytes) and 'timestamp' (optional)
            fps: Optional frame rate override
        
        Returns:
            Dict with pulse detection results
        """
        if fps:
            self.fps = fps
            self.min_freq = self.min_bpm / 60.0
            self.max_freq = self.max_bpm / 60.0

        if len(frames) < 5:
            return {
                "pulse_detected": False,
                "confidence": 0.0,
                "bpm": None,
                "snr": 0.0,
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
                    "bpm": None,
                    "snr": 0.0,
                    "error": "Could not decode enough valid frames"
                }
            
            # Extract ROI signals from each frame (Separate signals for consensus)
            roi_signals_map = self._extract_roi_signals(decoded_frames)
            
            if not roi_signals_map:
                return {
                    "pulse_detected": False,
                    "confidence": 0.0,
                    "bpm": None,
                    "snr": 0.0,
                    "assessment": "No face detected in video frames",
                    "details": "Could not extract facial ROI signals"
                }
            
            # Process each ROI signal
            roi_results = []
            pulse_signals = []
            
            for roi_name, rgb_signals in roi_signals_map.items():
                if len(rgb_signals) < 5:
                    continue
                    
                # Apply POS algorithm
                p_signal = self._apply_pos_algorithm(rgb_signals)
                
                # Apply Moving Average for smoothing
                p_signal = self._moving_average(p_signal, window=3)
                
                # Detrend signal (Remove mean and trend)
                p_signal = signal.detrend(p_signal)
                
                # Apply bandpass filter
                f_signal = self._bandpass_filter(p_signal)
                
                # Analyze frequency
                roi_bpm, roi_snr, roi_conf = self._analyze_frequency(f_signal)
                
                roi_results.append({
                    "roi": roi_name,
                    "bpm": roi_bpm,
                    "snr": roi_snr,
                    "confidence": roi_conf,
                    "signal": f_signal
                })
                pulse_signals.append(f_signal)
            
            if not roi_results:
                return {
                    "pulse_detected": False, 
                    "confidence": 0.0, 
                    "bpm": None,
                    "snr": 0.0,
                    "assessment": "ROI processing failed"
                }

            # Average signal for overall analysis and UI display
            pulse_signal = np.mean(pulse_signals, axis=0)
            bpm, snr, confidence = self._analyze_frequency(pulse_signal)
            
            # ROI Consensus Check
            # Human blood flows to all facial regions simultaneously
            bpms = [r['bpm'] for r in roi_results if r['confidence'] > 0.3]
            roi_consensus = False
            if len(bpms) >= 2:
                # Check if BPMs are within 10% of each other
                bpm_variance = np.std(bpms) / (np.mean(bpms) + 1e-8)
                roi_consensus = bpm_variance < 0.15
            
            # Determine if pulse is detected
            # Be more lenient if we have consensus
            pulse_detected = (confidence > 0.3 and snr > 2.0)
            if roi_consensus and snr > 1.5:
                pulse_detected = True
                confidence = min(0.95, confidence * 1.2)
            
            # If SNR is very high but no consensus, it might be a periodic noise
            if not roi_consensus and snr < 5.0:
                pulse_detected = False
                confidence *= 0.5

            
            # If we have good signal quality indicators, be more lenient
            if snr > 5.0 and 50 <= bpm <= 120:
                pulse_detected = True
            elif snr < 1.5:
                pulse_detected = False
            
            # Additional analysis: eye blink detection and landmark stability
            blink_analysis = self._analyze_eye_blinks(decoded_frames) if MEDIAPIPE_AVAILABLE else None
            landmark_stability = self._analyze_landmark_stability(decoded_frames) if MEDIAPIPE_AVAILABLE else None
            
            # Enhanced assessment with more details
            assessment_parts = []
            if pulse_detected:
                if snr > 10:
                    assessment_parts.append(f"Highly Likely Real - Strong biological pulse detected ({int(bpm)} BPM, SNR: {snr:.1f})")
                else:
                    assessment_parts.append(f"Likely Real - Biological pulse detected ({int(bpm)} BPM)")
            else:
                if snr < 1:
                    assessment_parts.append("Likely Fake - No biological pulse signal detected")
                else:
                    assessment_parts.append("Uncertain - Weak biological signals (may be compressed video)")
            
            # Add blink information if available
            if blink_analysis and blink_analysis.get("blinks_detected", 0) > 0:
                assessment_parts.append(f"Natural eye blinks detected ({blink_analysis['blinks_detected']} blinks)")
            
            # Add landmark stability if available
            if landmark_stability:
                stability_score = landmark_stability.get("stability_score", 0.5)
                if stability_score > 0.8:
                    assessment_parts.append("Stable facial landmarks detected")
                elif stability_score < 0.5:
                    assessment_parts.append("Unstable facial landmarks (possible manipulation)")
            
            assessment = ". ".join(assessment_parts) if assessment_parts else "Analysis complete"
            
            return {
                "pulse_detected": pulse_detected,
                "bpm": round(bpm, 1) if bpm else None,
                "confidence": round(confidence, 3),
                "snr": round(snr, 2),
                "assessment": assessment,
                "blink_analysis": blink_analysis,
                "landmark_stability": landmark_stability,
                "pulse_signal": pulse_signal.tolist() if len(pulse_signal) > 0 else [],
                "details": {
                    "frames_analyzed": len(decoded_frames),
                    "signal_quality": "good" if snr > 5 else "fair" if snr > 2 else "poor",
                    "algorithm": "POS (Plane-Orthogonal-to-Skin)",
                    "temporal_analysis": "enabled" if len(decoded_frames) >= 10 else "insufficient_frames"
                }
            }
            
        except Exception as e:
            return {
                "pulse_detected": False,
                "confidence": 0.0,
                "bpm": None,
                "snr": 0.0,
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
    
    def _extract_roi_signals(self, frames: List[np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Extract RGB signals from facial ROIs across all frames.
        Returns a map of ROI name to signal array.
        """
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None:
            # Fallback: use center of frame as ROI
            center_sig = self._extract_center_roi(frames)
            return {"center": center_sig} if center_sig is not None else {}
        
        roi_signals = {
            "forehead": [],
            "left_cheek": [],
            "right_cheek": []
        }
        
        for frame in frames:
            # Process with MediaPipe
            results = self.face_mesh.process(frame)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                h, w = frame.shape[:2]
                
                # Extract ROIs
                f_mean = self._get_roi_mean(frame, landmarks, self.forehead_landmarks, w, h)
                l_mean = self._get_roi_mean(frame, landmarks, self.left_cheek_landmarks, w, h)
                r_mean = self._get_roi_mean(frame, landmarks, self.right_cheek_landmarks, w, h)
                
                if f_mean is not None: roi_signals["forehead"].append(f_mean)
                if l_mean is not None: roi_signals["left_cheek"].append(l_mean)
                if r_mean is not None: roi_signals["right_cheek"].append(r_mean)
                
                # Handle skips by padding with previous value
                for key in roi_signals:
                    if len(roi_signals[key]) < len(roi_signals["forehead"]) and roi_signals[key]:
                        roi_signals[key].append(roi_signals[key][-1])
            else:
                # No face detected - pad all
                for key in roi_signals:
                    if roi_signals[key]:
                        roi_signals[key].append(roi_signals[key][-1])
        
        # Prune and convert to numpy
        result = {}
        for key, sig in roi_signals.items():
            if len(sig) >= 5:
                result[key] = np.array(sig)
                
        return result

    def _moving_average(self, x: np.ndarray, window: int = 3) -> np.ndarray:
        """Apply moving average to smooth signal"""
        if len(x) < window: return x
        return np.convolve(x, np.ones(window)/window, mode='same')
    
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
        """Fallback: extract RGB from face region using OpenCV or center region"""
        rgb_signals = []
        
        for frame in frames:
            h, w = frame.shape[:2]
            
            # Try OpenCV face detection first
            if hasattr(self, 'face_cascade') and self.face_cascade is not None:
                try:
                    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if len(frame.shape) == 3 else frame
                    faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                    if len(faces) > 0:
                        x, y, fw, fh = faces[0]
                        # Extract face region with some padding
                        y1 = max(0, y - int(fh * 0.1))
                        y2 = min(h, y + int(fh * 1.1))
                        x1 = max(0, x - int(fw * 0.1))
                        x2 = min(w, x + int(fw * 1.1))
                        roi = frame[y1:y2, x1:x2]
                        if roi.size > 0:
                            mean_rgb = np.mean(roi, axis=(0, 1))
                            rgb_signals.append(mean_rgb)
                            continue
                except:
                    pass
            
            # Fallback to center region
            y1, y2 = int(h * 0.3), int(h * 0.5)
            x1, x2 = int(w * 0.4), int(w * 0.6)
            
            roi = frame[y1:y2, x1:x2]
            if roi.size > 0:
                mean_rgb = np.mean(roi, axis=(0, 1))
                rgb_signals.append(mean_rgb)
        
        if len(rgb_signals) == 0:
            # Last resort: use entire frame center
            for frame in frames:
                h, w = frame.shape[:2]
                center_roi = frame[int(h*0.4):int(h*0.6), int(w*0.4):int(w*0.6)]
                if center_roi.size > 0:
                    mean_rgb = np.mean(center_roi, axis=(0, 1))
                    rgb_signals.append(mean_rgb)
        
        return np.array(rgb_signals) if rgb_signals else None
    
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
            # More generous confidence scoring for better detection
            if snr > 10:
                confidence = 0.95
            elif snr > 7:
                confidence = 0.85 + (snr - 7) * 0.033  # 0.85 to 0.95
            elif snr > 5:
                confidence = 0.70 + (snr - 5) * 0.075  # 0.70 to 0.85
            elif snr > 3:
                confidence = 0.50 + (snr - 3) * 0.10   # 0.50 to 0.70
            elif snr > 2:
                confidence = 0.35 + (snr - 2) * 0.15  # 0.35 to 0.50
            else:
                confidence = max(0.1, snr * 0.15)
            
            # Adjust confidence if BPM is in normal human range (strong indicator)
            if 50 <= bpm <= 120:
                confidence = min(1.0, confidence * 1.15)  # Boost for normal BPM
            elif 40 <= bpm <= 150:
                confidence = min(1.0, confidence * 1.05)  # Slight boost for acceptable range
            elif bpm < 30 or bpm > 200:
                confidence *= 0.4  # Strong penalty for unrealistic BPM
            else:
                confidence *= 0.7  # Moderate penalty for unusual BPM
            
            return bpm, max(0, snr), min(1.0, confidence)
            
        except Exception as e:
            return 0, 0, 0
    
    def _analyze_eye_blinks(self, frames: List[np.ndarray]) -> Optional[Dict]:
        """Analyze eye blinks as a sign of natural human behavior"""
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None or len(frames) < 10:
            return None
        
        try:
            # Eye landmark indices (left and right eye)
            left_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
            right_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
            
            eye_openness = []
            
            for frame in frames:
                results = self.face_mesh.process(frame)
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0]
                    h, w = frame.shape[:2]
                    
                    # Calculate eye aspect ratio (EAR) for both eyes
                    left_ear = self._calculate_eye_aspect_ratio(landmarks, left_eye_indices, w, h)
                    right_ear = self._calculate_eye_aspect_ratio(landmarks, right_eye_indices, w, h)
                    
                    # Average EAR
                    avg_ear = (left_ear + right_ear) / 2.0 if left_ear and right_ear else None
                    if avg_ear is not None:
                        eye_openness.append(avg_ear)
            
            if len(eye_openness) < 5:
                return None
            
            # Detect blinks (EAR drops below threshold)
            blink_threshold = 0.25  # Typical threshold for blink detection
            blinks = 0
            in_blink = False
            
            for ear in eye_openness:
                if ear < blink_threshold and not in_blink:
                    blinks += 1
                    in_blink = True
                elif ear >= blink_threshold:
                    in_blink = False
            
            # Real humans blink regularly (about 15-20 times per minute)
            # For a 15-frame sequence at 30fps (0.5 seconds), expect 0-1 blinks
            expected_blinks_min = 0.125  # 15 blinks/min * 0.5 sec / 60
            expected_blinks_max = 0.167  # 20 blinks/min * 0.5 sec / 60
            
            blink_rate_normal = 0 <= blinks <= 2  # Allow some variance
            
            return {
                "blinks_detected": blinks,
                "blink_rate_normal": blink_rate_normal,
                "avg_eye_openness": round(np.mean(eye_openness), 3),
                "eye_variance": round(np.var(eye_openness), 3),
                "assessment": "Natural blinking detected" if blink_rate_normal and blinks > 0 else "No blinks detected (may indicate static deepfake)"
            }
            
        except Exception as e:
            return None
    
    def _calculate_eye_aspect_ratio(self, landmarks, eye_indices: List[int], w: int, h: int) -> Optional[float]:
        """Calculate Eye Aspect Ratio (EAR) for blink detection"""
        try:
            points = []
            for idx in eye_indices:
                lm = landmarks.landmark[idx]
                x, y = int(lm.x * w), int(lm.y * h)
                points.append((x, y))
            
            if len(points) < 6:
                return None
            
            # Calculate vertical distances
            vertical_1 = np.linalg.norm(np.array(points[1]) - np.array(points[5]))
            vertical_2 = np.linalg.norm(np.array(points[2]) - np.array(points[4]))
            
            # Calculate horizontal distance
            horizontal = np.linalg.norm(np.array(points[0]) - np.array(points[3]))
            
            # EAR formula
            if horizontal == 0:
                return None
            
            ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
            return ear
            
        except Exception:
            return None
    
    def _analyze_landmark_stability(self, frames: List[np.ndarray]) -> Optional[Dict]:
        """Analyze stability of facial landmarks across frames"""
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None or len(frames) < 5:
            return None
        
        try:
            landmark_positions = []
            
            for frame in frames:
                results = self.face_mesh.process(frame)
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0]
                    h, w = frame.shape[:2]
                    
                    # Extract key landmark positions (nose, eyes, mouth)
                    key_indices = [1, 33, 61, 199, 291, 13, 14, 15, 16, 17, 18]  # Nose, eyes, mouth
                    positions = []
                    for idx in key_indices:
                        lm = landmarks.landmark[idx]
                        positions.append([lm.x * w, lm.y * h])
                    
                    landmark_positions.append(np.array(positions))
            
            if len(landmark_positions) < 3:
                return None
            
            # Calculate stability (low variance = stable)
            landmark_positions = np.array(landmark_positions)
            variances = np.var(landmark_positions, axis=0)
            avg_variance = np.mean(variances)
            
            # Normalize variance (lower is better, higher stability)
            # Typical variance for stable face: < 100 pixels^2
            if avg_variance < 50:
                stability_score = 0.95
                assessment = "Highly stable landmarks"
            elif avg_variance < 100:
                stability_score = 0.85
                assessment = "Stable landmarks"
            elif avg_variance < 200:
                stability_score = 0.65
                assessment = "Moderate stability"
            elif avg_variance < 500:
                stability_score = 0.4
                assessment = "Unstable landmarks (possible manipulation)"
            else:
                stability_score = 0.2
                assessment = "Very unstable landmarks (likely deepfake)"
            
            return {
                "stability_score": round(stability_score, 3),
                "variance": round(avg_variance, 2),
                "assessment": assessment
            }
            
        except Exception:
            return None
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'face_mesh') and self.face_mesh:
            self.face_mesh.close()
