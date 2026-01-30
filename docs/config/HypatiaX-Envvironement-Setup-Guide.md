# HypatiaX Environment Setup Guide

## 🎯 Overview

HypatiaX now supports **universal path configuration** that works seamlessly across:

- ✅ **Local Development** (Mac, Linux, Windows)
- ✅ **GitHub Actions** (CI/CD)
- ✅ **Docker** (Containers)
- ✅ **Cloud Platforms** (AWS, GCP, Azure)

No more hardcoded paths! 🎉

---

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/yourorg/hypatiax.git
cd hypatiax

# 2. Run setup script
./setup_environment.sh

# 3. Activate environment
source activate_hypatiax.sh

# 4. Verify setup
python -c "from hypatiax.config import config; config.print_config()"

# 5. Run tests from anywhere!
cd /tmp
python /path/to/hypatiax/tests/test_entity_desc.py
```

### GitHub Actions

Just push to GitHub! The workflow automatically:
1. Detects GitHub Actions environment
2. Sets up paths using `$GITHUB_WORKSPACE`
3. Runs all tests
4. Uploads artifacts

```yaml
# Already configured in .github/workflows/test.yml
# No additional setup needed!
```

### Docker

```bash
# Development mode
docker build --target development -t hypatiax:dev .
docker run -it hypatiax:dev bash

# Production mode
docker build --target production -t hypatiax:prod .
docker run hypatiax:prod

# Testing mode
docker build --target testing -t hypatiax:test .
docker run hypatiax:test
```

---

## 📁 Project Structure

```
hypatiax/
├── hypatiax/                    # Main package
│   ├── config.py               # ✨ Universal path configuration
│   ├── datasets/               # Data files
│   ├── data_spacy/            # SpaCy models & data
│   └── ...
├── tests/                      # Test files
│   ├── test_entity_desc.py    # ✨ Updated with config
│   ├── test_entity_formulas.py # ✨ Updated with config
│   └── ...
├── setup_environment.sh        # ✨ Universal setup script
├── activate_hypatiax.sh        # Auto-generated activation script
├── .env                        # Auto-generated environment file
├── Dockerfile                  # ✨ Multi-stage Docker build
└── .github/
    └── workflows/
        └── test.yml            # ✨ GitHub Actions workflow
```

---

## 🔧 How It Works

### 1. **Universal Path Detection**

The `config.py` module automatically detects the environment and finds the project root:

```python
from hypatiax.config import config

# Works everywhere!
data_path = config.get_dataset_path('queries', 'tableau', 'training')
output_path = config.get_output_path('results', 'analysis.json')
```

**Priority order:**
1. `HYPATIAX_ROOT` environment variable (explicit override)
2. `GITHUB_WORKSPACE` (GitHub Actions)
3. Search upward from current file (development)
4. Installed package location (production)
5. Current working directory (fallback)

### 2. **Environment Detection**

Automatically detects:
- **Local**: Standard development on your machine
- **GitHub**: GitHub Actions workflows
- **Docker**: Container environments
- **CI**: Generic CI/CD platforms
- **AWS/GCP**: Cloud platforms

### 3. **Smart Output Directories**

- **Local**: `outputs/` in project root
- **GitHub Actions**: `ci_outputs/` for artifacts
- **Docker**: `/tmp/hypatiax_outputs` or custom mount
- **Cloud**: Environment-specific paths

---

## 🛠️ Setup Script Details

### `setup_environment.sh`

The setup script adapts to your environment:

#### **Local Development**
```bash
./setup_environment.sh
```
Creates:
- `.env` file with environment variables
- `activate_hypatiax.sh` activation script
- `outputs/` directory
- Updates `.gitignore`

#### **GitHub Actions**
```bash
./setup_environment.sh  # Called automatically
```
- Sets `GITHUB_ENV` variables
- Creates `ci_outputs/` directory
- Configures for workflow steps

#### **Docker**
```bash
./setup_environment.sh  # Called in Dockerfile
```
- Sets container environment variables
- Creates output directories
- Validates installation

---

## 📝 Configuration Examples

### Running Tests

#### **From Project Root**
```bash
python tests/test_entity_desc.py
python tests/test_entity_formulas.py
```

#### **From Any Directory**
```bash
# After activating environment
source /path/to/hypatiax/activate_hypatiax.sh
cd /tmp
python /path/to/hypatiax/tests/test_entity_desc.py
```

#### **In Docker**
```bash
docker run hypatiax:test python tests/test_entity_desc.py
```

#### **In GitHub Actions**
Happens automatically on push!

### Custom Output Directory

```bash
# Local
export HYPATIAX_OUTPUT_DIR="/custom/path"
python tests/test_entity_desc.py

