#!/bin/bash

echo "=== Installing Python 3.12.2 (Colab version) ==="
pyenv install 3.12.2

echo ""
echo "=== Setting Python 3.12.2 as active ==="
pyenv global 3.12.2
python --version

echo ""
echo "=== Creating virtual environment ==="
python -m venv venv-312

echo ""
echo "=== Activating environment ==="
source venv-312/bin/activate
python --version

echo ""
echo "=== Installing build dependencies ==="
sudo apt-get update -qq
sudo apt-get install -y build-essential python3.12-dev gcc g++ make

echo ""
echo "=== Upgrading pip tools ==="
pip install --upgrade pip setuptools wheel

echo ""
echo "=== Installing packages ==="
# Try with existing requirements first
if [ -f "requirements-py312.txt" ]; then
    pip install --prefer-binary -r requirements-py312.txt
elif [ -f "requirements-py310.txt" ]; then
    pip install --prefer-binary -r requirements-py310.txt
else
    pip install --prefer-binary -r requirements.txt
fi

echo ""
echo "=== Creating missing rules file ==="
mkdir -p hypatiax/custom_ner/queries/tableau/rules/
echo '{"pattern": "example", "label": "EXAMPLE"}' > hypatiax/custom_ner/queries/tableau/rules/rules_tableau_desc_version1.jsonl

echo ""
echo "=== Verifying setup ==="
echo "Python version:"
python --version
echo ""
echo "Pip version:"
pip --version
echo ""
echo "Installed packages:"
pip list | head -20

echo ""
echo "=== Running tests ==="
python -m pytest tests/ -v

echo ""
echo "=== Setup complete! ==="
