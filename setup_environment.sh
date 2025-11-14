#!/bin/bash
# Universal environment setup for HypatiaX
# Works in: Local development, GitHub Actions, Docker, Cloud environments
# Version: 2.0

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Unicode symbols (with fallbacks)
CHECK="${GREEN}✅${NC}"
CROSS="${RED}❌${NC}"
WARN="${YELLOW}⚠️${NC}"
INFO="${BLUE}ℹ️${NC}"

echo ""
echo "=================================="
echo "  HypatiaX Environment Setup"
echo "=================================="
echo ""

# ============================================================================
# ENVIRONMENT DETECTION
# ============================================================================

detect_environment() {
    if [ -n "$GITHUB_ACTIONS" ]; then
        echo "github"
    elif [ -n "$DOCKER_CONTAINER" ]; then
        echo "docker"
    elif [ -n "$AWS_EXECUTION_ENV" ] || [ -n "$AWS_LAMBDA_FUNCTION_NAME" ]; then
        echo "aws"
    elif [ -n "$GOOGLE_CLOUD_PROJECT" ] || [ -n "$K_SERVICE" ]; then
        echo "gcp"
    elif [ -n "$AZURE_FUNCTIONS_ENVIRONMENT" ]; then
        echo "azure"
    elif [ -n "$CI" ]; then
        echo "ci"
    else
        echo "local"
    fi
}

ENV_TYPE=$(detect_environment)

case $ENV_TYPE in
    github)
        echo -e "${INFO} Environment: GitHub Actions"
        ;;
    docker)
        echo -e "${INFO} Environment: Docker"
        ;;
    aws)
        echo -e "${INFO} Environment: AWS"
        ;;
    gcp)
        echo -e "${INFO} Environment: Google Cloud Platform"
        ;;
    azure)
        echo -e "${INFO} Environment: Azure"
        ;;
    ci)
        echo -e "${INFO} Environment: CI/CD"
        ;;
    local)
        echo -e "${INFO} Environment: Local Development"
        ;;
esac
echo ""

# ============================================================================
# PROJECT ROOT DETECTION
# ============================================================================

detect_project_root() {
    # Priority order:
    # 1. GITHUB_WORKSPACE (GitHub Actions)
    # 2. HYPATIAX_ROOT (explicit override)
    # 3. Docker standard paths
    # 4. Script location
    
    if [ -n "$GITHUB_WORKSPACE" ]; then
        echo "$GITHUB_WORKSPACE"
    elif [ -n "$HYPATIAX_ROOT" ]; then
        echo "$HYPATIAX_ROOT"
    elif [ "$ENV_TYPE" = "docker" ]; then
        # Check common Docker mount points
        for path in /app /workspace /code /opt/hypatiax; do
            if [ -d "$path/hypatiax" ]; then
                echo "$path"
                return
            fi
        done
        # Fallback to script directory
        SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
        echo "$SCRIPT_DIR"
    else
        # Local development - use script location
        SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
        echo "$SCRIPT_DIR"
    fi
}

PROJECT_ROOT=$(detect_project_root)
echo -e "${INFO} Project Root: ${BLUE}$PROJECT_ROOT${NC}"

# ============================================================================
# PROJECT STRUCTURE VALIDATION
# ============================================================================

echo ""
echo "Validating project structure..."

validate_structure() {
    local errors=0
    
    # Critical directories
    if [ ! -d "$PROJECT_ROOT/hypatiax" ]; then
        echo -e "${CROSS} hypatiax directory not found"
        errors=$((errors + 1))
    else
        echo -e "${CHECK} hypatiax directory found"
    fi
    
    # Important directories (warnings only)
    for dir in datasets data_spacy core models tools agents; do
        if [ ! -d "$PROJECT_ROOT/hypatiax/$dir" ]; then
            echo -e "${WARN} hypatiax/$dir directory not found (optional)"
        fi
    done
    
    if [ $errors -gt 0 ]; then
        echo ""
        echo -e "${CROSS} Project structure validation failed!"
        echo "Expected structure:"
        echo "  $PROJECT_ROOT/"
        echo "  ├── hypatiax/"
        echo "  │   ├── agents/"
        echo "  │   ├── core/"
        echo "  │   ├── datasets/"
        echo "  │   ├── data_spacy/"
        echo "  │   ├── models/"
        echo "  │   └── tools/"
        echo "  ├── tests/"
        echo "  └── setup_environment.sh"
        return 1
    fi
    
    return 0
}

if ! validate_structure; then
    exit 1
fi

echo -e "${CHECK} Project structure validated"
echo ""

# ============================================================================
# ENVIRONMENT-SPECIFIC SETUP
# ============================================================================

