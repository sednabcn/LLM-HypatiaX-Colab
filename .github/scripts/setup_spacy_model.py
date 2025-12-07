#!/usr/bin/env python3
"""
Setup script to download required spaCy models for LLM-HypatiaX
"""

import subprocess
import sys


def install_spacy_model(model_name):
    """Install a spaCy model using pip"""
    print(f"Installing spaCy model: {model_name}")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
        print(f"✓ Successfully installed {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing {model_name}: {e}")
        return False


def verify_model(model_name):
    """Verify that a spaCy model can be loaded"""
    try:
        import spacy

        nlp = spacy.load(model_name)
        print(f"✓ {model_name} verified and ready to use")
        return True
    except Exception as e:
        print(f"✗ Error loading {model_name}: {e}")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("LLM-HypatiaX: spaCy Models Setup")
    print("=" * 60)

    models = [
        "en_core_web_sm",  # Small English model
        # Add more models if needed:
        # "en_core_web_md",  # Medium English model
        # "en_core_web_lg",  # Large English model
    ]

    success_count = 0

    for model in models:
        print(f"\n[{models.index(model) + 1}/{len(models)}] Processing {model}...")

        if install_spacy_model(model):
            if verify_model(model):
                success_count += 1

        print("-" * 60)

    print(f"\n{'=' * 60}")
    print(f"Setup Complete: {success_count}/{len(models)} models installed")
    print(f"{'=' * 60}")

    if success_count == len(models):
        print("✓ All models ready! You can now use LLM-HypatiaX.")
        return 0
    else:
        print("⚠ Some models failed to install. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
