# 🐳 Docker Environment Setup for HypatiaX

Complete guide for setting up Python 3.12 and 3.13 Docker environments.

## 📁 File Structure

Add these files to your `LLM-HypatiaX-Colab` repository:

```
LLM-HypatiaX-Colab/
├── Dockerfile                      # ← Create this
├── docker-compose.yml              # ← Create this
├── .devcontainer/
│   ├── devcontainer.json          # ← Python 3.12 (default)
│   └── devcontainer-py313.json    # ← Python 3.13
├── hypatiax/
│   ├── config.py
│   └── ...
├── tests/
├── setup_environment.sh
├── fix_vulnerabilities.sh
├── requirements.txt
└── .dockerignore                   # ← Create this
```

---

## 🚀 Quick Start

### Option 1: Using Docker Compose (Easiest)

```bash
cd ~/path/to/LLM-HypatiaX-Colab

# Build and start Python 3.12 environment
docker-compose up -d hypatiax-py312

# Enter the container
docker exec -it hypatiax-py312 bash

# Inside container:
python -c "from hypatiax.config import config; config.print_config()"
python tests/test_entity_desc.py
```

```bash
# Build and start Python 3.13 environment
docker-compose up -d hypatiax-py313

# Enter the container
docker exec -it hypatiax-py313 bash
```

### Option 2: Using Docker Directly

```bash
# Build for Python 3.12
docker build --build-arg PYTHON_VERSION=3.12 --target development -t hypatiax:py312 .

# Run interactively
docker run -it -v $(pwd):/workspace/hypatiax hypatiax:py312 bash

# Build for Python 3.13
docker build --build-arg PYTHON_VERSION=3.13 --target development -t hypatiax:py313 .

# Run interactively
docker run -it -v $(pwd):/workspace/hypatiax hypatiax:py313 bash
```

### Option 3: GitHub Codespaces

1. Go to your GitHub repo
2. Click **Code** → **Codespaces**
3. Click **"..."** → **"New with options"**
4. Select devcontainer:
   - `devcontainer.json` → Python 3.12 (stable)
   - `devcontainer-py313.json` → Python 3.13 (latest)

---

## 📋 Setup Steps

### Step 1: Create .dockerignore

```bash
# Create .dockerignore to exclude unnecessary files
cat > .dockerignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv*/
ENV/
.venv

# Project specific
outputs/
ci_outputs/
.env
activate_hypatiax.sh

# Git
.git/
.github/
.gitignore

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temp
*.log
*.tmp
.pytest_cache/
.coverage
htmlcov/

# Backups
*.backup.*
requirements.backup.*
EOF
```

### Step 2: Copy the Docker Files

Copy the following from the artifacts above:
1. `Dockerfile`
2. `docker-compose.yml`
3. `.devcontainer/devcontainer.json`
4. `.devcontainer/devcontainer-py313.json`

```bash
# Create devcontainer directory
mkdir -p .devcontainer

# Copy files (use the artifacts above)
# ... paste Dockerfile content
# ... paste docker-compose.yml content
# ... paste devcontainer configs
```

### Step 3: Build Docker Images

```bash
# Build all services
docker-compose build

# Or build specific services
docker-compose build hypatiax-py312
docker-compose build hypatiax-py313
```

### Step 4: Test the Environments

```bash
# Test Python 3.12
docker-compose run --rm hypatiax-py312 python --version
docker-compose run --rm hypatiax-py312 python -c "from hypatiax.config import config; config.print_config()"

# Test Python 3.13
docker-compose run --rm hypatiax-py313 python --version
docker-compose run --rm hypatiax-py313 python -c "from hypatiax.config import config; config.print_config()"
```

---

## 🎯 Usage Examples

### Interactive Development

```bash
# Start Python 3.12 container
docker-compose up -d hypatiax-py312

# Enter container
docker exec -it hypatiax-py312 bash

# Inside container:
cd /workspace/hypatiax
source activate_hypatiax.sh
python tests/test_entity_desc.py

# Exit container
exit

# Stop container
docker-compose down
```

### Running Tests

```bash
# Run tests in Python 3.12
docker-compose run --rm hypatiax-test-py312

# Run tests in Python 3.13
docker-compose run --rm hypatiax-test-py313

# Run specific test
docker-compose run --rm hypatiax-test-py312 pytest tests/test_entity_desc.py -v
```

### Running Scripts

```bash
# Run a Python script in 3.12
docker-compose run --rm hypatiax-py312 python your_script.py

# Run a Python script in 3.13
docker-compose run --rm hypatiax-py313 python your_script.py
```