# Docker
docker run -e HYPATIAX_OUTPUT_DIR=/data -v /host/path:/data hypatiax:prod
```

### Using Config in Your Code

```python
from hypatiax.config import config

# Get standard paths
print(f"Project root: {config.root}")
print(f"Datasets: {config.datasets}")
print(f"Outputs: {config.outputs}")

# Build custom paths
data_file = config.get_dataset_path('queries', 'tableau', 'data.xlsx')
output_file = config.get_output_path('results', 'analysis.json')

# Check environment
print(f"Environment: {config.environment}")

# Debug configuration
config.print_config()
```

---

## 🔍 Environment Variables

### Core Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `HYPATIAX_ROOT` | Project root directory | `/home/user/hypatiax` |
| `PYTHONPATH` | Python import path | `/home/user/hypatiax:...` |
| `HYPATIAX_OUTPUT_DIR` | Output directory | `/home/user/hypatiax/outputs` |
| `HYPATIAX_ENV` | Environment type | `local`, `github`, `docker` |

### Platform-Specific

| Variable | Platform | Purpose |
|----------|----------|---------|
| `GITHUB_WORKSPACE` | GitHub Actions | Project root in workflow |
| `GITHUB_ACTIONS` | GitHub Actions | Detect GitHub environment |
| `DOCKER_CONTAINER` | Docker | Detect container environment |
| `CI` | CI/CD | Detect generic CI environment |

---

## 🐛 Troubleshooting

### "Config module not found"

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="/path/to/hypatiax:$PYTHONPATH"

# Or install in development mode
pip install -e /path/to/hypatiax
```

### "Datasets directory not found"

```bash
# Verify project structure
ls -la hypatiax/datasets/

# Set explicit root
export HYPATIAX_ROOT="/correct/path/to/hypatiax"
```

### "Permission denied on outputs/"

```bash
# Check directory permissions
ls -la outputs/

# Create with correct permissions
mkdir -p outputs
chmod 755 outputs/
```

### Docker build fails

```bash
# Ensure setup script is executable
chmod +x setup_environment.sh

# Build with specific target
docker build --target development -t hypatiax:dev .

# Check logs
docker build --target development -t hypatiax:dev . --progress=plain
```

### GitHub Actions fails

```bash
# Check workflow logs for setup step
# Verify files are committed:
git ls-files | grep -E "(setup_environment|config.py|test_)"

# Validate workflow syntax
cat .github/workflows/test.yml
```

---

## 🎓 Best Practices

### 1. **Always Use Config Module**

❌ **Don't:**
```python
path = "/home/user/hypatiax/datasets/data.xlsx"
```

✅ **Do:**
```python
from hypatiax.config import config
path = config.get_dataset_path('data.xlsx')
```

### 2. **Activate Environment for Interactive Work**

```bash
# Add to ~/.bashrc or ~/.zshrc
source /path/to/hypatiax/activate_hypatiax.sh
```

### 3. **Use Development Mode for Local Testing**

```bash
pip install -e /path/to/hypatiax
```

### 4. **Test in Docker Before Pushing**

```bash
docker build --target testing -t hypatiax:test .
docker run hypatiax:test
```

