#!/bin/bash

# Fix script for Hypatiax environment issues
# This will reinstall the broken packages

set -e  # Exit on error

echo "========================================="
echo "HYPATIAX ENVIRONMENT FIX"
echo "========================================="
echo ""

# Activate environment
if [ -d "venv_clean" ]; then
    echo "✅ Activating venv_clean..."
    source venv_clean/bin/activate
else
    echo "❌ venv_clean not found!"
    exit 1
fi

echo "Python: $(which python)"
echo "Pip: $(which pip)"
echo ""

# Step 1: Fix PyTorch
echo "Step 1: Fixing PyTorch..."
echo "-----------------------------------"
echo "Uninstalling broken PyTorch..."
pip uninstall -y torch torchvision torchaudio 2>/dev/null || true

echo ""
echo "Reinstalling PyTorch (CPU version)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo ""
echo "Testing PyTorch..."
python -c "import torch; print('✅ PyTorch version:', torch.__version__); print('✅ CUDA available:', torch.cuda.is_available())"
echo ""

# Step 2: Fix spaCy and dependencies
echo "Step 2: Fixing spaCy..."
echo "-----------------------------------"
echo "Uninstalling broken spaCy packages..."
pip uninstall -y spacy spacy-legacy spacy-loggers srsly thinc 2>/dev/null || true

echo ""
echo "Reinstalling spaCy and dependencies..."
pip install -U pip setuptools wheel
pip install -U spacy srsly thinc

echo ""
echo "Testing spaCy..."
python -c "import spacy; print('✅ spaCy version:', spacy.__version__)"
echo ""

# Step 3: Download spaCy model
echo "Step 3: Downloading spaCy model..."
echo "-----------------------------------"
python -m spacy download en_core_web_sm

echo ""
echo "Testing model load..."
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ Model loaded successfully')"
echo ""

# Step 4: Fix Transformers
echo "Step 4: Fixing Transformers..."
echo "-----------------------------------"
pip install -U transformers

echo ""
echo "Testing Transformers..."
python -c "import transformers; print('✅ Transformers version:', transformers.__version__)"
echo ""

# Step 5: Verify everything
echo "========================================="
echo "VERIFICATION"
echo "========================================="
python << 'EOF'
import sys

print("Testing all imports...")
print("-" * 40)

errors = []

try:
    import spacy
    print("✅ spaCy:", spacy.__version__)
except Exception as e:
    print("❌ spaCy failed:", e)
    errors.append("spacy")

try:
    import torch
    print("✅ PyTorch:", torch.__version__)
except Exception as e:
    print("❌ PyTorch failed:", e)
    errors.append("torch")

try:
    import transformers
    print("✅ Transformers:", transformers.__version__)
except Exception as e:
    print("❌ Transformers failed:", e)
    errors.append("transformers")

try:
    import pandas as pd
    print("✅ Pandas:", pd.__version__)
except Exception as e:
    print("❌ Pandas failed:", e)
    errors.append("pandas")

try:
    import numpy as np
    print("✅ NumPy:", np.__version__)
except Exception as e:
    print("❌ NumPy failed:", e)
    errors.append("numpy")

print("-" * 40)
if errors:
    print(f"❌ {len(errors)} package(s) still broken: {', '.join(errors)}")
    sys.exit(1)
else:
    print("✅ All packages working!")
EOF

echo ""
echo "========================================="
echo "FIX COMPLETE!"
echo "========================================="
echo ""
echo "You can now run the diagnostic again:"
echo "  bash ./setup/test1v.sh"
echo ""