case $ENV_TYPE in
    # ========================================================================
    # GITHUB ACTIONS
    # ========================================================================
    github)
        echo "Configuring GitHub Actions environment..."
        
        # Set environment variables
        echo "HYPATIAX_ROOT=$PROJECT_ROOT" >> $GITHUB_ENV
        echo "PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH" >> $GITHUB_ENV
        echo "HYPATIAX_OUTPUT_DIR=$PROJECT_ROOT/ci_outputs" >> $GITHUB_ENV
        
        # Create outputs directory
        mkdir -p "$PROJECT_ROOT/ci_outputs"
        
        # Set output variables for workflow steps
        if [ -n "$GITHUB_OUTPUT" ]; then
            echo "project_root=$PROJECT_ROOT" >> $GITHUB_OUTPUT
            echo "environment=github" >> $GITHUB_OUTPUT
        fi
        
        echo -e "${CHECK} GitHub Actions environment configured"
        echo "   Variables added to GITHUB_ENV"
        ;;
    
    # ========================================================================
    # DOCKER
    # ========================================================================
    docker)
        echo "Configuring Docker environment..."
        
        export HYPATIAX_ROOT="$PROJECT_ROOT"
        export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
        export HYPATIAX_OUTPUT_DIR="${HYPATIAX_OUTPUT_DIR:-/tmp/hypatiax_outputs}"
        
        # Create outputs directory
        mkdir -p "$HYPATIAX_OUTPUT_DIR"
        
        # Try to persist to /etc/environment if writable
        if [ -w "/etc/environment" ]; then
            grep -q "HYPATIAX_ROOT" /etc/environment 2>/dev/null || \
                echo "HYPATIAX_ROOT=$PROJECT_ROOT" >> /etc/environment
            grep -q "PYTHONPATH.*$PROJECT_ROOT" /etc/environment 2>/dev/null || \
                echo "PYTHONPATH=$PROJECT_ROOT:\$PYTHONPATH" >> /etc/environment
        fi
        
        echo -e "${CHECK} Docker environment configured"
        echo "   Output directory: $HYPATIAX_OUTPUT_DIR"
        ;;
    
    # ========================================================================
    # CLOUD ENVIRONMENTS (AWS, GCP, Azure)
    # ========================================================================
    aws|gcp|azure)
        echo "Configuring cloud environment ($ENV_TYPE)..."
        
        export HYPATIAX_ROOT="$PROJECT_ROOT"
        export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
        export HYPATIAX_OUTPUT_DIR="${HYPATIAX_OUTPUT_DIR:-/tmp/hypatiax_outputs}"
        
        # Create outputs directory
        mkdir -p "$HYPATIAX_OUTPUT_DIR"
        
        echo -e "${CHECK} Cloud environment configured"
        echo "   Output directory: $HYPATIAX_OUTPUT_DIR"
        ;;
    
    # ========================================================================
    # LOCAL DEVELOPMENT
    # ========================================================================
    local|ci)
        echo "Configuring local development environment..."
        
        # Create .env file
        ENV_FILE="$PROJECT_ROOT/.env"
        echo -e "${INFO} Creating environment file: ${BLUE}$ENV_FILE${NC}"
        
        cat > "$ENV_FILE" << EOF
# HypatiaX Environment Configuration
# Auto-generated by setup_environment.sh on $(date)

# Project root directory
export HYPATIAX_ROOT="$PROJECT_ROOT"

# Python path (for importing hypatiax from anywhere)
export PYTHONPATH="\${HYPATIAX_ROOT}:\${PYTHONPATH}"

# Output directory for generated files
export HYPATIAX_OUTPUT_DIR="\${HYPATIAX_ROOT}/outputs"

# Optional: Add project bin to PATH
export PATH="\${HYPATIAX_ROOT}/bin:\${PATH}"

# Development environment flag
export HYPATIAX_ENV="local"

# Python settings
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
EOF
        
        echo -e "${CHECK} Environment file created"
        
        # Create activation script
        ACTIVATE_SCRIPT="$PROJECT_ROOT/activate_hypatiax.sh"
        echo -e "${INFO} Creating activation script: ${BLUE}$ACTIVATE_SCRIPT${NC}"
        
        cat > "$ACTIVATE_SCRIPT" << 'ACTIVATE_EOF'
#!/bin/bash
# Activate HypatiaX development environment
# Usage: source activate_hypatiax.sh

# Get script directory
if [ -n "${BASH_SOURCE[0]}" ]; then
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
else
    SCRIPT_DIR="$(pwd)"
fi

# Source environment file
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
    
    echo "✅ HypatiaX environment activated"
    echo ""
    echo "Configuration:"
    echo "  Project Root:  $HYPATIAX_ROOT"
    echo "  Python Path:   $PYTHONPATH"
    echo "  Output Dir:    $HYPATIAX_OUTPUT_DIR"
    echo ""
    echo "You can now run scripts from any location!"
    echo ""
    echo "Quick tests:"
    echo "  python -c 'from hypatiax.config import config; config.print_config()'"
    echo "  python -c 'import hypatiax; print(hypatiax.__file__)'"
    echo ""
else
    echo "❌ Error: .env file not found at $SCRIPT_DIR/.env"
    echo "   Run ./setup_environment.sh first"
    return 1
