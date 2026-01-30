# Security Vulnerability Fix Guide

## Vulnerabilities Identified

### 1. AIOHTTP Unicode Processing Vulnerability (Low Severity)
- **Package**: aiohttp
- **Location**: requirements/requirements.txt
- **Issue**: Unicode processing of header values could cause parsing discrepancies
- **Fix**: Upgrade to aiohttp >= 3.10.11

### 2. PyTorch Local Denial of Service (Low Severity)
- **Package**: torch
- **Location**: requirements/requirements-py311.txt
- **Issue**: Susceptible to local DoS attacks
- **Fix**: Upgrade to torch >= 2.5.0

## Quick Fix Commands

### Option 1: Direct Package Upgrade
```bash
# Fix AIOHTTP vulnerability
pip install --upgrade "aiohttp>=3.10.11"

# Fix PyTorch vulnerability
pip install --upgrade "torch>=2.5.0"
```

### Option 2: Update Requirements Files
1. Edit `requirements/requirements.txt`:
   ```
   # Change this:
   aiohttp==<old_version>
   
   # To this:
   aiohttp>=3.10.11
   ```

2. Edit `requirements/requirements-py311.txt`:
   ```
   # Change this:
   torch==<old_version>
   
   # To this:
   torch>=2.5.0
   ```

3. Reinstall dependencies:
   ```bash
   pip install -r requirements/requirements.txt --upgrade
   pip install -r requirements/requirements-py311.txt --upgrade
   ```

### Option 3: Use the Automated Script
```bash
python fix_vulnerabilities.py
```

## Verification Steps

After applying fixes, verify the updates:

```bash
# Check installed versions
pip show aiohttp
pip show torch

# Run security audit (if pip-audit is installed)
pip install pip-audit
pip-audit

# Or use safety
pip install safety
safety check
```

## Testing Checklist

- [ ] Packages upgraded successfully
- [ ] Application starts without errors
- [ ] Core functionality works as expected
- [ ] Run your test suite
- [ ] Check for any deprecation warnings
- [ ] Update your CI/CD pipelines if needed

## Additional Recommendations

1. **Enable Dependabot**: Keep automatic security updates enabled
2. **Regular Audits**: Run `pip-audit` or `safety check` regularly
3. **Pin Dependencies**: Consider using exact versions in production
4. **Review Release Notes**: Check PyTorch and AIOHTTP changelogs for breaking changes

## Breaking Changes to Watch For

### AIOHTTP 3.10.x
- Check if you're using any deprecated APIs
- Review header processing logic if you have custom implementations

### PyTorch 2.5.0
- Review PyTorch release notes for any API changes
- Test model loading/saving functionality
- Verify CUDA compatibility if using GPU

## Rollback Plan

If issues occur after upgrade:

```bash
# Restore previous versions from git
git checkout HEAD -- requirements/requirements.txt requirements/requirements-py311.txt

# Reinstall old versions
pip install -r requirements/requirements.txt
pip install -r requirements/requirements-py311.txt
```

## Need Help?

- AIOHTTP docs: https://docs.aiohttp.org/
- PyTorch docs: https://pytorch.org/docs/
- Security advisories: https://github.com/advisories
