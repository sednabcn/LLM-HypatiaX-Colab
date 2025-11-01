# HypatiaX Development Environments

## Available Python Versions

### Python 3.13 (Default - Local Development)
- **File:** `devcontainer.json`
- **Use:** Latest features, local development
- **Command:** Use default Codespace creation

### Python 3.11 (Stable)
- **File:** `devcontainer-py311.json`
- **Use:** Production-ready, stable
- **Command:** In Codespaces, select "Open in Codespace" → Advanced → Select config

### Python 3.10 (Colab-like)
- **File:** `devcontainer-py310-colab.json`
- **Use:** Google Colab compatibility testing
- **Command:** In Codespaces, select "Open in Codespace" → Advanced → Select config

## Switching Environments in Codespaces

1. Click "Code" button on GitHub
2. Click "Codespaces" tab
3. Click "..." → "New with options"
4. Select desired devcontainer configuration

## Docker Usage
```bash
# Build all versions
docker-compose build

# Run Python 3.10 (Colab-like)
docker-compose up hypatiax-py310

# Run Python 3.11 (Stable)
docker-compose up hypatiax-py311

# Run Python 3.13 (Latest)
docker-compose up hypatiax-py313
```

## Local Testing
```bash
# Test with Python 3.10
python3.10 -m venv venv-310
source venv-310/bin/activate
pip install -r requirements-py310.txt

# Test with Python 3.11
python3.11 -m venv venv-311
source venv-311/bin/activate
pip install -r requirements-py311.txt

# Test with Python 3.13
python3.13 -m venv venv-313
source venv-313/bin/activate
pip install -r requirements.txt
```
