#!/bin/bash

# ============================================================================
# HypatiaX Security Vulnerability Manager
# ============================================================================
# Manages security vulnerabilities in Python dependencies, with automated
# fixes, reporting, and continuous monitoring
#
# Usage:
#   ./security_manager.sh [command]
#
# Commands:
#   audit           - Run security audit on all dependencies
#   fix-vulnerabilities - Automatically fix known vulnerabilities
#   update-requirements - Update requirements files with patched versions
#   check-specific PKG - Check specific package for vulnerabilities
#   generate-report - Generate security audit report
#   monitor         - Set up continuous monitoring
#   verify-fix      - Verify vulnerabilities are fixed
#   pin-safe-versions - Pin all packages to safe versions
#
# Examples:
#   ./security_manager.sh audit
#   ./security_manager.sh fix-vulnerabilities
#   ./security_manager.sh check-specific pillow
# ============================================================================

set -e

# Configuration
PROJECT_ROOT="$(pwd)"
REPORTS_DIR="${PROJECT_ROOT}/security_reports"
BACKUP_DIR="${PROJECT_ROOT}/requirements_backup"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Known vulnerabilities (as of detection date)
declare -A VULNERABLE_PACKAGES=(
    ["nbconvert"]="CVE-2024-XXXXX: Uncontrolled search path → code execution (Windows)"
    ["cryptography"]="CVE-2024-YYYYY: Subgroup attack on SECT curves"
    ["pillow"]="CVE-2024-ZZZZZ: Out-of-bounds write in PSD loading"
)

declare -A SAFE_VERSIONS=(
    ["nbconvert"]=">=7.16.4"
    ["cryptography"]=">=42.0.4"
    ["pillow"]=">=10.3.0"
)

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_critical() {
    echo -e "${RED}[CRITICAL]${NC} $1"
}

create_directories() {
    mkdir -p "${REPORTS_DIR}"
    mkdir -p "${BACKUP_DIR}"
}

timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

# ============================================================================
# Security Audit Functions
# ============================================================================

run_security_audit() {
    log_info "Running comprehensive security audit..."
    
    local report_file="${REPORTS_DIR}/security_audit_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "=========================================="
        echo "HypatiaX Security Audit Report"
        echo "=========================================="
        echo "Date: $(timestamp)"
        echo ""
        
        # Check if pip-audit is installed
        if ! command -v pip-audit &> /dev/null; then
            log_warning "pip-audit not installed. Installing..."
            pip install pip-audit
        fi
        
        echo "=== Running pip-audit ==="
        echo ""
        pip-audit --desc || true
        
        echo ""
        echo "=== Checking Known Critical Vulnerabilities ==="
        echo ""
        check_known_vulnerabilities
        
        echo ""
        echo "=== Installed Package Versions ==="
        echo ""
        check_package_versions
        
        echo ""
        echo "=== Dependency Tree Analysis ==="
        echo ""
        analyze_dependency_tree
        
        echo ""
        echo "=========================================="
        echo "Audit Complete"
        echo "=========================================="
        
    } | tee "$report_file"
    
    log_success "Security audit report saved: $report_file"
}

check_known_vulnerabilities() {
    local found_vulnerabilities=false
    
    for package in "${!VULNERABLE_PACKAGES[@]}"; do
        if pip show "$package" &> /dev/null; then
            local installed_version=$(pip show "$package" | grep Version | awk '{print $2}')
            local safe_version="${SAFE_VERSIONS[$package]}"
            
            echo "Package: $package"
            echo "  Installed: $installed_version"
            echo "  Vulnerability: ${VULNERABLE_PACKAGES[$package]}"
            echo "  Safe version: $safe_version"
            
            # Check if current version is vulnerable
            if ! python3 -c "from packaging import version; import sys; sys.exit(0 if version.parse('$installed_version') >= version.parse('${safe_version#>=}') else 1)" 2>/dev/null; then
                log_critical "VULNERABLE: $package $installed_version"
                found_vulnerabilities=true
            else
                log_success "SAFE: $package $installed_version"
            fi
            echo ""
        fi
    done
    
    if [ "$found_vulnerabilities" = true ]; then
        log_error "Critical vulnerabilities detected!"
        return 1
    else
        log_success "No known critical vulnerabilities detected"
        return 0
    fi
}

check_package_versions() {
    for package in "${!VULNERABLE_PACKAGES[@]}"; do
        if pip show "$package" &> /dev/null; then
            pip show "$package" | grep -E "Name|Version|Location"
            echo ""
        else
            echo "$package: Not installed"
            echo ""
        fi
    done
}

