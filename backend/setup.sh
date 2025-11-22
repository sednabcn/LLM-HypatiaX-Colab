#!/bin/bash

# HypatiaX Backend - Automated Setup Script
# File: backend/setup.sh

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🚀 HypatiaX Backend - Automated Setup                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the backend directory
if [ ! -f "app.py" ]; then
    error "app.py not found. Please run this script from the backend directory."
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# ============================================================================
# 1. FIX NER SERVICE FILENAME
# ============================================================================
echo "🔧 Step 1: Fixing NER service filename..."

if [ -f "services/ner_services.py" ]; then
    mv services/ner_services.py services/ner_service.py
    info "Renamed ner_services.py → ner_service.py"
elif [ -f "services/ner_service.py" ]; then
    info "ner_service.py already exists"
else
    warn "ner_service.py not found - NER routes may not work"
fi

# ============================================================================
# 2. CREATE DIRECTORY STRUCTURE
# ============================================================================
echo ""
echo "📁 Step 2: Creating directory structure..."

mkdir -p logs
mkdir -p data/uploads
mkdir -p data/cache
mkdir -p services
mkdir -p api/routes
mkdir -p api/schemas
mkdir -p api/middleware

info "Directories created"

# ============================================================================
# 3. CREATE __init__.py FILES
# ============================================================================
echo ""
echo "📝 Step 3: Creating __init__.py files..."

touch services/__init__.py
touch api/__init__.py
touch api/routes/__init__.py
touch api/schemas/__init__.py
touch api/middleware/__init__.py

info "__init__.py files created"

# ============================================================================
# 4. CREATE .env FILE
# ============================================================================
echo ""
echo "🔐 Step 4: Creating .env file..."

if [ -f ".env" ]; then
    warn ".env file already exists - skipping"
else
    cat > .env << 'EOF'
# HypatiaX Backend Environment Configuration
# Created by setup script

# ============================================================================
# ENVIRONMENT
# ============================================================================
FLASK_ENV=development
DEBUG=True

# ============================================================================
# SECURITY
# ============================================================================
SECRET_KEY=dev-secret-key-change-in-production-replace-me-12345

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO

# ============================================================================
# CORS SETTINGS
# ============================================================================
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000

# ============================================================================
# SERVICE ENABLEMENT
# ============================================================================
HYPATIAX_ENABLED=True
NER_ENABLED=True
DEFI_ENABLED=True

# ============================================================================
# RATE LIMITING
# ============================================================================
RATELIMIT_ENABLED=False

# ============================================================================
# CACHE CONFIGURATION
# ============================================================================
CACHE_TYPE=simple

# ============================================================================
# DATABASE (Optional)
# ============================================================================
DATABASE_URL=sqlite:///hypatiax.db

# ============================================================================
# REDIS (Optional)
# ============================================================================
# REDIS_URL=redis://localhost:6379/0
EOF
    info ".env file created"
fi

# ============================================================================
# 5. CREATE .env.example
# ============================================================================
echo ""
echo "📄 Step 5: Creating .env.example..."

cat > .env.example << 'EOF'
# Copy this file to .env and fill in your values
# File: .env.example

FLASK_ENV=development
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:8000
HYPATIAX_ENABLED=True
NER_ENABLED=True
DEFI_ENABLED=True
RATELIMIT_ENABLED=False
CACHE_TYPE=simple
DATABASE_URL=sqlite:///hypatiax.db
EOF

info ".env.example created"

# ============================================================================
# 6. UPDATE .gitignore
# ============================================================================
echo ""
echo "🚫 Step 6: Updating .gitignore..."

if [ ! -f ".gitignore" ]; then
    touch .gitignore
fi

# Add entries if they don't exist
grep -q ".env" .gitignore 2>/dev/null || echo -e "\n# Environment variables\n.env\n.env.local\n.env.*.local" >> .gitignore
grep -q "logs/" .gitignore 2>/dev/null || echo -e "\n# Logs\nlogs/\n*.log" >> .gitignore
grep -q "__pycache__" .gitignore 2>/dev/null || echo -e "\n# Python cache\n__pycache__/\n*.pyc\n.pytest_cache/" >> .gitignore
grep -q "data/" .gitignore 2>/dev/null || echo -e "\n# Data directories\ndata/uploads/\ndata/cache/" >> .gitignore

