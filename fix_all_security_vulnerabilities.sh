#!/bin/bash
# Comprehensive Security Vulnerability Fix Script
# Fixes 10 vulnerabilities across 8 packages

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     COMPREHENSIVE SECURITY VULNERABILITY REMEDIATION          ║"
echo "║     10 vulnerabilities in 8 packages                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Vulnerability summary
echo -e "${YELLOW}VULNERABILITIES TO FIX:${NC}"
echo ""
echo "🔴 CRITICAL (SQL Injection):"
echo "   • Django 5.2.8 → 5.2.9+ (CVE-2025-13372)"
echo ""
echo "🟡 HIGH (DoS & Security):"
echo "   • werkzeug 3.1.3 → 3.1.4+"
echo "   • urllib3 2.5.0 → 2.6.0+ (2 CVEs)"
echo "   • sqlparse 0.5.3 → 0.5.4+"
echo "   • nbconvert 7.16.6 → 7.16.7+"
echo "   • marshmallow 4.1.0 → 4.1.2+"
echo "   • fonttools 4.60.1 → 4.61.0+"
echo "   • filelock 3.20.0 → 3.20.1+"
echo "   • Django 5.2.8 → 5.2.9+ (CVE-2025-64460)"
echo ""

# Check requirements file
if [ ! -f "requirements_hashed.txt" ]; then
    echo -e "${RED}✗ requirements_hashed.txt not found${NC}"
    echo "Please run from repository root"
    exit 1
fi

# Create backup
echo "💾 Creating backup..."
BACKUP="requirements_hashed.txt.backup_$(date +%Y%m%d_%H%M%S)"
cp requirements_hashed.txt "$BACKUP"
echo -e "${GREEN}✓ Backup: $BACKUP${NC}"
echo ""

# Display current versions
echo "📊 Current versions:"
echo "----------------------------------------"
for pkg in django werkzeug urllib3 sqlparse nbconvert marshmallow fonttools filelock; do
    if pip show "$pkg" > /dev/null 2>&1; then
        VERSION=$(pip show "$pkg" | grep "Version:" | awk '{print $2}')
        printf "%-15s %s\n" "$pkg" "$VERSION"
    else
        printf "%-15s %s\n" "$pkg" "Not installed"
    fi
done
echo ""

# Confirmation
read -p "Update all packages to fix vulnerabilities? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Update cancelled"
    exit 0
fi

echo ""
echo "🚀 Updating packages..."
echo ""

# Update each package with specific version requirements
UPDATES=(
    "django>=5.2.9"
    "werkzeug>=3.1.4"
    "urllib3>=2.6.0"
    "sqlparse>=0.5.4"
    "nbconvert>=7.16.7"
    "marshmallow>=4.1.2"
    "fonttools>=4.61.0"
    "filelock>=3.20.1"
)

SUCCESS_COUNT=0
FAIL_COUNT=0
FAILED_PACKAGES=()

for update in "${UPDATES[@]}"; do
    PKG=$(echo "$update" | cut -d'>' -f1)
    echo -ne "Updating ${BLUE}$PKG${NC}... "
    
    if pip install --upgrade "$update" > /tmp/pip_update.log 2>&1; then
        NEW_VERSION=$(pip show "$PKG" | grep "Version:" | awk '{print $2}')
        echo -e "${GREEN}✓ $NEW_VERSION${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}✗ Failed${NC}"
        ((FAIL_COUNT++))
        FAILED_PACKAGES+=("$PKG")
        echo "Error log: /tmp/pip_update.log"
    fi
done

echo ""

# Update requirements file
echo "📝 Updating requirements_hashed.txt..."
pip freeze > requirements_hashed.txt
echo -e "${GREEN}✓ Requirements updated${NC}"
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      UPDATE SUMMARY                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Updated versions:"
echo "----------------------------------------"
for pkg in django werkzeug urllib3 sqlparse nbconvert marshmallow fonttools filelock; do
    if pip show "$pkg" > /dev/null 2>&1; then
        VERSION=$(pip show "$pkg" | grep "Version:" | awk '{print $2}')
        printf "%-15s ${GREEN}%s${NC}\n" "$pkg" "$VERSION"
    fi
done
echo ""

echo "Results:"
echo "  ${GREEN}✓ Success: $SUCCESS_COUNT packages${NC}"
if [ $FAIL_COUNT -gt 0 ]; then
    echo "  ${RED}✗ Failed: $FAIL_COUNT packages${NC}"
    echo "  Failed packages: ${FAILED_PACKAGES[*]}"
fi
echo ""

# Verify fix
echo "🔐 Verifying security fixes..."
echo ""

if command -v pip-audit &> /dev/null; then
    echo "Running pip-audit..."
    if pip-audit 2>&1 | grep -E "django|werkzeug|urllib3|sqlparse|nbconvert|marshmallow|fonttools|filelock"; then
        echo -e "${YELLOW}⚠ Some vulnerabilities may still be present${NC}"
        echo "Review pip-audit output above"
    else
        echo -e "${GREEN}✓ pip-audit clean for updated packages${NC}"
    fi
else
    echo -e "${YELLOW}ℹ Install pip-audit for verification: pip install pip-audit${NC}"
fi
echo ""

if command -v safety &> /dev/null; then
    echo "Running safety check..."
    safety check --file requirements_hashed.txt > /tmp/safety_check.txt 2>&1 || true
    
    if grep -E "django|werkzeug|urllib3|sqlparse|nbconvert|marshmallow|fonttools|filelock" /tmp/safety_check.txt; then
        echo -e "${YELLOW}⚠ Some vulnerabilities may still be present${NC}"
    else
        echo -e "${GREEN}✓ safety check clean for updated packages${NC}"
    fi
else
    echo -e "${YELLOW}ℹ Install safety for verification: pip install safety${NC}"
fi
echo ""

# Next steps
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                       NEXT STEPS                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "1. ${GREEN}Test your application${NC}"
echo "   python -m pytest tests/"
echo "   # Or run your specific test suite"
echo ""
echo "2. ${GREEN}Commit the changes${NC}"
echo "   git add requirements_hashed.txt"
echo "   git commit -m \"Security: Update 8 packages (10 CVE fixes)\""
echo "   git push"
echo ""
echo "3. ${GREEN}Close GitHub security alerts${NC}"
echo "   Verify all 10 alerts are resolved"
echo ""
echo "4. ${GREEN}Install audit tools (if not installed)${NC}"
echo "   pip install pip-audit safety"
echo ""
echo "Backup location: $BACKUP"
echo ""
echo -e "${GREEN}✓ Security update complete!${NC}"