fi
ACTIVATE_EOF
        
        chmod +x "$ACTIVATE_SCRIPT"
        echo -e "${CHECK} Activation script created"
        
        # Create outputs directory
        OUTPUTS_DIR="$PROJECT_ROOT/outputs"
        mkdir -p "$OUTPUTS_DIR"
        echo -e "${CHECK} Outputs directory created: ${BLUE}$OUTPUTS_DIR${NC}"
        
        # Verify config.py exists
        CONFIG_FILE="$PROJECT_ROOT/hypatiax/config.py"
        if [ -f "$CONFIG_FILE" ]; then
            echo -e "${CHECK} config.py exists"
        else
            echo -e "${WARN} config.py not found at $CONFIG_FILE"
            echo "   The config module is required for path management"
        fi
        
        # Update .gitignore
        GITIGNORE="$PROJECT_ROOT/.gitignore"
        echo -e "${INFO} Updating .gitignore..."
        
        # Entries to add
        declare -a IGNORE_ENTRIES=(
            "outputs/"
            "ci_outputs/"
            "*.pyc"
            "__pycache__/"
            ".env"
            "*.egg-info/"
            ".pytest_cache/"
            ".coverage"
            "htmlcov/"
            "*.log"
            ".DS_Store"
            "*.swp"
            "*.swo"
            "*~"
        )
        
        # Create or update .gitignore
        touch "$GITIGNORE"
        for entry in "${IGNORE_ENTRIES[@]}"; do
            if ! grep -q "^${entry}$" "$GITIGNORE" 2>/dev/null; then
                echo "$entry" >> "$GITIGNORE"
            fi
        done
        
        echo -e "${CHECK} .gitignore configured"
        ;;
esac

echo ""

# ============================================================================
# PYTHON ENVIRONMENT VALIDATION
# ============================================================================

echo "Validating Python environment..."

# Check Python installation
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${CHECK} Python3 found: $PYTHON_VERSION"
    
    # Check Python version (require 3.8+)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        echo -e "${WARN} Python 3.8+ recommended (found $PYTHON_VERSION)"
    fi
else
    echo -e "${CROSS} Python3 not found in PATH"
fi

# Check if hypatiax is importable
if python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); import hypatiax" 2>/dev/null; then
    echo -e "${CHECK} hypatiax package is importable"
    
    # Try to get version
    HYPATIAX_VERSION=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); import hypatiax; print(getattr(hypatiax, '__version__', 'unknown'))" 2>/dev/null)
    if [ "$HYPATIAX_VERSION" != "unknown" ]; then
        echo "   Version: $HYPATIAX_VERSION"
    fi
else
    echo -e "${WARN} hypatiax package cannot be imported"
    echo "   This is normal if not yet installed"
fi

# Validate config module
echo ""
if python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from hypatiax.config import config; config.print_config()" 2>/dev/null; then
    : # Config printed successfully
else
    echo -e "${WARN} Config module validation failed"
    echo "   You may need to install dependencies or check config.py"
fi

echo ""

# ============================================================================
# COMPLETION MESSAGE
# ============================================================================

echo "=================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================="
echo ""

case $ENV_TYPE in
    github)
        echo "GitHub Actions environment is ready."
        echo "Environment variables have been set in GITHUB_ENV"
        ;;
    
    docker|aws|gcp|azure)
        echo "$ENV_TYPE environment is ready."
        echo "Environment variables are set for this session."
        echo ""
        echo "Verify with:"
        echo "  python -c 'from hypatiax.config import config; config.print_config()'"
        ;;
    
    local|ci)
        echo "Next steps for local development:"
        echo ""
        echo "1️⃣  Activate the environment:"
        echo -e "   ${BLUE}source activate_hypatiax.sh${NC}"
        echo ""
        echo "2️⃣  Or manually set environment variables:"
        echo "   export HYPATIAX_ROOT=\"$PROJECT_ROOT\""
        echo "   export PYTHONPATH=\"$PROJECT_ROOT:\$PYTHONPATH\""
        echo ""
        echo "3️⃣  Install dependencies (if not already done):"
        echo "   pip install -r requirements.txt"
        echo "   # or for development:"
        echo "   pip install -e ."
        echo ""
        echo "4️⃣  Verify configuration:"
        echo -e "   ${BLUE}python -c 'from hypatiax.config import config; config.print_config()'${NC}"
        echo ""
        echo "5️⃣  Run tests from any directory:"
        echo "   cd /any/directory"
        echo "   pytest \"$PROJECT_ROOT/tests/\""
        echo ""
        echo "6️⃣  Make permanent (optional):"
        echo "   echo 'source $ACTIVATE_SCRIPT' >> ~/.bashrc"
        echo "   # or for zsh:"
        echo "   echo 'source $ACTIVATE_SCRIPT' >> ~/.zshrc"
        ;;
esac

echo ""
echo "📚 Documentation: https://docs.hypatiax.io"
echo "🐛 Issues: https://github.com/yourorg/hypatiax/issues"
echo ""
