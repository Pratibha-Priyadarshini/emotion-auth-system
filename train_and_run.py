"""
Quick start script for training models and running the application.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with error code {e.returncode}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick start for emotion-aware authentication')
    parser.add_argument('--skip-install', action='store_true', help='Skip dependency installation')
    parser.add_argument('--skip-datasets', action='store_true', help='Skip dataset download')
    parser.add_argument('--skip-training', action='store_true', help='Skip model training')
    parser.add_argument('--run-server', action='store_true', help='Run the server after setup')
    parser.add_argument('--evaluate', action='store_true', help='Evaluate models after training')
    
    args = parser.parse_args()
    
    print("="*60)
    print("Emotion-Aware Authentication - Quick Start")
    print("="*60)
    
    # Step 1: Install dependencies
    if not args.skip_install:
        if not run_command(
            f"{sys.executable} -m pip install -r backend/requirements.txt",
            "Installing dependencies"
        ):
            print("\nFailed to install dependencies. Please check your Python environment.")
            return
    
    # Step 2: Download sample datasets
    if not args.skip_datasets:
        if not run_command(
            f"{sys.executable} -m backend.download_datasets --samples",
            "Downloading sample datasets"
        ):
            print("\nWarning: Dataset download failed. Training will use synthetic data.")
    
    # Step 3: Train models
    if not args.skip_training:
        if not run_command(
            f"{sys.executable} -m backend.train_models --all",
            "Training all models"
        ):
            print("\nWarning: Training failed. System will use heuristic fallbacks.")
    
    # Step 4: Evaluate models (optional)
    if args.evaluate:
        run_command(
            f"{sys.executable} -m backend.evaluate_models --all",
            "Evaluating trained models"
        )
    
    # Step 5: Run server (optional)
    if args.run_server:
        print("\n" + "="*60)
        print("Starting FastAPI server")
        print("="*60)
        print("\nServer will be available at:")
        print("  - Main UI: http://localhost:8000/web/index.html")
        print("  - Admin Dashboard: http://localhost:8000/web/admin.html")
        print("  - API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the server\n")
        
        try:
            subprocess.run(
                f"{sys.executable} -m uvicorn backend.main:app --reload",
                shell=True,
                check=True
            )
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
    else:
        print("\n" + "="*60)
        print("Setup Complete!")
        print("="*60)
        print("\nTo start the server, run:")
        print(f"  {sys.executable} -m uvicorn backend.main:app --reload")
        print("\nOr run this script with --run-server flag:")
        print(f"  {sys.executable} train_and_run.py --run-server")

if __name__ == "__main__":
    main()