### Jupyter Notebook

```bash
# Start with Jupyter
docker-compose up -d hypatiax-py312

# Install Jupyter if not in requirements.txt
docker exec -it hypatiax-py312 pip install jupyter

# Start Jupyter
docker exec -it hypatiax-py312 jupyter notebook --ip=0.0.0.0 --allow-root

# Access at: http://localhost:8888
```

### Security Scanning

```bash
# Run security fix inside container
docker exec -it hypatiax-py312 bash
./fix_vulnerabilities.sh

# Or from outside
docker-compose run --rm hypatiax-py312 bash -c "./fix_vulnerabilities.sh"
```

---

## 🔧 Advanced Usage

### Mount Local Data

```bash
# Edit docker-compose.yml to add volume
# Under hypatiax-py312 -> volumes:
#   - ./local_data:/workspace/hypatiax/data

# Or run with custom mount
docker run -it \
  -v $(pwd):/workspace/hypatiax \
  -v ~/my_data:/workspace/hypatiax/data \
  hypatiax:py312 bash
```

### Use Different Requirements

```bash
# For Python 3.12 specific requirements
# Create requirements-py312.txt

# Build with specific requirements
docker build \
  --build-arg PYTHON_VERSION=3.12 \
  --target development \
  -t hypatiax:py312-custom \
  -f - . << 'EOF'
FROM python:3.12-slim
WORKDIR /workspace/hypatiax
COPY requirements-py312.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN pip install -e .
EOF
```

### Multi-version Testing

```bash
# Test in both versions at once
docker-compose run --rm hypatiax-test-py312 & \
docker-compose run --rm hypatiax-test-py313 &
wait

echo "All tests completed!"
```

---

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs hypatiax-py312

# Rebuild without cache
docker-compose build --no-cache hypatiax-py312

# Check if ports are available
lsof -i :8888
```

### "Permission denied" errors

```bash
# The container runs as non-root in production
# For development, it runs as root by default

# If you get permission errors on mounted volumes:
docker-compose run --user $(id -u):$(id -g) hypatiax-py312 bash
```

### "Module not found" errors

```bash
# Reinstall project
docker exec -it hypatiax-py312 pip install -e .

# Or rebuild
docker-compose build hypatiax-py312
```

### Changes not reflected

```bash
# If you edit files locally and they don't update in container:
# Make sure volume mount is correct in docker-compose.yml
# The development target uses mounted volumes for live editing

# Restart container
docker-compose restart hypatiax-py312
```

### Large Docker images

```bash
# Clean up old images
docker system prune -a

# Remove unused volumes
docker volume prune

# Check image sizes
docker images | grep hypatiax
```

---

## 📊 Comparison: Local vs Docker

| Feature | Local (py312/py313) | Docker |
|---------|-------------------|--------|
| Setup time | Fast | Slower (first time) |
| Isolation | Shared | Complete |
| Consistency | Varies by OS | Identical everywhere |
| CI/CD | Manual setup | Automatic |
| Cleanup | Manual | Easy (`docker-compose down`) |
| Multi-version | Separate venvs | Parallel containers |

---

## 🎓 Best Practices

1. **Use docker-compose for development** - easier than raw docker commands
2. **Keep Dockerfile small** - use .dockerignore to exclude files
3. **Mount volumes for live editing** - don't rebuild for every change
4. **Use specific Python versions** - not `latest`
5. **Run tests in containers** - ensure consistency with CI/CD
6. **Clean up regularly** - `docker system prune`
7. **Tag images with versions** - `hypatiax:py312-v1.0.0`

---

## 🔄 GitHub Actions Integration

The Docker setup works seamlessly with GitHub Actions:

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12', '3.13']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build \
          --build-arg PYTHON_VERSION=${{ matrix.python-version }} \
          --target testing \
          -t hypatiax:py${{ matrix.python-version }}-test .
    
    - name: Run tests
      run: |
        docker run hypatiax:py${{ matrix.python-version }}-test
```

---

## 📝 Summary

✅ **Python 3.12** - Stable, production-ready  
✅ **Python 3.13** - Latest features, testing  
✅ **Docker Compose** - Easy multi-version management  
✅ **DevContainers** - GitHub Codespaces support  
✅ **Isolated environments** - No conflicts  
✅ **Consistent setup** - Works everywhere  

Now you can develop, test, and deploy HypatiaX across any environment! 🎉