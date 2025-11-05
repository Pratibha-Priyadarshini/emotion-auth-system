"""
Model evaluation script.
Tests trained models and reports performance metrics.
"""

import numpy as np
import pickle
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import json

STORAGE_DIR = Path(__file__).parent / "storage"
MODELS_DIR = STORAGE_DIR / "trained_models"
DATA_DIR = STORAGE_DIR / "datasets"


def evaluate_facial_model():
    """Evaluate facial emotion recognition model."""
    print("\n=== Evaluating Facial Emotion Model ===")
    
    model_path = MODELS_DIR / "facial_emotion_cnn.h5"
    if not model_path.exists():
        print(f"Model not found at {model_path}")
        print("Train the model first: python -m backend.train_models --facial")
        return None
    
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(model_path)
        print(f"Loaded model from {model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
    
    # Load test data
    fer_path = DATA_DIR / "fer2013" / "fer2013.csv"
    if not fer_path.exists():
        fer_path = DATA_DIR / "fer2013_sample" / "fer2013.csv"
    
    if not fer_path.exists():
        print("Test dataset not found")
        return None
    
    print(f"Loading test data from {fer_path}")
    import pandas as pd
    df = pd.read_csv(fer_path)
    test_df = df[df['Usage'] == 'PrivateTest']
    
    if len(test_df) == 0:
        test_df = df[df['Usage'] == 'PublicTest']
    
    # Parse test data
    pixels = test_df['pixels'].tolist()
    X_test = np.array([np.fromstring(pixel, dtype=int, sep=' ').reshape(48, 48, 1) 
                       for pixel in pixels], dtype=np.float32) / 255.0
    y_test = test_df['emotion'].values
    
    print(f"Test samples: {len(X_test)}")
    
    # Predict
    print("Running predictions...")
    y_pred = model.predict(X_test, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred_classes)
    print(f"\nAccuracy: {accuracy:.4f}")
    
    emotion_labels = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_classes, target_names=emotion_labels))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred_classes)
    print(cm)
    
    return {
        "accuracy": float(accuracy),
        "confusion_matrix": cm.tolist(),
        "model_path": str(model_path)
    }


def evaluate_voice_model():
    """Evaluate voice emotion recognition model."""
    print("\n=== Evaluating Voice Emotion Model ===")
    
    model_path = MODELS_DIR / "voice_emotion_rf.pkl"
    scaler_path = MODELS_DIR / "voice_emotion_scaler.pkl"
    
    if not model_path.exists() or not scaler_path.exists():
        print(f"Model not found at {model_path}")
        print("Train the model first: python -m backend.train_models --voice")
        return None
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        print(f"Loaded model from {model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
    
    # Generate test data (in practice, would load real audio features)
    print("Generating test data...")
    n_test = 200
    X_test = np.random.rand(n_test, 40).astype(np.float32)
    y_test = np.random.randint(0, 8, n_test)
    
    # Normalize and predict
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy:.4f}")
    
    emotion_labels = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=emotion_labels[:len(np.unique(y_test))]))
    
    return {
        "accuracy": float(accuracy),
        "model_path": str(model_path)
    }


