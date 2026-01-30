#!/bin/bash
# Create or Update requirements.txt for HypatiaX

PROJECT_DIR="$HOME/Downloads/LLM-HypatiaX"
cd "$PROJECT_DIR" || exit 1

echo "=========================================="
echo "HypatiaX Requirements Generator"
echo "=========================================="
echo ""

# Backup existing requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    BACKUP="requirements.txt.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Backing up existing requirements.txt to $BACKUP"
    cp requirements.txt "$BACKUP"
fi

# Create new requirements.txt based on notebook analysis
cat > requirements.txt << 'EOF'
# HypatiaX - NLP for Tableau Formula Mapping
# Core dependencies for NER training and evaluation
# Based on actual notebook imports and usage

# ============================================
# Core NLP Libraries
# ============================================
spacy>=3.7.0,<4.0.0
# For transformer models
spacy-transformers==1.3.4
spacy-curated-transformers>=0.2.0,<0.3.0
# Additional spaCy components
spacy-lookups-data>=1.0.0
# Alignment utilities
spacy-alignments>=0.9.0,<1.0.0

# ============================================
# Deep Learning & Transformers
# ============================================
torch>=2.2.0,<3.0.0
transformers>=4.36.0,<4.37.0
# CUDA support (if needed)
nvidia-cuda-nvrtc-cu12==12.1.105
nvidia-cuda-runtime-cu12==12.1.105
nvidia-cuda-cupti-cu12==12.1.105
nvidia-cudnn-cu12==8.9.2.26
nvidia-cublas-cu12==12.1.3.1
nvidia-cufft-cu12==11.0.2.54
nvidia-curand-cu12==10.3.2.106
nvidia-cusolver-cu12==11.4.5.107
nvidia-cusparse-cu12==12.1.0.106
nvidia-nccl-cu12==2.19.3
nvidia-nvtx-cu12==12.1.105
nvidia-nvjitlink-cu12>=12.4.0
triton==2.2.0

# ============================================
# Data Processing
# ============================================
pandas>=2.0.0,<3.0.0
numpy>=1.24.0,<2.0.0
openpyxl>=3.1.0  # For Excel file handling

# ============================================
# Machine Learning
# ============================================
scikit-learn>=1.3.0,<2.0.0

# ============================================
# NLP Utilities
# ============================================
nltk>=3.8.0

# ============================================
# Visualization & Image Processing
# ============================================
matplotlib>=3.7.0,<4.0.0
opencv-python>=4.8.0

# ============================================
# Development Tools
# ============================================
jupyter>=1.0.0
notebook>=7.0.0
ipython>=8.0.0

# ============================================
# Utility Libraries
# ============================================
setuptools-scm>=8.0.0

# ============================================
# Testing (optional)
# ============================================
pytest>=7.0.0
pytest-cov>=4.0.0

# ============================================
# spaCy Models (install separately)
# ============================================
# After pip install, run:
#   python -m spacy download en_core_web_sm
#   python -m spacy download en_core_web_trf
#
# Model versions used in notebook:
#   en_core_web_sm==3.7.1
#   en_core_web_trf==3.7.3
#
# Custom trained models (should exist in project):
#   - ner_desc
#   - ner_formulas
#   - Description_Tableau_data
#   - Formulas_Tableau_data
#   - Combined_multi_task_data_400.0.5.8

# ============================================
# Notes:
# ============================================
# For GPU support with CUDA 12.1, PyTorch should auto-install CUDA libs
# For CPU-only, remove nvidia-* packages and install:
#   pip install torch --index-url https://download.pytorch.org/whl/cpu
#
# Google Colab specific:
#   - google.colab.patches (pre-installed in Colab)
#   - cv2_imshow from google.colab.patches
EOF

echo "✓ Created requirements.txt"
echo ""#!/bin/bash
# Create or Update requirements.txt for HypatiaX

PROJECT_DIR="$HOME/Downloads/GITHUB/LLM-HypatiaX"
cd "$PROJECT_DIR" || exit 1

echo "=========================================="
echo "HypatiaX Requirements Generator"
echo "=========================================="
echo ""

# Backup existing requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    BACKUP="requirements.txt.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Backing up existing requirements.txt to $BACKUP"
    cp requirements.txt "$BACKUP"
fi

# Create new requirements.txt based on notebook analysis
cat > requirements.txt << 'EOF'
# HypatiaX - NLP for Tableau Formula Mapping
# Core dependencies for NER training and evaluation

# ============================================
# Core NLP Libraries
# ============================================
spacy>=3.7.0,<4.0.0
# For transformer models
spacy-transformers>=1.3.0
# Additional spaCy components
spacy-lookups-data>=1.0.0

# ============================================
# Deep Learning
# ============================================
torch>=2.0.0,<3.0.0
transformers>=4.30.0,<5.0.0

# ============================================
# Data Processing
# ============================================
pandas>=2.0.0,<3.0.0
numpy>=1.24.0,<2.0.0
openpyxl>=3.1.0  # For Excel file handling

# ============================================
# NLP Utilities
# ============================================
nltk>=3.8.0

# ============================================
# Visualization
# ============================================
matplotlib>=3.7.0,<4.0.0

# ============================================
# Development Tools
# ============================================
jupyter>=1.0.0
notebook>=7.0.0
ipython>=8.0.0

# ============================================
# Testing (optional)
# ============================================
pytest>=7.0.0
pytest-cov>=4.0.0

# ============================================
# Notes:
# ============================================
# After installing requirements, run:
#   python -m spacy download en_core_web_sm
#   python -m spacy download en_core_web_trf
#
# For GPU support, install PyTorch with CUDA:
#   pip install torch --index-url https://download.pytorch.org/whl/cu118
EOF

echo "✓ Created requirements.txt"
echo ""

# Create requirements-dev.txt for development dependencies
cat > requirements-dev.txt << 'EOF'
# Development dependencies for HypatiaX

# Code formatting
black>=23.0.0
isort>=5.12.0

# Linting
flake8>=6.0.0
pylint>=2.17.0

# Type checking
mypy>=1.4.0

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.11.0

# Documentation
sphinx>=7.0.0
sphinx-rtd-theme>=1.3.0

# Jupyter development
jupyterlab>=4.0.0
ipywidgets>=8.0.0
EOF

echo "✓ Created requirements-dev.txt"
echo ""

# Show what was created
echo "=== requirements.txt ==="
cat requirements.txt
echo ""
echo "=========================================="
echo ""

# Installation instructions
cat << 'INSTRUCTIONS'
Next Steps:
===========

1. Create/activate virtual environment:
   python3 -m venv venv
   source venv/bin/activate

2. Install dependencies:
   pip install --upgrade pip
   pip install -r requirements.txt

3. Install spaCy models:
   python -m spacy download en_core_web_sm
   python -m spacy download en_core_web_trf

4. Verify installation:
   python -c "import spacy; print(spacy.__version__)"
   python -c "import torch; print(torch.__version__)"

5. For development:
   pip install -r requirements-dev.txt

Optional - Freeze exact versions:
   pip freeze > requirements.lock.txt

INSTRUCTIONS

echo ""
echo "=========================================="
