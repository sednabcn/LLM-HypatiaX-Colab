#!/bin/bash

# Security Vulnerability Fix Script for Python Dependencies
# Usage: ./fix_vulnerabilities.sh [local|remote]
# Auto-detects py312 or py313 environment and uses appropriate requirements file

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Python Security Vulnerability Fix Script ===${NC}\n"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${RED}ERROR: No virtual environment detected!${NC}"
    echo "Please activate your virtual environment first:"
    echo "  source py312/bin/activate  # For Python 3.12"
    echo "  source py313/bin/activate  # For Python 3.13"
    exit 1
fi

# Auto-detect which environment and requirements file to use
VENV_NAME=$(basename "$VIRTUAL_ENV")
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')

echo -e "${YELLOW}Virtual Environment:${NC} $VIRTUAL_ENV"
echo -e "${YELLOW}Environment Name:${NC} $VENV_NAME"
echo -e "${YELLOW}Python Version:${NC} $PYTHON_VERSION"

# Determine requirements file based on environment
if [[ "$VENV_NAME" == "py312" ]] || [[ "$PYTHON_VERSION" == 3.12* ]]; then
    REQUIREMENTS_FILE="requirements-py312.txt"
    ENV_TYPE="py312"
    echo -e "${BLUE}Detected: Python 3.12 environment${NC}"
elif [[ "$VENV_NAME" == "py313" ]] || [[ "$PYTHON_VERSION" == 3.13* ]]; then
    REQUIREMENTS_FILE="requirements.txt"
    ENV_TYPE="py313"
    echo -e "${BLUE}Detected: Python 3.13 environment${NC}"
else
    echo -e "${YELLOW}Warning: Could not auto-detect environment type${NC}"
    echo "Please select your environment:"
    echo "1) py312 (use requirements-py312.txt)"
    echo "2) py313 (use requirements.txt)"
    read -p "Choose [1-2]: " env_choice
    case $env_choice in
        1)
            REQUIREMENTS_FILE="requirements-py312.txt"
            ENV_TYPE="py312"
            ;;
        2)
            REQUIREMENTS_FILE="requirements.txt"
            ENV_TYPE="py313"
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
fi

echo -e "${YELLOW}Requirements File:${NC} $REQUIREMENTS_FILE\n"

# Check if requirements file exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${RED}ERROR: Requirements file not found: $REQUIREMENTS_FILE${NC}"
    exit 1
fi

# Function to backup requirements
backup_requirements() {
    echo -e "${YELLOW}[1/5] Creating backup...${NC}"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)

    if [ -f "$REQUIREMENTS_FILE" ]; then
        cp "$REQUIREMENTS_FILE" "${REQUIREMENTS_FILE}.backup.${TIMESTAMP}"
        echo -e "${GREEN}✓ Backup created: ${REQUIREMENTS_FILE}.backup.${TIMESTAMP}${NC}"
    fi

    # Create current state backup
    pip freeze > "requirements.freeze.${ENV_TYPE}.backup.${TIMESTAMP}.txt"
    echo -e "${GREEN}✓ Current packages saved: requirements.freeze.${ENV_TYPE}.backup.${TIMESTAMP}.txt${NC}\n"
}

# Function to update pip tools
update_pip_tools() {
    echo -e "${YELLOW}[2/5] Updating pip, setuptools, and wheel...${NC}"
    pip install --upgrade pip setuptools wheel
    echo -e "${GREEN}✓ Core tools updated${NC}\n"
}

# Function to install security tools
install_security_tools() {
    echo -e "${YELLOW}[3/5] Installing security scanning tools...${NC}"
    pip install pip-audit safety
    echo -e "${GREEN}✓ Security tools installed${NC}\n"
}

# Function to scan vulnerabilities
scan_vulnerabilities() {
    echo -e "${YELLOW}[4/5] Scanning for vulnerabilities...${NC}\n"

    echo "=== pip-audit scan ==="
    pip-audit --desc || true

    echo -e "\n=== safety scan ==="
    safety check || true

    echo ""
}

# Function to fix critical vulnerabilities
fix_critical() {
    echo -e "${YELLOW}[5/5] Fixing CRITICAL and HIGH severity vulnerabilities...${NC}\n"

    # Critical fixes
    echo -e "${RED}Fixing CRITICAL issues...${NC}"
    pip install --upgrade 'h11>=0.14.0' || echo "h11 update failed (may not be installed)"

    # High severity fixes
    echo -e "${RED}Fixing HIGH severity issues...${NC}"
    pip install --upgrade 'django>=4.2.11' || echo "django update failed (may not be installed)"
    pip install --upgrade 'starlette>=0.36.2' || echo "starlette update failed (may not be installed)"
    pip install --upgrade 'brotli>=1.1.0' || echo "brotli update failed (may not be installed)"
    pip install --upgrade 'protobuf>=4.25.3' || echo "protobuf update failed (may not be installed)"
    pip install --upgrade 'jupyter-core>=5.7.2' || echo "jupyter-core update failed (may not be installed)"
    pip install --upgrade 'tornado>=6.4.1' || echo "tornado update failed (may not be installed)"
    pip install --upgrade 'setuptools>=70.0.0' || echo "setuptools already updated"
    pip install --upgrade 'redis>=5.0.3' || echo "redis update failed (may not be installed)"
    pip install --upgrade 'ecdsa>=0.19.0' || echo "ecdsa update failed (may not be installed)"

    echo -e "\n${GREEN}✓ Critical and High severity fixes attempted${NC}\n"
}

