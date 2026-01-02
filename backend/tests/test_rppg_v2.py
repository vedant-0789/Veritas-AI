
import numpy as np
import sys
import os
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.rppg import RPPGAnalyzer

def generate_synthetic_pulse(fps=15, duration=3, bpm=72, noise_level=0.1):
    """
    Generate a synthetic pulse signal for multi-ROI consensus testing.
    """
    t = np.linspace(0, duration, int(fps * duration))
    freq = bpm / 60.0
    
    # Pure pulse signal
    pulse = 0.5 * np.sin(2 * np.pi * freq * t)
    
    # Generate 3 similar signals with different noise
    signals = {}
    for roi in ["forehead", "left_cheek", "right_cheek"]:
        noise = np.random.normal(0, noise_level, len(t))
        # Add a slight trend to test detrending
        trend = 0.05 * t
        # Convert to RGB-like (just repeat for G, B slightly less)
        # In rPPG, Green has the strongest pulse signal
        g_channel = 128 + (pulse + noise + trend) * 5
        r_channel = 120 + (pulse * 0.5 + noise) * 3
        b_channel = 110 + (pulse * 0.4 + noise) * 3
        
        signals[roi] = np.stack([r_channel, g_channel, b_channel], axis=1)
        
    return signals, bpm

def test_rppg_logic():
    print("Testing Updated RPPG Logic...")
    analyzer = RPPGAnalyzer()
    
    fps = 15
    duration = 3
    expected_bpm = 75
    
    # 1. Test with clean signal
    print(f"\nScenario 1: Clean signal ({expected_bpm} BPM)")
    roi_data, _ = generate_synthetic_pulse(fps, duration, bpm=expected_bpm, noise_level=0.01)
    
    # Mocking _extract_roi_signals to return our synthetic data
    analyzer._extract_roi_signals = lambda frames: roi_data
    
    # We need to pass some mock frames to keep analyze() happy
    mock_frames = [{"data": b"", "timestamp": i/fps} for i in range(len(list(roi_data.values())[0]))]
    
    result = analyzer.analyze(mock_frames, fps=fps)
    print(f"  Result: {result}")
    print(f"  Pulse Detected: {result.get('pulse_detected')}")
    print(f"  BPM: {result.get('bpm')} (Expected: {expected_bpm})")
    print(f"  SNR: {result.get('snr')}")
    print(f"  Confidence: {result.get('confidence')}")
    
    # 2. Test with noisy signal (Detrending & MA test)
    print(f"\nScenario 2: Noisy & Drifting signal ({expected_bpm} BPM)")
    roi_data_noisy, _ = generate_synthetic_pulse(fps, duration, bpm=expected_bpm, noise_level=0.2)
    analyzer._extract_roi_signals = lambda frames: roi_data_noisy
    
    result_noisy = analyzer.analyze(mock_frames, fps=fps)
    print(f"  Pulse Detected: {result_noisy.get('pulse_detected')}")
    print(f"  BPM: {result_noisy.get('bpm')} (Expected: {expected_bpm})")
    print(f"  SNR: {result_noisy.get('snr')}")
    
    # 3. Test for Disconsensus (Fake indicator)
    print("\nScenario 3: Disconsensus (Different BPMs in ROIs)")
    f_data, _ = generate_synthetic_pulse(fps, duration, bpm=60, noise_level=0.05)
    l_data, _ = generate_synthetic_pulse(fps, duration, bpm=90, noise_level=0.05)
    r_data, _ = generate_synthetic_pulse(fps, duration, bpm=120, noise_level=0.05)
    
    bad_data = {
        "forehead": f_data["forehead"],
        "left_cheek": l_data["left_cheek"],
        "right_cheek": r_data["right_cheek"]
    }
    analyzer._extract_roi_signals = lambda frames: bad_data
    
    result_bad = analyzer.analyze(mock_frames, fps=fps)
    print(f"  Pulse Detected: {result_bad.get('pulse_detected')}")
    if not result_bad.get('pulse_detected'):
        print("  ✅ Correctly rejected due to lack of consensus")
    else:
        print("  ❌ Failed to reject disconsensus signal")

if __name__ == "__main__":
    test_rppg_logic()
