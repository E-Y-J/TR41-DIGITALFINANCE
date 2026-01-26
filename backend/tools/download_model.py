#!/usr/bin/env python
# =============================================================================
# Digital Finance Tracker - Download HuggingFace Model
# PURPOSE: Pre-download the AI categorization model for offline use
# =============================================================================
"""
Model Download Script

Downloads the HuggingFace transaction categorization model to local storage.
Run this script once to pre-download the model for faster first-time inference.

Usage:
    python tools/download_model.py

    # Or with custom path:
    python tools/download_model.py --path app/ai/model_store

    # Use HuggingFace cache instead:
    python tools/download_model.py --use-cache

Notes:
    - Model: mitulshah/global-financial-transaction-classifier
    - Size: ~267MB
    - The model_store/ directory is gitignored
    - Model auto-downloads on first use if not pre-downloaded
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def download_model(model_path: str = None, use_cache: bool = False):
    """
    Download the HuggingFace model.

    Args:
        model_path: Path to store the model (default: app/ai/model_store)
        use_cache: If True, use HuggingFace's default cache
    """
    print("=" * 60)
    print("Digital Finance Tracker - Model Download")
    print("=" * 60)

    model_name = "mitulshah/global-financial-transaction-classifier"

    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        if use_cache:
            print(f"\nDownloading model to HuggingFace cache...")
            print(f"Model: {model_name}")
            print("-" * 60)

            # Download to default cache
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)

            print("\n✅ Model downloaded to HuggingFace cache!")
            print(f"   Cache location: ~/.cache/huggingface/hub/")

        else:
            # Use custom path
            if model_path is None:
                model_path = Path(__file__).parent.parent / "app" / "ai" / "model_store"
            else:
                model_path = Path(model_path)

            # Create directory if needed
            model_path.mkdir(parents=True, exist_ok=True)

            print(f"\nDownloading model to: {model_path}")
            print(f"Model: {model_name}")
            print("-" * 60)

            # Download and save
            print("\n[1/2] Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            tokenizer.save_pretrained(model_path)

            print("[2/2] Downloading model...")
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            model.save_pretrained(model_path)

            print("\n✅ Model downloaded successfully!")
            print(f"   Location: {model_path}")
            print(f"   Size: ~267MB")

        print("\n" + "=" * 60)
        print("Model is ready for use!")
        print("=" * 60)

    except ImportError:
        print("\n❌ Error: transformers package not installed")
        print("   Run: pip install transformers torch")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error downloading model: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Download HuggingFace transaction categorization model"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="Path to store the model (default: app/ai/model_store)",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Use HuggingFace's default cache instead of local storage",
    )

    args = parser.parse_args()
    download_model(model_path=args.path, use_cache=args.use_cache)


if __name__ == "__main__":
    main()
