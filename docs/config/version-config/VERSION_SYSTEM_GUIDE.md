# HypatiaX Automatic Version Management System

Complete guide for automatic version management across all data types in HypatiaX.

## 📁 System Overview

The version management system consists of three main components:

1. **Global Version Manager** (`global_version_manager.py`) - Tracks all data across the system
2. **Version Injector** (`version_injector.py`) - Automatically feeds version numbers to components
3. **Local Version Managers** (`version_manager.py`) - Manages specific directories

## 🚀 Quick Start

### 1. Initial Setup

```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

# Create initial snapshot of all data
python global_version_manager.py . snapshot --name "initial_setup" --notes "First snapshot"

# Scan what can be versioned
python global_version_manager.py . scan
```

### 2. Set Up Version Injection

```bash
# Create version loader module (import in your scripts)
python version_injector.py . create-loader

# Export environment variables
python version_injector.py . export-env

# Apply to current session
source .env.versions
```

### 3. Use in Your Code

```python
# At the top of any script
import version_loader  # Automatically loads all versions

# Or use specific versions
from version_loader import get_version

version = get_version('rules', 'ruler_tableau_formulas')
print(f"Using version {version}")
```

## 📋 Complete Workflow

### Day-to-Day Usage

#### **Morning: Start with Fresh Versions**
```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

# Load today's versions
source .env.versions

# Or create a new version loader
python version_injector.py . create-loader
```

#### **During Development: Make Changes**
```bash
# Edit your rules, training data, etc.
# No manual version tracking needed!
```

#### **After Successful Run: Auto-Version Everything**
```bash
# Automatically version all changed files
python global_version_manager.py . auto-version --notes "After successful training run"

# Sync version injector with new versions
python version_injector.py . sync

# Update environment
python version_injector.py . export-env
source .env.versions
```

#### **End of Day: Create Snapshot**
```bash
# Create daily snapshot
python global_version_manager.py . snapshot --name "daily_$(date +%Y%m%d)" --notes "End of day snapshot"
```

### Major Milestones

#### **Before Major Changes**
```bash
# Create milestone snapshot
python global_version_manager.py . snapshot \
    --name "before_model_refactor" \
    --notes "Before refactoring model architecture"
```

#### **After Successful Training**
```bash
# Auto-version changed files
python global_version_manager.py . auto-version \
    --notes "After successful model training - 95% accuracy"

# Set specific versions for critical components
python version_injector.py . set rules ruler_tableau_formulas 5
python version_injector.py . set models ner_tableau_formulas 3
```

#### **Before Release**
```bash
# Create release snapshot
python global_version_manager.py . snapshot \
    --name "release_v1.0" \
    --notes "Production release version 1.0"

# Export version manifest
python global_version_manager.py . export-manifest
```

## 🔧 Integration with Existing Code

### Update Your Scripts

Add this to the top of all your main scripts:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add hypatiax to path
HYPATIAX_PATH = Path(__file__).parent.parent.parent  # Adjust as needed
sys.path.insert(0, str(HYPATIAX_PATH))

# Load versions automatically
try:
    import version_loader
    print("✅ Versions loaded automatically")
except ImportError:
    print("⚠️  Version loader not found - using default versions")
```

### Update Component Files

Your component files already support version loading via environment variables:

```python
# In custom_tableau_formulas_components.py (already implemented)
env_version = os.environ.get('HYPATIAX_FORMULAS_VERSION')
if env_version:
    rules = load_rules("ruler_tableau_formulas", use_version=int(env_version))
else:
    rules = load_rules("ruler_tableau_formulas")
```

### Update Workflow Runner

Add to your `workflow_runner.py`:

```python
from pathlib import Path
import sys

class WorkflowRunner:
    def __init__(self, base_path: Path, report_dir: Path):
        # ... existing code ...

        # Load versions
        try:
            sys.path.insert(0, str(base_path))
            import version_loader
            self.versions_loaded = True
            print("✅ Versions loaded from version_loader")
        except ImportError:
            self.versions_loaded = False
            print("⚠️  Version loader not available")

    def run_workflow(self, modules=None):
        # ... existing code ...

        # After successful workflow
        if all_successful:
            print("\n🎯 Workflow succeeded - auto-versioning...")
            self._auto_version_on_success()

    def _auto_version_on_success(self):
        """Auto-version all data after successful workflow."""
        try:
            from global_version_manager import GlobalVersionManager

            manager = GlobalVersionManager(self.base_path)
            versioned = manager.auto_version_all(
                notes="Auto-versioned after successful workflow run"
            )

            if versioned:
                # Update version injector
                from version_injector import VersionInjector
                injector = VersionInjector(self.base_path)
                injector.sync_with_global_manager()
                injector.export_env_file()

                print("✅ Versions updated successfully")
        except Exception as e:
            print(f"⚠️  Auto-versioning failed: {e}")
