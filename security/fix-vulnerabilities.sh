#!/bin/bash

# Security Vulnerability Fix Script for Python Virtual Environments
# Fixes vulnerabilities found by pip-audit or safety check

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Security Vulnerability Fix Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}Error: No virtual environment detected!${NC}"
    echo -e "Please activate your virtual environment first:"
    echo -e "  ${YELLOW}source /path/to/venv/bin/activate${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Virtual environment detected: ${BLUE}$VIRTUAL_ENV${NC}"
echo ""

# Check temp directory
if [ -z "$TMPDIR" ] || [ ! -d "$TMPDIR" ]; then
    echo -e "${YELLOW}⚠${NC}  No TMPDIR set or directory doesn't exist"
    echo -e "  Using default: ~/tmp_pip"
    export TMPDIR=~/tmp_pip
    mkdir -p "$TMPDIR"
fi
echo -e "${GREEN}✓${NC} Temp directory: ${BLUE}$TMPDIR${NC}"
echo ""

# Create backup
BACKUP_FILE="requirements.backup.$(date +%Y%m%d_%H%M%S).txt"
echo -e "${YELLOW}Creating backup...${NC}"
pip freeze > "$BACKUP_FILE"
echo -e "${GREEN}✓${NC} Backup saved to: ${BLUE}$BACKUP_FILE${NC}"
echo ""

# Update pip tools
echo -e "${YELLOW}Updating pip, setuptools, and wheel...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓${NC} Tools updated"
echo ""

# Install security scanner if not present
echo -e "${YELLOW}Checking for pip-audit...${NC}"
if ! command -v pip-audit &> /dev/null; then
    echo -e "  Installing pip-audit..."
    pip install pip-audit
    echo -e "${GREEN}✓${NC} pip-audit installed"
else
    echo -e "${GREEN}✓${NC} pip-audit already installed"
fi
echo ""

# Show vulnerability summary
echo -e "${YELLOW}Scanning for vulnerabilities...${NC}"
pip-audit --desc || true
echo ""

