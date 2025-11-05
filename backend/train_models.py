"""
Training script for emotion-aware authentication models using real datasets.

Datasets used:
- Facial Emotion: FER2013 or CK+ (via Kaggle)
- Voice Emotion: RAVDESS, TESS, or CREMA-D
- Keystroke Dynamics: CMU Keystroke Dynamics dataset or synthetic generation

Run: python -m backend.train_models --all
"""

import os
import sys
import argparse
import numpy as np
import pickle
from pathlib import Path

# Create directories
STORAGE_DIR = Path(__file__).parent / "storage"
MODELS_DIR = STORAGE_DIR / "trained_models"
DATA_DIR = STORAGE_DIR / "datasets"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def train_facial_emotion():
    """Train facial emotion recognition model using FER2013 or similar dataset."""
    print("\n=== Training Facial Emotion Model ===")
    
    try:
        # Try different import methods for TensorFlow/Keras compatibility
        try:
            import tensorflow.keras as keras
            from tensorflow.keras import layers
        except:
            import keras
            from keras import layers
        print(f"Keras loaded successfully")
    except ImportError as e:
        print(f"ERROR: Keras not installed. Run: pip install tensorflow")
        print(f"Import error: {e}")
        print("\nSkipping facial emotion training. System will use heuristic fallback.")
        return None
    except Exception as e:
        print(f"ERROR loading Keras: {e}")
        print("\nSkipping facial emotion training. System will use heuristic fallback.")
        return None
    
    # Check for dataset
    fer_path = DATA_DIR / "fer2013" / "fer2013.csv"
    if not fer_path.exists():
        print(f"Dataset not found at {fer_path}")
        print("Please download FER2013 dataset from:")
        print("https://www.kaggle.com/datasets/msambare/fer2013")
        print(f"Extract to: {DATA_DIR / 'fer2013'}")
        
        # Create synthetic training data for demo
        print("\nGenerating synthetic training data for demonstration...")
        X_train = np.random.rand(1000, 48, 48, 1).astype(np.float32)
        y_train = np.random.randint(0, 7, 1000)
        X_val = np.random.rand(200, 48, 48, 1).astype(np.float32)
        y_val = np.random.randint(0, 7, 200)
    else:
        # Load FER2013 dataset
        print(f"Loading dataset from {fer_path}")
        import pandas as pd
        df = pd.read_csv(fer_path)
        
        def parse_data(df_subset):
            pixels = df_subset['pixels'].tolist()
            images = np.array([np.fromstring(pixel, dtype=int, sep=' ').reshape(48, 48, 1) 
                             for pixel in pixels], dtype=np.float32) / 255.0
            labels = df_subset['emotion'].values
            return images, labels
        
        train_df = df[df['Usage'] == 'Training']
        val_df = df[df['Usage'] == 'PublicTest']
        
        X_train, y_train = parse_data(train_df)
        X_val, y_val = parse_data(val_df)
        print(f"Loaded {len(X_train)} training samples, {len(X_val)} validation samples")
    
    # Build CNN model
    model = keras.Sequential([
        layers.Conv2D(64, (3, 3), activation='relu', input_shape=(48, 48, 1)),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(256, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(7, activation='softmax')  # 7 emotions
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("\nModel architecture:")
    model.summary()
    
    # Train
    print("\nTraining...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=30,
        batch_size=64,
        callbacks=[
            keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3)
        ]
    )
    
    # Save model
    model_path = MODELS_DIR / "facial_emotion_cnn.h5"
    model.save(model_path)
    print(f"\nModel saved to: {model_path}")
    print(f"Final validation accuracy: {history.history['val_accuracy'][-1]:.4f}")
    
    return model_path


def train_voice_emotion():
    """Train voice emotion recognition model using RAVDESS or similar dataset."""
    print("\n=== Training Voice Emotion Model ===")
    
    try:
        import librosa
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        print("ERROR: Required packages not installed. Run:")
        print("pip install librosa scikit-learn")
        return None
    
    # Check for dataset
    ravdess_path = DATA_DIR / "RAVDESS"
    if not ravdess_path.exists():
        print(f"Dataset not found at {ravdess_path}")
        print("Please download RAVDESS dataset from:")
        print("https://www.kaggle.com/datasets/uwrfkaggle/ravdess-emotional-speech-audio")
        print(f"Extract to: {DATA_DIR / 'RAVDESS'}")
        
        # Create synthetic training data
        print("\nGenerating synthetic training data for demonstration...")
        X_train = np.random.rand(500, 40).astype(np.float32)  # 40 MFCC features
        y_train = np.random.randint(0, 8, 500)
        X_val = np.random.rand(100, 40).astype(np.float32)
        y_val = np.random.randint(0, 8, 100)
    else:
        # Load and extract features from RAVDESS
        print(f"Loading audio files from {ravdess_path}")
        
        def extract_features(file_path):
            """Extract MFCC, chroma, mel spectrogram features."""
            y, sr = librosa.load(file_path, duration=3, offset=0.5)
            mfcc = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).T, axis=0)
            chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr).T, axis=0)
            mel = np.mean(librosa.feature.melspectrogram(y=y, sr=sr).T, axis=0)
            return np.hstack([mfcc, chroma, mel])
        
        X, y = [], []
        for audio_file in ravdess_path.rglob("*.wav"):
            # RAVDESS filename format: 03-01-06-01-02-01-12.wav
            # emotion is 3rd field (01=neutral, 02=calm, 03=happy, 04=sad, 05=angry, 06=fearful, 07=disgust, 08=surprised)
            parts = audio_file.stem.split('-')
            if len(parts) >= 3:
                emotion = int(parts[2]) - 1  # 0-indexed
                features = extract_features(str(audio_file))
                X.append(features)
                y.append(emotion)
        
        X = np.array(X)
        y = np.array(y)
        
        # Split train/val
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        print(f"Loaded {len(X_train)} training samples, {len(X_val)} validation samples")
    
    # Normalize features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    
    # Train Random Forest classifier
    print("\nTraining Random Forest classifier...")
    clf = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    
    # Evaluate
    train_acc = clf.score(X_train, y_train)
    val_acc = clf.score(X_val, y_val)
    print(f"Training accuracy: {train_acc:.4f}")
    print(f"Validation accuracy: {val_acc:.4f}")
    
    # Save model and scaler
    model_path = MODELS_DIR / "voice_emotion_rf.pkl"
    scaler_path = MODELS_DIR / "voice_emotion_scaler.pkl"
    
    with open(model_path, 'wb') as f:
        pickle.dump(clf, f)
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"\nModel saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")
    
    return model_path


