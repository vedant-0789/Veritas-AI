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
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini AI initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini: {e}")
        else:
            if not GEMINI_AVAILABLE:
                print("⚠️ Gemini SDK not installed")
            if not self.api_key:
                print("⚠️ GEMINI_API_KEY not set")
    
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
        """Create the analysis prompt for Gemini"""
        return """You are an expert forensic analyst specialized in detecting AI-generated and manipulated video content (deepfakes).

Analyze these video frames carefully for signs of synthetic or manipulated content. Look for:

1. **Facial Boundary Artifacts**: Unnatural edges, blending, or flickering around the face, hair, and neck boundaries.

2. **Lighting Inconsistencies**: 
   - Shadows that don't match the apparent light source
   - Inconsistent highlights on the face vs. background
   - Specular reflections that seem wrong

3. **Eye Anomalies**:
   - Unusual reflections in the eyes
   - Asymmetric eye movements or blinks
   - Unnatural iris patterns

4. **Temporal Inconsistencies** (comparing frames):
   - Flickering textures or colors
   - Inconsistent skin texture between frames
   - Background stability issues

5. **Physical Impossibilities**:
   - Teeth appearing through lips
   - Hair moving unnaturally
   - Clothing/jewelry inconsistencies

6. **Compression Artifacts vs. Deepfake Artifacts**:
   - Distinguish between normal video compression and AI manipulation

Respond ONLY with a valid JSON object (no markdown, no code blocks) in this exact format:
{
    "is_suspicious": true or false,
    "confidence": 0.0 to 1.0,
    "findings": ["finding 1", "finding 2", ...],
    "artifact_types": ["type1", "type2", ...],
    "assessment": "One sentence summary"
}

Be conservative: if unsure, indicate lower confidence. Real videos may have compression artifacts that look suspicious."""
    
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
            is_suspicious = result.get("is_suspicious", None)
            confidence = float(result.get("confidence", 0.5))
            findings = result.get("findings", [])
            artifact_types = result.get("artifact_types", [])
            assessment = result.get("assessment", "Analysis complete")
            
            return {
                "available": True,
                "is_suspicious": is_suspicious,
                "confidence": round(confidence, 3),
                "findings": findings,
                "artifact_types": artifact_types,
                "assessment": assessment,
                "details": {
                    "model": "gemini-1.5-flash",
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