def evaluate_keystroke_model():
    """Evaluate keystroke dynamics model."""
    print("\n=== Evaluating Keystroke Dynamics Model ===")
    
    model_path = MODELS_DIR / "keystroke_dynamics_models.pkl"
    
    if not model_path.exists():
        print(f"Model not found at {model_path}")
        print("Train the model first: python -m backend.train_models --keystroke")
        return None
    
    try:
        with open(model_path, 'rb') as f:
            models = pickle.load(f)
        print(f"Loaded {len(models)} user models from {model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
    
    # Evaluate each user model
    results = {}
    
    for user_id, model in models.items():
        # Generate genuine and impostor samples
        n_genuine = 50
        n_impostor = 50
        
        # Genuine samples (similar to training)
        genuine_samples = np.random.randn(n_genuine, 11) * 0.5 + model.support_vectors_.mean(axis=0)
        
        # Impostor samples (different distribution)
        impostor_samples = np.random.randn(n_impostor, 11) * 2.0 + 5.0
        
        # Predict
        genuine_pred = model.predict(genuine_samples)
        impostor_pred = model.predict(impostor_samples)
        
        # Calculate metrics
        genuine_accept_rate = np.mean(genuine_pred == 1)
        impostor_reject_rate = np.mean(impostor_pred == -1)
        
        results[user_id] = {
            "genuine_accept_rate": float(genuine_accept_rate),
            "impostor_reject_rate": float(impostor_reject_rate)
        }
        
        print(f"{user_id}: GAR={genuine_accept_rate:.3f}, IRR={impostor_reject_rate:.3f}")
    
    # Average metrics
    avg_gar = np.mean([r["genuine_accept_rate"] for r in results.values()])
    avg_irr = np.mean([r["impostor_reject_rate"] for r in results.values()])
    
    print(f"\nAverage GAR: {avg_gar:.4f}")
    print(f"Average IRR: {avg_irr:.4f}")
    
    return {
        "average_gar": float(avg_gar),
        "average_irr": float(avg_irr),
        "per_user": results,
        "model_path": str(model_path)
    }


def evaluate_fusion_model():
    """Evaluate fusion decision model."""
    print("\n=== Evaluating Fusion Model ===")
    
    model_path = MODELS_DIR / "fusion_classifier.pkl"
    
    if not model_path.exists():
        print(f"Model not found at {model_path}")
        print("Train the model first: python -m backend.train_models --fusion")
        return None
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"Loaded model from {model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
    
    # Generate test data
    print("Generating test data...")
    n_test = 1000
    
    X_test = []
    y_test = []
    
    for _ in range(n_test):
        facial_stress = np.random.rand()
        voice_stress = np.random.rand()
        kd_match = np.random.rand()
        kd_anomaly = np.random.rand()
        env_noise = np.random.rand()
        env_brightness = np.random.rand()
        
        features = [facial_stress, voice_stress, kd_match, kd_anomaly, env_noise, env_brightness]
        
        # Ground truth decision
        if kd_anomaly > 0.7 or env_noise > 0.8:
            label = 0  # deny
        elif (facial_stress + voice_stress) / 2 > 0.6 or env_brightness < 0.2:
            label = 1  # delay
        else:
            label = 2  # permit
        
        X_test.append(features)
        y_test.append(label)
    
    X_test = np.array(X_test)
    y_test = np.array(y_test)
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy:.4f}")
    
    decision_labels = ["deny", "delay", "permit"]
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=decision_labels))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    return {
        "accuracy": float(accuracy),
        "confusion_matrix": cm.tolist(),
        "model_path": str(model_path)
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate trained models')
    parser.add_argument('--all', action='store_true', help='Evaluate all models')
    parser.add_argument('--facial', action='store_true', help='Evaluate facial emotion model')
    parser.add_argument('--voice', action='store_true', help='Evaluate voice emotion model')
    parser.add_argument('--keystroke', action='store_true', help='Evaluate keystroke dynamics model')
    parser.add_argument('--fusion', action='store_true', help='Evaluate fusion model')
    parser.add_argument('--output', type=str, help='Save results to JSON file')
    
    args = parser.parse_args()
    
    if not any([args.all, args.facial, args.voice, args.keystroke, args.fusion]):
        parser.print_help()
        return
    
    print("=" * 60)
    print("Model Evaluation")
    print("=" * 60)
    
    results = {}
    
    if args.all or args.facial:
        results['facial'] = evaluate_facial_model()
    
    if args.all or args.voice:
        results['voice'] = evaluate_voice_model()
    
    if args.all or args.keystroke:
        results['keystroke'] = evaluate_keystroke_model()
    
    if args.all or args.fusion:
        results['fusion'] = evaluate_fusion_model()
    
    print("\n" + "=" * 60)
    print("Evaluation Complete!")
    print("=" * 60)
    
    # Save results if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_path}")
    
    return results


if __name__ == "__main__":
    main()
