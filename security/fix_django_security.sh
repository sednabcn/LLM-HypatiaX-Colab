#!/bin/bash
# Django Security Vulnerability Fix Script
# Addresses Alerts #410 (SQL Injection) and #386 (Algorithmic Complexity)

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Django Security Vulnerability Remediation Script       ║"
echo "║   Fixes: Alert #410 (HIGH) + Alert #386 (LOW)           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if requirements file exists
echo "📋 Step 1: Locating requirements file..."
if [ ! -f "requirements_hashed.txt" ]; then
    echo -e "${RED}✗ requirements_hashed.txt not found in current directory${NC}"
    echo "Please run this script from the repository root directory."
    exit 1
fi
echo -e "${GREEN}✓ Found requirements_hashed.txt${NC}"
echo ""

# Step 2: Check current Django version
echo "🔍 Step 2: Checking current Django version..."
if pip show django > /dev/null 2>&1; then
    CURRENT_VERSION=$(pip show django | grep "Version:" | awk '{print $2}')
    echo -e "${YELLOW}Current Django version: $CURRENT_VERSION${NC}"
else
    echo -e "${YELLOW}Django not currently installed or not found${NC}"
    CURRENT_VERSION="Not installed"
fi
echo ""

# Step 3: Check if Django is actually used
echo "🔎 Step 3: Checking if Django is used in codebase..."
DJANGO_USAGE=$(find . -name "*.py" -type f -exec grep -l "import django\|from django" {} \; 2>/dev/null | wc -l)
if [ "$DJANGO_USAGE" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Django is used in $DJANGO_USAGE Python file(s)${NC}"
    echo "Files using Django:"
    find . -name "*.py" -type f -exec grep -l "import django\|from django" {} \; 2>/dev/null | head -5
else
    echo -e "${GREEN}ℹ Django not directly used (likely a transitive dependency)${NC}"
fi
echo ""

# Step 4: Check what requires Django
echo "🔗 Step 4: Checking dependencies..."
if pip show django > /dev/null 2>&1; then
    REQUIRED_BY=$(pip show django | grep "Required-by:" | cut -d: -f2 | xargs)
    if [ -z "$REQUIRED_BY" ]; then
        echo -e "${YELLOW}⚠ No packages explicitly require Django${NC}"
        echo "  (May be in requirements but not actively used)"
    else
        echo -e "${GREEN}Django required by: $REQUIRED_BY${NC}"
    fi
else
    echo "Django not installed, skipping dependency check"
fi
echo ""

# Step 5: Create backup
echo "💾 Step 5: Creating backup..."
BACKUP_FILE="requirements_hashed.txt.backup_$(date +%Y%m%d_%H%M%S)"
cp requirements_hashed.txt "$BACKUP_FILE"
echo -e "${GREEN}✓ Backup created: $BACKUP_FILE${NC}"
echo ""

# Step 6: Prompt for confirmation
echo "⚠️  CONFIRMATION REQUIRED ⚠️"
echo ""
echo "This script will:"
echo "  1. Update Django to the latest stable version"
echo "  2. Update requirements_hashed.txt"
echo "  3. Verify the security fix"
echo ""
echo "Backup location: $BACKUP_FILE"
echo ""
read -p "Continue with update? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo ""
    echo "❌ Update cancelled by user"
    echo "Backup preserved at: $BACKUP_FILE"
    exit 0
fi

echo ""
echo "🚀 Step 6: Updating Django..."

# Update Django
if pip install --upgrade django; then
    NEW_VERSION=$(pip show django | grep "Version:" | awk '{print $2}')
    echo -e "${GREEN}✓ Django updated successfully${NC}"
    echo -e "  Old version: ${YELLOW}$CURRENT_VERSION${NC}"
    echo -e "  New version: ${GREEN}$NEW_VERSION${NC}"
else
    echo -e "${RED}✗ Failed to update Django${NC}"
    echo "Restoring backup..."
    mv "$BACKUP_FILE" requirements_hashed.txt
    exit 1
fi
echo ""

# Step 7: Update requirements file
echo "📝 Step 7: Updating requirements file..."
pip freeze > requirements_hashed.txt
echo -e "${GREEN}✓ requirements_hashed.txt updated${NC}"
echo ""

# Step 8: Verify fix
echo "🔐 Step 8: Verifying security fix..."
echo ""

# Check if pip-audit is installed
if command -v pip-audit &> /dev/null; then
    echo "Running pip-audit..."
    if pip-audit --desc 2>/dev/null | grep -i django; then
        echo -e "${RED}⚠ Django vulnerabilities still detected${NC}"
        echo "You may need to update other dependencies or wait for patches"
    else
        echo -e "${GREEN}✓ No Django vulnerabilities found by pip-audit${NC}"
    fi
else
    echo -e "${YELLOW}ℹ pip-audit not installed${NC}"
    echo "Install with: pip install pip-audit"
    echo "Then run: pip-audit"
fi
echo ""

# Check if safety is installed
if command -v safety &> /dev/null; then
    echo "Running safety check..."
    if safety check --json 2>/dev/null | grep -i django; then
        echo -e "${YELLOW}⚠ Django vulnerabilities may still be present${NC}"
    else
        echo -e "${GREEN}✓ No Django vulnerabilities found by safety${NC}"
    fi
else
    echo -e "${YELLOW}ℹ safety not installed${NC}"
    echo "Install with: pip install safety"
    echo "Then run: safety check"
fi
echo ""

# Step 9: Summary
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    UPDATE COMPLETE                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  • Django updated: $CURRENT_VERSION → $NEW_VERSION"
echo "  • requirements_hashed.txt updated"
echo "  • Backup saved: $BACKUP_FILE"
echo ""
echo "Next Steps:"
echo "  1. ${GREEN}Test your application${NC}"
echo "     - Run your test suite"
echo "     - Verify functionality"
echo ""
echo "  2. ${GREEN}Commit the changes${NC}"
echo "     git add requirements_hashed.txt"
echo "     git commit -m \"Security: Update Django (fixes #410, #386)\""
echo "     git push"
echo ""
echo "  3. ${GREEN}Install security audit tools (if not already installed)${NC}"
echo "     pip install pip-audit safety"
echo ""
echo "  4. ${GREEN}Run final security check${NC}"
echo "     pip-audit"
echo "     safety check"
echo ""
echo "  5. ${GREEN}Close GitHub alerts${NC}"
echo "     - Verify alerts #410 and #386 are resolved"
echo "     - Comment on alerts with new version number"
echo ""
echo "📧 If issues occur:"
echo "   Restore backup: mv $BACKUP_FILE requirements_hashed.txt"
echo "   Reinstall:      pip install -r requirements_hashed.txt"
echo ""
echo -e "${GREEN}✓ Remediation script completed successfully${NC}"
