"""
Veritas-AI Physics-Guard Module - Gemini AI Analysis
Uses Google's Gemini AI to analyze video frames for physical inconsistencies
that indicate AI-generated or manipulated content.
"""

import os
import base64
import json
from typing import List, Dict, Optional
import io

try:
    import google.generativeai as genai
    from PIL import Image
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not available. Gemini analysis will be disabled.")


class GeminiAnalyzer:
    """
    Physics-Guard Module using Gemini AI
    Analyzes video frames for physical inconsistencies and deepfake artifacts.
    """
    
    def __init__(self):
        """Initialize Gemini AI with API key from environment"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                print("Gemini AI initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
        else:
            if not GEMINI_AVAILABLE:
                print("Gemini SDK not installed")
            if not self.api_key:
                print("GEMINI_API_KEY not set")
    
    def analyze(self, frames: List[Dict]) -> Dict:
        """
        Analyze video frames using Gemini AI for deepfake detection.
        
        Args:
            frames: List of dicts with 'data' (bytes) and 'timestamp' (optional)
        
        Returns:
            Dict with physics-based analysis results
        """
        if not self.model:
            return {
                "available": False,
                "confidence": 0.5,
                "is_suspicious": None,
                "findings": ["Gemini AI not available - API key not configured"],
                "assessment": "Unable to perform AI analysis - using Bio-Guard only",
                "details": {
                    "reason": "no_api_key" if not self.api_key else "sdk_not_available"
                }
            }
        
        try:
            # Select key frames for analysis (first, middle, last + 2 random)
            selected_indices = self._select_key_frames(len(frames))
            selected_frames = [frames[i] for i in selected_indices]
            
            # Convert frames to PIL Images
            images = []
            for frame_data in selected_frames[:3]:  # Limit to 3 frames for API efficiency
                img = self._decode_to_pil(frame_data["data"])
                if img:
                    images.append(img)
            
            if not images:
                return {
                    "available": True,
                    "confidence": 0.0,
                    "is_suspicious": None,
                    "findings": ["Could not decode frames for analysis"],
                    "assessment": "Frame processing error"
                }
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt()
            
            # Send to Gemini for analysis
            response = self.model.generate_content([prompt] + images)
            
            # Parse and structure the response
            result = self._parse_response(response.text)
            
            return result
            
        except Exception as e:
            return {
                "available": True,
                "confidence": 0.3,
                "is_suspicious": None,
                "findings": [f"Analysis error: {str(e)}"],
                "assessment": "Error during AI analysis",
                "error": str(e)
            }
    
    def _select_key_frames(self, total_frames: int) -> List[int]:
        """Select key frame indices for analysis"""
        if total_frames <= 5:
            return list(range(total_frames))
        
        indices = [
            0,  # First frame
            total_frames // 4,  # Quarter
            total_frames // 2,  # Middle
            3 * total_frames // 4,  # Three-quarters
            total_frames - 1  # Last frame
        ]
        
        return sorted(set(indices))
    
    def _decode_to_pil(self, frame_bytes: bytes) -> Optional[Image.Image]:
        """Decode frame bytes to PIL Image"""
        try:
            img = Image.open(io.BytesIO(frame_bytes))
            # Resize if too large (for API efficiency)
            max_size = 1024
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            return img
        except Exception:
            return None
    
    def _create_analysis_prompt(self) -> str:
        """Create the enhanced analysis prompt for Gemini with real/fake discrimination"""
        return """You are an expert forensic video analyst specializing in deepfake detection. Your task is to determine if a video is REAL (authentic human) or FAKE (AI-generated/manipulated).

CRITICAL INSTRUCTIONS:
- You MUST be able to confidently identify REAL videos, not just detect fakes
- Real videos should show STRONG POSITIVE EVIDENCE of authenticity
- Be decisive: if evidence strongly points to real, say so with confidence
- If evidence strongly points to fake, say so with confidence
- Only be uncertain if evidence is genuinely mixed

REAL VIDEO INDICATORS (Positive Evidence - Look for these):
1. Natural skin texture with subtle variations, pores, and imperfections
2. Consistent lighting and shadows that match physics and light sources
3. Natural eye movements, blinks, and realistic eye reflections (eyes should reflect environment)
4. Realistic micro-expressions and natural facial movements
5. Natural hair movement, texture, and individual strands visible
6. Consistent background depth of field changes when face moves
7. Natural lip-sync with jaw and cheek movement coordination
8. Subtle skin imperfections (pores, blemishes, natural variations)
9. Natural head movement that feels connected to body movement
10. Realistic skin tone variations and natural color gradients
11. Natural breathing movements (subtle chest/neck movement)
12. Realistic shadows under chin, nose, and facial features
13. Natural eye contact and pupil dilation
14. Realistic skin elasticity and natural wrinkles