```

## 📊 Version Tracking

### What Gets Versioned

The system automatically tracks:

- **Rules** (`.jsonl` files)
  - `ruler_tableau_desc.jsonl`
  - `ruler_tableau_formulas.jsonl`
  - `ruler_tableau.jsonl`

- **Training Data**
  - Excel files (`.xlsx`)
  - CSV files (`.csv`)
  - spaCy format (`.json`)

- **Models**
  - Trained NER models
  - Model configurations

- **Vocabularies**
  - Vocab files

- **Patterns**
  - Pattern generation scripts

### Version Numbers

Version numbers are:
- **Automatic**: Incremented automatically
- **Per Data Type**: Each data type has its own version sequence
- **Hash-based**: Only version when content actually changes

## 🔍 Querying Versions

### List All Snapshots
```bash
python global_version_manager.py . list-snapshots
```

### Show Current Versions
```bash
python version_injector.py . show
```

### Check Specific Version
```bash
python version_injector.py . get rules ruler_tableau_formulas
```

### Export Version Manifest
```bash
python global_version_manager.py . export-manifest
```

## 🔄 Restoring Versions

### Restore Complete Snapshot
```bash
# Restore everything from snapshot 5
python global_version_manager.py . restore 5
```

### Restore Specific Data Types
```bash
# Restore only rules from snapshot 5
python global_version_manager.py . restore 5 --data-types rules
```

### Restore Specific Component (Local)
```bash
# Restore specific rule file to version 3
cd custom_ner/queries/tableau/rules
python version_manager.py . restore ruler_tableau_formulas 3
```

## 📝 Environment Variables

The system creates these environment variables:

```bash
# Rules
HYPATIAX_DESC_VERSION=2
HYPATIAX_FORMULAS_VERSION=5
HYPATIAX_TABLEAU_VERSION=3

# Training Data
HYPATIAX_TRAINING_FORMULAS_VERSION=4

# Models
HYPATIAX_MODEL_NER_TABLEAU_VERSION=2
```

## 🎯 Best Practices

### 1. **Daily Snapshots**
Create a snapshot at the end of each day:
```bash
python global_version_manager.py . snapshot --name "daily_$(date +%Y%m%d)"
```

### 2. **Auto-Version After Success**
Always auto-version after successful runs:
```bash
python global_version_manager.py . auto-version --notes "After test suite passed"
```

### 3. **Use Version Loader**
Import version_loader in all scripts:
```python
import version_loader  # Automatic version loading
```

### 4. **Sync Regularly**
Keep version injector in sync:
```bash
python version_injector.py . sync
python version_injector.py . export-env
```

### 5. **Document Changes**
Always add meaningful notes:
```bash
python global_version_manager.py . snapshot \
    --name "pre_production" \
    --notes "All tests passed, ready for production deployment"
```

## 🆘 Troubleshooting

### Versions Not Loading
```bash
# Recreate version loader
python version_injector.py . create-loader

# Reload environment
source .env.versions
```

### Missing Versions
```bash
# Sync with global manager
python version_injector.py . sync
python version_injector.py . show
```

### Need to Rollback
```bash
# List snapshots
python global_version_manager.py . list-snapshots

# Restore specific snapshot
python global_version_manager.py . restore <snapshot_id>
```

## 📦 Directory Structure

After setup, your structure will be:

```
hypatiax/
├── .versions/                      # Version storage
│   ├── global_versions.json        # Global version metadata
│   ├── version_config.json         # Version injection config
│   ├── snapshot_1_20250103_120000/ # Snapshots
│   ├── rules/                      # Versioned rules
│   ├── training_data/              # Versioned training data
│   └── ...
├── .env.versions                   # Environment variables
├── version_loader.py               # Auto-generated version loader
├── global_version_manager.py       # Global version manager
├── version_injector.py             # Version injector
└── [existing directories...]
```

## 🎓 Example: Complete Daily Workflow

```bash
#!/bin/bash
# daily_workflow.sh

HYPATIAX_PATH=~/Downloads/LLM-HypatiaX-OLD/hypatiax
cd $HYPATIAX_PATH

echo "🌅 Starting daily workflow..."

# 1. Load versions
source .env.versions
echo "✅ Versions loaded"

# 2. Run your scripts
python -m hypatiax.scripts_.script_custom_ner
python -m hypatiax.core.training.training_spacy
# ... other scripts ...

# 3. If successful, auto-version
if [ $? -eq 0 ]; then
    echo "✅ Scripts successful - auto-versioning..."
    python global_version_manager.py . auto-version \
        --notes "Daily run $(date +%Y-%m-%d)"

    # 4. Update environment
    python version_injector.py . sync
    python version_injector.py . export-env

    # 5. Create daily snapshot
    python global_version_manager.py . snapshot \
        --name "daily_$(date +%Y%m%d)" \
        --notes "End of day $(date +%Y-%m-%d)"

    echo "✅ Daily workflow complete!"
else
    echo "❌ Scripts failed - versions not updated"
fi
```

Make it executable:
```bash
chmod +x daily_workflow.sh
./daily_workflow.sh
```

## 🚀 Quick Command Reference

```bash
# Setup
python version_injector.py . create-loader
python version_injector.py . export-env

# Daily use
source .env.versions
python global_version_manager.py . auto-version --notes "Your note"
python version_injector.py . sync

# Snapshots
python global_version_manager.py . snapshot --name "name" --notes "notes"
python global_version_manager.py . list-snapshots
python global_version_manager.py . restore <id>

# Query
python version_injector.py . show
python global_version_manager.py . scan
```

---

**🎉 You now have automatic version management across your entire HypatiaX system!**
