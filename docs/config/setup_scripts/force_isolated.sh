#!/bin/bash

# Force completely isolated virtual environment
# This explicitly blocks system site-packages

set -e

echo "========================================="
echo "FORCE ISOLATED ENVIRONMENT"
echo "========================================="
echo ""

# Step 1: Remove old environment
echo "Step 1: Cleaning up..."
echo "-----------------------------------"
deactivate 2>/dev/null || true
rm -rf venv_clean
echo "✅ Cleaned"
echo ""

# Step 2: Create truly isolated venv (no system packages)
echo "Step 2: Creating isolated environment..."
echo "-----------------------------------"
python3 -m venv venv_clean --without-pip --clear
source venv_clean/bin/activate

# Manually install pip inside the venv
echo "Installing pip from scratch..."
curl -s https://bootstrap.pypa.io/get-pip.py | python
echo "✅ Isolated venv created with pip"
echo ""

# Step 3: Verify isolation
echo "Step 3: Verifying isolation..."
echo "-----------------------------------"
python << 'EOF'
import sys
print("Python:", sys.executable)
print("Site packages:", sys.path)
print("")
# Check if system packages are visible
try:
    import torch
    print("❌ WARNING: System torch is still visible!")
except ImportError:
    print("✅ System packages properly isolated")
EOF
echo ""

# Step 4: Install packages
echo "Step 4: Installing packages..."
echo "-----------------------------------"

echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo ""

echo "Installing NumPy and Pandas..."
pip install --no-cache-dir numpy==1.26.4 pandas==2.2.3
echo ""

echo "Installing PyTorch (CPU)..."
pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
echo ""

echo "Installing spaCy..."
pip install --no-cache-dir spacy[transformers]
echo ""

echo "Installing Transformers..."
pip install --no-cache-dir transformers
echo ""

# Step 5: Download spaCy model
echo "Step 5: Downloading spaCy model..."
echo "-----------------------------------"
python -m spacy download en_core_web_sm
echo ""

# Step 6: Final verification
echo "========================================="
echo "FINAL VERIFICATION"
echo "========================================="
python << 'EOF'
import sys
print("Python:", sys.executable)
print("=" * 50)

success = True

try:
    import numpy as np
    print("✅ NumPy:", np.__version__)
    assert 'venv_clean' in np.__file__, f"NumPy from wrong location: {np.__file__}"
except Exception as e:
    print("❌ NumPy:", str(e))
    success = False

try:
    import pandas as pd
    print("✅ Pandas:", pd.__version__)
    assert 'venv_clean' in pd.__file__, f"Pandas from wrong location: {pd.__file__}"
except Exception as e:
    print("❌ Pandas:", str(e))
    success = False

try:
    import torch
    print("✅ PyTorch:", torch.__version__)
    print("   Location:", torch.__file__)
    assert 'venv_clean' in torch.__file__, f"PyTorch from wrong location: {torch.__file__}"
    print("   CUDA:", torch.cuda.is_available())
except Exception as e:
    print("❌ PyTorch:", str(e))
    success = False

try:
    import spacy
    print("✅ spaCy:", spacy.__version__)
    assert 'venv_clean' in spacy.__file__, f"spaCy from wrong location: {spacy.__file__}"
    nlp = spacy.load('en_core_web_sm')
    print("   Model: en_core_web_sm loaded")
except Exception as e:
    print("❌ spaCy:", str(e))
    success = False

try:
    import transformers
    print("✅ Transformers:", transformers.__version__)
    assert 'venv_clean' in transformers.__file__, f"Transformers from wrong location: {transformers.__file__}"
except Exception as e:
    print("❌ Transformers:", str(e))
    success = False

print("=" * 50)
if success:
    print("🎉 ALL PACKAGES WORKING FROM VENV!")
    sys.exit(0)
else:
    print("❌ Some packages failed")
    sys.exit(1)
EOF

echo ""
echo "========================================="
echo "SETUP COMPLETE!"
echo "========================================="
echo ""
echo "To use: source venv_clean/bin/activate"
echo ""
