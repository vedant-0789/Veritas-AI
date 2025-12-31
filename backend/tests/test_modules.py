"""
Test script for Veritas-AI detection modules
Tests all analyzers with sample data
"""

import os
import sys
import numpy as np
from PIL import Image
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.rppg import RPPGAnalyzer
from modules.gemini_analyzer import GeminiAnalyzer
from modules.temporal_analyzer import TemporalAnalyzer
from modules.advanced_analyzer import AdvancedAnalyzer
from modules.ensemble import EnsembleDecision
from modules.logger import logger


def create_test_frames(count: int = 15) -> list:
    """Create synthetic test frames"""
    frames = []
    for i in range(count):
        # Create a simple test image (640x480 RGB)
        img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Add a "face" region (simpler for testing)
        cv2.rectangle(img, (200, 150), (440, 350), (220, 180, 140), -1)  # Face color
        
        # Convert to bytes
        pil_img = Image.fromarray(img)
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        frames.append({
            "data": img_bytes.read(),
            "timestamp": i / 30.0  # 30 fps
        })
    
    return frames


def test_rppg_analyzer():
    """Test rPPG analyzer"""
    print("\n" + "="*50)
    print("Testing rPPG Analyzer")
    print("="*50)
    
    analyzer = RPPGAnalyzer()
    frames = create_test_frames(15)
    
    result = analyzer.analyze(frames)
    
    print(f"Pulse Detected: {result.get('pulse_detected', False)}")
    print(f"BPM: {result.get('bpm', 'N/A')}")
    print(f"SNR: {result.get('snr', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 0):.3f}")
    print(f"Assessment: {result.get('assessment', 'N/A')}")
    
    if result.get('blink_analysis'):
        print(f"Blinks Detected: {result['blink_analysis'].get('blinks_detected', 0)}")
    
    if result.get('landmark_stability'):
        print(f"Landmark Stability: {result['landmark_stability'].get('stability_score', 0):.3f}")
    
    return result


def test_temporal_analyzer():
    """Test temporal analyzer"""
    print("\n" + "="*50)
    print("Testing Temporal Analyzer")
    print("="*50)
    
    analyzer = TemporalAnalyzer()
    frames = create_test_frames(15)
    
    result = analyzer.analyze(frames)
    
    print(f"Available: {result.get('available', False)}")
    print(f"Temporal Consistency: {result.get('temporal_consistency', 0):.3f}")
    print(f"Confidence: {result.get('confidence', 0):.3f}")
    print(f"Assessment: {result.get('assessment', 'N/A')}")
    print(f"Findings: {len(result.get('findings', []))} items")
    
    for finding in result.get('findings', [])[:3]:
        print(f"  - {finding}")
    
    return result


def test_advanced_analyzer():
    """Test advanced analyzer"""
    print("\n" + "="*50)
    print("Testing Advanced Analyzer")
    print("="*50)
    
    analyzer = AdvancedAnalyzer()
    frames = create_test_frames(15)
    
    result = analyzer.analyze(frames)
    
    print(f"Available: {result.get('available', False)}")
    print(f"Advanced Score: {result.get('advanced_score', 0):.3f}")
    print(f"Confidence: {result.get('confidence', 0):.3f}")
    print(f"Assessment: {result.get('assessment', 'N/A')}")
    
    details = result.get('details', {})
    if details.get('lip_sync'):
        print(f"Lip Sync Score: {details['lip_sync'].get('score', 0):.3f}")
    if details.get('breathing'):
        print(f"Breathing Detected: {details['breathing'].get('breathing_detected', False)}")
    
    return result


def test_ensemble():
    """Test ensemble decision"""
    print("\n" + "="*50)
    print("Testing Ensemble Decision")
    print("="*50)
    
    # Create mock results
    bio_result = {
        "pulse_detected": True,
        "bpm": 72,
        "snr": 8.5,
        "confidence": 0.75
    }
    
    physics_result = {
        "available": True,
        "is_real": True,
        "is_suspicious": False,
        "confidence": 0.8,
        "findings": ["Natural skin texture", "Consistent lighting"]
    }
    
    temporal_result = {
        "available": True,
        "temporal_consistency": 0.85,
        "confidence": 0.8
    }
    
    ensemble = EnsembleDecision()
    result = ensemble.make_decision(bio_result, physics_result, None, temporal_result)
    
    print(f"Verdict: {result.get('verdict', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 0):.3f}")
    print(f"Authenticity Score: {result.get('authenticity_score', 0):.3f}")
    print(f"Real Indicators: {result.get('real_indicators_count', 0)}")
    print(f"Fake Indicators: {result.get('fake_indicators_count', 0)}")
    print(f"\nEvidence:")
    for evidence in result.get('evidence', [])[:5]:
        print(f"  {evidence}")
    
    if result.get('summary'):
        print(f"\nSummary: {result['summary']}")
    
    return result


def test_gemini_analyzer():
    """Test Gemini analyzer (requires API key)"""
    print("\n" + "="*50)
    print("Testing Gemini Analyzer")
    print("="*50)
    
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  GEMINI_API_KEY not set. Skipping Gemini test.")
        return None
    
    analyzer = GeminiAnalyzer()
    frames = create_test_frames(5)  # Gemini only needs a few frames
    
    result = analyzer.analyze(frames)
    
    print(f"Available: {result.get('available', False)}")
    print(f"Is Real: {result.get('is_real', 'N/A')}")
    print(f"Is Suspicious: {result.get('is_suspicious', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 0):.3f}")
    print(f"Assessment: {result.get('assessment', 'N/A')}")
    
    if result.get('real_indicators'):
        print(f"Real Indicators: {len(result['real_indicators'])}")
    if result.get('fake_indicators'):
        print(f"Fake Indicators: {len(result['fake_indicators'])}")
    
    return result


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Veritas-AI Module Test Suite")
    print("="*60)
    
    try:
        # Test individual modules
        bio_result = test_rppg_analyzer()
        temporal_result = test_temporal_analyzer()
        advanced_result = test_advanced_analyzer()
        gemini_result = test_gemini_analyzer()
        
        # Test ensemble
        ensemble_result = test_ensemble()
        
        print("\n" + "="*60)
        print("All Tests Completed!")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        print(f"\n❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Import cv2 for test frame creation
    try:
        import cv2
    except ImportError:
        print("⚠️  OpenCV not available. Some tests may fail.")
    
    success = run_all_tests()
    sys.exit(0 if success else 1)

