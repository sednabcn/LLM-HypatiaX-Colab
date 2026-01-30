# HypatiaX Version Management - Organized Structure Guide

## 🎯 Overview

Your version management system is now organized in a clean, professional directory structure:

```
hypatiax/
├── scripts/
│   └── version_management/
│       ├── core/                    # Core system scripts
│       ├── utils/                   # Utility scripts
│       ├── workflows/               # Workflow scripts
│       ├── config/                  # Configuration
│       └── docs/                    # Documentation
│
├── .versions/                       # Version data storage
├── .env.versions                    # Environment variables (auto-generated)
└── version_loader.py                # Loader module (auto-generated)
```

## 📦 Installation

### Step 1: Create the Directory Structure

```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

# Run the directory creation script
chmod +x create_scripts_directory.sh
./create_scripts_directory.sh .
```

### Step 2: Copy Core Scripts

```bash
# Copy your version management scripts to the core directory
cp global_version_manager.py scripts/version_management/core/
cp version_injector.py scripts/version_management/core/

# Make them executable
chmod +x scripts/version_management/core/*.py
```

### Step 3: Initialize the System

```bash
cd scripts/version_management/core

# Create initial snapshot
python3 global_version_manager.py ../../../ snapshot \
    --name "initial_setup" \
    --notes "Initial snapshot after organizing directory structure"

# Initialize version injector
python3 version_injector.py ../../../ create-loader
python3 version_injector.py ../../../ export-env

cd ../../../
```

### Step 4: Load Versions

```bash
source .env.versions
```

### Step 5: Verify Installation

```bash
# Using symlink (if created)
./version_status.sh

# Or using full path
./scripts/version_management/utils/version_status.sh
```

## 🚀 Daily Usage

### Morning Routine

```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

# Load today's versions
source .env.versions

# Check status
./version_status.sh
```

### During the Day

Work on your files normally. The system tracks:
- Rules (`.jsonl` files)
- Training data (`.xlsx`, `.csv` files)
- spaCy data (`.json` files)
- Models and configs
- Vocabulary files

### End of Day

```bash
# Run the complete daily update workflow
./daily_version_update.sh

# Or use full path
./scripts/version_management/workflows/daily_version_update.sh

# Reload environment
source .env.versions
```

## 🔄 Training Workflows

### Before Training

```bash
# Create a pre-training snapshot
./scripts/version_management/workflows/pre_training_snapshot.sh

# Or with custom name
./scripts/version_management/workflows/pre_training_snapshot.sh "before_model_v2" "Before version 2 training"
```

### Run Your Training

```bash
# Your normal training commands
python -m hypatiax.core.training.training_spacy
# etc.
```

### After Successful Training

```bash
# Version the changes
./scripts/version_management/workflows/post_training_version.sh "Model v2 - 95% accuracy"

# Reload environment
source .env.versions
```

## 📝 Manual Operations

### Create Snapshot

```bash
python3 scripts/version_management/core/global_version_manager.py . snapshot \
    --name "my_snapshot_name" \
    --notes "Description of what changed"
```

### List All Snapshots

```bash
python3 scripts/version_management/core/global_version_manager.py . list-snapshots
```

### Restore a Snapshot

```bash
# Using convenience script
./restore_version.sh 5

# Or restore specific data types
./restore_version.sh 5 rules training_data

# Or use full path
./scripts/version_management/utils/restore_version.sh 5
```

### Auto-Version Changed Files

```bash
python3 scripts/version_management/core/global_version_manager.py . auto-version \
    --notes "What changed"
```

### Check Version Status

```bash
# Quick status
./version_status.sh

# Show all version mappings
python3 scripts/version_management/core/version_injector.py . show

# Scan versionable files
python3 scripts/version_management/core/global_version_manager.py . scan
```

### Set Specific Version

```bash
python3 scripts/version_management/core/version_injector.py . set \
    rules ruler_tableau_formulas 5
```

### Export Version Manifest

```bash
python3 scripts/version_management/core/global_version_manager.py . export-manifest
```

