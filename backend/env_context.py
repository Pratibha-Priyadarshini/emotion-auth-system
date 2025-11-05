from typing import Dict, Any
import numpy as np

def analyze_env(face_info: Dict[str, Any], voice_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced environmental context analysis with multiple factors:
    - Lighting conditions (brightness)
    - Ambient noise levels (loudness)
    - Voice characteristics (pitch variation, energy)
    - Potential coercion indicators
    - Environmental stability
    """
    
    # Extract features
    brightness = float(face_info.get("brightness", 0.5))
    contrast = float(face_info.get("contrast", 0.0))
    rms = float(voice_info.get("features", {}).get("rms", 0.0))
    zcr = float(voice_info.get("features", {}).get("zcr", 0.0))
    pitch = float(voice_info.get("features", {}).get("pitch_hz", 0.0))
    
    # Environmental flags
    flags = {}
    
    # Lighting analysis (more lenient)
    flags["dark"] = brightness < 0.2
    flags["very_dark"] = brightness < 0.1
    flags["bright"] = brightness > 0.8
    flags["low_contrast"] = contrast < 30
    
    # Noise analysis (more lenient)
    flags["noisy"] = rms > 0.75
    flags["very_loud"] = rms > 0.9
    flags["quiet"] = rms < 0.15
    
    # Voice characteristics (potential stress/coercion indicators)
    flags["high_pitch"] = pitch > 280  # Elevated pitch may indicate stress
    flags["voice_tremor"] = zcr > 0.7  # High zero-crossing rate may indicate trembling
    flags["shouting"] = rms > 0.85 and pitch > 270
    
    # Environmental stability score (0-1, higher is better) - more lenient
    stability_factors = [
        1.0 if 0.2 <= brightness <= 0.8 else 0.6,  # Good lighting (wider range)
        1.0 if rms < 0.6 else 0.5,  # Reasonable noise (more tolerant)
        1.0 if 100 <= pitch <= 300 else 0.7,  # Normal pitch range (wider)
        1.0 if contrast > 30 else 0.8,  # Good contrast (lower threshold)
    ]
    stability = float(np.mean(stability_factors))
    
    # Coercion risk assessment (more conservative)
    coercion_indicators = [
        flags["very_loud"],
        flags["shouting"],
        flags["very_dark"],
        flags["voice_tremor"] and flags["high_pitch"]
    ]
    # Weight the indicators - not all are equally important
    coercion_weights = [0.3, 0.4, 0.1, 0.2]  # Shouting is most important
    coercion_risk = sum(ind * weight for ind, weight in zip(coercion_indicators, coercion_weights))
    
    # Environmental quality score (more lenient)
    quality_score = (
        (1.0 - abs(brightness - 0.5) * 1.5) * 0.3 +  # Optimal brightness around 0.5 (less penalty)
        (1.0 - rms * 0.8) * 0.3 +  # Lower noise is better (reduced impact)
        (1.0 if 100 <= pitch <= 300 else 0.6) * 0.2 +  # Normal pitch (wider range)
        (min(contrast / 80, 1.0)) * 0.2  # Good contrast (lower threshold)
    )
    quality_score = max(0.0, min(1.0, quality_score))  # Clamp to [0, 1]
    
    # Risk level categorization (more conservative)
    if coercion_risk > 0.6 or flags["shouting"]:
        risk_level = "high"
    elif coercion_risk > 0.4 or flags["very_loud"]:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Recommendations (only for significant issues)
    recommendations = []
    if flags["very_dark"]:
        recommendations.append("Improve lighting conditions")
    if flags["very_loud"]:
        recommendations.append("Move to a quieter location")
    if flags["shouting"]:
        recommendations.append("Speak in a normal tone")
    if coercion_risk > 0.5:
        recommendations.append("Environmental conditions suggest potential duress")
    if flags["dark"] and not flags["very_dark"]:
        recommendations.append("Consider improving lighting")
    if flags["noisy"] and not flags["very_loud"]:
        recommendations.append("Environment is somewhat noisy")
    
    return {
        "brightness": brightness,
        "contrast": contrast,
        "loudness": rms,
        "pitch": pitch,
        "zcr": zcr,
        "flags": flags,
        "stability": float(stability),
        "coercion_risk": float(coercion_risk),
        "quality_score": float(quality_score),
        "risk_level": risk_level,
        "recommendations": recommendations,
        "suitable_for_auth": stability > 0.5 and coercion_risk < 0.6
    }
