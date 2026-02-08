#!/usr/bin/env python
# =============================================================================
# Digital Finance Tracker - Download AI Models
# PURPOSE: Pre-download AI models for faster startup and offline use
# =============================================================================
"""
Model Download Script

Downloads the required AI models for RUNTIME:
1. MiniLM (sentence-transformers) - Intent classification & embeddings (~80MB)

The fine-tuned DistilBERT model (transaction_classification_model/) must be
obtained separately from Jae - it contains the custom trained weights.

Note: DistilBERT base is NOT needed at runtime. The fine-tuned model is
self-contained. Base model is only used during training (see training/ folder).

Usage:
    # Download MiniLM model
    python tools/download_model.py

    # Check model status only
    python tools/download_model.py --check

Models:
    - MiniLM: sentence-transformers/multi-qa-MiniLM-L6-cos-v1 (~80MB)
    - Fine-tuned: app/ai/transaction_classification_model/ (from Jae, ~250MB)
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Model names
MINILM_MODEL = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
FINE_TUNED_DIR = "transaction_classification_model"


def check_models() -> dict:
    """
    Check which models are available.

    Returns:
        Dict with model availability status
    """
    status = {
        "minilm": False,
        "fine_tuned": False,
        "fine_tuned_path": None,
    }

    # Check fine-tuned model (local directory)
    fine_tuned_path = Path(__file__).parent.parent / "app" / "ai" / FINE_TUNED_DIR
    status["fine_tuned_path"] = str(fine_tuned_path)

    if fine_tuned_path.exists():
        # Check for required files
        required_files = ["config.json", "pytorch_model.bin", "tokenizer_config.json"]
        alt_files = ["config.json", "model.safetensors", "tokenizer_config.json"]
        has_required = all((fine_tuned_path / f).exists() for f in required_files)
        has_alt = all((fine_tuned_path / f).exists() for f in alt_files)
        status["fine_tuned"] = has_required or has_alt

    # Check MiniLM (in HuggingFace cache)
    try:
        from sentence_transformers import SentenceTransformer
        # Check if model is cached (won't download if not)
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        minilm_cache = list(cache_dir.glob("*multi-qa-MiniLM*")) if cache_dir.exists() else []
        status["minilm"] = len(minilm_cache) > 0
    except ImportError:
        pass

    return status


def download_minilm():
    """Download MiniLM model for intent classification."""
    print(f"\n[MiniLM] Downloading {MINILM_MODEL}...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MINILM_MODEL)
        print(f"[MiniLM] ✅ Downloaded successfully (~80MB)")
        return True
    except Exception as e:
        print(f"[MiniLM] ❌ Failed: {e}")
        return False


def print_status(status: dict):
    """Print model status in a nice format."""
    print("\n" + "=" * 60)
    print("AI Model Status")
    print("=" * 60)

    def icon(ok): return "✅" if ok else "❌"

    print(f"\n{icon(status['minilm'])} MiniLM (Intent Classifier)")
    print(f"   Model: {MINILM_MODEL}")
    print(f"   Size: ~80MB | Source: HuggingFace")

    print(f"\n{icon(status['fine_tuned'])} Fine-Tuned Categorizer (Jae's model)")
    print(f"   Path: {status['fine_tuned_path']}")
    print(f"   Size: ~250MB | Source: Shared separately")

    if not status['fine_tuned']:
        print("\n" + "-" * 60)
        print("⚠️  Fine-tuned model not found!")
        print("")
        print("Get the fine-tuned model files from Jae and place them in:")
        print(f"  {status['fine_tuned_path']}/")
        print("")
        print("Required files:")
        print("  - config.json")
        print("  - pytorch_model.bin (or model.safetensors)")
        print("  - tokenizer_config.json")
        print("  - vocab.txt")
        print("-" * 60)

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Download AI models for Digital Finance Tracker"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check model status without downloading",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (for Docker builds)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Digital Finance Tracker - AI Model Setup")
    print("=" * 60)

    # Check current status
    status = check_models()

    if args.check:
        print_status(status)
        sys.exit(0 if status['fine_tuned'] else 1)

    # Download MiniLM (only HuggingFace model needed at runtime)
    success = True

    if not status['minilm']:
        success = download_minilm()
    else:
        print("\n[MiniLM] Already cached, skipping...")

    # Show final status
    if not args.quiet:
        status = check_models()  # Refresh status
        print_status(status)

    if success:
        print("\n✅ HuggingFace models ready!")
    else:
        print("\n⚠️  Some downloads failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
