import numpy as np
from PIL import Image
import io, base64, cv2

# Minimal heuristic "emotion" from facial frame (no heavy ML): uses brightness & contrast as proxy.
# Replace with real CNN as needed.

CLASSES = ["happy","sad","neutral","angry","fear","surprise","disgust"]

def _read_image_from_base64(data_url: str):
    # data_url like: data:image/png;base64,XXXX
    if ";base64," in data_url:
        base64_data = data_url.split(";base64,")[1]
    else:
        base64_data = data_url
    img_bytes = base64.b64decode(base64_data)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)

def analyze_frame(data_url: str):
    img = _read_image_from_base64(data_url)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Calculate image statistics
    brightness = float(gray.mean()) / 255.0
    contrast = float(gray.std()) / 128.0  # ~0..2
    
    # Calculate additional features for better emotion detection
    # Edge detection for facial features
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.sum(edges > 0)) / edges.size
    
    # Histogram analysis
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_std = float(np.std(hist))
    
    # Enhanced emotion mapping with more variation
    # Happy: bright, high contrast, moderate edges
    happy = max(0.0, min(1.0, 
        0.5 * brightness + 
        0.3 * contrast + 
        0.2 * edge_density
    ))
    
    # Sad: low brightness, low contrast
    sad = max(0.0, min(1.0,
        0.6 * (1.0 - brightness) + 
        0.3 * (1.0 - contrast) +
        0.1 * (1.0 - edge_density)
    ))
    
    # Surprise: high contrast, high edges
    surprise = max(0.0, min(1.0,
        0.5 * contrast + 
        0.4 * edge_density +
        0.1 * brightness
    ))
    
    # Angry: moderate-low brightness, high contrast
    angry = max(0.0, min(1.0,
        0.4 * (1.0 - brightness) + 
        0.4 * contrast +
        0.2 * edge_density
    ))
    
    # Fear: low brightness, moderate contrast, high edges
    fear = max(0.0, min(1.0,
        0.5 * (1.0 - brightness) +
        0.3 * edge_density +
        0.2 * contrast
    ))
    
    # Disgust: variable brightness, moderate contrast
    disgust = max(0.0, min(1.0,
        0.4 * abs(brightness - 0.5) +
        0.3 * contrast +
        0.3 * (1.0 - brightness)
    ))
    
    # Neutral: balanced features
    neutral = max(0.0, 1.0 - (happy + sad + surprise + angry + fear + disgust) / 2.5)
    
    # Create probability array
    probs = np.array([happy, sad, neutral, angry, fear, surprise, disgust], dtype=float)
    probs = np.clip(probs, 0.05, 1.0)  # Minimum 5% for each emotion
    
    # Normalize to sum to 1
    if probs.sum() == 0:
        probs = np.ones_like(probs) / len(probs)
    else:
        probs = probs / probs.sum()
    
    # Enhanced stress calculation with more variation
    # Stress is higher for negative emotions
    stress_weights = {
        "angry": 1.0,      # Highest stress
        "fear": 0.9,       # Very high stress
        "disgust": 0.7,    # High stress
        "sad": 0.6,        # Moderate-high stress
        "surprise": 0.3,   # Low stress (can be positive or negative)
        "neutral": 0.2,    # Low stress
        "happy": 0.1       # Lowest stress
    }
    
    stress = sum(probs[i] * stress_weights[CLASSES[i]] for i in range(len(CLASSES)))
    stress = float(np.clip(stress, 0.0, 1.0))
    
    # Get dominant emotion
    dominant_idx = np.argmax(probs)
    dominant_emotion = CLASSES[dominant_idx]
    dominant_confidence = float(probs[dominant_idx])
    
    return {
        "probs": {c: float(p) for c, p in zip(CLASSES, probs)},
        "stress": stress,
        "brightness": brightness,
        "contrast": float(gray.std()),
        "edge_density": edge_density,
        "dominant_emotion": dominant_emotion,
        "dominant_confidence": dominant_confidence
    }
