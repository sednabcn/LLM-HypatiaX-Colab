#!/bin/bash

echo "=== Complete Python 3.12 Setup ==="
echo ""

# Check current directory
echo "Current directory: $(pwd)"
echo ""

# Install Python 3.12
echo "=== Installing Python 3.12 ==="
sudo apt-get update -qq
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev build-essential

# Verify Python 3.12
echo ""
echo "Python 3.12 version:"
python3.12 --version

# Create virtual environment
echo ""
echo "=== Creating virtual environment ==="
python3.12 -m venv venv-312

# Check if it was created
if [ -d "venv-312" ]; then
    echo "✓ venv-312 created successfully"
    ls -la venv-312/ | head -5
else
    echo "✗ Failed to create venv-312"
    exit 1
fi

# Activate and install
echo ""
echo "=== Activating environment and installing packages ==="
source venv-312/bin/activate

echo "Python in venv: $(which python)"
echo "Python version: $(python --version)"

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
if [ -f "requirements-py312.txt" ]; then
    echo ""
    echo "Installing from requirements-py312.txt..."
    pip install -r requirements-py312.txt
elif [ -f "requirements.txt" ]; then
    echo ""
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠ No requirements file found"
fi

# Verify key packages
echo ""
echo "=== Verifying installations ==="
python -c "import sys; print(f'Python: {sys.version}')"
python -c "import nltk; print(f'nltk: {nltk.__version__}')" 2>/dev/null || echo "nltk: Not installed"
python -c "import torch; print(f'torch: {torch.__version__}')" 2>/dev/null || echo "torch: Not installed"
python -c "import transformers; print(f'transformers: {transformers.__version__}')" 2>/dev/null || echo "transformers: Not installed"

echo ""
echo "=== Setup complete! ==="
echo ""
echo "To activate this environment in the future, run:"
echo "  source venv-312/bin/activate"
echo ""
echo "To deactivate, run:"
echo "  deactivate"
