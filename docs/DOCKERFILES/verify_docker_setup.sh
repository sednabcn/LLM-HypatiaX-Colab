#!/bin/bash
# HypatiaX Docker Setup Verification Script
# Run this to verify your Docker setup is correct

set -e  # Exit on error

echo "================================================"
echo "HypatiaX Docker Setup Verification"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if we're in the repo root
echo "1. Checking repository structure..."
if [ ! -d ".git" ]; then
    print_warning "Not in git repository root. Make sure you're in ~/LLM-HypatiaX-Colab/"
    echo "   Current directory: $(pwd)"
else
    print_status 0 "In git repository root"
fi

# Check for Dockerfile.sh at root
echo ""
echo "2. Checking for Dockerfile.sh at repo root..."
if [ -f "Dockerfile.sh" ]; then
    print_status 0 "Dockerfile.sh found at repo root"
    # Check if it's the integrated version
    if grep -q "Version: 3.0" Dockerfile.sh; then
        print_status 0 "Using integrated Dockerfile version 3.0"
    elif grep -q "Version: 2.0" Dockerfile.sh; then
        print_warning "Dockerfile is version 2.0, consider upgrading to integrated 3.0"
    else
        print_warning "Dockerfile version unclear, verify it's the latest"
    fi
else
    print_status 1 "Dockerfile.sh NOT found at repo root"
    echo "   Expected location: $(pwd)/Dockerfile.sh"
fi

# Check for docker-compose.yml
echo ""
echo "3. Checking for docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    print_status 0 "docker-compose.yml found"
    # Check if it references Dockerfile.sh
    if grep -q "dockerfile: Dockerfile.sh" docker-compose.yml; then
        print_status 0 "docker-compose.yml correctly references Dockerfile.sh"
    else
        print_warning "docker-compose.yml may not be using Dockerfile.sh"
    fi
else
    print_status 1 "docker-compose.yml NOT found"
fi

# Check for requirements.txt
echo ""
echo "4. Checking for requirements.txt..."
if [ -f "requirements.txt" ]; then
    print_status 0 "requirements.txt found"
    echo "   $(wc -l < requirements.txt) packages listed"
else
    print_status 1 "requirements.txt NOT found"
fi

# Check for key directories
echo ""
echo "5. Checking project structure..."
if [ -d "hypatiax" ]; then
    print_status 0 "hypatiax/ directory exists"
else
    print_status 1 "hypatiax/ directory NOT found"
fi

if [ -d "tests" ]; then
    print_status 0 "tests/ directory exists"
else
    print_warning "tests/ directory not found"
fi

# Check for setup script
echo ""
echo "6. Checking for setup_environment.sh..."
if [ -f "setup_environment.sh" ]; then
    print_status 0 "setup_environment.sh found"
    if [ -x "setup_environment.sh" ]; then
        print_status 0 "setup_environment.sh is executable"
    else
        print_warning "setup_environment.sh is not executable (chmod +x setup_environment.sh)"
    fi
else
    print_warning "setup_environment.sh not found (optional)"
fi

# Check Docker installation
echo ""
echo "7. Checking Docker installation..."
if command -v docker &> /dev/null; then
    print_status 0 "Docker is installed"
    echo "   Version: $(docker --version)"
else
    print_status 1 "Docker is NOT installed"
fi

if command -v docker-compose &> /dev/null; then
    print_status 0 "docker-compose is installed"
    echo "   Version: $(docker-compose --version)"
else
    print_status 1 "docker-compose is NOT installed"
fi

# Check Docker daemon
echo ""
echo "8. Checking Docker daemon..."
if docker info &> /dev/null; then
    print_status 0 "Docker daemon is running"
else
    print_status 1 "Docker daemon is NOT running"
    echo "   Try: sudo systemctl start docker"
fi

# Check for local virtual environments
echo ""
echo "9. Checking local virtual environments..."
if [ -d "$HOME/Downloads/py312" ]; then
    print_status 0 "Local py312 venv found at ~/Downloads/py312"
else
    print_warning "Local py312 venv not found at ~/Downloads/py312"
fi

if [ -d "$HOME/Downloads/py313" ]; then
    print_status 0 "Local py313 venv found at ~/Downloads/py313"
else
    print_warning "Local py313 venv not found at ~/Downloads/py313"
fi

# Check .gitignore
echo ""
echo "10. Checking .gitignore..."
if [ -f ".gitignore" ]; then
    print_status 0 ".gitignore exists"
    
    # Check for important entries
    if grep -q "test-results/" .gitignore 2>/dev/null; then
        print_status 0 ".gitignore contains test-results/"
    else
        print_warning ".gitignore missing: test-results/"
    fi
    
    if grep -q "htmlcov/" .gitignore 2>/dev/null; then
        print_status 0 ".gitignore contains htmlcov/"
    else
        print_warning ".gitignore missing: htmlcov/"
    fi
    
    if grep -q "__pycache__/" .gitignore 2>/dev/null; then
        print_status 0 ".gitignore contains __pycache__/"
    else
        print_warning ".gitignore missing: __pycache__/"
    fi
else
    print_warning ".gitignore not found"
fi

# Summary
echo ""
echo "================================================"
echo "Summary"
echo "================================================"

# Try to build (dry run check)
echo ""
echo "11. Testing docker-compose configuration..."
if [ -f "docker-compose.yml" ] && [ -f "Dockerfile.sh" ]; then
    if docker-compose config > /dev/null 2>&1; then
        print_status 0 "docker-compose.yml syntax is valid"
    else
        print_status 1 "docker-compose.yml has syntax errors"
        echo "   Run: docker-compose config"
    fi
else
    print_warning "Cannot test docker-compose config (missing files)"
fi

echo ""
echo "================================================"
echo "Next Steps:"
echo "================================================"
echo ""
echo "If all checks passed, you can:"
echo "  1. Build images:       docker-compose build"
echo "  2. Run tests:          docker-compose run --rm hypatiax-test-py312"
echo "  3. Start development:  docker-compose run --rm hypatiax-py312"
echo ""
echo "If there were warnings:"
echo "  - Review the items marked with ⚠"
echo "  - Fix any missing files or configurations"
echo "  - Re-run this script to verify"
echo ""
echo "For detailed help, see the Quick Start Guide"
echo "================================================"
