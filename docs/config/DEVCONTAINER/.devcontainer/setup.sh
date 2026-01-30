#!/bin/bash
set -e

# Ensure the script runs from the repo root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"  # This ensures you're always in the root of your repo

PYTHON_VERSION=${1:-"3.13"}

echo "=========================================="
echo "Setting up HypatiaX for Python $PYTHON_VERSION"
echo "=========================================="

# Determine Python executable
if [ "$PYTHON_VERSION" = "3.10" ]; then
    PYTHON_CMD="python3.10"
elif [ "$PYTHON_VERSION" = "3.11" ]; then
    PYTHON_CMD="python3.11"
elif [ "$PYTHON_VERSION" = "3.12" ] || [ "$PYTHON_VERSION" = "3.12.2" ]; then
    PYTHON_CMD="python3.12"
elif [ "$PYTHON_VERSION" = "3.13" ]; then
    PYTHON_CMD="python3.13"
else
    PYTHON_CMD="python3"
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Upgrade pip
$PYTHON_CMD -m pip install --upgrade pip setuptools wheel

# Install dependencies based on Python version
echo ""
echo "Installing dependencies for Python $PYTHON_VERSION..."

if [ "$PYTHON_VERSION" = "3.10" ]; then
    echo "📦 Installing Colab-compatible versions..."
    if [ -f "requirements-py310.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements-py310.txt
    else
        $PYTHON_CMD -m pip install \
            spacy==3.7.2 \
            torch==2.0.1 \
            transformers==4.35.0 \
            pandas==2.0.3 \
            numpy==1.24.3 \
            nltk==3.8.1 \
            matplotlib==3.7.1 \
            jupyter notebook ipython
    fi
elif [ "$PYTHON_VERSION" = "3.11" ]; then
    echo "📦 Installing Python 3.11 compatible versions..."
    if [ -f "requirements-py311.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements-py311.txt
    else
        $PYTHON_CMD -m pip install \
            spacy==3.8.0 \
            torch==2.1.0 \
            transformers==4.40.0 \
            pandas==2.1.0 \
            numpy==1.26.0 \
            nltk==3.8.1 \
            matplotlib==3.8.0 \
            jupyter notebook ipython
    fi
elif [ "$PYTHON_VERSION" = "3.12" ] || [ "$PYTHON_VERSION" = "3.12.2" ]; then
    echo "📦 Installing Python 3.12 compatible versions..."
    if [ -f "requirements-py312.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements-py312.txt
    else
        $PYTHON_CMD -m pip install \
            spacy==3.8.2 \
            torch==2.2.0 \
            transformers==4.41.2 \
            pandas==2.2.1 \
            numpy==1.26.4 \
            nltk==3.8.1 \
            matplotlib==3.8.3 \
            jupyter notebook ipython
    fi
else
    echo "📦 Installing latest versions for Python 3.13..."
    if [ -f "requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements.txt
    else
        $PYTHON_CMD -m pip install \
            spacy \
            torch \
            transformers \
            pandas \
            numpy \
            nltk \
            matplotlib \
            jupyter notebook ipython
    fi
fi

# Install spaCy models
echo ""
echo "📥 Downloading spaCy models..."
$PYTHON_CMD -m spacy download en_core_web_sm

# Install project in editable mode
echo ""
echo "📦 Installing hypatiax package..."
if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    $PYTHON_CMD -m pip install -e .
else
    echo "⚠️  No setup.py or pyproject.toml found"
fi

# Verify installation
echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="
$PYTHON_CMD -c "import sys; print(f'✅ Python: {sys.version}')"
$PYTHON_CMD -c "import spacy; print(f'✅ spaCy: {spacy.__version__}')"
$PYTHON_CMD -c "import torch; print(f'✅ PyTorch: {torch.__version__}')"
$PYTHON_CMD -c "import transformers; print(f'✅ Transformers: {transformers.__version__}')"
$PYTHON_CMD -c "import pandas; print(f'✅ Pandas: {pandas.__version__}')"
$PYTHON_CMD -c "import numpy; print(f'✅ NumPy: {numpy.__version__}')"

# Try to import hypatiax
$PYTHON_CMD -c "import hypatiax; print('✅ HypatiaX package installed')" 2>/dev/null || echo "⚠️  HypatiaX package not installed (optional)"

echo ""
echo "=========================================="
echo "Setup Complete for Python $PYTHON_VERSION!"
echo "==========================================
