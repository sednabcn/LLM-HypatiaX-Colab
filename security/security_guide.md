# Security Vulnerability Fix Guide

## Quick Start

### For Local Environment

1. **Save the script**
   ```bash
   # Copy the "Security Vulnerability Fix Script" artifact content
   nano fix_vulnerabilities.sh
   # Paste the script, then Ctrl+X, Y, Enter
   
   # Make it executable
   chmod +x fix_vulnerabilities.sh
   ```

2. **Set temp directory** (to avoid the /tmp space issue)
   ```bash
   export TMPDIR=~/tmp_pip
   mkdir -p ~/tmp_pip
   ```

3. **Activate your virtual environment**
   ```bash
   source ~/path/to/venv-312/bin/activate
   ```

4. **Run the script**
   ```bash
   ./fix_vulnerabilities.sh
   ```

5. **Choose option 1** (Critical and High severity only - safest)

### For Remote Server

1. **Save the remote script**
   ```bash
   nano fix_remote_vulnerabilities.sh
   # Paste the "Remote Server Vulnerability Fix Script" content
   chmod +x fix_remote_vulnerabilities.sh
   ```

2. **Run it**
   ```bash
   ./fix_remote_vulnerabilities.sh user@server.com /path/to/remote/venv
   ```

## Manual Method (If Scripts Don't Work)

### Local Fix

```bash
# 1. Activate venv
source ~/path/to/venv/bin/activate

# 2. Set temp directory
export TMPDIR=~/tmp_pip
mkdir -p ~/tmp_pip

# 3. Backup
pip freeze > requirements.backup.txt

# 4. Update tools
pip install --upgrade pip setuptools wheel

# 5. Install security scanner
pip install pip-audit

# 6. Fix automatically
pip-audit --fix

# 7. Or fix manually (critical only)
pip install --upgrade h11>=0.14.0
pip install --upgrade django>=4.2.11
pip install --upgrade starlette>=0.36.2
pip install --upgrade brotli>=1.1.0
pip install --upgrade protobuf>=4.25.3
```

### Remote Fix

```bash
# SSH into server
ssh user@server.com

# Follow the same steps as local
source /path/to/venv/bin/activate
export TMPDIR=~/tmp_pip
mkdir -p ~/tmp_pip

# ... rest of commands same as local
```

## What Gets Fixed

### Priority 1 - CRITICAL (Fix Immediately)
- **h11** - Malformed chunked encoding vulnerability

### Priority 2 - HIGH (Fix ASAP)
- **Django** - SQL injection (3 vulnerabilities!)
- **Starlette** - DoS via Range header
- **Brotli** - DoS via decompression
- **protobuf** - DoS issue
- **jupyter-core** - Local privilege escalation
- **tornado** - Excessive logging DoS
- **setuptools** - Path traversal
- **redis** - Race condition
- **ecdsa** - Timing attack

### Priority 3 - MODERATE (Fix Soon)
- **transformers** - Multiple ReDoS attacks
- **urllib3** - Redirect issues
- **requests** - Credential leak
- **pypdf** - Multiple DoS issues
- **torch** - Resource management
- And others...

## Rollback Instructions

If something breaks after the fix:

```bash
# Activate venv
source /path/to/venv/bin/activate

# Restore from backup
pip install -r requirements.backup.YYYYMMDD_HHMMSS.txt

# Or if using the script backups
pip install -r requirements.freeze.backup.*.txt
```

## Testing After Fix

```bash
# Check what was updated
pip list --outdated

# Test your application
python your_app.py

# Verify vulnerabilities are fixed
pip-audit

# Or use safety
safety check
```

## Common Issues

### "No space left on device" 
```bash
export TMPDIR=~/tmp_pip
mkdir -p ~/tmp_pip
```

### "Permission denied"
```bash
# Don't use sudo with pip in venv
# Make sure venv is activated first
source /path/to/venv/bin/activate
```

### "Package conflicts"
```bash
# Fix one package at a time
pip install --upgrade package-name

# Or use --force-reinstall
pip install --force-reinstall package-name
```

### Large packages (like torch, transformers)
```bash
# Use --no-cache-dir to save space
pip install --no-cache-dir --upgrade torch

# Or increase timeout
pip install --timeout=300 --upgrade transformers
```

## Prevention

### Regular Security Scans
```bash
# Weekly scan
pip-audit

# Or use safety
safety check
```

### Keep Dependencies Updated
```bash
# Check outdated packages monthly
pip list --outdated

# Update non-breaking packages
pip install --upgrade package-name
```

### Use Requirements Files
```bash
# Pin exact versions
pip freeze > requirements.txt

# Use separate files for different environments
pip freeze > requirements-prod.txt
pip freeze > requirements-dev.txt
```

## Need Help?

If you encounter issues:
1. Check the backup files created
2. Read error messages carefully
3. Try fixing packages one at a time
4. Use `--verbose` flag for more info: `pip install --upgrade --verbose package-name`
5. Check package documentation for breaking changes