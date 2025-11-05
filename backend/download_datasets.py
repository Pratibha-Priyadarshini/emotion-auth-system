"""
Automated dataset download script.
Downloads publicly available emotion recognition datasets.
"""

import os
import sys
import urllib.request
import zipfile
import tarfile
from pathlib import Path

STORAGE_DIR = Path(__file__).parent / "storage"
DATA_DIR = STORAGE_DIR / "datasets"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url: str, destination: Path, description: str = ""):
    """Download file with progress bar."""
    print(f"Downloading {description}...")
    print(f"URL: {url}")
    print(f"Destination: {destination}")
    
    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r{percent}% complete")
        sys.stdout.flush()
    
    try:
        urllib.request.urlretrieve(url, destination, progress_hook)
        print("\nDownload complete!")
        return True
    except Exception as e:
        print(f"\nError downloading: {e}")
        return False


def extract_archive(archive_path: Path, extract_to: Path):
    """Extract zip or tar archive."""
    print(f"Extracting {archive_path.name}...")
    
    try:
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_path.suffix in ['.tar', '.gz', '.tgz']:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_to)
        
        print("Extraction complete!")
        return True
    except Exception as e:
        print(f"Error extracting: {e}")
        return False


def download_fer2013():
    """
    Download FER2013 dataset.
    Note: Requires Kaggle API credentials.
    """
    print("\n=== FER2013 Facial Emotion Dataset ===")
    
    fer_dir = DATA_DIR / "fer2013"
    fer_dir.mkdir(exist_ok=True)
    
    print("\nFER2013 requires Kaggle API access.")
    print("Steps to download:")
    print("1. Install Kaggle CLI: pip install kaggle")
    print("2. Get API credentials from https://www.kaggle.com/settings")
    print("3. Place kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\\Users\\<user>\\.kaggle\\ (Windows)")
    print("4. Run: kaggle datasets download -d msambare/fer2013 -p", fer_dir)
    print("5. Unzip the downloaded file")
    
    try:
        import kaggle
        print("\nKaggle API detected. Attempting download...")
        os.system(f"kaggle datasets download -d msambare/fer2013 -p {fer_dir}")
        
        # Extract if zip exists
        zip_path = fer_dir / "fer2013.zip"
        if zip_path.exists():
            extract_archive(zip_path, fer_dir)
            zip_path.unlink()  # Remove zip after extraction
            print(f"FER2013 dataset ready at {fer_dir}")
            return True
    except ImportError:
        print("\nKaggle API not installed. Install with: pip install kaggle")
    except Exception as e:
        print(f"\nError: {e}")
    
    return False


def download_ravdess():
    """
    Download RAVDESS voice emotion dataset.
    Note: Large dataset, requires manual download.
    """
    print("\n=== RAVDESS Voice Emotion Dataset ===")
    
    ravdess_dir = DATA_DIR / "RAVDESS"
    ravdess_dir.mkdir(exist_ok=True)
    
    print("\nRAVDESS is a large dataset (24GB) and requires manual download.")
    print("Steps to download:")
    print("1. Visit: https://www.kaggle.com/datasets/uwrfkaggle/ravdess-emotional-speech-audio")
    print("2. Download the dataset")
    print("3. Extract to:", ravdess_dir)
    print("\nAlternatively, download from Zenodo:")
    print("https://zenodo.org/record/1188976")
    
    return False


def download_sample_datasets():
    """
    Download small sample datasets for testing.
    """
    print("\n=== Downloading Sample Datasets ===")
    
    # Create sample facial emotion data
    print("\nCreating sample facial emotion dataset...")
    fer_sample_dir = DATA_DIR / "fer2013_sample"
    fer_sample_dir.mkdir(exist_ok=True)
    
    # Generate sample CSV
    import csv
    import numpy as np
    
    sample_csv = fer_sample_dir / "fer2013.csv"
    with open(sample_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['emotion', 'pixels', 'Usage'])
        
        # Generate 1000 random samples
        for i in range(1000):
            emotion = np.random.randint(0, 7)
            pixels = ' '.join([str(np.random.randint(0, 256)) for _ in range(48*48)])
            usage = 'Training' if i < 800 else 'PublicTest'
            writer.writerow([emotion, pixels, usage])
    
    print(f"Sample FER2013 dataset created at {sample_csv}")
    
    # Create sample voice data
    print("\nCreating sample voice emotion dataset...")
    ravdess_sample_dir = DATA_DIR / "RAVDESS_sample"
    ravdess_sample_dir.mkdir(exist_ok=True)
    
    print(f"Sample RAVDESS directory created at {ravdess_sample_dir}")
    print("Note: Audio files need to be recorded or downloaded separately")
    
    # Create sample keystroke data
    print("\nCreating sample keystroke dataset...")
    cmu_sample_dir = DATA_DIR / "CMU_Keystroke_sample"
    cmu_sample_dir.mkdir(exist_ok=True)
    
    import json
    
    # Generate sample keystroke data for 5 users
    for user_id in range(5):
        user_file = cmu_sample_dir / f"user_{user_id}.json"
        samples = []
        
        for _ in range(50):
            n_keys = np.random.randint(8, 15)
            base_hold = 80 + user_id * 10
            base_flight = 120 + user_id * 15
            
            events = []
            t = 0
            for j in range(n_keys):
                t_down = t
                t_up = t + np.random.normal(base_hold, 20)
                events.append({
                    'key': chr(65 + j % 26),
                    't_down': t_down,
                    't_up': t_up
                })
                t = t_up + np.random.normal(base_flight, 30)
            
            samples.append(events)
        
        with open(user_file, 'w') as f:
            json.dump(samples, f, indent=2)
    
    print(f"Sample keystroke dataset created at {cmu_sample_dir}")
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Download emotion recognition datasets')
    parser.add_argument('--fer2013', action='store_true', help='Download FER2013 facial emotion dataset')
    parser.add_argument('--ravdess', action='store_true', help='Download RAVDESS voice emotion dataset')
    parser.add_argument('--samples', action='store_true', help='Create sample datasets for testing')
    parser.add_argument('--all', action='store_true', help='Attempt to download all datasets')
    
    args = parser.parse_args()
    
    if not any([args.fer2013, args.ravdess, args.samples, args.all]):
        parser.print_help()
        return
    
    print("=" * 60)
    print("Dataset Download Utility")
    print("=" * 60)
    
    if args.samples or args.all:
        download_sample_datasets()
    
    if args.fer2013 or args.all:
        download_fer2013()
    
    if args.ravdess or args.all:
        download_ravdess()
    
    print("\n" + "=" * 60)
    print("Dataset download process complete!")
    print("=" * 60)
    print(f"\nDatasets location: {DATA_DIR}")
    print("\nNext steps:")
    print("1. Verify datasets are properly extracted")
    print("2. Run training: python -m backend.train_models --all")


if __name__ == "__main__":
    main()
