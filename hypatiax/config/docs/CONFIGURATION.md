# HypatiaX Configuration Guide

Complete guide for setting up HypatiaX across different environments.

## Table of Contents

- [Quick Start](#quick-start)
- [Environment Support](#environment-support)
- [Local Development](#local-development)
- [Docker](#docker)
- [GitHub Actions](#github-actions)
- [Cloud Platforms](#cloud-platforms)
- [Configuration Reference](#configuration-reference)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### For Local Development

```bash
# 1. Clone the repository
git clone https://github.com/yourorg/hypatiax.git
cd hypatiax

# 2. Run the setup script
./setup_environment.sh

# 3. Activate the environment
source activate_hypatiax.sh

# 4. Verify installation
python -c 'from hypatiax.config import config; config.print_config()'
```

### For Docker

```bash
# Build and run development container
docker build --target development -t hypatiax:dev .
docker run -v $(pwd):/app -it hypatiax:dev bash
```

### For GitHub Actions

The setup script automatically detects and configures GitHub Actions. Just include in your workflow:

```yaml
- name: Setup HypatiaX
  run: ./setup_environment.sh
```

---

## Environment Support

HypatiaX automatically detects and configures itself for:

| Environment | Detection Method | Output Directory |
|------------|------------------|------------------|
| **Local Development** | Default | `./outputs/` |
| **GitHub Actions** | `$GITHUB_ACTIONS` | `./ci_outputs/` |
| **Docker** | `$DOCKER_CONTAINER` | `/tmp/hypatiax_outputs/` |
| **AWS Lambda/EC2** | `$AWS_EXECUTION_ENV` | `/tmp/hypatiax_outputs/` |
| **Google Cloud** | `$GOOGLE_CLOUD_PROJECT` | `/tmp/hypatiax_outputs/` |
| **Azure** | `$AZURE_FUNCTIONS_ENVIRONMENT` | `/tmp/hypatiax_outputs/` |
| **Generic CI/CD** | `$CI` | `./ci_outputs/` |

---

## Local Development

### Initial Setup

1. **Run Setup Script**

   ```bash
   ./setup_environment.sh
   ```

   This creates:
   - `.env` - Environment variables
   - `activate_hypatiax.sh` - Activation script
   - `outputs/` - Output directory
   - `.gitignore` - Git ignore rules

2. **Activate Environment**

   ```bash
   source activate_hypatiax.sh
   ```

3. **Make Permanent (Optional)**

   ```bash
   # For bash
   echo 'source /path/to/hypatiax/activate_hypatiax.sh' >> ~/.bashrc

   # For zsh
   echo 'source /path/to/hypatiax/activate_hypatiax.sh' >> ~/.zshrc
   ```

### Alternative: Install in Development Mode

```bash
cd /path/to/hypatiax
pip install -e .
```

This installs hypatiax as a package, making it importable from anywhere.

### Using Configuration in Code

```python
from hypatiax.config import config

# Access paths
print(config.root)
print(config.datasets)
print(config.outputs)

# Get specific paths
dataset_path = config.get_dataset_path('queries', 'tableau', 'training.json')
output_path = config.get_output_path('results', 'experiment_1.json')

# Create multiple output directories
dirs = config.ensure_output_dirs('training', 'testing', 'validation')

# Print full configuration
config.print_config()
```

---

## Docker

### Building Images

```bash
# Development image (includes all dev tools)
docker build --target development -t hypatiax:dev .

# Testing image (runs tests)
docker build --target testing -t hypatiax:test .

# Production image (optimized, minimal)
docker build --target production -t hypatiax:prod .

# API server image
docker build --target api -t hypatiax:api .

# Jupyter notebook image
docker build --target notebook -t hypatiax:notebook .
```

### Running Containers

**Development with live code updates:**

```bash
docker run -v $(pwd):/app -it hypatiax:dev bash
```

**Run tests:**

```bash
docker run hypatiax:test
```

**Production with output volume:**

```bash
docker run -v /host/outputs:/tmp/hypatiax_outputs hypatiax:prod
```

**API server:**

```bash
docker run -p 8000:8000 hypatiax:api
```

**Jupyter notebook:**

```bash
docker run -p 8888:8888 -v $(pwd):/app hypatiax:notebook
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  hypatiax:
    build:
      context: .
      target: production
    volumes:
      - ./outputs:/tmp/hypatiax_outputs
    environment:
      - HYPATIAX_ENV=production
      - HYPATIAX_OUTPUT_DIR=/tmp/hypatiax_outputs
    restart: unless-stopped

  hypatiax-api:
    build:
      context: .
      target: api
    ports:
      - "8000:8000"
    volumes:
      - ./outputs:/tmp/hypatiax_outputs
    restart: unless-stopped

  hypatiax-notebook:
    build:
      context: .
      target: notebook
    ports:
      - "8888:8888"
    volumes:
      - ./:/app
    restart: unless-stopped
```

Run with:

```bash
docker-compose up -d
```

---

## GitHub Actions

### Workflow Configuration

The setup script automatically detects GitHub Actions. Example workflow:

```yaml
name: HypatiaX Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Setup HypatiaX Environment
      run: ./setup_environment.sh

    - name: Install Dependencies
      run: |
        pip install -r requirements.txt

    - name: Run Tests
      run: |
        pytest tests/ -v --cov=hypatiax

    - name: Upload Coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Environment Variables Set

The setup script automatically sets:

- `HYPATIAX_ROOT` - Project root directory
- `PYTHONPATH` - Python import path
- `HYPATIAX_OUTPUT_DIR` - Output directory (`ci_outputs/`)

---

## Cloud Platforms

### AWS Lambda

**Function Configuration:**

```python
# lambda_function.py
from hypatiax.config import config

def lambda_handler(event, context):
    # Config automatically uses /tmp for outputs
    output_path = config.get_output_path('results.json')

    # Your code here

    return {
        'statusCode': 200,
        'body': 'Success'
    }
```

**Environment Variables:**

```bash
HYPATIAX_ROOT=/var/task
HYPATIAX_OUTPUT_DIR=/tmp/hypatiax_outputs
```

### AWS EC2 / ECS

**User Data Script:**

```bash
#!/bin/bash
cd /opt/hypatiax
export HYPATIAX_ROOT=/opt/hypatiax
export DOCKER_CONTAINER=1
./setup_environment.sh
```

### Google Cloud Run

**Dockerfile:**

```dockerfile
FROM hypatiax:prod
ENV HYPATIAX_OUTPUT_DIR=/tmp/hypatiax_outputs
CMD ["python", "-m", "hypatiax.api"]
```

### Azure Functions

**Function App Configuration:**

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.*, 4.0.0)"
  },
  "applicationSettings": [
    {
      "name": "HYPATIAX_ROOT",
      "value": "/home/site/wwwroot"
    },
    {
      "name": "HYPATIAX_OUTPUT_DIR",
      "value": "/tmp/hypatiax_outputs"
    }
  ]
}
```

---

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HYPATIAX_ROOT` | Project root directory | Auto-detected |
| `HYPATIAX_OUTPUT_DIR` | Output directory | `./outputs` (local) or `/tmp/hypatiax_outputs` (cloud) |
| `HYPATIAX_ENV` | Environment name | Auto-detected |
| `PYTHONPATH` | Python import path | Includes project root |

### Path Properties

```python
from hypatiax.config import config

# Core paths
config.root              # Project root
config.hypatiax          # hypatiax/ package
config.outputs           # Output directory

# Data paths
config.datasets          # hypatiax/datasets/
config.data_spacy        # hypatiax/data_spacy/

# Code organization
config.agents            # hypatiax/agents/
config.core              # hypatiax/core/
config.models            # hypatiax/models/
config.tools             # hypatiax/tools/
config.utils             # hypatiax/utils/

# Additional
config.tests             # tests/
config.examples          # hypatiax/examples/
config.docs              # hypatiax/docs/
```

### Path Builder Methods

```python
# Get dataset path
path = config.get_dataset_path('queries', 'tableau', 'data.json')

# Get spacy data path
path = config.get_spacy_path('models', 'ner_model')

# Get output path (creates parent dirs automatically)
path = config.get_output_path('experiments', 'run_1', 'results.json')

# Get test path
path = config.get_test_path('fixtures', 'sample_data.json')

# Create multiple output directories
dirs = config.ensure_output_dirs('training', 'testing', 'validation')
# Returns: {'training': Path(...), 'testing': Path(...), 'validation': Path(...)}
```

### Utility Methods

```python
# Check if path exists
if config.exists('datasets'):
    print("Datasets directory exists")

# List all available paths
paths = config.list_available_paths()

# Export as dictionary
config_dict = config.to_dict()

# Print full configuration
config.print_config()
```

---

## Troubleshooting

### "Module 'hypatiax' not found"

**Solution 1:** Activate the environment

```bash
source activate_hypatiax.sh
```

**Solution 2:** Set PYTHONPATH manually

```bash
export PYTHONPATH="/path/to/hypatiax:$PYTHONPATH"
```

**Solution 3:** Install in development mode

```bash
pip install -e /path/to/hypatiax
```

### "Config module cannot be imported"

1. Check that `hypatiax/config.py` exists
2. Verify PYTHONPATH includes project root
3. Run setup script: `./setup_environment.sh`

### "Permission denied" when creating output directories

**Local Development:**

```bash
sudo chown -R $USER:$USER /path/to/hypatiax/outputs
```

**Docker:**

```bash
docker run -v $(pwd)/outputs:/tmp/hypatiax_outputs \
           -e HYPATIAX_OUTPUT_DIR=/tmp/hypatiax_outputs \
           hypatiax:prod
```

**Cloud:** Use `/tmp` for outputs (already configured automatically)

### Paths not found in Docker

Ensure volumes are mounted correctly:

```bash
# Mount entire project
docker run -v $(pwd):/app hypatiax:dev

# Or mount specific directories
docker run -v $(pwd)/hypatiax:/app/hypatiax \
           -v $(pwd)/outputs:/tmp/hypatiax_outputs \
           hypatiax:prod
```

### GitHub Actions failing

Check that setup script is executable:

```yaml
- name: Make setup script executable
  run: chmod +x setup_environment.sh

- name: Setup environment
  run: ./setup_environment.sh
```

---

## Best Practices

1. **Always use config paths** instead of hardcoded paths

   ```python
   # ❌ Bad
   path = "/home/user/hypatiax/outputs/result.json"

   # ✅ Good
   path = config.get_output_path('result.json')
   ```

2. **Use environment activation** for local development

   ```bash
   source activate_hypatiax.sh
   ```

3. **Check paths exist** before using them

   ```python
   if config.exists('datasets'):
       dataset_path = config.get_dataset_path('data.json')
   ```

4. **Use appropriate output directories** for each environment
   - Local: `outputs/` (git-ignored)
   - CI: `ci_outputs/` (temporary)
   - Cloud: `/tmp/hypatiax_outputs/` (temporary)

5. **Test configuration** after setup

   ```bash
   python -c 'from hypatiax.config import config; config.print_config()'
   ```

---

## Support

- **Documentation:** <https://docs.hypatiax.io>
- **Issues:** <https://github.com/yourorg/hypatiax/issues>
- **Discussions:** <https://github.com/yourorg/hypatiax/discussions>

For configuration-specific issues, include the output of:

```bash
python -c 'from hypatiax.config import config; config.print_config()'
```
