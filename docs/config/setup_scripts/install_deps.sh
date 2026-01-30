#!/bin/bash
# HypatiaX Dependency Installation Script
# Handles proper installation order and spaCy models

set -e  # Exit on error

echo "=========================================="
echo "HypatiaX Dependency Installation"
echo "=========================================="
echo ""

PROJECT_DIR="$HOME/Downloads/GITHUB/LLM-HypatiaX"
cd "$PROJECT_DIR" || exit 1

# Check for requirements file
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    echo "Run the create_requirements.sh script first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "⚠ No virtual environment found."
    read -p "Create one now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        echo "✓ Virtual environment created"
    else
        echo "Proceeding without virtual environment..."
    fi
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "✓ Virtual environment activated"
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
fi

echo ""
echo "=========================================="
echo "Step 1: Upgrading pip, setuptools, wheel"
echo "=========================================="
python -m pip install --upgrade pip setuptools wheel
echo "✓ Core tools upgraded"
echo ""

echo "=========================================="
echo "Step 2: Installing setuptools-scm (needed for spacy-transformers)"
echo "=========================================="
pip install setuptools-scm
echo "✓ setuptools-scm installed"
echo ""

echo "=========================================="
echo "Step 3: Installing PyTorch"
echo "=========================================="
echo "Detecting GPU..."
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA GPU detected"
    echo "Installing PyTorch with CUDA 12.1 support..."
    pip install torch==2.2.1 --index-url https://download.pytorch.org/whl/cu121
else
    echo "⚠ No GPU detected, installing CPU-only version..."
    pip install torch==2.2.1 --index-url https://download.pytorch.org/whl/cpu
fi
echo "✓ PyTorch installed"
echo ""

echo "=========================================="
echo "Step 4: Installing spacy-transformers"
echo "=========================================="
pip install spacy-transformers==1.3.4
echo "✓ spacy-transformers installed"
echo ""

echo "=========================================="
echo "Step 5: Installing spacy-lookups-data"
echo "=========================================="
pip install spacy-lookups-data
echo "✓ spacy-lookups-data installed"
echo ""

echo "=========================================="
echo "Step 6: Installing remaining dependencies"
echo "=========================================="
pip install -r requirements.txt
echo "✓ All dependencies installed"
echo ""

echo "=========================================="
echo "Step 7: Installing spaCy models"
echo "=========================================="

echo "Installing en_core_web_sm..."
python -m spacy download en_core_web_sm
echo "✓ en_core_web_sm installed"
echo ""

echo "Installing en_core_web_trf..."
python -m spacy download en_core_web_trf
echo "✓ en_core_web_trf installed"
echo ""

echo "=========================================="
echo "Step 8: Verification"
echo "=========================================="

echo "Testing installations..."
python << 'EOF'
import sys

# Test imports
tests = [
    ("spacy", "spaCy"),
    ("torch", "PyTorch"),
    ("transformers", "Transformers"),
    ("pandas", "Pandas"),
    ("numpy", "NumPy"),
    ("nltk", "NLTK"),
    ("sklearn", "scikit-learn"),
    ("cv2", "OpenCV"),
    ("matplotlib", "Matplotlib"),
]

print("\n=== Import Tests ===")
failed = []
for module, name in tests:
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {name:20s} : {version}")
    except ImportError as e:
        print(f"✗ {name:20s} : FAILED")
        failed.append(name)

# Test spaCy models
print("\n=== spaCy Models ===")
try:
    import spacy
    
    models = ['en_core_web_sm', 'en_core_web_trf']
    for model in models:
        try:
            nlp = spacy.load(model)
            print(f"✓ {model:20s} : Loaded successfully")
        except OSError:
            print(f"✗ {model:20s} : Not found")
            failed.append(model)
except Exception as e:
    print(f"✗ spaCy model test failed: {e}")
    failed.append("spaCy models")

# Test GPU availability
print("\n=== GPU Status ===")
try:
    import torch
    if torch.cuda.is_available():
        print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
        print(f"  CUDA version: {torch.version.cuda}")
        print(f"  Devices: {torch.cuda.device_count()}")
    else:
        print("⚠ CUDA not available (CPU-only mode)")
except Exception as e:
    print(f"⚠ Could not check GPU: {e}")

# Summary
print("\n=== Summary ===")
if failed:
    print(f"❌ {len(failed)} component(s) failed:")
    for item in failed:
        print(f"   - {item}")
    sys.exit(1)
else:
    print("✅ All components installed successfully!")
    sys.exit(0)
EOF

RESULT=$?

echo ""
echo "=========================================="
if [ $RESULT -eq 0 ]; then
    echo "✅ INSTALLATION SUCCESSFUL!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Activate virtual environment (if not active):"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Test with your notebook:"
    echo "   jupyter notebook"
    echo ""
    echo "3. Check custom models:"
    echo "   ls -la ner_* Description_* Formulas_* Combined_*"
else
    echo "❌ INSTALLATION HAD ISSUES"
    echo "=========================================="
    echo ""
    echo "Please review the errors above and:"
    echo "1. Check your Python version (3.8+ required)"
    echo "2. Ensure you have enough disk space"
    echo "3. Check your internet connection"
    echo "4. Try running individual failed components manually"
fi

echo ""
echo "=========================================="
