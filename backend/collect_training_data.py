"""
Data collection utilities for gathering real training data.
Helps users collect their own datasets for model training.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

STORAGE_DIR = Path(__file__).parent / "storage"
COLLECTED_DATA_DIR = STORAGE_DIR / "collected_data"
COLLECTED_DATA_DIR.mkdir(parents=True, exist_ok=True)


class DataCollector:
    """Collects and stores training data from authentication attempts."""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = COLLECTED_DATA_DIR / self.session_id
        self.session_dir.mkdir(exist_ok=True)
        
        self.facial_dir = self.session_dir / "facial"
        self.voice_dir = self.session_dir / "voice"
        self.keystroke_dir = self.session_dir / "keystroke"
        
        for d in [self.facial_dir, self.voice_dir, self.keystroke_dir]:
            d.mkdir(exist_ok=True)
        
        self.metadata = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "samples": []
        }
    
    def collect_facial_sample(self, user_id: str, frame_data: str, emotion_label: str = None):
        """Save facial image sample with optional emotion label."""
        timestamp = int(time.time() * 1000)
        filename = f"{user_id}_{timestamp}.json"
        
        sample = {
            "user_id": user_id,
            "timestamp": timestamp,
            "frame_data": frame_data,
            "emotion_label": emotion_label,
            "type": "facial"
        }
        
        filepath = self.facial_dir / filename
        with open(filepath, 'w') as f:
            json.dump(sample, f)
        
        self.metadata["samples"].append({
            "type": "facial",
            "file": str(filepath),
            "user_id": user_id,
            "label": emotion_label
        })
        
        return filepath
    
    def collect_voice_sample(self, user_id: str, features: Dict[str, float], emotion_label: str = None):
        """Save voice features with optional emotion label."""
        timestamp = int(time.time() * 1000)
        filename = f"{user_id}_{timestamp}.json"
        
        sample = {
            "user_id": user_id,
            "timestamp": timestamp,
            "features": features,
            "emotion_label": emotion_label,
            "type": "voice"
        }
        
        filepath = self.voice_dir / filename
        with open(filepath, 'w') as f:
            json.dump(sample, f)
        
        self.metadata["samples"].append({
            "type": "voice",
            "file": str(filepath),
            "user_id": user_id,
            "label": emotion_label
        })
        
        return filepath
    
    def collect_keystroke_sample(self, user_id: str, events: List[Dict[str, Any]], is_genuine: bool = True):
        """Save keystroke events with authenticity label."""
        timestamp = int(time.time() * 1000)
        filename = f"{user_id}_{timestamp}.json"
        
        sample = {
            "user_id": user_id,
            "timestamp": timestamp,
            "events": events,
            "is_genuine": is_genuine,
            "type": "keystroke"
        }
        
        filepath = self.keystroke_dir / filename
        with open(filepath, 'w') as f:
            json.dump(sample, f)
        
        self.metadata["samples"].append({
            "type": "keystroke",
            "file": str(filepath),
            "user_id": user_id,
            "is_genuine": is_genuine
        })
        
        return filepath
    
    def save_metadata(self):
        """Save session metadata."""
        self.metadata["end_time"] = datetime.now().isoformat()
        self.metadata["total_samples"] = len(self.metadata["samples"])
        
        metadata_path = self.session_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        return metadata_path
    
    def get_summary(self):
        """Get collection summary."""
        facial_count = sum(1 for s in self.metadata["samples"] if s["type"] == "facial")
        voice_count = sum(1 for s in self.metadata["samples"] if s["type"] == "voice")
        keystroke_count = sum(1 for s in self.metadata["samples"] if s["type"] == "keystroke")
        
        return {
            "session_id": self.session_id,
            "session_dir": str(self.session_dir),
            "total_samples": len(self.metadata["samples"]),
            "facial_samples": facial_count,
            "voice_samples": voice_count,
            "keystroke_samples": keystroke_count
        }


def load_collected_data(session_id: str = None):
    """Load collected data from a session."""
    if session_id:
        session_dir = COLLECTED_DATA_DIR / session_id
    else:
        # Load most recent session
        sessions = sorted(COLLECTED_DATA_DIR.iterdir(), key=lambda x: x.name, reverse=True)
        if not sessions:
            return None
        session_dir = sessions[0]
    
    metadata_path = session_dir / "metadata.json"
    if not metadata_path.exists():
        return None
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Load all samples
    samples = {"facial": [], "voice": [], "keystroke": []}
    
    for sample_info in metadata["samples"]:
        sample_type = sample_info["type"]
        filepath = Path(sample_info["file"])
        
        if filepath.exists():
            with open(filepath, 'r') as f:
                sample_data = json.load(f)
                samples[sample_type].append(sample_data)
    
    return {
        "metadata": metadata,
        "samples": samples
    }


def export_for_training(output_dir: str = None):
    """Export all collected data in format suitable for training."""
    if output_dir is None:
        output_dir = STORAGE_DIR / "datasets" / "collected"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Aggregate all sessions
    all_facial = []
    all_voice = []
    all_keystroke = []
    
    for session_dir in COLLECTED_DATA_DIR.iterdir():
        if not session_dir.is_dir():
            continue
        
        data = load_collected_data(session_dir.name)
        if data:
            all_facial.extend(data["samples"]["facial"])
            all_voice.extend(data["samples"]["voice"])
            all_keystroke.extend(data["samples"]["keystroke"])
    
    # Save aggregated data
    with open(output_dir / "facial_data.json", 'w') as f:
        json.dump(all_facial, f, indent=2)
    
    with open(output_dir / "voice_data.json", 'w') as f:
        json.dump(all_voice, f, indent=2)
    
    with open(output_dir / "keystroke_data.json", 'w') as f:
        json.dump(all_keystroke, f, indent=2)
    
    summary = {
        "export_time": datetime.now().isoformat(),
        "facial_samples": len(all_facial),
        "voice_samples": len(all_voice),
        "keystroke_samples": len(all_keystroke),
        "output_dir": str(output_dir)
    }
    
    with open(output_dir / "export_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Exported {summary['facial_samples']} facial, {summary['voice_samples']} voice, "
          f"{summary['keystroke_samples']} keystroke samples to {output_dir}")
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage collected training data')
    parser.add_argument('--export', action='store_true', help='Export all collected data for training')
    parser.add_argument('--list', action='store_true', help='List all collection sessions')
    parser.add_argument('--summary', type=str, help='Show summary for specific session')
    
    args = parser.parse_args()
    
    if args.export:
        export_for_training()
    elif args.list:
        sessions = sorted(COLLECTED_DATA_DIR.iterdir(), key=lambda x: x.name, reverse=True)
        print(f"Found {len(sessions)} collection sessions:")
        for session_dir in sessions:
            data = load_collected_data(session_dir.name)
            if data:
                print(f"\n  {session_dir.name}:")
                print(f"    Facial: {len(data['samples']['facial'])}")
                print(f"    Voice: {len(data['samples']['voice'])}")
                print(f"    Keystroke: {len(data['samples']['keystroke'])}")
    elif args.summary:
        data = load_collected_data(args.summary)
        if data:
            print(json.dumps(data["metadata"], indent=2))
        else:
            print(f"Session {args.summary} not found")
    else:
        parser.print_help()