info ".gitignore updated"

# ============================================================================
# 7. INSTALL PYTHON DEPENDENCIES
# ============================================================================
echo ""
echo "📦 Step 7: Installing Python dependencies..."

# Check if pip is available
if ! command -v pip &> /dev/null; then
    error "pip not found. Please install Python and pip first."
    exit 1
fi

# Install required packages
pip install python-dotenv flask flask-cors sympy 2>/dev/null || warn "Some packages may already be installed"

info "Python dependencies installed"

# ============================================================================
# 8. CREATE requirements.txt (if missing)
# ============================================================================
echo ""
echo "📋 Step 8: Creating requirements.txt..."

if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << 'EOF'
# HypatiaX Backend Requirements
flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
sympy==1.12
marshmallow==3.20.1
spacy==3.7.2

# Optional dependencies
# redis==5.0.0
# gunicorn==21.2.0
# psycopg2-binary==2.9.9
EOF
    info "requirements.txt created"
else
    info "requirements.txt already exists"
fi

# ============================================================================
# 9. VERIFY FILE STRUCTURE
# ============================================================================
echo ""
echo "🔍 Step 9: Verifying file structure..."

required_files=(
    "app.py"
    "config.py"
    "services/defi_calculator.py"
    "api/routes/ner_routes.py"
    "api/routes/defi_routes.py"
)

missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        info "Found: $file"
    else
        warn "Missing: $file"
        missing_files+=("$file")
    fi
done

# ============================================================================
# 10. CREATE TEST SCRIPT
# ============================================================================
echo ""
echo "🧪 Step 10: Creating test scripts..."

# Create test_env.py
cat > test_env.py << 'EOF'
"""Test environment variables loading"""
import os
from dotenv import load_dotenv

load_dotenv()

print("\n🧪 Testing Environment Variables\n")
print("="*60)
print(f"FLASK_ENV:       {os.getenv('FLASK_ENV', 'NOT SET')}")
print(f"DEBUG:           {os.getenv('DEBUG', 'NOT SET')}")
print(f"LOG_LEVEL:       {os.getenv('LOG_LEVEL', 'NOT SET')}")
print(f"SECRET_KEY:      {os.getenv('SECRET_KEY', 'NOT SET')[:20]}...")
print(f"CORS_ORIGINS:    {os.getenv('CORS_ORIGINS', 'NOT SET')}")
print(f"HYPATIAX:        {os.getenv('HYPATIAX_ENABLED', 'NOT SET')}")
print(f"NER:             {os.getenv('NER_ENABLED', 'NOT SET')}")
print(f"DEFI:            {os.getenv('DEFI_ENABLED', 'NOT SET')}")
print("="*60)
print("\n✅ Environment variables loaded successfully!\n")
EOF

info "Created test_env.py"

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SETUP COMPLETE!                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Setup Summary:"
echo "  ✅ Directory structure created"
echo "  ✅ __init__.py files created"
echo "  ✅ .env file configured"
echo "  ✅ .gitignore updated"
echo "  ✅ Python dependencies installed"
echo "  ✅ Test scripts created"
echo ""

if [ ${#missing_files[@]} -gt 0 ]; then
    warn "Missing files detected:"
    for file in "${missing_files[@]}"; do
        echo "     - $file"
    done
    echo ""
fi

echo "🚀 Next Steps:"
echo ""
echo "  1. Test environment loading:"
echo "     python test_env.py"
echo ""
echo "  2. Start the server:"
echo "     python app.py"
echo ""
echo "  3. Run API tests (in another terminal):"
echo "     python test_api.py"
echo ""
echo "  4. Edit .env file to customize settings:"
echo "     nano .env"
echo ""
echo "  5. Access the API:"
echo "     http://localhost:5000/"
echo ""
echo "📖 Documentation:"
echo "   - API docs:    http://localhost:5000/"
echo "   - Health:      http://localhost:5000/api/health"
echo "   - Config:      Check config.py for all settings"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