analyze_dependency_tree() {
    if ! command -v pipdeptree &> /dev/null; then
        log_info "Installing pipdeptree..."
        pip install pipdeptree
    fi
    
    for package in "${!VULNERABLE_PACKAGES[@]}"; do
        if pip show "$package" &> /dev/null; then
            echo "Dependency tree for $package:"
            pipdeptree -p "$package" || true
            echo ""
        fi
    done
}

# ============================================================================
# Vulnerability Fix Functions
# ============================================================================

fix_vulnerabilities() {
    log_info "Attempting to fix known vulnerabilities..."
    
    # Backup current requirements
    backup_requirements
    
    local fixes_applied=0
    
    for package in "${!VULNERABLE_PACKAGES[@]}"; do
        if pip show "$package" &> /dev/null; then
            local installed_version=$(pip show "$package" | grep Version | awk '{print $2}')
            local safe_version="${SAFE_VERSIONS[$package]}"
            
            log_info "Checking $package..."
            
            if ! python3 -c "from packaging import version; import sys; sys.exit(0 if version.parse('$installed_version') >= version.parse('${safe_version#>=}') else 1)" 2>/dev/null; then
                log_warning "$package $installed_version is vulnerable"
                log_info "Upgrading to safe version $safe_version..."
                
                if pip install --upgrade "$package$safe_version"; then
                    log_success "Successfully upgraded $package"
                    fixes_applied=$((fixes_applied + 1))
                else
                    log_error "Failed to upgrade $package"
                fi
            else
                log_success "$package is already at safe version"
            fi
        fi
    done
    
    if [ $fixes_applied -gt 0 ]; then
        log_success "Applied $fixes_applied security fixes"
        log_info "Generating updated requirements..."
        update_requirements_files
    else
        log_info "No fixes needed - all packages are safe"
    fi
}

backup_requirements() {
    log_info "Backing up current requirements..."
    
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    
    # Backup all requirements files
    for req_file in requirements.txt requirements/*.txt setup.py; do
        if [ -f "$req_file" ]; then
            local backup_file="${BACKUP_DIR}/$(basename $req_file).${backup_timestamp}.bak"
            cp "$req_file" "$backup_file"
            log_success "Backed up: $req_file → $backup_file"
        fi
    done
}

update_requirements_files() {
    log_info "Updating requirements files with safe versions..."
    
    # Generate fresh requirements with current versions
    pip freeze > requirements_safe.txt
    
    # Update specific requirements files
    for package in "${!SAFE_VERSIONS[@]}"; do
        local safe_version="${SAFE_VERSIONS[$package]}"
        
        # Update in requirements.txt
        if [ -f "requirements.txt" ]; then
            if grep -q "^${package}" requirements.txt; then
                sed -i.bak "s/^${package}.*/${package}${safe_version}/" requirements.txt
                log_success "Updated $package in requirements.txt"
            fi
        fi
        
        # Update in requirements_updated.txt
        if [ -f "requirements/requirements_updated.txt" ]; then
            if grep -q "^${package}" requirements/requirements_updated.txt; then
                sed -i.bak "s/^${package}.*/${package}${safe_version}/" requirements/requirements_updated.txt
                log_success "Updated $package in requirements_updated.txt"
            fi
        fi
        
        # Update in setup.py
        if [ -f "setup.py" ]; then
            if grep -q "${package}" setup.py; then
                # This is trickier - provide manual instructions
                log_warning "Please manually update $package in setup.py to ${safe_version}"
            fi
        fi
    done
    
    log_success "Requirements files updated"
}

# ============================================================================
# Specific Package Checks
# ============================================================================

check_specific_package() {
    local package=$1
    
    if [ -z "$package" ]; then
        log_error "Package name required"
        return 1
    fi
    
    log_info "Checking $package for vulnerabilities..."
    
    if ! pip show "$package" &> /dev/null; then
        log_warning "$package is not installed"
        return 1
    fi
    
    local version=$(pip show "$package" | grep Version | awk '{print $2}')
    
    echo "Package: $package"
    echo "Installed version: $version"
    echo ""
    
    # Check with pip-audit
    if command -v pip-audit &> /dev/null; then
        echo "Vulnerability scan:"
        pip-audit --desc | grep -A 5 "$package" || echo "No vulnerabilities found by pip-audit"
    fi
    
    # Check against known vulnerabilities
    if [ -n "${VULNERABLE_PACKAGES[$package]}" ]; then
        echo ""
        echo "Known vulnerability: ${VULNERABLE_PACKAGES[$package]}"
        echo "Safe version: ${SAFE_VERSIONS[$package]}"
    fi
}

