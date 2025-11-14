#!/bin/bash

# Remote Server Security Vulnerability Fix Script
# Usage: ./fix_remote_vulnerabilities.sh user@hostname /path/to/venv

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}Usage: $0 user@hostname /path/to/venv${NC}"
    echo "Example: $0 user@example.com /home/user/venv-312"
    exit 1
fi

REMOTE_HOST=$1
REMOTE_VENV=$2

echo -e "${GREEN}=== Remote Security Vulnerability Fix ===${NC}\n"
echo -e "${YELLOW}Remote host:${NC} $REMOTE_HOST"
echo -e "${YELLOW}Virtual env:${NC} $REMOTE_VENV\n"

# Test SSH connection
echo -e "${YELLOW}Testing SSH connection...${NC}"
if ! ssh -o ConnectTimeout=5 "$REMOTE_HOST" "echo 'Connection successful'"; then
    echo -e "${RED}ERROR: Cannot connect to $REMOTE_HOST${NC}"
    exit 1
fi
echo -e "${GREEN}✓ SSH connection successful${NC}\n"

# Create remote script
REMOTE_SCRIPT=$(cat << 'REMOTE_SCRIPT_EOF'
#!/bin/bash
set -e

VENV_PATH=$1
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[Remote] Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

echo -e "${GREEN}✓ Virtual environment activated: $VIRTUAL_ENV${NC}\n"

# Create backup
echo -e "${YELLOW}[Remote] Creating backup...${NC}"
BACKUP_DIR="$HOME/venv_backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pip freeze > "$BACKUP_DIR/requirements.backup.$TIMESTAMP.txt"
echo -e "${GREEN}✓ Backup saved: $BACKUP_DIR/requirements.backup.$TIMESTAMP.txt${NC}\n"

# Update pip tools
echo -e "${YELLOW}[Remote] Updating pip, setuptools, wheel...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ Core tools updated${NC}\n"

# Install security tools
echo -e "${YELLOW}[Remote] Installing security tools...${NC}"
pip install pip-audit safety
echo -e "${GREEN}✓ Security tools installed${NC}\n"

# Scan
echo -e "${YELLOW}[Remote] Scanning vulnerabilities...${NC}\n"
pip-audit --desc || true
echo ""

# Fix critical and high
echo -e "${YELLOW}[Remote] Fixing CRITICAL and HIGH severity issues...${NC}\n"

# Set temp directory to avoid tmpfs issues
export TMPDIR="$HOME/tmp_pip"
mkdir -p "$TMPDIR"

pip install --upgrade 'h11>=0.14.0' || true
pip install --upgrade 'django>=4.2.11' || true
pip install --upgrade 'starlette>=0.36.2' || true
pip install --upgrade 'brotli>=1.1.0' || true
pip install --upgrade 'protobuf>=4.25.3' || true
pip install --upgrade 'jupyter-core>=5.7.2' || true
pip install --upgrade 'tornado>=6.4.1' || true
pip install --upgrade 'setuptools>=70.0.0' || true
pip install --upgrade 'redis>=5.0.3' || true
pip install --upgrade 'ecdsa>=0.19.0' || true

echo -e "\n${GREEN}✓ Critical/High fixes completed${NC}\n"

# Save fixed requirements
pip freeze > "$HOME/requirements.fixed.$TIMESTAMP.txt"
echo -e "${GREEN}✓ Fixed requirements saved: $HOME/requirements.fixed.$TIMESTAMP.txt${NC}\n"

# Final scan
echo -e "${YELLOW}[Remote] Final vulnerability scan...${NC}\n"
pip-audit || true

echo -e "\n${GREEN}=== Remote Fix Complete ===${NC}"
echo -e "${YELLOW}Backup location:${NC} $BACKUP_DIR/requirements.backup.$TIMESTAMP.txt"
echo -e "${YELLOW}Fixed requirements:${NC} $HOME/requirements.fixed.$TIMESTAMP.txt"
REMOTE_SCRIPT_EOF
)

# Upload and execute script
echo -e "${YELLOW}Uploading and executing fix script on remote host...${NC}\n"

ssh "$REMOTE_HOST" "bash -s -- $REMOTE_VENV" <<< "$REMOTE_SCRIPT"

echo -e "\n${GREEN}=== Remote Vulnerability Fix Complete ===${NC}\n"

# Download fixed requirements
echo -e "${YELLOW}Downloading fixed requirements file...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
scp "$REMOTE_HOST:~/requirements.fixed.*.txt" "./requirements.remote.$TIMESTAMP.txt" 2>/dev/null || \
    echo -e "${YELLOW}Could not download fixed requirements (check manually)${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Test your remote application"
echo "2. Monitor logs for any issues"
echo "3. Rollback if needed:"
echo "   ssh $REMOTE_HOST"
echo "   source $REMOTE_VENV/bin/activate"
echo "   pip install -r ~/venv_backups/requirements.backup.*.txt"