# Function to fix all vulnerabilities automatically
fix_all_auto() {
    echo -e "${YELLOW}Attempting automatic fix of all vulnerabilities...${NC}\n"
    pip-audit --fix || echo -e "${YELLOW}Some vulnerabilities could not be auto-fixed${NC}"
}

# Function to update moderate/low severity packages
fix_moderate_low() {
    echo -e "${YELLOW}Fixing MODERATE and LOW severity issues...${NC}\n"

    pip install --upgrade 'pypdf>=4.1.0' || echo "pypdf update failed (may not be installed)"
    pip install --upgrade 'transformers>=4.38.0' || echo "transformers update failed (may not be installed)"
    pip install --upgrade 'urllib3>=2.2.1' || echo "urllib3 update failed (may not be installed)"
    pip install --upgrade 'requests>=2.32.0' || echo "requests update failed (may not be installed)"
    pip install --upgrade 'cryptography>=42.0.5' || echo "cryptography update failed (may not be installed)"
    pip install --upgrade 'aiohttp>=3.9.4' || echo "aiohttp update failed (may not be installed)"
    pip install --upgrade 'flask>=3.0.3' || echo "flask update failed (may not be installed)"
    pip install --upgrade 'torch>=2.2.2' || echo "torch update failed (may not be installed)"
    pip install --upgrade 'scapy>=2.5.0' || echo "scapy update failed (may not be installed)"
    pip install --upgrade 'python-socketio>=5.11.2' || echo "python-socketio update failed (may not be installed)"
    pip install --upgrade 'mitmproxy>=10.2.4' || echo "mitmproxy update failed (may not be installed)"
    pip install --upgrade 'h2>=4.1.0' || echo "h2 update failed (may not be installed)"
    pip install --upgrade 'pycares>=4.4.0' || echo "pycares update failed (may not be installed)"

    echo -e "\n${GREEN}✓ Moderate and Low severity fixes attempted${NC}\n"
}

# Function to save new requirements
save_requirements() {
    echo -e "${YELLOW}Saving updated requirements...${NC}"
    OUTPUT_FILE="requirements.fixed.${ENV_TYPE}.txt"
    pip freeze > "$OUTPUT_FILE"
    echo -e "${GREEN}✓ New requirements saved to $OUTPUT_FILE${NC}\n"
}

# Function to show summary
show_summary() {
    echo -e "${GREEN}=== Fix Summary ===${NC}\n"
    echo -e "${BLUE}Environment: $ENV_TYPE${NC}"
    echo -e "${BLUE}Requirements File: $REQUIREMENTS_FILE${NC}\n"

    echo "Backups created:"
    ls -lh *backup*.${ENV_TYPE}* 2>/dev/null || ls -lh ${REQUIREMENTS_FILE}.backup* 2>/dev/null || echo "  No backups found"
    echo ""
    echo "New requirements file: requirements.fixed.${ENV_TYPE}.txt"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Test your application thoroughly"
    echo "2. If everything works:"
    echo "   mv requirements.fixed.${ENV_TYPE}.txt $REQUIREMENTS_FILE"
    echo "3. If issues occur, restore from backup:"
    echo "   pip install -r requirements.freeze.${ENV_TYPE}.backup.<timestamp>.txt"
    echo ""
    echo -e "${YELLOW}Re-scan for remaining vulnerabilities:${NC}"
    echo "  pip-audit"
    echo ""
    echo -e "${YELLOW}To apply to the other environment:${NC}"
    if [[ "$ENV_TYPE" == "py312" ]]; then
        echo "  deactivate"
        echo "  source py313/bin/activate"
        echo "  ./fix_vulnerabilities.sh"
    else
        echo "  deactivate"
        echo "  source py312/bin/activate"
        echo "  ./fix_vulnerabilities.sh"
    fi
}

# Main execution
main() {
    MODE=${1:-local}

    echo -e "Running in ${GREEN}$MODE${NC} mode\n"

    # Always create backup first
    backup_requirements

    # Update core tools
    update_pip_tools

    # Install security tools
    install_security_tools

    # Initial scan
    scan_vulnerabilities

    # Ask user what to fix
    echo -e "${YELLOW}What would you like to fix?${NC}"
    echo "1) Critical and High severity only (recommended)"
    echo "2) All vulnerabilities (automatic)"
    echo "3) Everything including Moderate/Low"
    echo "4) Exit without fixing"
    read -p "Choose [1-4]: " choice

    case $choice in
        1)
            fix_critical
            ;;
        2)
            fix_all_auto
            ;;
        3)
            fix_critical
            fix_moderate_low
            ;;
        4)
            echo "Exiting without fixes"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac

    # Save new requirements
    save_requirements

    # Final scan
    echo -e "\n${YELLOW}Running final security scan...${NC}\n"
    pip-audit --desc || true

    # Show summary
    show_summary
}

# Run main function
main "$@"