# Ask user which priority level to fix
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Choose Fix Priority Level${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e ""
echo -e "${RED}1)${NC} Critical and High severity only ${YELLOW}(Recommended - Safest)${NC}"
echo -e "${YELLOW}2)${NC} Critical, High, and Moderate severity"
echo -e "${GREEN}3)${NC} All vulnerabilities ${YELLOW}(May cause breaking changes)${NC}"
echo -e "${BLUE}4)${NC} Automatic fix using pip-audit --fix ${YELLOW}(Fastest)${NC}"
echo -e "${MAGENTA}5)${NC} Manual - Show commands only ${YELLOW}(No changes)${NC}"
echo -e ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo -e "\n${YELLOW}Fixing CRITICAL and HIGH severity vulnerabilities...${NC}\n"

        # CRITICAL
        echo -e "${RED}[CRITICAL]${NC} Updating h11..."
        pip install --upgrade "h11>=0.14.0" || echo "Failed to update h11"

        # HIGH
        echo -e "${YELLOW}[HIGH]${NC} Updating Django..."
        pip install --upgrade "django>=4.2.11" || echo "Failed to update django"

        echo -e "${YELLOW}[HIGH]${NC} Updating Starlette..."
        pip install --upgrade "starlette>=0.36.2" || echo "Failed to update starlette"

        echo -e "${YELLOW}[HIGH]${NC} Updating Brotli..."
        pip install --upgrade "brotli>=1.1.0" || echo "Failed to update brotli"

        echo -e "${YELLOW}[HIGH]${NC} Updating protobuf..."
        pip install --upgrade "protobuf>=4.25.3" || echo "Failed to update protobuf"

        echo -e "${YELLOW}[HIGH]${NC} Updating jupyter-core..."
        pip install --upgrade "jupyter-core>=5.7.2" || echo "Failed to update jupyter-core"

        echo -e "${YELLOW}[HIGH]${NC} Updating tornado..."
        pip install --upgrade "tornado>=6.3.3" || echo "Failed to update tornado"

        echo -e "${YELLOW}[HIGH]${NC} Updating setuptools..."
        pip install --upgrade "setuptools>=70.0.0" || echo "Failed to update setuptools"

        echo -e "${YELLOW}[HIGH]${NC} Updating redis..."
        pip install --upgrade "redis>=5.0.8" || echo "Failed to update redis"

        echo -e "${YELLOW}[HIGH]${NC} Updating ecdsa..."
        pip install --upgrade "ecdsa>=0.19.0" || echo "Failed to update ecdsa"

        echo -e "\n${GREEN}✓${NC} Critical and High severity fixes complete"
        ;;

    2)
        echo -e "\n${YELLOW}Fixing CRITICAL, HIGH, and MODERATE severity vulnerabilities...${NC}\n"

        # CRITICAL
        echo -e "${RED}[CRITICAL]${NC} Updating h11..."
        pip install --upgrade "h11>=0.14.0" || echo "Failed to update h11"

        # HIGH
        echo -e "${YELLOW}[HIGH]${NC} Updating multiple packages..."
        pip install --upgrade "django>=4.2.11" "starlette>=0.36.2" "brotli>=1.1.0" \
                              "protobuf>=4.25.3" "jupyter-core>=5.7.2" "tornado>=6.3.3" \
                              "setuptools>=70.0.0" "redis>=5.0.8" "ecdsa>=0.19.0" || echo "Some packages failed"

        # MODERATE
        echo -e "${BLUE}[MODERATE]${NC} Updating transformers..."
        pip install --upgrade "transformers>=4.38.0" || echo "Failed to update transformers"

        echo -e "${BLUE}[MODERATE]${NC} Updating urllib3..."
        pip install --upgrade "urllib3>=2.0.7" || echo "Failed to update urllib3"

        echo -e "${BLUE}[MODERATE]${NC} Updating requests..."
        pip install --upgrade "requests>=2.32.0" || echo "Failed to update requests"

        echo -e "${BLUE}[MODERATE]${NC} Updating pypdf..."
        pip install --upgrade "pypdf>=4.0.0" || echo "Failed to update pypdf"

        echo -e "${BLUE}[MODERATE]${NC} Updating torch..."
        pip install --no-cache-dir --upgrade "torch>=2.1.0" || echo "Failed to update torch"

        echo -e "${BLUE}[MODERATE]${NC} Updating other packages..."
        pip install --upgrade "pillow>=10.3.0" "aiohttp>=3.9.2" "jinja2>=3.1.4" \
                              "certifi>=2024.7.4" "cryptography>=42.0.4" || echo "Some packages failed"

        echo -e "\n${GREEN}✓${NC} Critical, High, and Moderate severity fixes complete"
        ;;

    3)
        echo -e "\n${YELLOW}Fixing ALL vulnerabilities...${NC}\n"
        echo -e "${RED}Warning: This may cause breaking changes!${NC}\n"
        read -p "Are you sure? (yes/no): " confirm

        if [ "$confirm" != "yes" ]; then
            echo -e "${YELLOW}Aborted${NC}"
            exit 0
        fi

        # Update all packages with known vulnerabilities
        pip install --upgrade \
            "h11>=0.14.0" "django>=4.2.11" "starlette>=0.36.2" "brotli>=1.1.0" \
            "protobuf>=4.25.3" "jupyter-core>=5.7.2" "tornado>=6.3.3" "setuptools>=70.0.0" \
            "redis>=5.0.8" "ecdsa>=0.19.0" "transformers>=4.38.0" "urllib3>=2.0.7" \
            "requests>=2.32.0" "pypdf>=4.0.0" "pillow>=10.3.0" "aiohttp>=3.9.2" \
            "jinja2>=3.1.4" "certifi>=2024.7.4" "cryptography>=42.0.4" \
            "zipp>=3.19.1" "werkzeug>=3.0.3" "gunicorn>=22.0.0" "tqdm>=4.66.3" \
            "idna>=3.7" || echo "Some packages failed to update"

        # Large packages separately to avoid memory issues
        echo -e "\n${YELLOW}Updating large packages...${NC}"
        pip install --no-cache-dir --upgrade "torch>=2.1.0" || echo "Failed to update torch"

        echo -e "\n${GREEN}✓${NC} All vulnerability fixes complete"
        ;;

    4)
        echo -e "\n${YELLOW}Running automatic fix with pip-audit...${NC}\n"
        echo -e "${RED}Warning: This may update many packages!${NC}\n"
        read -p "Continue? (yes/no): " confirm

        if [ "$confirm" != "yes" ]; then
            echo -e "${YELLOW}Aborted${NC}"
            exit 0
        fi

        pip-audit --fix

        echo -e "\n${GREEN}✓${NC} Automatic fix complete"
        ;;

    5)
        echo -e "\n${MAGENTA}Manual Fix Commands:${NC}\n"
        echo -e "${RED}CRITICAL:${NC}"
        echo -e "  pip install --upgrade 'h11>=0.14.0'"
        echo -e ""
        echo -e "${YELLOW}HIGH:${NC}"
        echo -e "  pip install --upgrade 'django>=4.2.11'"
        echo -e "  pip install --upgrade 'starlette>=0.36.2'"
        echo -e "  pip install --upgrade 'brotli>=1.1.0'"
        echo -e "  pip install --upgrade 'protobuf>=4.25.3'"
        echo -e "  pip install --upgrade 'jupyter-core>=5.7.2'"
        echo -e "  pip install --upgrade 'tornado>=6.3.3'"
        echo -e "  pip install --upgrade 'setuptools>=70.0.0'"
        echo -e "  pip install --upgrade 'redis>=5.0.8'"
        echo -e "  pip install --upgrade 'ecdsa>=0.19.0'"
        echo -e ""
        echo -e "${BLUE}MODERATE:${NC}"
        echo -e "  pip install --upgrade 'transformers>=4.38.0'"
        echo -e "  pip install --upgrade 'urllib3>=2.0.7'"
        echo -e "  pip install --upgrade 'requests>=2.32.0'"
        echo -e "  pip install --upgrade 'pypdf>=4.0.0'"
        echo -e "  pip install --no-cache-dir --upgrade 'torch>=2.1.0'"
        echo -e "  pip install --upgrade 'pillow>=10.3.0'"
        echo -e "  pip install --upgrade 'aiohttp>=3.9.2'"
        echo -e "  pip install --upgrade 'jinja2>=3.1.4'"
        echo -e "  pip install --upgrade 'certifi>=2024.7.4'"
        echo -e "  pip install --upgrade 'cryptography>=42.0.4'"
        echo -e ""
        echo -e "${GREEN}No changes made. Run commands manually as needed.${NC}"
        exit 0
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Final scan
echo -e "\n${YELLOW}Running final vulnerability scan...${NC}\n"
pip-audit --desc || true

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}Fix Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e ""
echo -e "Backup file: ${BLUE}$BACKUP_FILE${NC}"
echo -e ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Test your application: ${BLUE}python your_app.py${NC}"
echo -e "2. If issues occur, restore backup: ${BLUE}pip install -r $BACKUP_FILE${NC}"
echo -e "3. Commit updated requirements: ${BLUE}pip freeze > requirements.txt${NC}"
echo -e ""
echo -e "${GREEN}Security vulnerabilities have been addressed!${NC}"
echo ""
