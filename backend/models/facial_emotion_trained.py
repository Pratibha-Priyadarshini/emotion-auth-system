"""
Facial emotion recognition using trained CNN model.
Falls back to heuristic if trained model not available.
"""

import numpy as np
from PIL import Image
import io
import base64
import cv2
import os
from pathlib import Path

CLASSES = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
MODEL_PATH = Path(__file__).parent.parent / "storage" / "trained_models" / "facial_emotion_cnn.h5"

# Load Haar Cascade for face detection
FACE_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
print(f"Loaded face detection cascade from OpenCV")

# Try to load trained model
trained_model = None
try:
    if MODEL_PATH.exists():
        try:
            import tensorflow.keras as keras
            trained_model = keras.models.load_model(MODEL_PATH)
        except:
            import keras
            trained_model = keras.models.load_model(MODEL_PATH)
        print(f"Loaded trained facial emotion model from {MODEL_PATH}")
except Exception as e:
    print(f"Could not load trained model: {e}")
    print("Using heuristic fallback")


def _read_image_from_base64(data_url: str):
    """Parse base64 image data."""
    if ";base64," in data_url:
        base64_data = data_url.split(";base64,")[1]
    else:
        base64_data = data_url
    img_bytes = base64.b64decode(base64_data)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)


def detect_face_count(img: np.ndarray) -> int:
    """Detect the number of faces in the image using Haar Cascade."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Detect faces with optimized parameters
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    num_faces = len(faces)
    print(f"SECURITY CHECK - Detected {num_faces} face(s) in frame")
    
    return num_faces


def analyze_frame_trained(data_url: str):
    """Analyze facial emotion using trained CNN model with improved detection."""
    img = _read_image_from_base64(data_url)
    
    # Preprocess for model (48x48 grayscale)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Apply histogram equalization for better contrast
    gray = cv2.equalizeHist(gray)
    
    resized = cv2.resize(gray, (48, 48))
    normalized = resized.astype(np.float32) / 255.0
    input_img = normalized.reshape(1, 48, 48, 1)
    
    # Predict
    predictions = trained_model.predict(input_img, verbose=0)[0]
    probs = {cls: float(prob) for cls, prob in zip(CLASSES, predictions)}
    
    # Get brightness and contrast for additional context
    brightness = float(gray.mean()) / 255.0
    contrast = float(gray.std())
    
    # Aggressive bias correction - CNN is heavily biased toward "sad"
    # Apply brightness and contrast-based adjustments
    if brightness > 0.7:
        # Very bright - likely happy or neutral
        probs["happy"] = min(1.0, probs["happy"] * 3.0)
        probs["neutral"] = min(1.0, probs["neutral"] * 2.5)
        probs["surprise"] = min(1.0, probs["surprise"] * 2.0)
        probs["sad"] = probs["sad"] * 0.3
    elif brightness > 0.5:
        # Bright - boost positive emotions
        probs["happy"] = min(1.0, probs["happy"] * 2.5)
        probs["neutral"] = min(1.0, probs["neutral"] * 2.0)
        probs["sad"] = probs["sad"] * 0.5
    elif brightness > 0.3:
        # Medium - boost neutral
        probs["neutral"] = min(1.0, probs["neutral"] * 2.0)
        probs["sad"] = probs["sad"] * 0.7
    
    # High contrast suggests more expressive emotions
    if contrast > 40:
        probs["surprise"] = min(1.0, probs["surprise"] * 1.5)
        probs["angry"] = min(1.0, probs["angry"] * 1.3)
        probs["sad"] = probs["sad"] * 0.8
    
    # Renormalize
    total = sum(probs.values())
    if total > 0:
        probs = {k: v / total for k, v in probs.items()}
    
    # Calculate stress index (negative emotions)
    stress = float(
        probs["angry"] * 0.9 + 
        probs["fear"] * 0.8 + 
        probs["disgust"] * 0.7 + 
        probs["sad"] * 0.4  # Reduced weight for sad
    )
    
    # Get dominant emotion
    dominant_emotion = max(probs.items(), key=lambda x: x[1])[0]
    dominant_confidence = float(probs[dominant_emotion])
    
    return {
        "probs": probs,
        "stress": stress,
        "brightness": brightness,
        "contrast": contrast,
        "dominant_emotion": dominant_emotion,
        "dominant_confidence": dominant_confidence,
        "model": "trained_cnn"
    }


def analyze_frame_heuristic(data_url: str):
    """Facial emotion analysis based on lip and eye curvature."""
    img = _read_image_from_base64(data_url)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Apply histogram equalization for better feature detection
    gray_eq = cv2.equalizeHist(gray)
    
    h, w = gray.shape
    
    # Define facial regions (assuming face is centered)
    # Eye region: top 30-50% of image
    eye_y_start = int(h * 0.30)
    eye_y_end = int(h * 0.50)
    eye_region = gray_eq[eye_y_start:eye_y_end, :]
    
    # Mouth region: bottom 60-80% of image
    mouth_y_start = int(h * 0.60)
    mouth_y_end = int(h * 0.80)
    mouth_region = gray_eq[mouth_y_start:mouth_y_end, :]
    
    # MOUTH CURVATURE ANALYSIS
    # Detect edges in mouth region
    mouth_edges = cv2.Canny(mouth_region, 50, 150)
    
    # Analyze mouth shape by looking at edge distribution
    # Smile: edges curve upward (more edges in top of mouth region)
    # Frown: edges curve downward (more edges in bottom of mouth region)
    mouth_h = mouth_region.shape[0]
    mouth_top_half = mouth_edges[:mouth_h//2, :]
    mouth_bottom_half = mouth_edges[mouth_h//2:, :]
    
    top_edges = float(np.sum(mouth_top_half > 0))
    bottom_edges = float(np.sum(mouth_bottom_half > 0))
    total_mouth_edges = top_edges + bottom_edges + 1.0
    
    # Smile indicator: more edges in top = upward curve
    mouth_curvature = (top_edges - bottom_edges) / total_mouth_edges
    # Positive = smile (upward), Negative = frown (downward), ~0 = neutral
    
    # Horizontal vs vertical edges in mouth (smile has more horizontal)
    sobelx = cv2.Sobel(mouth_region, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(mouth_region, cv2.CV_64F, 0, 1, ksize=3)
    horizontal_strength = float(np.abs(sobelx).mean())
    vertical_strength = float(np.abs(sobely).mean())
    smile_ratio = horizontal_strength / (vertical_strength + 1.0)
    
    # EYE CURVATURE ANALYSIS
    # Detect edges in eye region
    eye_edges = cv2.Canny(eye_region, 50, 150)
    
    # Wide eyes (surprise/fear): more edges overall
    eye_edge_density = float(np.sum(eye_edges > 0)) / (eye_edges.size + 1.0)
    
    # Analyze eye shape
    eye_h = eye_region.shape[0]
    eye_top = eye_edges[:eye_h//3, :]
    eye_middle = eye_edges[eye_h//3:2*eye_h//3, :]
    eye_bottom = eye_edges[2*eye_h//3:, :]
    
    eye_top_edges = float(np.sum(eye_top > 0))
    eye_middle_edges = float(np.sum(eye_middle > 0))
    eye_bottom_edges = float(np.sum(eye_bottom > 0))
    
    # Eye openness: more edges in middle = more open
    eye_openness = eye_middle_edges / (eye_top_edges + eye_middle_edges + eye_bottom_edges + 1.0)
    
    # Calculate overall statistics for context
    brightness = float(gray.mean()) / 255.0
    contrast = float(gray.std())
    
    # EMOTION CALCULATION BASED PURELY ON LIP AND EYE CURVATURE
    # NO brightness dependency - only facial feature geometry
    
    # Happy: Upward mouth curvature (smile) + high smile ratio + squinted eyes
    happy = max(0.0, min(1.0,
        0.60 * max(0, mouth_curvature * 12) +  # Strong upward curve = smile
        0.25 * min(1.0, smile_ratio / 1.8) +   # Horizontal mouth edges
        0.15 * (0.5 - abs(eye_openness - 0.4)) # Slightly squinted eyes from smiling
    ))
    
    # Sad: Downward mouth curvature (frown) + droopy features
    sad = max(0.0, min(1.0,
        0.60 * max(0, -mouth_curvature * 12) +  # Strong downward curve = frown
        0.25 * (1.0 - min(1.0, smile_ratio / 1.8)) +  # Less horizontal edges
        0.15 * (0.3 - abs(eye_openness - 0.3))  # Droopy, less open eyes
    ))
    
    # Surprise: Wide open eyes + open mouth (high edge density)
    surprise = max(0.0, min(1.0,
        0.60 * eye_openness +                   # Wide eyes
        0.30 * eye_edge_density +               # Lots of eye edges
        0.10 * (1.0 - abs(mouth_curvature))     # Mouth open but not curved
    ))
    
    # Angry: Tense features + slight frown + intense eyes
    angry = max(0.0, min(1.0,
        0.40 * eye_edge_density +               # Tense, sharp eye features
        0.35 * max(0, -mouth_curvature * 8) +   # Slight frown
        0.25 * (0.5 - abs(eye_openness - 0.5))  # Eyes neither too wide nor closed
    ))
    
    # Fear: Wide eyes + slightly raised mouth corners
    fear = max(0.0, min(1.0,
        0.50 * eye_openness +                   # Wide eyes
        0.30 * eye_edge_density +               # Visible eye features
        0.20 * max(0, mouth_curvature * 4)      # Slight upward mouth (tension)
    ))
    
    # Disgust: Slight frown + wrinkled features (unbalanced smile ratio)
    disgust = max(0.0, min(1.0,
        0.45 * max(0, -mouth_curvature * 6) +  # Slight downward mouth
        0.35 * abs(smile_ratio - 1.0) +         # Asymmetric features
        0.20 * eye_edge_density                 # Wrinkled eye area
    ))
    
    # Neutral: Balanced features (no strong curvature, relaxed)
    neutral = max(0.0, min(1.0,
        0.50 * (1.0 - abs(mouth_curvature * 12)) +  # Flat, straight mouth
        0.30 * (1.0 - abs(smile_ratio - 1.0)) +     # Balanced features
        0.20 * (0.5 - abs(eye_openness - 0.4))      # Normal eye openness
    ))
    
    # Boost neutral as baseline
    neutral = neutral * 1.2
    
    # Clip values
    happy = max(0.0, min(1.0, happy))
    sad = max(0.0, min(1.0, sad))
    surprise = max(0.0, min(1.0, surprise))
    angry = max(0.0, min(1.0, angry))
    fear = max(0.0, min(1.0, fear))
    disgust = max(0.0, min(1.0, disgust))
    neutral = max(0.0, min(1.0, neutral))
    
    # Create probability array
    probs = np.array([angry, disgust, fear, happy, sad, surprise, neutral], dtype=float)
    
    # Debug: Print curvature-based analysis
    print(f"DEBUG - Mouth curvature: {mouth_curvature:.3f}, Smile ratio: {smile_ratio:.2f}, Eye openness: {eye_openness:.2f}")
    print(f"DEBUG - Raw emotions: happy={happy:.2f}, sad={sad:.2f}, neutral={neutral:.2f}, surprise={surprise:.2f}")
    
    probs = np.clip(probs, 0.05, 1.0)  # Minimum 5% for each
    
    # Normalize
    if probs.sum() == 0:
        probs = np.ones_like(probs) / len(probs)
    else:
        probs = probs / probs.sum()
    
    probs_dict = {cls: float(prob) for cls, prob in zip(CLASSES, probs)}
    
    # Debug: Print final result
    print(f"DEBUG - Dominant: {max(probs_dict.items(), key=lambda x: x[1])}")
    
    # Reduce stress calculation (less pessimistic)
    stress = float(
        probs_dict["angry"] * 0.8 + 
        probs_dict["fear"] * 0.7 + 
        probs_dict["disgust"] * 0.6 + 
        probs_dict["sad"] * 0.3
    )
    
    # Get dominant emotion
    dominant_emotion = max(probs_dict.items(), key=lambda x: x[1])[0]
    dominant_confidence = float(probs_dict[dominant_emotion])
    
    # Create visualization overlay data (skip individual edge images to reduce payload size)
    
    # Create overlay image with detection regions and edge lines
    # Start with a semi-transparent black background for better edge visibility
    overlay_img = img.copy()
    
    # Make edges MUCH more visible by dilating them
    kernel = np.ones((3, 3), np.uint8)
    mouth_edges_thick = cv2.dilate(mouth_edges, kernel, iterations=2)
    eye_edges_thick = cv2.dilate(eye_edges, kernel, iterations=2)
    
    # Draw BRIGHT mouth edge lines in CYAN (BGR format)
    mouth_mask = mouth_edges_thick > 0
    if np.any(mouth_mask):
        overlay_img[mouth_y_start:mouth_y_end, :][mouth_mask] = [255, 255, 0]  # Bright cyan
    
    # Draw BRIGHT eye edge lines in YELLOW (BGR format)
    eye_mask = eye_edges_thick > 0
    if np.any(eye_mask):
        overlay_img[eye_y_start:eye_y_end, :][eye_mask] = [0, 255, 255]  # Bright yellow
    
    print(f"DEBUG - Mouth edges detected: {np.sum(mouth_mask)}, Eye edges: {np.sum(eye_mask)}")
    
    # Draw eye region box (green)
    cv2.rectangle(overlay_img, (0, eye_y_start), (w, eye_y_end), (0, 255, 0), 2)
    cv2.putText(overlay_img, "Eye Curvature", (10, eye_y_start - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Draw mouth region box (magenta/pink)
    cv2.rectangle(overlay_img, (0, mouth_y_start), (w, mouth_y_end), (255, 0, 255), 2)
    cv2.putText(overlay_img, "Lip Curvature", (10, mouth_y_start - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    
    # Draw mouth curvature indicator with actual curve visualization
    mouth_center_y = (mouth_y_start + mouth_y_end) // 2
    mouth_center_x = w // 2
    
    if mouth_curvature > 0.05:
        # Smile - upward curve (draw a smile arc)
        cv2.ellipse(overlay_img, (mouth_center_x, mouth_center_y + 10), 
                   (40, 20), 0, 0, 180, (0, 255, 255), 3)
        cv2.arrowedLine(overlay_img, (mouth_center_x - 50, mouth_center_y + 15), 
                       (mouth_center_x - 50, mouth_center_y - 10), (0, 255, 255), 3)
        cv2.putText(overlay_img, f"SMILE {mouth_curvature:.2f}", (mouth_center_x - 100, mouth_center_y - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    elif mouth_curvature < -0.05:
        # Frown - downward curve (draw a frown arc)
        cv2.ellipse(overlay_img, (mouth_center_x, mouth_center_y - 10), 
                   (40, 20), 0, 180, 360, (0, 100, 255), 3)
        cv2.arrowedLine(overlay_img, (mouth_center_x - 50, mouth_center_y - 15), 
                       (mouth_center_x - 50, mouth_center_y + 10), (0, 100, 255), 3)
        cv2.putText(overlay_img, f"FROWN {mouth_curvature:.2f}", (mouth_center_x - 100, mouth_center_y + 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)
    else:
        # Neutral - straight line
        cv2.line(overlay_img, (mouth_center_x - 40, mouth_center_y), 
                (mouth_center_x + 40, mouth_center_y), (200, 200, 200), 3)
        cv2.putText(overlay_img, f"NEUTRAL {mouth_curvature:.2f}", (mouth_center_x - 100, mouth_center_y - 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
    
    # Draw eye openness indicator with visualization
    eye_center_y = (eye_y_start + eye_y_end) // 2
    eye_center_x = w // 2
    
    if eye_openness > 0.4:
        # Wide eyes - draw open circles
        cv2.circle(overlay_img, (eye_center_x - 30, eye_center_y), 15, (255, 255, 0), 3)
        cv2.circle(overlay_img, (eye_center_x + 30, eye_center_y), 15, (255, 255, 0), 3)
        cv2.putText(overlay_img, f"WIDE {eye_openness:.2f}", (eye_center_x + 50, eye_center_y + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    else:
        # Squinted eyes - draw ellipses
        cv2.ellipse(overlay_img, (eye_center_x - 30, eye_center_y), (15, 6), 0, 0, 360, (150, 150, 255), 3)
        cv2.ellipse(overlay_img, (eye_center_x + 30, eye_center_y), (15, 6), 0, 0, 360, (150, 150, 255), 3)
        cv2.putText(overlay_img, f"SQUINT {eye_openness:.2f}", (eye_center_x + 50, eye_center_y + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 255), 2)
    
    # Add legend in top-right corner
    legend_x = w - 200
    cv2.putText(overlay_img, "Edge Detection:", (legend_x, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.line(overlay_img, (legend_x, 45), (legend_x + 30, 45), (255, 255, 0), 3)
    cv2.putText(overlay_img, "Mouth", (legend_x + 35, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.line(overlay_img, (legend_x, 65), (legend_x + 30, 65), (0, 255, 255), 3)
    cv2.putText(overlay_img, "Eyes", (legend_x + 35, 70), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Resize overlay for faster transmission (reduce to 50% size)
    overlay_resized = cv2.resize(overlay_img, (w//2, h//2), interpolation=cv2.INTER_LINEAR)
    
    # Encode overlay image with JPEG for smaller size and faster transmission
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
    _, overlay_encoded = cv2.imencode('.jpg', overlay_resized, encode_param)
    overlay_b64 = base64.b64encode(overlay_encoded).decode('utf-8')
    
    return {
        "probs": probs_dict,
        "stress": stress,
        "brightness": brightness,
        "contrast": contrast,
        "smile_ratio": smile_ratio,
        "mouth_curvature": mouth_curvature,
        "eye_openness": eye_openness,
        "dominant_emotion": dominant_emotion,
        "dominant_confidence": dominant_confidence,
        "model": "realtime_heuristic",
        "visualization": {
            "overlay_image": f"data:image/jpeg;base64,{overlay_b64}"
        }
    }


def analyze_frame(data_url: str):
    """Main entry point - uses enhanced heuristic for better accuracy."""
    # SECURITY CHECK: Detect number of faces
    img = _read_image_from_base64(data_url)
    num_faces = detect_face_count(img)
    
    # DENY ACCESS if more than 1 person detected
    if num_faces > 1:
        print(f"🚨 SECURITY ALERT: Multiple people detected ({num_faces} faces) - ACCESS DENIED")
        return {
            "probs": {"angry": 0.0, "disgust": 0.0, "fear": 0.0, "happy": 0.0, "sad": 0.0, "surprise": 0.0, "neutral": 0.0},
            "stress": 1.0,  # Maximum stress
            "brightness": 0.0,
            "contrast": 0.0,
            "smile_ratio": 0.0,
            "mouth_curvature": 0.0,
            "eye_openness": 0.0,
            "dominant_emotion": "MULTIPLE_PEOPLE_DETECTED",
            "dominant_confidence": 1.0,
            "model": "security_check",
            "security_violation": True,
            "num_faces": num_faces,
            "violation_reason": f"Multiple people detected: {num_faces} faces in frame"
        }
    
    # DENY ACCESS if no face detected
    if num_faces == 0:
        print(f"⚠️ WARNING: No face detected in frame")
        return {
            "probs": {"angry": 0.0, "disgust": 0.0, "fear": 0.0, "happy": 0.0, "sad": 0.0, "surprise": 0.0, "neutral": 0.0},
            "stress": 0.5,
            "brightness": 0.0,
            "contrast": 0.0,
            "smile_ratio": 0.0,
            "mouth_curvature": 0.0,
            "eye_openness": 0.0,
            "dominant_emotion": "NO_FACE_DETECTED",
            "dominant_confidence": 1.0,
            "model": "security_check",
            "security_violation": True,
            "num_faces": 0,
            "violation_reason": "No face detected in frame"
        }
    
    # Proceed with emotion analysis if exactly 1 face detected
    print(f"✓ Security check passed: Exactly 1 face detected")
    return analyze_frame_heuristic(data_url)