def train_keystroke_dynamics():
    """Train keystroke dynamics model using CMU dataset or synthetic data."""
    print("\n=== Training Keystroke Dynamics Model ===")
    
    from sklearn.svm import OneClassSVM
    from sklearn.ensemble import IsolationForest
    
    # Check for dataset
    cmu_path = DATA_DIR / "CMU_Keystroke"
    if not cmu_path.exists():
        print(f"Dataset not found at {cmu_path}")
        print("CMU Keystroke Dynamics dataset can be found at:")
        print("http://www.cs.cmu.edu/~keystroke/")
        
        # Generate synthetic keystroke data
        print("\nGenerating synthetic keystroke data for demonstration...")
        
        def generate_user_typing(n_samples=50, user_id=0):
            """Generate synthetic keystroke timing patterns for a user."""
            np.random.seed(user_id)
            # Each user has characteristic typing patterns
            base_hold = 80 + user_id * 10  # ms
            base_flight = 120 + user_id * 15  # ms
            
            samples = []
            for _ in range(n_samples):
                n_keys = np.random.randint(8, 15)
                holds = np.random.normal(base_hold, 20, n_keys)
                flights = np.random.normal(base_flight, 30, n_keys-1)
                
                # Feature vector: hold stats + flight stats + metadata
                total_time = np.sum(holds) + np.sum(flights)
                features = [
                    np.mean(holds), np.std(holds), np.percentile(holds, 25), np.percentile(holds, 75),
                    np.mean(flights), np.std(flights), np.percentile(flights, 25), np.percentile(flights, 75),
                    n_keys, total_time / 1000.0, n_keys / (total_time / 1000.0) if total_time > 0 else 0.0
                ]
                samples.append(features)
            return np.array(samples)
        
        # Generate data for multiple users
        n_users = 10
        user_data = {}
        for user_id in range(n_users):
            user_data[f"user_{user_id}"] = generate_user_typing(100, user_id)
        
        print(f"Generated synthetic data for {n_users} users")
    else:
        # Load CMU dataset
        print(f"Loading CMU Keystroke dataset from {cmu_path}")
        # Parse CMU format (implementation depends on specific dataset format)
        user_data = {}
        # ... dataset-specific parsing code ...
    
    # Train one-class SVM for each user
    print("\nTraining anomaly detection models for each user...")
    models = {}
    
    for user_id, X in user_data.items():
        # Split into train/test
        split = int(0.8 * len(X))
        X_train = X[:split]
        X_test = X[split:]
        
        # Train One-Class SVM
        clf = OneClassSVM(kernel='rbf', gamma='auto', nu=0.1)
        clf.fit(X_train)
        
        # Evaluate
        train_pred = clf.predict(X_train)
        test_pred = clf.predict(X_test)
        train_acc = np.mean(train_pred == 1)
        test_acc = np.mean(test_pred == 1)
        
        models[user_id] = clf
        print(f"{user_id}: train_acc={train_acc:.3f}, test_acc={test_acc:.3f}")
    
    # Save models
    model_path = MODELS_DIR / "keystroke_dynamics_models.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(models, f)
    
    print(f"\nModels saved to: {model_path}")
    print(f"Trained {len(models)} user-specific models")
    
    return model_path


