#!/bin/bash
echo "=========================================="
echo "HypatiaX Multi-Python Setup Verification"
echo "=========================================="
echo ""

# Check root requirements files
echo "📋 Requirements Files:"
for file in requirements.txt requirements-py310.txt requirements-py311.txt; do
    if [ -f "$file" ]; then
        echo "  ✅ $file ($(wc -l < "$file") lines)"
    else
        echo "  ❌ $file MISSING"
    fi
done
echo ""

# Check devcontainer configs
echo "🐳 Devcontainer Configs:"
for file in .devcontainer/devcontainer.json .devcontainer/devcontainer-py311.json .devcontainer/devcontainer-py310-colab.json; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MISSING"
    fi
done
echo ""

# Check GitHub Actions
echo "⚙️  GitHub Actions:"
if [ -f ".github/workflows/ci-multi-python.yml" ]; then
    echo "  ✅ .github/workflows/ci-multi-python.yml"
else
    echo "  ❌ .github/workflows/ci-multi-python.yml MISSING"
fi
echo ""

# Check Docker files
echo "🐋 Docker Files:"
for file in Dockerfile docker-compose.yml; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MISSING"
    fi
done
echo ""

echo "=========================================="
echo "Verification Complete!"
echo "=========================================="
