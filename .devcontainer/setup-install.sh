# Check Python version
python --version
# Should be: Python 3.12.2

# Check key packages match Colab
python -c "import sys; print(f'Python: {sys.version}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
