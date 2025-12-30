"""
Veritas-AI Ensemble Module - Decision Fusion
Combines Bio-Guard (rPPG) and Physics-Guard (Gemini) results for final verdict.
"""

from typing import Dict, List, Optional


class EnsembleDecision:
    """
    Ensemble Decision Module
    Combines results from Bio-Guard and Physics-Guard for final deepfake verdict.
    """
    
    def __init__(self):
        """Initialize with default weights"""
        # Bio-Guard (rPPG) is primary - biological signals are hard to fake
        self.bio_weight = 0.6
        # Physics-Guard (Gemini AI) is secondary - provides context
        self.physics_weight = 0.4
        
        # Thresholds
        self.high_confidence_threshold = 0.75
        self.low_confidence_threshold = 0.35
    
    def make_decision(self, bio_result: Dict, physics_result: Dict) -> Dict:
        """
        Make final decision combining Bio-Guard and Physics-Guard results.
        
        Args:
            bio_result: Result from rPPG Bio-Guard module
            physics_result: Result from Gemini Physics-Guard module
        
        Returns:
            Final verdict with confidence and evidence
        """
        evidence = []
        
        # Extract Bio-Guard signals
        bio_confidence = bio_result.get("confidence", 0.0)
        pulse_detected = bio_result.get("pulse_detected", False)
        bpm = bio_result.get("bpm")
        snr = bio_result.get("snr", 0.0)
        bio_assessment = bio_result.get("assessment", "")
        
        # Extract Physics-Guard signals
        physics_available = physics_result.get("available", False)
        physics_confidence = physics_result.get("confidence", 0.5)
        is_suspicious = physics_result.get("is_suspicious", None)
        physics_findings = physics_result.get("findings", [])
        physics_assessment = physics_result.get("assessment", "")
        
        # Calculate individual scores
        # Bio score: high if pulse detected with good confidence
        if pulse_detected and bio_confidence > 0.6:
            bio_score = bio_confidence  # Real signal
            evidence.append(f"✅ Biological pulse detected: {int(bpm)} BPM (SNR: {snr:.1f})")
        elif pulse_detected and bio_confidence > 0.3:
            bio_score = bio_confidence * 0.8  # Weak signal
            evidence.append(f"⚠️ Weak biological signal detected: {int(bpm) if bpm else '?'} BPM")
        else:
            bio_score = 1 - max(bio_confidence, 0.3)  # No pulse = likely fake
            evidence.append("❌ No biological pulse detected")
        
        # Physics score: low if suspicious artifacts found
        if physics_available:
            if is_suspicious is True and physics_confidence > 0.6:
                physics_score = 1 - physics_confidence  # Suspicious = low score
                evidence.append(f"❌ AI detected suspicious artifacts")
                for finding in physics_findings[:3]:  # Limit to 3 findings
                    evidence.append(f"   • {finding}")
            elif is_suspicious is False and physics_confidence > 0.6:
                physics_score = physics_confidence  # Not suspicious = high score
                evidence.append(f"✅ AI found no manipulation artifacts")
            else:
                physics_score = 0.5  # Uncertain
                evidence.append(f"⚠️ AI analysis inconclusive")
        else:
            physics_score = 0.5  # No physics analysis available
            evidence.append("ℹ️ AI analysis not available (Gemini API key not configured)")
            # Adjust weights to rely more on bio
            self.bio_weight = 0.9
            self.physics_weight = 0.1
        
        # Weighted ensemble score
        # Higher score = more likely REAL
        final_score = (self.bio_weight * bio_score + self.physics_weight * physics_score)
        
        # Special cases that override ensemble
        
        # Case 1: Strong pulse with high SNR is very strong evidence of authenticity
        if pulse_detected and snr > 10 and bio_confidence > 0.8:
            final_score = max(final_score, 0.9)
            if "Strong biological signals" not in str(evidence):
                evidence.insert(0, "🔬 Strong biological authenticity signals")
        
        # Case 2: No pulse at all is strong evidence of fake (unless video is too compressed)
        if not pulse_detected and snr < 1:
            if physics_available and is_suspicious:
                final_score = min(final_score, 0.2)
                evidence.insert(0, "🚨 Multiple indicators of synthetic content")
        
        # Case 3: Gemini strongly suspicious + weak bio = likely fake
        if is_suspicious and physics_confidence > 0.8 and bio_confidence < 0.5:
            final_score = min(final_score, 0.3)
        
        # Determine verdict
        if final_score >= self.high_confidence_threshold:
            verdict = "LIKELY_REAL"
            verdict_display = "✅ LIKELY REAL"
        elif final_score <= self.low_confidence_threshold:
            verdict = "LIKELY_FAKE"
            verdict_display = "❌ LIKELY FAKE"
        else:
            verdict = "UNCERTAIN"
            verdict_display = "⚠️ UNCERTAIN"
        
        # Calculate final confidence in the verdict
        if verdict == "UNCERTAIN":
            # Confidence in uncertainty is based on how close to middle
            verdict_confidence = 1 - abs(final_score - 0.5) * 2
        else:
            # Confidence is based on how far from threshold
            if verdict == "LIKELY_REAL":
                verdict_confidence = min(1.0, (final_score - 0.5) * 2)
            else:
                verdict_confidence = min(1.0, (0.5 - final_score) * 2)
        
        # Generate summary
        summary = self._generate_summary(verdict, bio_result, physics_result)
        
        return {
            "verdict": verdict,
            "verdict_display": verdict_display,
            "confidence": round(verdict_confidence, 3),
            "authenticity_score": round(final_score, 3),
            "evidence": evidence,
            "summary": summary,
            "breakdown": {
                "bio_guard": {
                    "score": round(bio_score, 3),
                    "weight": self.bio_weight,
                    "pulse_detected": pulse_detected,
                    "bpm": bpm,
                    "snr": snr
                },
                "physics_guard": {
                    "score": round(physics_score, 3),
                    "weight": self.physics_weight,
                    "available": physics_available,
                    "suspicious": is_suspicious
                }
            }
        }
    
    def _generate_summary(self, verdict: str, bio_result: Dict, physics_result: Dict) -> str:
        """Generate a human-readable summary of the analysis"""
        pulse_detected = bio_result.get("pulse_detected", False)
        bpm = bio_result.get("bpm")
        is_suspicious = physics_result.get("is_suspicious")
        
        if verdict == "LIKELY_REAL":
            if pulse_detected and bpm:
                return f"This video shows biological signs of authenticity. A pulse of {int(bpm)} BPM was detected, indicating a real human presence."
            else:
                return "This video appears authentic based on AI analysis, though biological signals were weak."
        
        elif verdict == "LIKELY_FAKE":
            reasons = []
            if not pulse_detected:
                reasons.append("no biological pulse detected")
            if is_suspicious:
                reasons.append("AI detected manipulation artifacts")
            
            reason_str = " and ".join(reasons) if reasons else "multiple indicators"
            return f"This video shows signs of synthetic generation or manipulation: {reason_str}."
        
        else:  # UNCERTAIN
            return "The analysis is inconclusive. The video may be authentic but heavily compressed, or it may be a sophisticated fake. Manual review recommended."
