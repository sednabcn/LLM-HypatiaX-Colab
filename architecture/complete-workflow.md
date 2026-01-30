# === Test in Python 3.10 ===
source venv-310/bin/activate
pip install -r requirements-py310.txt
python -m pytest tests/
deactivate

# === Test in Python 3.11 ===
source venv-311/bin/activate
pip install -r requirements-py311.txt
python -m pytest tests/
deactivate

# === Test in Python 3.13 ===
source venv-313/bin/activate
pip install -r requirements.txt
python -m pytest tests/
deactivate