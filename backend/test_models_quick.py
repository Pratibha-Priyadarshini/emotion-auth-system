"""Quick test to verify models are working correctly."""
import numpy as np
from models.facial_emotion_trained import analyze_frame
from models.voice_emotion_trained import analyze_voice_feats
import base64
from PIL import Image
import io

print("=" * 60)
print("QUICK MODEL TEST")
print("=" * 60)

# Test 1: Facial Emotion Model
print("\n1. Testing Facial Emotion Model...")
try:
    # Create a test image (48x48 grayscale)
    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    pil_img = Image.fromarray(test_img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    data_url = f"data:image/png;base64,{img_str}"
    
    result = analyze_frame(data_url)
    print(f"   ✓ Model loaded and working")
    print(f"   Dominant emotion: {result.get('dominant_emotion', 'N/A')}")
    print(f"   Confidence: {result.get('dominant_confidence', 0):.2%}")
    print(f"   Stress level: {result.get('stress', 0):.2%}")
    print(f"   All emotions: {list(result.get('probs', {}).keys())}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Voice Emotion Model
print("\n2. Testing Voice Emotion Model...")
try:
    # Test with different voice features
    test_cases = [
        {"rms": 0.8, "zcr": 0.3, "pitch_hz": 250, "expected": "happy/surprised"},
        {"rms": 0.2, "zcr": 0.1, "pitch_hz": 120, "expected": "calm/sad"},
        {"rms": 0.9, "zcr": 0.7, "pitch_hz": 280, "expected": "angry/fearful"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        feats = {k: v for k, v in test.items() if k != "expected"}
        result = analyze_voice_feats(feats)
        print(f"   Test {i} ({test['expected']}):")
        print(f"      Dominant emotion: {result.get('dominant_emotion', 'N/A')}")
        print(f"      Confidence: {result.get('dominant_confidence', 0):.2%}")
        print(f"      Stress level: {result.get('stress', 0):.2%}")
    
    print(f"   ✓ Model loaded and working")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Check emotion variety
print("\n3. Testing Emotion Variety...")
try:
    emotions_detected = set()
    
    # Test facial with different brightness levels
    for brightness in [50, 100, 150, 200, 250]:
        test_img = np.full((100, 100, 3), brightness, dtype=np.uint8)
        pil_img = Image.fromarray(test_img)
        buffer = io.BytesIO()
        pil_img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        data_url = f"data:image/png;base64,{img_str}"
        
        result = analyze_frame(data_url)
        emotions_detected.add(result.get('dominant_emotion', 'unknown'))
    
    print(f"   Facial emotions detected: {emotions_detected}")
    print(f"   Variety: {len(emotions_detected)} different emotions")
    
    if len(emotions_detected) > 1:
        print(f"   ✓ Good variety (not stuck on one emotion)")
    else:
        print(f"   ⚠ Limited variety - may need adjustment")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
