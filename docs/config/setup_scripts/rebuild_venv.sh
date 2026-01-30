#!/bin/bash

# Complete rebuild of virtual environment to fix system package conflicts
# This creates a truly isolated environment

set -e

echo "========================================="
echo "REBUILD HYPATIAX ENVIRONMENT"
echo "========================================="
echo ""

# Step 1: Backup requirements if they exist
echo "Step 1: Checking for requirements..."
echo "-----------------------------------"
if [ -f "requirements.txt" ]; then
    echo "✅ Found requirements.txt"
    cp requirements.txt requirements.txt.backup
    echo "✅ Backed up to requirements.txt.backup"
else
    echo "⚠️  No requirements.txt found"
fi
echo ""

# Step 2: Remove old venv_clean
echo "Step 2: Removing old venv_clean..."
echo "-----------------------------------"
if [ -d "venv_clean" ]; then
    echo "Removing venv_clean directory..."
    rm -rf venv_clean
    echo "✅ Removed"
else
    echo "✅ Already clean"
fi
echo ""

# Step 3: Create new isolated virtual environment
echo "Step 3: Creating new virtual environment..."
echo "-----------------------------------"
echo "Using system Python 3..."
python3 -m venv venv_clean --clear

echo "✅ Virtual environment created"
echo ""

# Step 4: Activate and upgrade pip
echo "Step 4: Setting up environment..."
echo "-----------------------------------"
source venv_clean/bin/activate

echo "Python: $(which python)"
echo "Pip: $(which pip)"
echo ""

echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel
echo "✅ Base tools upgraded"
echo ""

# Step 5: Install packages in correct order
echo "Step 5: Installing core packages..."
echo "-----------------------------------"

echo "Installing NumPy and Pandas..."
pip install numpy pandas
echo "✅ NumPy and Pandas installed"
echo ""

echo "Installing PyTorch (CPU version)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
echo "✅ PyTorch installed"
echo ""

echo "Installing spaCy and dependencies..."
pip install -U spacy[transformers]
echo "✅ spaCy installed"
echo ""

echo "Installing Transformers..."
pip install transformers
echo "✅ Transformers installed"
echo ""

# Step 6: Download spaCy model
echo "Step 6: Downloading spaCy model..."
echo "-----------------------------------"
python -m spacy download en_core_web_sm
echo "✅ Model downloaded"
echo ""

# Step 7: Install project-specific requirements if they exist
echo "Step 7: Installing project requirements..."
echo "-----------------------------------"
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    # Install without dependencies to avoid conflicts
    pip install -r requirements.txt --no-deps || echo "⚠️  Some packages failed, continuing..."
    # Then install dependencies
    pip install -r requirements.txt || echo "⚠️  Some dependencies failed"
else
    echo "⚠️  No requirements.txt found, skipping"
fi
echo ""

# Step 8: Verify installation
echo "========================================="
echo "VERIFICATION"
echo "========================================="
python << 'EOF'
import sys
print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("-" * 50)

errors = []

try:
    import numpy as np
    print("✅ NumPy:", np.__version__)
except Exception as e:
    print("❌ NumPy:", str(e)[:50])
    errors.append("numpy")

try:
    import pandas as pd
    print("✅ Pandas:", pd.__version__)
except Exception as e:
    print("❌ Pandas:", str(e)[:50])
    errors.append("pandas")

try:
    import torch
    print("✅ PyTorch:", torch.__version__)
    print("   CUDA available:", torch.cuda.is_available())
except Exception as e:
    print("❌ PyTorch:", str(e)[:50])
    errors.append("torch")

try:
    import spacy
    print("✅ spaCy:", spacy.__version__)
    nlp = spacy.load('en_core_web_sm')
    print("   Model loaded: en_core_web_sm")
except Exception as e:
    print("❌ spaCy:", str(e)[:50])
    errors.append("spacy")

try:
    import transformers
    print("✅ Transformers:", transformers.__version__)
except Exception as e:
    print("❌ Transformers:", str(e)[:50])
    errors.append("transformers")

print("-" * 50)
if errors:
    print(f"❌ {len(errors)} package(s) failed: {', '.join(errors)}")
    sys.exit(1)
else:
    print("🎉 ALL PACKAGES WORKING!")
    print("")
    print("Environment is ready to use!")
EOF

echo ""
echo "========================================="
echo "REBUILD COMPLETE!"
echo "========================================="
echo ""
echo "To use this environment:"
echo "  source venv_clean/bin/activate"
echo ""
echo "To verify:"
echo "  bash ./setup/test1v.sh"
echo ""
