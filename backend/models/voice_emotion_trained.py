"""
Voice emotion recognition using trained Random Forest model.
Falls back to heuristic if trained model not available.
"""

import numpy as np
import pickle
from pathlib import Path
from typing import Dict, Any

MODEL_PATH = Path(__file__).parent.parent / "storage" / "trained_models" / "voice_emotion_rf.pkl"
SCALER_PATH = Path(__file__).parent.parent / "storage" / "trained_models" / "voice_emotion_scaler.pkl"

# Try to load trained model
trained_model = None
scaler = None
try:
    if MODEL_PATH.exists() and SCALER_PATH.exists():
        with open(MODEL_PATH, 'rb') as f:
            trained_model = pickle.load(f)
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        print(f"Loaded trained voice emotion model from {MODEL_PATH}")
except Exception as e:
    print(f"Could not load trained model: {e}")
    print("Using heuristic fallback")

EMOTION_LABELS = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]


def analyze_voice_trained(feats: Dict[str, float]) -> Dict[str, Any]:
    """Analyze voice emotion using enhanced heuristic (RF model has limited features)."""
    # Extract features
    rms = float(feats.get("rms", 0.0))
    zcr = float(feats.get("zcr", 0.0))
    pitch = float(feats.get("pitch_hz", 0.0))
    
    # Debug: Print voice features
    print(f"DEBUG VOICE - RMS: {rms:.3f}, ZCR: {zcr:.3f}, Pitch: {pitch:.1f} Hz")
    
    # Enhanced emotion detection based on voice characteristics
    # RMS: volume/energy, ZCR: voice quality/roughness, Pitch: tone
    
    # Normalize pitch to 0-1 range (typical speech: 80-300 Hz)
    norm_pitch = min(1.0, max(0.0, (pitch - 80) / 220))
    
    # Calculate emotion probabilities with better logic
    probs = {}
    
    # Happy: moderate-high energy, moderate pitch, smooth voice
    probs["happy"] = max(0.0, min(1.0, 
        0.4 * rms + 
        0.3 * (1.0 - abs(norm_pitch - 0.6)) +  # Prefer slightly higher pitch
        0.3 * (1.0 - zcr)  # Smooth voice
    ))
    
    # Calm: low energy, low ZCR, moderate-low pitch
    probs["calm"] = max(0.0, min(1.0,
        0.4 * (1.0 - rms) +
        0.3 * (1.0 - zcr) +
        0.3 * (1.0 - abs(norm_pitch - 0.3))  # Prefer lower pitch
    ))
    
    # Sad: low energy, low pitch, smooth voice
    probs["sad"] = max(0.0, min(1.0,
        0.4 * (1.0 - rms) +
        0.3 * (1.0 - norm_pitch) +  # Lower pitch
        0.3 * (1.0 - zcr)
    ))
    
    # Angry: high energy, high ZCR, variable pitch
    probs["angry"] = max(0.0, min(1.0,
        0.5 * rms +
        0.4 * zcr +  # Rough voice
        0.1 * norm_pitch
    ))
    
    # Fearful: moderate energy, high ZCR, high pitch
    probs["fearful"] = max(0.0, min(1.0,
        0.3 * rms +
        0.4 * zcr +
        0.3 * norm_pitch  # Higher pitch
    ))
    
    # Surprised: high energy, high pitch
    probs["surprised"] = max(0.0, min(1.0,
        0.5 * rms +
        0.5 * norm_pitch
    ))
    
    # Neutral: balanced features
    probs["neutral"] = max(0.0, min(1.0,
        0.5 * (1.0 - abs(rms - 0.5)) +
        0.5 * (1.0 - abs(norm_pitch - 0.5))
    ))
    
    # Disgust: moderate energy, variable characteristics
    probs["disgust"] = max(0.0, min(1.0,
        0.4 * (1.0 - abs(rms - 0.4)) +
        0.3 * zcr +
        0.3 * (1.0 - norm_pitch)
    ))
    
    # Normalize probabilities
    total = sum(probs.values())
    if total > 0:
        probs = {k: v / total for k, v in probs.items()}
    else:
        probs = {k: 1.0 / len(probs) for k in probs}
    
    # Calculate stress (negative emotions)
    stress = float(
        probs.get("angry", 0.0) * 0.9 + 
        probs.get("fearful", 0.0) * 0.8 + 
        probs.get("sad", 0.0) * 0.4 +
        probs.get("disgust", 0.0) * 0.6
    )
    
    # Get dominant emotion
    dominant_emotion = max(probs.items(), key=lambda x: x[1])[0]
    dominant_confidence = float(probs[dominant_emotion])
    
    # Debug: Print emotion detection result
    print(f"DEBUG VOICE - Dominant: {dominant_emotion} ({dominant_confidence:.2f}), Stress: {stress:.2f}")
    print(f"DEBUG VOICE - Top 3: {sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]}")
    
    return {
        "probs": probs,
        "stress": stress,
        "features": {"rms": rms, "zcr": zcr, "pitch_hz": pitch},
        "dominant_emotion": dominant_emotion,
        "dominant_confidence": dominant_confidence,
        "model": "enhanced_heuristic"
    }


def analyze_voice_heuristic(feats: Dict[str, float]) -> Dict[str, Any]:
    """Fallback heuristic-based voice emotion analysis."""
    rms = float(feats.get("rms", 0.0))
    zcr = float(feats.get("zcr", 0.0))
    pitch = float(feats.get("pitch_hz", 0.0))
    
    # Normalize pitch bands
    high_pitch = 1.0 if pitch > 260 else (pitch - 180) / 80 if pitch > 180 else 0.0
    
    # Stress proxy
    stress = max(0.0, min(1.0, 0.6 * rms + 0.4 * zcr + 0.2 * high_pitch))
    
    probs = {
        "calm": max(0.0, 1.0 - stress),
        "happy": max(0.0, min(1.0, 0.5 * (1.0 - zcr) + 0.3 * (1.0 - rms))),
        "sad": max(0.0, min(1.0, 0.5 * (1.0 - pitch / 240.0) + 0.2 * (1.0 - zcr))),
        "angry": max(0.0, min(1.0, stress)),
    }
    
    # Normalize
    s = sum(probs.values())
    probs = {k: v / s for k, v in probs.items()} if s > 0 else {k: 0.25 for k in probs}
    
    # Get dominant emotion
    dominant_emotion = max(probs.items(), key=lambda x: x[1])[0]
    dominant_confidence = float(probs[dominant_emotion])
    
    return {
        "probs": probs,
        "stress": stress,
        "features": {"rms": rms, "zcr": zcr, "pitch_hz": pitch},
        "dominant_emotion": dominant_emotion,
        "dominant_confidence": dominant_confidence,
        "model": "heuristic"
    }


def analyze_voice_feats(feats: Dict[str, float]) -> Dict[str, Any]:
    """Main entry point - uses enhanced heuristic for better emotion variety."""
    # Use enhanced heuristic instead of RF model (which has limited features)
    return analyze_voice_trained(feats)