def train_fusion_model():
    """Train a meta-classifier for decision fusion."""
    print("\n=== Training Fusion Model ===")
    
    from sklearn.ensemble import GradientBoostingClassifier
    
    # Generate synthetic fusion training data
    # Features: [facial_stress, voice_stress, kd_match, kd_anomaly, env_noise, env_brightness]
    # Labels: 0=deny, 1=delay, 2=permit
    
    print("Generating synthetic fusion training data...")
    n_samples = 5000
    
    # Simulate different scenarios
    X = []
    y = []
    
    for _ in range(n_samples):
        facial_stress = np.random.rand()
        voice_stress = np.random.rand()
        kd_match = np.random.rand()
        kd_anomaly = np.random.rand()
        env_noise = np.random.rand()
        env_brightness = np.random.rand()
        
        features = [facial_stress, voice_stress, kd_match, kd_anomaly, env_noise, env_brightness]
        
        # Decision logic
        if kd_anomaly > 0.7 or env_noise > 0.8:
            label = 0  # deny
        elif (facial_stress + voice_stress) / 2 > 0.6 or env_brightness < 0.2:
            label = 1  # delay
        else:
            label = 2  # permit
        
        X.append(features)
        y.append(label)
    
    X = np.array(X)
    y = np.array(y)
    
    # Split train/val
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Gradient Boosting classifier
    print("\nTraining Gradient Boosting classifier...")
    clf = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluate
    train_acc = clf.score(X_train, y_train)
    val_acc = clf.score(X_val, y_val)
    print(f"Training accuracy: {train_acc:.4f}")
    print(f"Validation accuracy: {val_acc:.4f}")
    
    # Save model
    model_path = MODELS_DIR / "fusion_classifier.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(clf, f)
    
    print(f"\nModel saved to: {model_path}")
    
    return model_path


def main():
    parser = argparse.ArgumentParser(description='Train emotion-aware authentication models')
    parser.add_argument('--all', action='store_true', help='Train all models')
    parser.add_argument('--facial', action='store_true', help='Train facial emotion model')
    parser.add_argument('--voice', action='store_true', help='Train voice emotion model')
    parser.add_argument('--keystroke', action='store_true', help='Train keystroke dynamics model')
    parser.add_argument('--fusion', action='store_true', help='Train fusion model')
    
    args = parser.parse_args()
    
    if not any([args.all, args.facial, args.voice, args.keystroke, args.fusion]):
        parser.print_help()
        return
    
    print("=" * 60)
    print("Emotion-Aware Authentication Model Training")
    print("=" * 60)
    
    results = {}
    
    if args.all or args.facial:
        results['facial'] = train_facial_emotion()
    
    if args.all or args.voice:
        results['voice'] = train_voice_emotion()
    
    if args.all or args.keystroke:
        results['keystroke'] = train_keystroke_dynamics()
    
    if args.all or args.fusion:
        results['fusion'] = train_fusion_model()
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print("\nTrained models:")
    for model_type, path in results.items():
        if path:
            print(f"  {model_type}: {path}")
    
    print("\nNext steps:")
    print("1. Update model inference code to use trained models")
    print("2. Test models with real data")
    print("3. Fine-tune hyperparameters as needed")


if __name__ == "__main__":
    main()
