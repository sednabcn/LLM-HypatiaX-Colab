# 🔧 Environment Variables Setup Guide

## 📍 Where to Set Environment Variables

You have **4 main options** for setting environment variables:

---

## Option 1: `.env` File (RECOMMENDED) ⭐

Create a `.env` file in your backend directory:

```bash
cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/backend/
touch .env
```

### **File: `backend/.env`**

```bash
# Environment
FLASK_ENV=development

# App Settings
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production

# Logging
LOG_LEVEL=INFO

# CORS Settings
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000

# Database (if using)
DATABASE_URL=sqlite:///hypatiax.db

# Redis (if using)
REDIS_URL=redis://localhost:6379/0

# Feature Flags
HYPATIAX_ENABLED=True
NER_ENABLED=True
DEFI_ENABLED=True
```

### **Load .env in your app:**

Install python-dotenv:

```bash
pip install python-dotenv
```

Update your `app.py` (add at the top):

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Now all your os.getenv() calls will work
```

### **Important: Add .env to .gitignore**

```bash
echo ".env" >> .gitignore
```

---

## Option 2: Shell Terminal (Temporary)

Set variables in your current terminal session:

```bash
# These expire when you close the terminal

# Basic setup
export FLASK_ENV=development
export DEBUG=True
export LOG_LEVEL=INFO
export SECRET_KEY=my-secret-key

# CORS
export CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Then run your app
python app.py
```

**One-liner before running:**

```bash
FLASK_ENV=development DEBUG=True LOG_LEVEL=INFO python app.py
```

---

## Option 3: Shell Profile (Permanent)

Add to your shell configuration file (survives terminal restarts):

### **For Bash (`.bashrc` or `.bash_profile`):**

```bash
# Edit your bash profile
nano ~/.bashrc

# Add these lines at the end:
export FLASK_ENV=development
export DEBUG=True
export LOG_LEVEL=INFO
export SECRET_KEY=my-secret-key

# Save and reload
source ~/.bashrc
```

### **For Zsh (`.zshrc`):**

```bash
# Edit your zsh profile
nano ~/.zshrc

# Add the same exports
export FLASK_ENV=development
export DEBUG=True

# Save and reload
source ~/.zshrc
```

---

## Option 4: Systemd Service File (Production Linux)

For production servers running as a service:

### **File: `/etc/systemd/system/hypatiax.service`**

```ini
[Unit]
Description=HypatiaX API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/hypatiax/backend
Environment="FLASK_ENV=production"
Environment="DEBUG=False"
Environment="LOG_LEVEL=WARNING"
Environment="SECRET_KEY=your-production-secret-key"
Environment="CORS_ORIGINS=https://yourdomain.com"
ExecStart=/var/www/hypatiax/venv/bin/python app.py

[Install]
WantedBy=multi-user.target
```

```bash
# Reload systemd
sudo systemctl daemon-reload
sudo systemctl enable hypatiax
sudo systemctl start hypatiax
```

---

## 🎯 RECOMMENDED Setup for Your Project

### **Step 1: Create `.env` file**

```bash
cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/backend/
cat > .env << 'EOF'
# Development Environment Configuration
FLASK_ENV=development
DEBUG=True
LOG_LEVEL=INFO

# Security (change in production!)
SECRET_KEY=dev-secret-key-change-in-production-12345

# CORS - Allow your frontend
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000

# Services
HYPATIAX_ENABLED=True
NER_ENABLED=True
DEFI_ENABLED=True

# Rate Limiting
RATELIMIT_ENABLED=False

# Cache
CACHE_TYPE=simple

# Database (optional)
DATABASE_URL=sqlite:///hypatiax.db
EOF
```

### **Step 2: Install python-dotenv**

```bash
pip install python-dotenv
```

### **Step 3: Update your `app.py`**

Add these lines at the very top of your `app.py`:

```python
"""
Unified Backend API - HypatiaX + DeFi + NER
File: backend/app.py
Version: 2.1.0
"""

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()  # This loads .env file

import os
import sys
import time
import logging
# ... rest of your imports
```

### **Step 4: Update `.gitignore`**

```bash
# Add to .gitignore
cat >> .gitignore << 'EOF'

# Environment variables
.env
.env.local
.env.*.local

# Logs
logs/
*.log

# Cache
__pycache__/
*.pyc
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
EOF
```

### **Step 5: Create `.env.example` (for team)**

```bash
cat > .env.example << 'EOF'
# Copy this to .env and fill in your values
FLASK_ENV=development
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:8000
HYPATIAX_ENABLED=True
NER_ENABLED=True
DEFI_ENABLED=True
EOF
```

---

## 🔐 Production Environment Variables

For production, create a separate `.env.production` file:

```bash
# File: backend/.env.production
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=WARNING

# Use strong secret key!
SECRET_KEY=your-super-strong-secret-key-generated-randomly

# Your production domain
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Enable security features
RATELIMIT_ENABLED=True

# Production cache (if using Redis)
CACHE_TYPE=redis
REDIS_URL=redis://your-redis-server:6379/0

# Production database
DATABASE_URL=postgresql://user:password@localhost:5432/hypatiax
```

Load it with:

```bash
python app.py --env production
# Or
FLASK_ENV=production python app.py
```

---

## 📋 Complete Setup Script

Create a setup script to do everything:

### **File: `backend/setup_env.sh`**

```bash
#!/bin/bash

echo "🔧 Setting up HypatiaX Backend Environment"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
FLASK_ENV=development
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
HYPATIAX_ENABLED=True
NER_ENABLED=True
DEFI_ENABLED=True
RATELIMIT_ENABLED=False
CACHE_TYPE=simple
EOF
    echo "✅ .env file created"
else
    echo "ℹ️  .env file already exists"
fi

# Install python-dotenv
echo "📦 Installing python-dotenv..."
pip install python-dotenv

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/uploads
mkdir -p data/cache

# Add .env to .gitignore
if ! grep -q ".env" .gitignore 2>/dev/null; then
    echo "📝 Adding .env to .gitignore..."
    echo -e "\n# Environment variables\n.env\n.env.local" >> .gitignore
fi

echo "✅ Environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your settings"
echo "2. Run: python app.py"
```

Make it executable and run:

```bash
chmod +x setup_env.sh
./setup_env.sh
```

---

## 🧪 Testing Your Environment

### **Quick test script: `test_env.py`**

```python
import os
from dotenv import load_dotenv

load_dotenv()

print("🧪 Testing Environment Variables\n")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
print(f"DEBUG: {os.getenv('DEBUG')}")
print(f"LOG_LEVEL: {os.getenv('LOG_LEVEL')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')[:10]}...")
print(f"CORS_ORIGINS: {os.getenv('CORS_ORIGINS')}")
print("\n✅ Environment variables loaded successfully!")
```

Run it:

```bash
python test_env.py
```

---

## 🎯 Summary

| Method | When to Use | Persistence |
|--------|-------------|-------------|
| **`.env` file** | ⭐ Development (BEST) | Per project |
| Shell export | Quick testing | Current session |
| Shell profile | Personal dev setup | All sessions |
| Systemd | Production Linux | System-wide |

**RECOMMENDED FOR YOU:**

1. Create `.env` file in `backend/` directory
2. Install `python-dotenv`
3. Add `load_dotenv()` to top of `app.py`
4. Add `.env` to `.gitignore`

Done! 🚀
