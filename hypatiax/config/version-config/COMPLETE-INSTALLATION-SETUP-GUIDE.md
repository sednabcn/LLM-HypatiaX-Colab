# HypatiaX Version Management - Complete Installation Guide

## 🎯 Overview

This guide walks you through installing the complete version management system with GitHub Actions automation for your HypatiaX project.

## 📋 Prerequisites

- Python 3.10+
- Git repository initialized
- GitHub account with Actions enabled
- Bash shell access

## 🚀 Installation Steps

### Step 1: Download All Scripts

Save these files to your local machine first:

1. **`global_version_manager.py`** - Global version manager
2. **`version_injector.py`** - Version injector
3. **`setup_version_system.sh`** - Setup script
4. **`setup_version_directories.sh`** - Directory setup script
5. **`version-management.yml`** - GitHub Actions workflow

### Step 2: Create Directory Structure

```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

# Make directory setup script executable
chmod +x setup_version_directories.sh

# Run directory setup
./setup_version_directories.sh .
```

This creates:

- ✅ `.versions/` - Version storage
- ✅ `.github/workflows/` - GitHub Actions
- ✅ All data type directories
- ✅ Helper scripts
- ✅ Documentation files

### Step 3: Copy Version Management Scripts

```bash
# Copy main scripts to hypatiax root
cp global_version_manager.py ~/Downloads/LLM-HypatiaX-OLD/hypatiax/
cp version_injector.py ~/Downloads/LLM-HypatiaX-OLD/hypatiax/
cp setup_version_system.sh ~/Downloads/LLM-HypatiaX-OLD/hypatiax/

# Make them executable
chmod +x ~/Downloads/LLM-HypatiaX-OLD/hypatiax/global_version_manager.py
chmod +x ~/Downloads/LLM-HypatiaX-OLD/hypatiax/version_injector.py
chmod +x ~/Downloads/LLM-HypatiaX-OLD/hypatiax/setup_version_system.sh
```

### Step 4: Copy GitHub Actions Workflow

```bash
# Copy workflow file
cp version-management.yml ~/Downloads/LLM-HypatiaX-OLD/hypatiax/.github/workflows/

# Verify it's in place
ls -la ~/Downloads/LLM-HypatiaX-OLD/hypatiax/.github/workflows/
```

### Step 5: Run System Setup

```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

# Run the complete setup
./setup_version_system.sh .
```

This will:

- ✅ Scan your system for versionable files
- ✅ Create initial snapshot
- ✅ Initialize version injector
- ✅ Create version loader module
- ✅ Export environment variables
- ✅ Create helper scripts

### Step 6: Configure Git

```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

# Add version management gitignore
cat .gitignore.version_mgmt >> .gitignore

# Or merge manually if you have custom .gitignore
cat .gitignore.version_mgmt
```

### Step 7: Initial Commit

```bash
# Add all new files (excluding git-ignored items)
git add .github/
git add global_version_manager.py
git add version_injector.py
git add setup_version_system.sh
git add daily_version_update.sh
git add version_status.sh
git add restore_version.sh
git add *.md
git add .versions/global_versions.json
git add .versions/version_config.json
git add .versions/README.md

# Commit
git commit -m "Add version management system with GitHub Actions"

# Push to GitHub
git push origin main  # or your branch name
```

### Step 8: Enable GitHub Actions

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Actions** → **General**
3. Ensure "Allow all actions and reusable workflows" is selected
4. Enable "Read and write permissions" for GITHUB_TOKEN

### Step 9: Test the System

```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

# Test version status
./version_status.sh

# Load versions into environment
source .env.versions

# Verify version loader
python3 version_loader.py

# Test auto-versioning
python3 global_version_manager.py . auto-version --notes "Test run"
```

## 📂 Directory Structure After Installation

```
hypatiax/
├── .github/
│   └── workflows/
│       └── version-management.yml          # ← GitHub Actions workflow
│
├── .versions/
│   ├── global_versions.json                # ← Version metadata
│   ├── version_config.json                 # ← Configuration
│   ├── README.md                           # ← Documentation
│   └── snapshot_1_TIMESTAMP/               # ← Initial snapshot
│
├── global_version_manager.py               # ← Global manager
├── version_injector.py                     # ← Version injector
├── version_loader.py                       # ← Auto-generated loader
├── .env.versions                           # ← Environment variables
│
├── daily_version_update.sh                 # ← Daily workflow
├── version_status.sh                       # ← Status checker
├── restore_version.sh                      # ← Restore helper
│
├── VERSION_MANAGEMENT_README.md            # ← Quick reference
├── VERSION_SYSTEM_GUIDE.md                 # ← Complete guide
├── DIRECTORY_STRUCTURE.md                  # ← Structure map
│
└── [existing project files...]
```

## 🤖 GitHub Actions Configuration

### Automatic Triggers

1. **On Push** (main/develop branches)
   - Auto-versions changed files
   - Commits updated versions

