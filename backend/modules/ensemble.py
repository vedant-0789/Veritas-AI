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
        # Balanced approach: 50/50 baseline
        self.bio_weight = 0.5
        self.physics_weight = 0.5
        
        # Thresholds
        self.high_confidence_threshold = 0.75
        self.low_confidence_threshold = 0.35
    
    def make_decision(self, bio_result: Dict, physics_result: Dict, vision_result: Optional[Dict] = None, temporal_result: Optional[Dict] = None) -> Dict:
        """
        Enhanced decision logic with better real/fake discrimination.
        Combines Bio-Guard, Physics-Guard, and optionally Vision API results.
        
        Args:
            bio_result: Result from rPPG Bio-Guard module
            physics_result: Result from Gemini Physics-Guard module
            vision_result: Optional result from Google Vision API
        
        Returns:
            Final verdict with confidence and evidence
        """
        evidence = []
        real_indicators = []
        fake_indicators = []
        
        # Reset weights to defaults
        self.bio_weight = 0.5
        self.physics_weight = 0.5
        
        # Extract Bio-Guard signals
        bio_confidence = bio_result.get("confidence", 0.0)
        pulse_detected = bio_result.get("pulse_detected", False)
        is_synthetic = bio_result.get("is_synthetic", False)
        bpm = bio_result.get("bpm")
        snr = bio_result.get("snr", 0.0)
        
        # Extract Physics-Guard signals
        physics_available = physics_result.get("available", False)
        physics_confidence = physics_result.get("confidence", 0.5)
        is_suspicious = physics_result.get("is_suspicious", None)
        is_real = physics_result.get("is_real", None)  # New field from enhanced prompt
        physics_findings = physics_result.get("findings", [])
        
        # REAL VIDEO INDICATORS (Positive Evidence)
        
        # Strong Real Indicator 1: Biological pulse with good quality
        # More lenient thresholds for better detection
        if pulse_detected and snr > 6 and bpm and 50 <= bpm <= 120:
            real_indicators.append(("strong_pulse", 0.40))
            evidence.append(f"✅ Strong biological pulse detected: {int(bpm)} BPM (SNR: {snr:.1f})")
        elif pulse_detected and snr > 3 and bio_confidence > 0.4:
            real_indicators.append(("moderate_pulse", 0.30))
            evidence.append(f"✅ Biological pulse detected: {int(bpm) if bpm else '?'} BPM")
        elif pulse_detected and snr > 2:
            real_indicators.append(("weak_pulse", 0.20))
            evidence.append(f"✅ Weak biological pulse detected: {int(bpm) if bpm else '?'} BPM (may be compressed video)")
        
        # Strong Real Indicator 2: AI confirms no artifacts
        if physics_available:
            if is_real is True and physics_confidence > 0.7:
                real_indicators.append(("ai_confirms_real", 0.30))
                evidence.append("✅ AI analysis confirms authentic human characteristics")
            elif is_suspicious is False and physics_confidence > 0.7:
                real_indicators.append(("no_artifacts", 0.25))
                evidence.append("✅ No AI manipulation artifacts detected")
            elif is_suspicious is True and physics_confidence > 0.7:
                fake_indicators.append(("suspicious_artifacts", 0.35))
                evidence.append("❌ AI detected manipulation artifacts")
                for finding in physics_findings[:2]:
                    evidence.append(f"   • {finding}")
        
        # FAKE VIDEO INDICATORS (Negative Evidence)
        
        # Strong Fake Indicator 1: No pulse with low SNR
        # More strict - only flag as fake if really no signal
        if not pulse_detected and snr < 0.5:
            fake_indicators.append(("no_pulse", 0.35))
            evidence.append("❌ No biological pulse signal detected")
        elif not pulse_detected and snr < 1.5:
            fake_indicators.append(("weak_pulse", 0.25))
            evidence.append("❌ Very weak or no biological signals")
        elif not pulse_detected and snr < 2.5:
            fake_indicators.append(("very_weak_pulse", 0.15))
            evidence.append("⚠️ Weak biological signals (possible deepfake or heavy compression)")
        
        # Strong Fake Indicator 2: AI strongly indicates fake
        if physics_available and is_suspicious is True and physics_confidence > 0.6:
            fake_indicators.append(("ai_detected_fake", 0.45))
            evidence.append("🤖 AI analysis detected specific manipulation artifacts")
            
        # New: Synthetic Pulse Detection
        if is_synthetic:
            fake_indicators.append(("synthetic_pulse", 0.50))
            evidence.append("🚨 Suspiciously perfect periodic signal detected (Synthetic Pulse Artifact)")
        
        # Vision API indicators (if available)
        if vision_result and vision_result.get("available"):
            face_confidence = vision_result.get("face_confidence", 0)
            if face_confidence > 0.8:
                real_indicators.append(("vision_high_quality", 0.10))
                evidence.append("✅ High-quality face detection (Vision API)")
        
        # Temporal consistency indicators (if available)
        if temporal_result and temporal_result.get("available"):
            temporal_consistency = temporal_result.get("temporal_consistency", 0.5)
            temporal_findings = temporal_result.get("findings", [])
            
            if temporal_consistency > 0.75:
                real_indicators.append(("high_temporal_consistency", 0.20))
                evidence.append("✅ High temporal consistency detected")
                for finding in temporal_findings[:2]:
                    if "✅" in finding or "consistent" in finding.lower():
                        evidence.append(f"   • {finding}")
            elif temporal_consistency < 0.4:
                fake_indicators.append(("low_temporal_consistency", 0.25))
                evidence.append("❌ Low temporal consistency (possible manipulation)")
                for finding in temporal_findings[:2]:
                    if "❌" in finding or "inconsistent" in finding.lower():
                        evidence.append(f"   • {finding}")
        
        # Adjust weights based on available data
        if not physics_available:
            self.bio_weight = 0.7
            self.physics_weight = 0.1
            if temporal_result and temporal_result.get("available"):
                self.bio_weight = 0.5
            evidence.append("ℹ️ Using Bio-Guard primarily (AI analysis unavailable)")
        elif temporal_result and temporal_result.get("available"):
            # Rebalance weights when temporal analysis is available
            self.bio_weight = 0.4
            self.physics_weight = 0.4
            # Temporal gets implicit weight through indicators
        
        # Calculate REAL score (0-1, higher = more real)
        real_score = 0.5  # Neutral baseline
        
        # Add positive evidence
        for indicator, weight in real_indicators:
            if indicator == "strong_pulse":
                real_score += weight * min(1.0, bio_confidence)
            elif indicator == "moderate_pulse":
                real_score += weight * min(1.0, bio_confidence * 0.8)
            elif indicator in ["ai_confirms_real", "no_artifacts"]:
                real_score += weight * physics_confidence
            elif indicator == "vision_high_quality":
                real_score += weight
            elif indicator == "high_temporal_consistency":
                temporal_consistency = temporal_result.get("temporal_consistency", 0.5) if temporal_result else 0.5
                real_score += weight * temporal_consistency
        
        # Subtract negative evidence
        for indicator, weight in fake_indicators:
            if indicator == "no_pulse":
                real_score -= weight * (1.0 - min(bio_confidence, 0.3))
            elif indicator == "weak_pulse":
                real_score -= weight * 0.5
            elif indicator == "suspicious_artifacts":
                real_score -= weight * physics_confidence
            elif indicator == "strong_ai_fake":
                real_score -= weight * min(1.0, physics_confidence)
            elif indicator == "low_temporal_consistency":
                temporal_consistency = temporal_result.get("temporal_consistency", 0.5) if temporal_result else 0.5
                real_score -= weight * (1.0 - temporal_consistency)
        
        # Special overrides for very strong evidence
        # Override 1: Very strong pulse = definitely real (tightened thresholds)
        if pulse_detected and 5 <= snr <= 15 and bio_confidence > 0.80 and 60 <= bpm <= 95 and not is_synthetic:
            real_score = max(real_score, 0.90)
            if "🔬 Strong biological authenticity" not in str(evidence):
                evidence.insert(0, "🔬 Strong biological authenticity signals detected")
        
        # Override 1b: If pulse is TOO strong, it's a fake
        if snr > 20:
            real_score = min(real_score, 0.15)
            evidence.append("🚨 Excessive Signal-to-Noise ratio detected (Common in AI generation)")
        
        # Override 1b: Good pulse + AI confirms real = very high confidence real
        if pulse_detected and snr > 5 and is_real is True and physics_confidence > 0.75:
            real_score = max(real_score, 0.88)
        
        # Override 2: Strong AI fake + no pulse = definitely fake (high confidence)
        if not pulse_detected and snr < 1.5 and physics_available and is_suspicious and physics_confidence > 0.80:
            real_score = min(real_score, 0.12)
            if "🚨 Multiple indicators" not in str(evidence):
                evidence.insert(0, "🚨 Multiple strong indicators of synthetic content")
        
        # Override 2b: Very strong AI fake signal = high confidence fake
        if physics_available and is_suspicious and physics_confidence > 0.90:
            real_score = min(real_score, 0.20)
        
        # Override 3: AI confirms real + any pulse = likely real
        if is_real is True and physics_confidence > 0.85 and pulse_detected:
            real_score = max(real_score, 0.85)
        
        # Override 4: Strong temporal consistency + pulse = likely real
        if temporal_result and temporal_result.get("available"):
            temporal_consistency = temporal_result.get("temporal_consistency", 0.5)
            if temporal_consistency > 0.85 and pulse_detected:
                real_score = max(real_score, 0.88)
                if "⏱️ High temporal consistency" not in str(evidence):
                    evidence.insert(0, "⏱️ High temporal consistency with biological signals")
        
        # Override 5: Very low temporal consistency + no pulse = likely fake
        if temporal_result and temporal_result.get("available"):
            temporal_consistency = temporal_result.get("temporal_consistency", 0.5)
            if temporal_consistency < 0.3 and not pulse_detected:
                real_score = min(real_score, 0.20)
                if "🚨 Temporal inconsistencies" not in str(evidence):
                    evidence.insert(0, "🚨 Temporal inconsistencies detected")
        
        # Clamp to [0, 1]
        real_score = max(0.0, min(1.0, real_score))
        
        # Determine verdict with improved thresholds and confidence scoring
        # Real videos should show 80-95% confidence
        # Fake videos should show 85-100% confidence
        
        if real_score >= 0.65:  # 65%+ = LIKELY REAL
            verdict = "LIKELY_REAL"
            verdict_display = "✅ LIKELY REAL"
            # For real videos: map 0.65-1.0 to 0.75-0.95 confidence
            # Strong real evidence (0.85+) gets 90-95% confidence
            if real_score >= 0.85:
                confidence = 0.90 + (real_score - 0.85) * 0.33  # 0.90 to 0.95
            elif real_score >= 0.75:
                confidence = 0.85 + (real_score - 0.75) * 0.50  # 0.85 to 0.90
            else:
                confidence = 0.75 + (real_score - 0.65) * 0.50  # 0.75 to 0.85
            
        elif real_score <= 0.35:  # 35%- = LIKELY FAKE
            verdict = "LIKELY_FAKE"
            verdict_display = "❌ LIKELY FAKE"
            # For fake videos: map 0.35-0.0 to 0.85-1.0 confidence
            # Strong fake evidence (0.15-) gets 95-100% confidence
            if real_score <= 0.15:
                confidence = 0.95 + (0.15 - real_score) * 0.33  # 0.95 to 1.0
            elif real_score <= 0.25:
                confidence = 0.90 + (0.25 - real_score) * 0.50  # 0.90 to 0.95
            else:
                confidence = 0.85 + (0.35 - real_score) * 0.50  # 0.85 to 0.90
                
        else:  # 35-65% = UNCERTAIN
            verdict = "UNCERTAIN"
            verdict_display = "⚠️ UNCERTAIN"
            # For uncertain: lower confidence
            confidence = 0.40 + (abs(real_score - 0.50) * 0.40)
            
        # Final penalty: If AI is uncertain but Score is high, reduce confidence
        if verdict == "LIKELY_REAL" and physics_available and physics_confidence < 0.5:
            confidence *= 0.85
            evidence.append("⚠️ Bio-Guard is confident but Physics-Guard remains uncertain")
        
        # Generate summary
        summary = self._generate_summary(verdict, bio_result, physics_result)
        
        return {
            "verdict": verdict,
            "verdict_display": verdict_display,
            "confidence": round(confidence, 3),
            "authenticity_score": round(real_score, 3),
            "evidence": evidence,
            "summary": summary,
            "real_indicators_count": len(real_indicators),
            "fake_indicators_count": len(fake_indicators),
            "breakdown": {
                "bio_guard": {
                    "score": round(bio_confidence if pulse_detected else 0.0, 3),
                    "weight": self.bio_weight,
                    "pulse_detected": pulse_detected,
                    "bpm": bpm,
                    "snr": snr
                },
                "physics_guard": {
                    "score": round(physics_confidence if physics_available else 0.5, 3),
                    "weight": self.physics_weight,
                    "available": physics_available,
                    "is_real": is_real,
                    "is_suspicious": is_suspicious
                },
                "vision_guard": {
                    "available": vision_result.get("available", False) if vision_result else False
                },
                "temporal_guard": {
                    "available": temporal_result.get("available", False) if temporal_result else False,
                    "score": round(temporal_result.get("temporal_consistency", 0.5), 3) if temporal_result else 0.5
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
