from typing import Dict, Any
import numpy as np

def fuse(facial: Dict[str, Any], voice: Dict[str, Any], kd: Dict[str, Any], env: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced fusion decision engine with:
    - Multi-modal emotion aggregation
    - Environmental context integration
    - Coercion detection
    - Adaptive response generation
    - Confidence scoring with multiple factors
    """
    
    # Extract emotion and biometric scores
    stress_f = float(facial.get("stress", 0.0))
    stress_v = float(voice.get("stress", 0.0))
    match = float(kd.get("match", 0.0))
    anomaly = float(kd.get("anomaly", 0.0))
    kd_confidence = float(kd.get("confidence", 0.5))
    
    # Extract environmental factors
    env_flags = env.get("flags", {})
    env_stability = float(env.get("stability", 0.5))
    coercion_risk = float(env.get("coercion_risk", 0.0))
    env_quality = float(env.get("quality_score", 0.5))
    risk_level = env.get("risk_level", "low")
    env_recommendations = env.get("recommendations", [])
    
    # Weighted stress calculation (facial + voice) - REDUCED IMPACT
    # Apply dampening factor to make stress less sensitive
    stress = (0.5 * stress_f + 0.5 * stress_v) * 0.7  # 30% reduction
    
    # Overall biometric score
    biometric_score = (
        (1.0 - stress) * 0.4 +  # Lower stress is better
        match * 0.4 +  # Keystroke match
        (1.0 - anomaly) * 0.2  # Lower anomaly is better
    )
    
    # Environmental suitability score
    env_score = env_stability * 0.6 + env_quality * 0.4
    
    # Combined authentication score
    auth_score = (
        biometric_score * 0.7 +  # Biometric factors (70%)
        env_score * 0.3  # Environmental factors (30%)
    )
    
    # Get dominant emotions
    facial_probs = facial.get("probs", {})
    voice_probs = voice.get("probs", {})
    
    dominant_facial = max(facial_probs.items(), key=lambda x: x[1])[0] if facial_probs else "neutral"
    dominant_voice = max(voice_probs.items(), key=lambda x: x[1])[0] if voice_probs else "calm"
    
    # Define positive and neutral emotions
    positive_emotions = ["happy", "surprised", "calm", "neutral"]
    negative_emotions = ["sad", "angry", "fear", "fearful", "disgust"]
    
    # Check if both facial and voice emotions are positive/neutral
    facial_is_positive = dominant_facial in positive_emotions
    voice_is_positive = dominant_voice in positive_emotions
    
    print(f"DEBUG FUSION - Facial: {dominant_facial} ({'✓' if facial_is_positive else '✗'}), Voice: {dominant_voice} ({'✓' if voice_is_positive else '✗'})")
    
    # Decision logic with STRICT emotion-based access control
    decision = "permit"
    reason = []
    alert_level = "normal"
    
    # CRITICAL: Both emotions must be positive/neutral for access
    if not facial_is_positive or not voice_is_positive:
        decision = "deny"
        if not facial_is_positive and not voice_is_positive:
            reason.append(f"Negative emotions detected - Facial: {dominant_facial}, Voice: {dominant_voice}")
        elif not facial_is_positive:
            reason.append(f"Negative facial emotion detected: {dominant_facial}")
        else:
            reason.append(f"Negative voice emotion detected: {dominant_voice}")
        alert_level = "high"
        print(f"🚫 ACCESS DENIED - Emotion check failed")
    
    # Additional critical denial conditions
    elif coercion_risk > 0.85:
        decision = "deny"
        reason.append("High coercion risk detected")
        alert_level = "critical"
    
    elif env_flags.get("shouting") and stress > 0.8:
        decision = "deny"
        reason.append("Shouting detected - potential duress")
        alert_level = "critical"
    
    elif env_flags.get("very_loud") and stress > 0.85:
        decision = "deny"
        reason.append("Very loud environment with elevated stress")
        alert_level = "high"
    
    elif anomaly > 0.85:
        decision = "deny"
        reason.append("Keystroke pattern anomaly detected")
        alert_level = "high"
    
    elif match < 0.2 and anomaly > 0.8:
        decision = "deny"
        reason.append("Keystroke pattern does not match enrolled profile")
        alert_level = "medium"
    
    # Delay conditions (suspicious but not critical) - MUCH MORE LENIENT
    elif stress > 0.9:
        decision = "delay"
        reason.append("Very high emotional stress detected")
        alert_level = "medium"
    
    elif coercion_risk > 0.7:
        decision = "delay"
        reason.append("Moderate coercion risk detected")
        alert_level = "medium"
    
    elif stress > 0.85 and env_stability < 0.3:
        decision = "delay"
        reason.append("Elevated stress in unstable environment")
        alert_level = "medium"
    
    elif env_flags.get("very_dark") and stress > 0.7:
        decision = "delay"
        reason.append("Very poor lighting with high stress")
        alert_level = "low"
    
    elif env_flags.get("high_pitch") and env_flags.get("voice_tremor") and stress > 0.8:
        decision = "delay"
        reason.append("Voice characteristics suggest distress")
        alert_level = "medium"
    
    elif anomaly > 0.85 and match < 0.2:
        decision = "delay"
        reason.append("Keystroke pattern shows significant anomalies")
        alert_level = "low"
    
    elif match < 0.15:
        decision = "delay"
        reason.append("Keystroke pattern differs significantly from usual")
        alert_level = "low"
    
    # Permit with warnings - VERY LENIENT
    else:
        decision = "permit"
        
        # Good keystroke match
        if match > 0.3:
            reason.append("Keystroke pattern verified")
        elif match > 0.15:
            reason.append("Keystroke pattern acceptable")
        else:
            reason.append("Authentication successful")
        
        if stress > 0.7:
            reason.append("Note: Elevated stress detected")
            alert_level = "low"
        
        if not reason:
            reason.append("All checks passed")
    
    # Confidence and stress adjustment based on decision type
    # PERMIT: High confidence (0.75-0.95), Low stress (0.0-0.3)
    # DELAY: Medium confidence (0.45-0.65), Medium-low stress (0.3-0.6)
    # DENY: Low confidence (0.15-0.45), High-low stress (0.5-0.9)
    
    if decision == "permit":
        # High confidence for permit
        base_confidence = 0.75 + (match * 0.2)  # 0.75 to 0.95
        confidence = min(0.95, max(0.75, base_confidence))
        
        # Low stress for permit (reduce stress significantly)
        stress = stress * 0.4  # Reduce to 0.0-0.3 range
        stress = min(0.3, stress)
        
    elif decision == "delay":
        # Medium confidence for delay
        base_confidence = 0.45 + (match * 0.2)  # 0.45 to 0.65
        confidence = min(0.65, max(0.45, base_confidence))
        
        # Medium-low stress for delay
        stress = stress * 0.6  # Reduce to medium-low range
        stress = min(0.6, max(0.3, stress))
        
    elif decision == "deny":
        # Low confidence for deny
        base_confidence = 0.15 + (match * 0.3)  # 0.15 to 0.45
        confidence = min(0.45, max(0.15, base_confidence))
        
        # High-low stress for deny (keep stress in reasonable range)
        stress = stress * 0.8  # Keep in 0.5-0.9 range
        stress = min(0.9, max(0.5, stress))
    
    else:
        # Fallback
        confidence = 0.5
    
    confidence = float(confidence)
    stress = float(stress)
    
    # Debug: Print final decision with confidence and stress
    print(f"DEBUG FUSION - Decision: {decision.upper()}, Confidence: {confidence:.2f}, Stress: {stress:.2f}")
    
    # Generate adaptive guidance
    guidance = generate_guidance(decision, stress, env_flags, coercion_risk, env_recommendations, dominant_facial, dominant_voice)
    
    # System adaptation recommendations
    ui_adaptation = generate_ui_adaptation(stress, decision, env_flags)
    
    # Mental health support trigger
    mental_health_alert = stress > 0.75 or (stress > 0.6 and decision == "delay")
    
    # Emotional profile
    emotional_state = categorize_emotion(stress_f, stress_v, facial, voice)
    
    return {
        "decision": decision,
        "confidence": float(confidence),
        "score": float(auth_score),
        "stress": float(stress),
        "stress_facial": float(stress_f),
        "stress_voice": float(stress_v),
        "reason": ", ".join(reason) if reason else "Authentication successful",
        "guidance": guidance,
        "alert_level": alert_level,
        "coercion_risk": float(coercion_risk),
        "environmental_quality": float(env_quality),
        "biometric_score": float(biometric_score),
        "ui_adaptation": ui_adaptation,
        "mental_health_alert": mental_health_alert,
        "emotional_state": emotional_state,
        "recommendations": env_recommendations,
        "suitable_environment": env.get("suitable_for_auth", True),
        "facial_emotion": dominant_facial,
        "voice_emotion": dominant_voice,
        "emotion_check_passed": facial_is_positive and voice_is_positive
    }


def generate_guidance(decision: str, stress: float, env_flags: Dict, coercion_risk: float, env_recommendations: list, facial_emotion: str = None, voice_emotion: str = None) -> str:
    """Generate context-aware guidance for the user."""
    
    if decision == "deny":
        # Check if denial is due to negative emotions
        if facial_emotion and voice_emotion:
            positive_emotions = ["happy", "surprised", "calm", "neutral"]
            if facial_emotion not in positive_emotions or voice_emotion not in positive_emotions:
                return f"Access denied. Negative emotions detected (Facial: {facial_emotion}, Voice: {voice_emotion}). Please relax and try again when you feel calm."
        
        if coercion_risk > 0.5:
            return "Access denied. Environmental conditions suggest potential duress. Please contact support if you need assistance."
        elif env_flags.get("very_loud") or env_flags.get("shouting"):
            return "Access denied. Please move to a quieter, calmer location and try again."
        elif env_flags.get("very_dark"):
            return "Access denied. Please ensure adequate lighting and try again."
        else:
            return "Access denied. Please verify your credentials and ensure you're in a suitable environment."
    
    elif decision == "delay":
        if stress > 0.7:
            return "High stress detected. Take a few deep breaths, relax for a moment, and try again."
        elif stress > 0.5 and env_flags.get("noisy"):
            return "Elevated stress in a noisy environment. Find a quieter space and try again when you feel calmer."
        elif env_flags.get("dark"):
            return "Poor lighting detected. Please improve lighting conditions and try again."
        elif env_recommendations:
            return f"Please address: {', '.join(env_recommendations[:2])} and try again."
        else:
            return "Authentication delayed. Please wait a moment and try again."
    
    else:  # permit
        if stress > 0.6:
            return "Access granted. You seem a bit stressed - consider taking a break soon."
        elif stress > 0.4:
            return "Access granted. Welcome! Remember to take care of yourself."
        else:
            return "Access granted. Welcome! You're doing great!"


def generate_ui_adaptation(stress: float, decision: str, env_flags: Dict) -> Dict[str, Any]:
    """Generate UI adaptation recommendations based on user state."""
    
    adaptations = {
        "color_scheme": "default",
        "reduce_animations": False,
        "show_wellness_tips": False,
        "restrict_features": False,
        "suggest_break": False,
        "calming_mode": False
    }
    
    # High stress adaptations
    if stress > 0.7:
        adaptations["color_scheme"] = "calming"  # Blue/green tones
        adaptations["reduce_animations"] = True
        adaptations["show_wellness_tips"] = True
        adaptations["suggest_break"] = True
        adaptations["calming_mode"] = True
    
    elif stress > 0.5:
        adaptations["color_scheme"] = "soft"
        adaptations["show_wellness_tips"] = True
    
    # Restrict features if denied
    if decision == "deny":
        adaptations["restrict_features"] = True
    
    # Dark environment adaptation
    if env_flags.get("dark") or env_flags.get("very_dark"):
        adaptations["color_scheme"] = "high_contrast"
    
    return adaptations


def categorize_emotion(stress_f: float, stress_v: float, facial: Dict, voice: Dict) -> str:
    """Categorize overall emotional state."""
    
    avg_stress = (stress_f + stress_v) / 2
    
    # Get dominant facial emotion
    facial_probs = facial.get("probs", {})
    dominant_facial = max(facial_probs.items(), key=lambda x: x[1])[0] if facial_probs else "neutral"
    
    # Get dominant voice emotion
    voice_probs = voice.get("probs", {})
    dominant_voice = max(voice_probs.items(), key=lambda x: x[1])[0] if voice_probs else "calm"
    
    # Categorize based on stress and emotions (more optimistic)
    if avg_stress > 0.75:
        return "highly_stressed"
    elif avg_stress > 0.6:
        return "moderately_stressed"
    elif dominant_facial in ["happy", "surprise"] or dominant_voice in ["happy", "calm"]:
        return "positive"
    elif avg_stress < 0.3:
        return "calm"
    elif dominant_facial in ["sad", "fear"] and avg_stress > 0.5:
        return "negative"
    elif dominant_facial == "angry" or dominant_voice == "angry":
        return "agitated"
    else:
        return "neutral"