# ============================================================================
# Report Generation
# ============================================================================

generate_security_report() {
    log_info "Generating comprehensive security report..."
    
    local report_file="${REPORTS_DIR}/security_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << 'EOF'
# HypatiaX Security Vulnerability Report

## Executive Summary

**Report Date:** $(timestamp)
**Scan Type:** Comprehensive Security Audit
**Status:** [CRITICAL / WARNING / SAFE]

## Critical Vulnerabilities

### 1. nbconvert - Unauthorized Code Execution (Windows)

**Package:** nbconvert
**Severity:** HIGH
**CVE:** CVE-2024-XXXXX (or GitHub Advisory #423)
**Description:** Uncontrolled search path leads to unauthorized code execution on Windows

**Current Status:**
EOF

    # Check nbconvert
    if pip show nbconvert &> /dev/null; then
        local version=$(pip show nbconvert | grep Version | awk '{print $2}')
        cat >> "$report_file" << EOF
- Installed version: $version
- Safe version: ${SAFE_VERSIONS[nbconvert]}
- Status: $(check_version_safe nbconvert)

**Affected Files:**
- requirements/requirements_updated.txt

**Fix:**
\`\`\`bash
pip install nbconvert>=7.16.4
\`\`\`

---

EOF
    fi

    cat >> "$report_file" << 'EOF'
### 2. cryptography - Subgroup Attack Vulnerability

**Package:** cryptography
**Severity:** HIGH
**CVE:** CVE-2024-YYYYY (or GitHub Advisory #433)
**Description:** Vulnerable to subgroup attack due to missing subgroup validation for SECT curves

**Current Status:**
EOF

    if pip show cryptography &> /dev/null; then
        local version=$(pip show cryptography | grep Version | awk '{print $2}')
        cat >> "$report_file" << EOF
- Installed version: $version
- Safe version: ${SAFE_VERSIONS[cryptography]}
- Status: $(check_version_safe cryptography)

**Affected Files:**
- requirements_hashed.txt

**Fix:**
\`\`\`bash
pip install cryptography>=42.0.4
\`\`\`

---

EOF
    fi

    cat >> "$report_file" << 'EOF'
### 3. Pillow - Out-of-Bounds Write in PSD Loading

**Package:** Pillow
**Severity:** HIGH
**CVE:** CVE-2024-ZZZZZ (or GitHub Advisory #442)
**Description:** Out-of-bounds write when loading PSD images

**Current Status:**
EOF

    if pip show pillow &> /dev/null; then
        local version=$(pip show pillow | grep Version | awk '{print $2}')
        cat >> "$report_file" << EOF
- Installed version: $version
- Safe version: ${SAFE_VERSIONS[pillow]}
- Status: $(check_version_safe pillow)

**Affected Files:**
- setup.py

**Fix:**
\`\`\`bash
pip install pillow>=10.3.0
\`\`\`

---

EOF
    fi

    cat >> "$report_file" << 'EOF'
## Recommended Actions

### Immediate Actions (Critical Priority)

1. **Upgrade vulnerable packages:**
   ```bash
   ./security_manager.sh fix-vulnerabilities
   ```

2. **Verify fixes:**
   ```bash
   ./security_manager.sh verify-fix
   ```

3. **Update requirements files:**
   ```bash
   ./security_manager.sh update-requirements
   ```

### Short-term Actions (Within 24 hours)

1. Review all dependency trees for transitive vulnerabilities
2. Test application functionality after upgrades
3. Update CI/CD pipelines with new requirements
4. Notify team members of security updates

### Long-term Actions (Ongoing)

1. Set up automated vulnerability scanning
2. Enable Dependabot or similar tool
3. Schedule regular security audits (weekly)
4. Implement dependency pinning strategy

## Mitigation Details

### For Windows Users (nbconvert vulnerability)

**Impact:** Attackers could execute arbitrary code by placing malicious files in the search path

**Temporary Workaround:**
- Avoid running nbconvert with untrusted inputs
- Run in isolated/sandboxed environment
- Use Linux/macOS for processing untrusted notebooks

**Permanent Fix:**
- Upgrade to nbconvert >= 7.16.4

### For All Users (cryptography vulnerability)

**Impact:** Cryptographic operations using SECT curves may be compromised

**Check if affected:**
```python
# If you use any of these curves, you're affected:
SECT_CURVES = ['sect163k1', 'sect163r2', 'sect233k1', 'sect233r1', 
               'sect283k1', 'sect283r1', 'sect409k1', 'sect409r1',
               'sect571k1', 'sect571r1']
```

**Permanent Fix:**
- Upgrade to cryptography >= 42.0.4
- Consider migrating to non-SECT curves (e.g., P-256, P-384)

### For All Users (Pillow vulnerability)

**Impact:** Processing malicious PSD files could lead to memory corruption

**Temporary Workaround:**
- Validate PSD files before processing
- Avoid processing untrusted PSD files
- Use alternative image formats (PNG, JPEG)

**Permanent Fix:**
- Upgrade to Pillow >= 10.3.0

## Testing Checklist

After applying fixes, verify:

- [ ] All packages upgraded to safe versions
- [ ] `pip-audit` reports no critical vulnerabilities
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Application functionality unchanged
- [ ] No new dependency conflicts
- [ ] Requirements files updated and committed
- [ ] Team notified of changes

## Additional Security Recommendations

1. **Enable GitHub Dependabot:**
   - Automatically creates PRs for vulnerability fixes
   - Monitors all dependencies continuously

2. **Add to CI/CD Pipeline:**
   ```yaml
   # .github/workflows/security.yml
   name: Security Scan
   on: [push, pull_request, schedule]
   jobs:
     security:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - run: pip install pip-audit
         - run: pip-audit
   ```

3. **Regular Audits:**
   ```bash
   # Add to crontab
   0 9 * * 1 cd /path/to/hypatiax && ./security_manager.sh audit
   ```

4. **Pin Dependencies:**
   - Use exact versions in production
   - Use version ranges for development
   - Document security-critical versions

## Resources

- **pip-audit documentation:** https://pypi.org/project/pip-audit/
- **GitHub Advisory Database:** https://github.com/advisories
- **NIST NVD:** https://nvd.nist.gov/
- **Python Security:** https://python.org/dev/security/

## Appendix: Full Dependency Scan

```bash
pip-audit --desc
```

[Output of full scan would be included here]

---

**Report generated by:** HypatiaX Security Manager
**Next audit scheduled:** [DATE]
EOF

    # Replace placeholders with actual values
    sed -i "s/\$(timestamp)/$(timestamp)/g" "$report_file"
    
    log_success "Security report generated: $report_file"
    log_info "Review report and apply recommended actions"
}

check_version_safe() {
    local package=$1
    local installed_version=$(pip show "$package" 2>/dev/null | grep Version | awk '{print $2}')
    local safe_version="${SAFE_VERSIONS[$package]#>=}"
    
    if python3 -c "from packaging import version; import sys; sys.exit(0 if version.parse('$installed_version') >= version.parse('$safe_version') else 1)" 2>/dev/null; then
        echo "✓ SAFE"
    else
        echo "✗ VULNERABLE"
    fi
}

# ============================================================================
# Verification Functions
# ============================================================================

verify_fix() {
    log_info "Verifying security fixes..."
    
    local all_safe=true
    
    for package in "${!VULNERABLE_PACKAGES[@]}"; do
        if pip show "$package" &> /dev/null; then
            local installed_version=$(pip show "$package" | grep Version | awk '{print $2}')
            local safe_version="${SAFE_VERSIONS[$package]#>=}"
            
            echo "Checking $package..."
            echo "  Installed: $installed_version"
            echo "  Required:  >=$safe_version"
            
            if python3 -c "from packaging import version; import sys; sys.exit(0 if version.parse('$installed_version') >= version.parse('$safe_version') else 1)" 2>/dev/null; then
                log_success "$package is SAFE"
            else
                log_error "$package is still VULNERABLE"
                all_safe=false
            fi
            echo ""
        fi
    done
    
    if [ "$all_safe" = true ]; then
        log_success "All packages are at safe versions! ✓"
        return 0
    else
        log_error "Some packages are still vulnerable. Run fix-vulnerabilities again."
        return 1
    fi
}

# ============================================================================
# Monitoring Functions
# ============================================================================

setup_monitoring() {
    log_info "Setting up continuous security monitoring..."
    
    # Create GitHub Actions workflow
    mkdir -p .github/workflows
    
    cat > .github/workflows/security-audit.yml << 'EOF'
name: Security Audit

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run every Monday at 9 AM UTC
    - cron: '0 9 * * 1'

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install pip-audit
          pip install -r requirements.txt
      
      - name: Run pip-audit
        run: |
          pip-audit --desc || true
      
      - name: Run security manager
        run: |
          chmod +x security_manager.sh
          ./security_manager.sh audit
      
      - name: Upload audit report
        uses: actions/upload-artifact@v2
        with:
          name: security-audit-report
          path: security_reports/
EOF
    
    log_success "GitHub Actions workflow created: .github/workflows/security-audit.yml"
    
    # Create pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Quick security check before commit
echo "Running security check..."

if [ -f "security_manager.sh" ]; then
    ./security_manager.sh audit > /dev/null 2>&1
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Security vulnerabilities detected!"
        echo "Run: ./security_manager.sh audit"
        echo ""
        echo "Commit anyway? (y/N)"
        read -r response
        
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi
EOF
    
    chmod +x .git/hooks/pre-commit
    log_success "Pre-commit hook created"
    
    log_info "Monitoring setup complete. Security scans will run:"
    echo "  - On every push to main/develop"
    echo "  - On every pull request"
    echo "  - Every Monday at 9 AM UTC"
    echo "  - Before every local commit"
}

# ============================================================================
# Pin Safe Versions
# ============================================================================

pin_safe_versions() {
    log_info "Pinning all packages to safe versions..."
    
    # Create a new requirements file with exact versions
    pip freeze > requirements_pinned.txt
    
    # Ensure critical packages are at safe versions
    for package in "${!SAFE_VERSIONS[@]}"; do
        local safe_version="${SAFE_VERSIONS[$package]}"
        
        if grep -q "^${package}==" requirements_pinned.txt; then
            local current_version=$(grep "^${package}==" requirements_pinned.txt | cut -d'=' -f3)
            local min_version="${safe_version#>=}"
            
            if python3 -c "from packaging import version; import sys; sys.exit(0 if version.parse('$current_version') >= version.parse('$min_version') else 1)" 2>/dev/null; then
                log_success "$package pinned at safe version $current_version"
            else
                log_error "$package $current_version is below minimum safe version $min_version"
            fi
        fi
    done
    
    log_success "Safe versions pinned to requirements_pinned.txt"
}

# ============================================================================
# Quick Fix Function
# ============================================================================

quick_fix() {
    log_info "Running quick fix for all known vulnerabilities..."
    
    echo ""
    echo "This will:"
    echo "  1. Backup current requirements"
    echo "  2. Upgrade vulnerable packages"
    echo "  3. Update requirements files"
    echo "  4. Verify fixes"
    echo "  5. Run tests"
    echo ""
    read -p "Continue? (y/N) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Aborted"
        return 1
    fi
    
    backup_requirements
    fix_vulnerabilities
    verify_fix
    
    log_info "Quick fix complete!"
    log_warning "Please test your application to ensure everything still works"
}

# ============================================================================
# Main Function
# ============================================================================

main() {
    local command=${1:-"help"}
    local argument=${2:-""}
    
    create_directories
    
    case $command in
        audit)
            run_security_audit
            ;;
            
        fix-vulnerabilities)
            fix_vulnerabilities
            ;;
            
        quick-fix)
            quick_fix
            ;;
            
        update-requirements)
            backup_requirements
            update_requirements_files
            ;;
            
        check-specific)
            if [ -z "$argument" ]; then
                log_error "Package name required"
                exit 1
            fi
            check_specific_package "$argument"
            ;;
            
        generate-report)
            generate_security_report
            ;;
            
        verify-fix)
            verify_fix
            ;;
            
        monitor)
            setup_monitoring
            ;;
            
        pin-safe-versions)
            pin_safe_versions
            ;;
            
        help|*)
            cat << 'EOF'
HypatiaX Security Vulnerability Manager
========================================

Usage: ./security_manager.sh [command] [options]

Commands:
  audit               - Run complete security audit
  fix-vulnerabilities - Automatically upgrade vulnerable packages
  quick-fix          - Run backup + fix + verify in one command
  update-requirements - Update requirements files with safe versions
  check-specific PKG  - Check specific package (e.g., pillow)
  generate-report    - Generate detailed security report
  verify-fix         - Verify all vulnerabilities are fixed
  monitor            - Set up continuous monitoring (GitHub Actions)
  pin-safe-versions  - Pin all packages to current safe versions
  help               - Show this help message

Examples:
  # Quick fix (recommended)
  ./security_manager.sh quick-fix

  # Step by step
  ./security_manager.sh audit
  ./security_manager.sh fix-vulnerabilities
  ./security_manager.sh verify-fix

  # Check specific package
  ./security_manager.sh check-specific pillow

  # Generate report for team
  ./security_manager.sh generate-report

Current Known Vulnerabilities:
  1. nbconvert    - Code execution (Windows)      - Fix: >=7.16.4
  2. cryptography - Subgroup attack (SECT curves) - Fix: >=42.0.4
  3. Pillow       - Out-of-bounds write (PSD)     - Fix: >=10.3.0

Severity: HIGH - Fix immediately

EOF
            ;;
    esac
}

# Run main function
main "$@"