## 🐍 Python Integration

### Method 1: Use Version Loader (Recommended)

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add scripts path
SCRIPT_PATH = Path(__file__).parent / "scripts" / "version_management" / "core"
sys.path.insert(0, str(SCRIPT_PATH))

# Import version loader - automatically loads all versions
import version_loader

# Now all environment variables are set!
print(f"Formulas version: {version_loader.get_version('rules', 'ruler_tableau_formulas')}")
```

### Method 2: Use Environment Variables

```python
import os

# Get version from environment
formulas_version = os.environ.get('HYPATIAX_FORMULAS_VERSION')
desc_version = os.environ.get('HYPATIAX_DESC_VERSION')

if formulas_version:
    print(f"Using formulas version: {formulas_version}")
```

### Method 3: Direct Integration

```python
import sys
from pathlib import Path

# Import the managers directly
CORE_PATH = Path(__file__).parent / "scripts" / "version_management" / "core"
sys.path.insert(0, str(CORE_PATH))

from global_version_manager import GlobalVersionManager
from version_injector import VersionInjector

# Use them in your code
manager = GlobalVersionManager(Path.cwd())
injector = VersionInjector(Path.cwd())

# Get version
version = injector.get_version('rules', 'ruler_tableau_formulas')
```

## 📁 Directory Details

### Core Scripts (`scripts/version_management/core/`)

Contains the main system components:

- **`global_version_manager.py`**: Manages all versions globally
- **`version_injector.py`**: Injects versions as environment variables
- **`version_loader.py`**: Auto-generated module for easy imports

### Utilities (`scripts/version_management/utils/`)

Helper scripts for common tasks:

- **`version_status.sh`**: Quick status check
- **`restore_version.sh`**: Interactive restore helper

### Workflows (`scripts/version_management/workflows/`)

Pre-built workflows:

- **`daily_version_update.sh`**: Complete daily update
- **`pre_training_snapshot.sh`**: Snapshot before training
- **`post_training_version.sh`**: Version after training

### Configuration (`scripts/version_management/config/`)

Configuration examples and documentation:

- **`example.env.versions`**: Example environment file
- **`README.md`**: Configuration guide

## 🔧 Customization

### Adding New Versionable Directories

Edit `scripts/version_management/core/global_version_manager.py`:

```python
VERSION_DIRECTORIES = {
    # Add your custom directory
    "my_data_type": {
        "path": "path/to/your/data",
        "patterns": ["*.ext"],
        "exclude": ["versions/*"]
    },
    # ... existing directories
}
```

### Creating Custom Workflows

Create new scripts in `scripts/version_management/workflows/`:

```bash
#!/bin/bash
# custom_workflow.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
HYPATIAX_ROOT="$SCRIPT_DIR/../../.."
CORE_DIR="$HYPATIAX_ROOT/scripts/version_management/core"

cd "$HYPATIAX_ROOT"

# Your custom workflow logic here
python3 "$CORE_DIR/global_version_manager.py" . snapshot --name "custom"
```

### Modifying Environment Variables

Edit `scripts/version_management/core/version_injector.py` in the `inject_environment_variables()` method to customize variable names.

## 📊 File Locations Reference

| Item | Location |
|------|----------|
| Core scripts | `scripts/version_management/core/` |
| Utility scripts | `scripts/version_management/utils/` |
| Workflow scripts | `scripts/version_management/workflows/` |
| Version data | `.versions/` |
| Environment file | `.env.versions` |
| Version loader | `version_loader.py` |
| Main README | `scripts/version_management/README.md` |
| Quick reference | `scripts/version_management/QUICK_REFERENCE.md` |

## 🎯 Common Tasks

### Task 1: Start Your Day

```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax
source .env.versions
./version_status.sh
```

### Task 2: Before Major Changes

```bash
./scripts/version_management/workflows/pre_training_snapshot.sh "before_major_refactor"
```

### Task 3: After Successful Work

```bash
./scripts/version_management/workflows/post_training_version.sh "Successfully implemented feature X"
source .env.versions
```

### Task 4: End of Day

```bash
./daily_version_update.sh
source .env.versions
```

### Task 5: Check What Changed

```bash
./version_status.sh
python3 scripts/version_management/core/global_version_manager.py . list-snapshots
```

### Task 6: Rollback Changes

```bash
./restore_version.sh <snapshot_id>
source .env.versions
```

## 🆘 Troubleshooting

### Problem: Scripts Not Found

**Solution**:
```bash
# Ensure you're in the hypatiax root
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

