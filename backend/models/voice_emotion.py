# Browser sends lightweight voice features (no raw audio) computed via WebAudio (rms, zcr, pitch).
# This module maps those to a simple emotion/stress estimate.
from typing import Dict, Any

def analyze_voice_feats(feats: Dict[str, float]) -> Dict[str, Any]:
    rms = float(feats.get("rms", 0.0))          # 0..1
    zcr = float(feats.get("zcr", 0.0))          # 0..1
    pitch = float(feats.get("pitch_hz", 0.0))   # Hz
    # Normalize pitch bands (roughly): calm speech ~120-220Hz typical
    high_pitch = 1.0 if pitch > 260 else (pitch-180)/80 if pitch>180 else 0.0
    # Stress proxy: loud + jittery (zcr)
    stress = max(0.0, min(1.0, 0.6*rms + 0.4*zcr + 0.2*high_pitch))
    probs = {
        "calm": max(0.0, 1.0 - stress),
        "happy": max(0.0, min(1.0, 0.5*(1.0 - zcr) + 0.3*(1.0 - rms))),
        "sad": max(0.0, min(1.0, 0.5*(1.0 - pitch/240.0) + 0.2*(1.0 - zcr))),
        "angry": max(0.0, min(1.0, stress)),
    }
    # Normalize
    s = sum(probs.values())
    probs = {k: v/s for k, v in probs.items()} if s>0 else {k: 0.25 for k in probs}
    return {"probs": probs, "stress": stress, "features": {"rms": rms, "zcr": zcr, "pitch_hz": pitch}}