### 5. **Check Configuration When Debugging**

```python
from hypatiax.config import config
config.print_config()
```

---

## 📊 Testing the Setup

### Validation Script

```bash
#!/bin/bash
# test_setup.sh

echo "Testing HypatiaX setup..."

# Test 1: Import config
python -c "from hypatiax.config import config; print('✅ Config imported')"

# Test 2: Check paths exist
python -c "from hypatiax.config import config; assert config.datasets.exists(), 'Datasets not found'"
echo "✅ Paths validated"

# Test 3: Run sample test
python tests/test_entity_desc.py
echo "✅ Tests completed"

echo "✅ All validation passed!"
```

---

## 🔄 Migration from Old Setup

### Old Code (Hardcoded Paths)

```python
import os
path = os.path.expanduser('~/Downloads/LLM-HypatiaX-OLD/hypatiax/datasets')
```

### New Code (Universal Config)

```python
from hypatiax.config import config
path = config.datasets
```

### Migration Steps

1. **Update imports**
   ```python
   # Add to top of file
   from hypatiax.config import config
   ```

2. **Replace hardcoded paths**
   ```python
   # Old: path = '/home/user/hypatiax/outputs'
   # New: path = config.outputs
   ```

3. **Use path builders**
   ```python
   # Old: os.path.join(base, 'queries', 'tableau')
   # New: config.get_dataset_path('queries', 'tableau')
   ```

4. **Test in all environments**
   ```bash
   # Local
   python tests/test_entity_desc.py

   # Docker
   docker build --target testing -t hypatiax:test .
   docker run hypatiax:test
   ```

---

## 📚 Additional Resources

- **Config Module Documentation**: `hypatiax/config.py`
- **Test Examples**: `tests/test_entity_desc.py`, `tests/test_entity_formulas.py`
- **GitHub Workflow**: `.github/workflows/test.yml`
- **Dockerfile**: `Dockerfile`

---

## 🤝 Contributing

When adding new code that uses file paths:

1. **Always use config module** - Never hardcode paths
2. **Test in multiple environments** - Local, Docker, GitHub Actions
3. **Update documentation** - Add examples to this guide
4. **Follow conventions** - Use the path builder methods

---

## ❓ FAQ

**Q: Do I need to run setup_environment.sh every time?**
A: No! Once set up, just activate with `source activate_hypatiax.sh`

**Q: Can I customize the output directory?**
A: Yes! Set `HYPATIAX_OUTPUT_DIR` environment variable

**Q: Does this work on Windows?**
A: The bash scripts work in WSL/Git Bash. The Python config works everywhere.

**Q: How do I test locally before pushing to GitHub?**
A: Use Docker: `docker build --target testing -t hypatiax:test . && docker run hypatiax:test`

**Q: Can I still use absolute paths?**
A: Yes, but use config: `str(config.get_dataset_path('data.xlsx'))` gives absolute path

---

## ✨ Summary

The updated HypatiaX setup provides:

✅ **Universal compatibility** - Works everywhere
✅ **No hardcoded paths** - Dynamic path resolution
✅ **Environment detection** - Automatic adaptation
✅ **Easy testing** - Run from anywhere
✅ **CI/CD ready** - GitHub Actions configured
✅ **Docker support** - Multi-stage builds
✅ **Developer friendly** - Simple activation script

**Just run `./setup_environment.sh` and you're ready to go!** 🚀
Key Improvements:
Feature             Old Script             New Solution
GitHub Actions     ❌ Not supported        ✅ Full integration
Docker             ❌ Basic support        ✅ Multi-stage builds
Cloud              ❌ Not supported        ✅ Environment detection
Config overwrite   ❌ Overwrites config.py ✅ Preserves existing
Output paths       ❌ Fixed to outputs/    ✅ Environment-aware
Validation         ❌ Basic                ✅ Comprehensive

The solution is now production-ready for all environments! 🎉