# Check directory structure
ls -la scripts/version_management/
```

### Problem: Permission Denied

**Solution**:
```bash
# Make all scripts executable
chmod +x scripts/version_management/core/*.py
chmod +x scripts/version_management/utils/*.sh
chmod +x scripts/version_management/workflows/*.sh
```

### Problem: Versions Not Loading

**Solution**:
```bash
# Recreate version files
cd scripts/version_management/core
python3 version_injector.py ../../../ create-loader
python3 version_injector.py ../../../ export-env
cd ../../../
source .env.versions
```

### Problem: Symlinks Not Working

**Solution**:
```bash
# Use full paths instead
./scripts/version_management/utils/version_status.sh
./scripts/version_management/workflows/daily_version_update.sh
```

### Problem: Import Errors in Python

**Solution**:
```python
import sys
from pathlib import Path

# Adjust the path based on your script location
CORE_PATH = Path(__file__).parent / "scripts" / "version_management" / "core"
if not CORE_PATH.exists():
    # Try alternative path
    CORE_PATH = Path(__file__).parent.parent / "scripts" / "version_management" / "core"

sys.path.insert(0, str(CORE_PATH))
import version_loader
```

## 📚 Documentation Index

- **Main README**: `scripts/version_management/README.md`
- **Quick Reference**: `scripts/version_management/QUICK_REFERENCE.md`
- **Core Docs**: `scripts/version_management/core/README.md`
- **Utils Docs**: `scripts/version_management/utils/README.md`
- **Workflows Docs**: `scripts/version_management/workflows/README.md`
- **Config Docs**: `scripts/version_management/config/README.md`

## 🎓 Best Practices

1. **Always load versions**: Start every session with `source .env.versions`
2. **Use workflows**: Don't reinvent the wheel - use pre-built workflows
3. **Snapshot before risk**: Create snapshots before major changes
4. **Version after success**: Version your changes after successful runs
5. **Check status regularly**: Use `version_status.sh` to stay informed
6. **Use convenience scripts**: Leverage symlinks for quick access
7. **Read the docs**: Each directory has its own README with details

## 🚀 Advanced Usage

### Integrate with Git Hooks

```bash
# .git/hooks/post-commit
#!/bin/bash
cd /path/to/hypatiax
./scripts/version_management/workflows/daily_version_update.sh
```

### Automated Testing Integration

```python
# In your test suite
import subprocess

def test_with_versioning():
    # Create pre-test snapshot
    subprocess.run([
        "./scripts/version_management/workflows/pre_training_snapshot.sh",
        "pre_test"
    ])
    
    # Run tests
    result = run_your_tests()
    
    # Version if successful
    if result.success:
        subprocess.run([
            "./scripts/version_management/workflows/post_training_version.sh",
            "Tests passed"
        ])
```

### Continuous Integration

```yaml
# .github/workflows/ci.yml
steps:
  - name: Setup Version Management
    run: |
      source .env.versions
      ./scripts/version_management/utils/version_status.sh
  
  - name: Run Tests
    run: |
      ./scripts/version_management/workflows/pre_training_snapshot.sh "ci_test"
      # Your test commands
```

---

## 📞 Support

If you encounter issues:

1. Check the relevant README in the subdirectory
2. Run `./version_status.sh` to diagnose
3. Review the Quick Reference: `scripts/version_management/QUICK_REFERENCE.md`
4. Check file permissions with `ls -la scripts/version_management/`

---

**🎉 Your organized version management system is ready to use!**