FAKE VIDEO INDICATORS (Negative Evidence - Red flags):
1. Unnatural facial boundaries, blending, or flickering edges
2. Inconsistent lighting/shadows that don't match physics
3. Unusual eye reflections, "dead eyes", or unnatural iris patterns
4. Flickering textures or colors between frames
5. Perfect symmetry (too perfect to be natural)
6. Static background with no depth of field changes
7. Lip-sync issues (mouth moves but jaw/cheeks don't)
8. Unnatural hair movement or texture (too smooth or too uniform)
9. Teeth appearing through lips or other physical impossibilities
10. Robotic or disconnected head/body movement
11. Unnatural skin smoothness (too perfect)
12. Inconsistent shadows or lighting on face vs background
13. Eyes that don't reflect environment or look "pasted on"
14. Unnatural color bleeding or halo effects around face

IMPORTANT DISTINCTIONS:
- Real videos may have compression artifacts - don't confuse these with deepfake artifacts
- Compression artifacts are uniform and affect the whole frame; deepfake artifacts are localized to face/body areas
- Real videos should show natural human characteristics and imperfections
- High-quality real videos may look "too good" but will have natural imperfections
- Be confident when you see strong evidence of authenticity

ANALYSIS PROCESS:
1. Examine each frame carefully for the indicators above
2. Count REAL indicators vs FAKE indicators
3. If REAL indicators > FAKE indicators by 2+, set is_real=true with high confidence
4. If FAKE indicators > REAL indicators by 2+, set is_suspicious=true with high confidence
5. If indicators are balanced, be uncertain but explain why

Respond ONLY with a valid JSON object (no markdown, no code blocks) in this exact format:
{
    "reasoning": "Brief step-by-step analysis: [your specific observations from the frames]",
    "is_real": true/false/null,
    "is_suspicious": true/false/null,
    "confidence": 0.0-1.0,
    "real_indicators": ["specific indicator 1", "specific indicator 2", ...],
    "fake_indicators": ["specific indicator 1", "specific indicator 2", ...],
    "findings": ["detailed finding 1", "detailed finding 2", ...],
    "assessment": "One clear sentence: This video appears [REAL/FAKE/UNCERTAIN] because [specific reason]"
}

Be decisive and specific. If you see strong evidence of authenticity, set is_real=true with confidence > 0.7. If you see manipulation artifacts, set is_suspicious=true with confidence > 0.7."""
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini response into structured format"""
        try:
            # Try to extract JSON from response
            # Handle cases where response has markdown code blocks
            text = response_text.strip()
            
            if text.startswith("```"):
                # Remove markdown code blocks
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            
            if text.startswith("json"):
                text = text[4:].strip()
            
            result = json.loads(text)
            
            # Ensure required fields exist
            is_real = result.get("is_real", None)
            is_suspicious = result.get("is_suspicious", None)
            confidence = float(result.get("confidence", 0.5))
            real_indicators = result.get("real_indicators", [])
            fake_indicators = result.get("fake_indicators", [])
            findings = result.get("findings", [])
            artifact_types = result.get("artifact_types", [])
            assessment = result.get("assessment", "Analysis complete")
            
            return {
                "available": True,
                "is_real": is_real,
                "is_suspicious": is_suspicious,
                "confidence": round(confidence, 3),
                "real_indicators": real_indicators,
                "fake_indicators": fake_indicators,
                "findings": findings,
                "artifact_types": artifact_types,
                "assessment": assessment,
                "details": {
                    "model": "gemini-2.0-flash",
                    "frames_analyzed": 3
                }
            }
            
        except json.JSONDecodeError:
            # If JSON parsing fails, extract what we can from text
            is_suspicious = "suspicious" in response_text.lower() or "fake" in response_text.lower()
            
            return {
                "available": True,
                "is_suspicious": is_suspicious,
                "confidence": 0.5,
                "findings": [response_text[:500]],  # Truncate long responses
                "assessment": "Partial analysis - response parsing issue",
                "raw_response": response_text[:1000]
            }
    
    def test_connection(self) -> bool:
        """Test if Gemini API is working"""
        if not self.model:
            return False
        
        try:
            response = self.model.generate_content("Reply with only: OK")
            return "OK" in response.text
        except Exception:
            return False