2. **Daily at 2 AM UTC**
   - Creates daily snapshot
   - Exports version manifest
   - Uploads artifacts

3. **On Pull Request**
   - Shows version status
   - Comments on PR with current versions

### Manual Triggers

From GitHub Actions UI, you can manually trigger:

- **Auto-version**: Version changed files
- **Create Snapshot**: Create named snapshot
- **List Snapshots**: View all snapshots
- **Restore Snapshot**: Restore specific version
- **Export Manifest**: Export version manifest
- **Status Check**: Check version status

### How to Trigger Manually

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **HypatiaX Version Management** workflow
4. Click **Run workflow** button
5. Select action and fill parameters
6. Click **Run workflow**

## 📝 Daily Workflow

### Morning Routine

```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

# Load latest versions
source .env.versions

# Check status
./version_status.sh
```

### After Successful Work

```bash
# Run daily update
./daily_version_update.sh

# Reload environment
source .env.versions
```

### In Your Python Scripts

```python
#!/usr/bin/env python3

# Add at the top of your scripts
import version_loader  # Auto-loads all versions

# Your code here
# All version environment variables are now set!
```

## 🔧 Configuration

### Customize Snapshot Schedule

Edit `.github/workflows/version-management.yml`:

```yaml
schedule:
  # Change from 2 AM to your preferred time
  - cron: '0 14 * * *'  # 2 PM UTC
```

### Customize Version Directories

Edit `global_version_manager.py` → `VERSION_DIRECTORIES`:

```python
VERSION_DIRECTORIES = {
    "rules": {
        "path": "custom_ner/queries/tableau/rules",
        "patterns": ["*.jsonl"],
        "exclude": ["rules_versions/*"]
    },
    # Add your custom directories here
}
```

### Customize Artifact Retention

Edit `.github/workflows/version-management.yml`:

```yaml
- name: Upload Version Artifacts
  uses: actions/upload-artifact@v3
  with:
    retention-days: 30  # Change retention period
```

## 🆘 Troubleshooting

### GitHub Actions Not Running

**Check**:

1. Actions are enabled in repository settings
2. Workflow file is in `.github/workflows/`
3. YAML syntax is valid
4. Branch names match workflow triggers

**Solution**:

```bash
# Validate YAML
cat .github/workflows/version-management.yml | python3 -c "import yaml, sys; yaml.safe_load(sys.stdin)"

# Check Actions status
# Go to GitHub → Settings → Actions
```

### Versions Not Loading

**Check**:

```bash
# Verify version loader exists
ls -la version_loader.py

# Verify environment file exists
ls -la .env.versions

# Recreate if missing
python3 version_injector.py . create-loader
python3 version_injector.py . export-env
```

### Scripts Not Executable

**Fix**:

```bash
chmod +x global_version_manager.py
chmod +x version_injector.py
chmod +x setup_version_system.sh
chmod +x daily_version_update.sh
chmod +x version_status.sh
chmod +x restore_version.sh
```

### Missing Directories

**Fix**:

```bash
# Rerun directory setup
./setup_version_directories.sh .

# Or create manually
mkdir -p .versions
mkdir -p .github/workflows
```

## 🎯 Testing Checklist

After installation, verify everything works:

- [ ] Directory structure exists
- [ ] Scripts are executable
- [ ] Initial snapshot created
- [ ] Version loader works (`python3 version_loader.py`)
- [ ] Environment variables load (`source .env.versions`)
- [ ] Status check works (`./version_status.sh`)
- [ ] GitHub Actions workflow appears in Actions tab
- [ ] Can trigger manual workflow from GitHub UI

## 📚 Additional Resources

- **Quick Reference**: `VERSION_MANAGEMENT_README.md`
- **Complete Guide**: `VERSION_SYSTEM_GUIDE.md`
- **Setup Guide**: `COMPLETE_VERSION_SETUP_GUIDE.md`
- **Directory Map**: `DIRECTORY_STRUCTURE.md`
- **Actions Guide**: `.github/docs/VERSION_ACTIONS.md`

## 🎉 Success

You now have:

- ✅ Complete version management system
- ✅ Automated GitHub Actions workflows
- ✅ Daily snapshots
- ✅ Auto-versioning on push
- ✅ PR status checks
- ✅ Manual control via workflow dispatch
- ✅ Complete documentation

## 🚀 Next Steps

1. **Integrate with your workflow**:

   ```python
   import version_loader  # Add to your scripts
   ```

2. **Set up daily routine**:

   ```bash
   # Add to your daily workflow
   source .env.versions
   ```

3. **Monitor via GitHub**:
   - Check Actions tab for automated runs
   - Download artifacts for backup
   - Trigger manual actions as needed

4. **Customize as needed**:
   - Adjust snapshot schedule
   - Add custom version directories
   - Modify retention periods

---

**🎊 Your HypatiaX project now has enterprise-grade version management with full automation!**
