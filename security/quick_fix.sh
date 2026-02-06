#!/bin/bash
#
# Quick Security Vulnerability Fix Script
# Simple bash script to update all vulnerable packages
#
# Usage:
#   ./quick_fix.sh [options]
#
# Options:
#   --priority    Update only CRITICAL and HIGH severity packages
#   --backup      Create backup before updating
#   --skip-major  Skip major version upgrades
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
PRIORITY_ONLY=false
CREATE_BACKUP=false
SKIP_MAJOR=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --priority)
            PRIORITY_ONLY=true
            shift
            ;;
        --backup)
            CREATE_BACKUP=true
            shift
            ;;
        --skip-major)
            SKIP_MAJOR=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --priority    Update only CRITICAL and HIGH severity packages"
            echo "  --backup      Create backup before updating"
            echo "  --skip-major  Skip major version upgrades"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "Security Vulnerability Fix Script"
echo "=========================================="
echo ""

# Create backup if requested
if [ "$CREATE_BACKUP" = true ]; then
    BACKUP_FILE="requirements_backup_$(date +%Y%m%d_%H%M%S).txt"
    echo -e "${BLUE}Creating backup: $BACKUP_FILE${NC}"
    pip freeze > "$BACKUP_FILE"
    echo -e "${GREEN}✓ Backup created${NC}"
    echo ""
fi

# Function to update a package
update_package() {
    local package=$1
    local version=$2
    local description=$3
    local severity=$4
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Package:${NC} $package"
    echo -e "${YELLOW}Version:${NC} $version"
    echo -e "${YELLOW}Severity:${NC} $severity"
    echo -e "${YELLOW}Issue:${NC} $description"
    echo ""
    
    if pip install --upgrade "$package==$version"; then
        echo -e "${GREEN}✓ Successfully updated $package to $version${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ Failed to update $package${NC}"
        echo ""
        return 1
    fi
}

# Counter for tracking
UPDATED=0
FAILED=0

echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}CRITICAL UPDATES${NC}"
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# CRITICAL
if update_package "fonttools" "4.61.0" "Path traversal (CVE-2025-66034, CVSS 9.8)" "CRITICAL"; then
    ((UPDATED++))
else
    ((FAILED++))
fi

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}HIGH PRIORITY UPDATES${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# HIGH PRIORITY
if update_package "urllib3" "2.6.3" "3 DoS vulnerabilities" "HIGH"; then ((UPDATED++)); else ((FAILED++)); fi
if update_package "pyasn1" "0.6.2" "DoS via malformed RELATIVE-OID (CVE-2026-23490)" "HIGH"; then ((UPDATED++)); else ((FAILED++)); fi
if update_package "nbconvert" "7.17.0" "Search path vulnerability (CVE-2025-53000)" "HIGH"; then ((UPDATED++)); else ((FAILED++)); fi
if update_package "marshmallow" "4.1.2" "DoS via validation errors (CVE-2025-68480)" "HIGH"; then ((UPDATED++)); else ((FAILED++)); fi
if update_package "django" "5.2.11" "8 vulnerabilities including SQL injection" "HIGH"; then ((UPDATED++)); else ((FAILED++)); fi
if update_package "aiohttp" "3.13.3" "8 vulnerabilities including DoS" "HIGH"; then ((UPDATED++)); else ((FAILED++)); fi

# Skip remaining updates if priority only
if [ "$PRIORITY_ONLY" = true ]; then
    echo -e "${BLUE}Priority-only mode: Skipping medium and standard updates${NC}"
    echo ""
else
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}MEDIUM PRIORITY UPDATES${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # MEDIUM PRIORITY
    if update_package "werkzeug" "3.1.5" "2 DoS vulnerabilities" "MEDIUM"; then ((UPDATED++)); else ((FAILED++)); fi
    if update_package "filelock" "3.20.3" "3 TOCTOU race conditions" "MEDIUM"; then ((UPDATED++)); else ((FAILED++)); fi
    if update_package "virtualenv" "20.36.1" "Race condition vulnerability" "MEDIUM"; then ((UPDATED++)); else ((FAILED++)); fi
    if update_package "authlib" "1.6.6" "CSRF vulnerability" "MEDIUM"; then ((UPDATED++)); else ((FAILED++)); fi
    
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}STANDARD UPDATES${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # STANDARD
    if update_package "wheel" "0.46.2" "Path traversal vulnerability" "STANDARD"; then ((UPDATED++)); else ((FAILED++)); fi
    if update_package "sqlparse" "0.5.4" "Algorithmic complexity DoS" "STANDARD"; then ((UPDATED++)); else ((FAILED++)); fi
    
    # MAJOR VERSION UPDATES
    if [ "$SKIP_MAJOR" = false ]; then
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}MAJOR VERSION UPDATES (May have breaking changes)${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        
        if update_package "transformers" "5.0.0" "Insecure deserialization (4.x → 5.0.0)" "MAJOR"; then ((UPDATED++)); else ((FAILED++)); fi
        if update_package "protobuf" "6.33.5" "DoS via recursion depth (5.x → 6.x)" "MAJOR"; then ((UPDATED++)); else ((FAILED++)); fi
        if update_package "pip" "26.0" "Path traversal (25.x → 26.0)" "MAJOR"; then ((UPDATED++)); else ((FAILED++)); fi
    else
        echo -e "${YELLOW}Skipping major version updates (use without --skip-major to include)${NC}"
        echo ""
    fi
fi

# Summary
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo -e "${GREEN}Successfully updated: $UPDATED packages${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed to update: $FAILED packages${NC}"
fi

if [ "$CREATE_BACKUP" = true ]; then
    echo ""
    echo -e "${BLUE}Backup file: $BACKUP_FILE${NC}"
    echo -e "${BLUE}To rollback: pip install -r $BACKUP_FILE${NC}"
fi

echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Run your test suite to verify everything works!${NC}"
echo ""

# Exit with error if any updates failed
if [ $FAILED -gt 0 ]; then
    exit 1
fi

exit 0
