# Multi-stage Dockerfile for HypatiaX - Integrated Version
# Combines best practices from both versions
# Supports Python 3.12 (Stable) and 3.13 (Latest)
# Version: 3.0

# ==============================================================================
# BASE STAGE - Common dependencies for all Python versions
# ==============================================================================

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim as base

# Metadata
LABEL maintainer="HypatiaX Team"
LABEL description="HypatiaX - Advanced NLP and Agent System"
LABEL version="3.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DOCKER_CONTAINER=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /workspace/hypatiax

# ==============================================================================
# DEPENDENCIES STAGE - Install Python packages (cached separately)
# ==============================================================================

FROM base as dependencies

# Copy requirements files first (better caching)
# Using Python 3.12 requirements with security fixes
COPY requirements-py312.txt requirements.txt 2>/dev/null || \
     COPY requirements/requirements-py312.txt requirements.txt 2>/dev/null || \
     COPY requirements.txt requirements.txt

COPY requirements/ requirements/ 2>/dev/null || true

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies with security fixes applied
# Security fixes: torch>=2.5.1, transformers>=4.55.4, nltk>=3.9.1, notebook>=7.0.7, urllib3>=2.2.3
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy models if needed (uncomment as required)
# RUN python -m spacy download en_core_web_sm
# RUN python -m spacy download en_core_web_md

# ==============================================================================
# DEVELOPMENT STAGE - For local development with full tooling
# ==============================================================================

FROM dependencies as development

# Install additional dev tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    nano \
    tmux \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install development and security tools
RUN pip install --no-cache-dir \
    ipython \
    jupyter \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    ipdb \
    pip-audit \
    safety

# Copy entire project
COPY . .

# Set HypatiaX environment variables
ENV HYPATIAX_ROOT=/workspace/hypatiax \
    PYTHONPATH=/workspace/hypatiax:$PYTHONPATH \
    HYPATIAX_OUTPUT_DIR=/workspace/hypatiax/outputs \
    HYPATIAX_ENV=docker

# Run setup script
RUN chmod +x setup_environment.sh && \
    bash setup_environment.sh || echo "Setup script completed with warnings"

# Create output directories
RUN mkdir -p /workspace/hypatiax/outputs /tmp/hypatiax_outputs

# Validate installation
RUN python -c "from hypatiax.config import config; print('Config loaded successfully')" || \
    echo "Warning: Config validation failed"

# Expose ports for Jupyter and API
EXPOSE 8888 8000

# Default command for development (start bash)
CMD ["bash"]

# ==============================================================================
# TESTING STAGE - For CI/CD testing
# ==============================================================================

FROM development as testing

# Install additional test dependencies
RUN pip install --no-cache-dir \
    pytest-xdist \
    pytest-timeout \
    coverage[toml]

# Copy test configuration
COPY pytest.ini setup.cfg pyproject.toml ./ 2>/dev/null || true

# Set test environment
ENV HYPATIAX_ENV=testing \
    HYPATIAX_OUTPUT_DIR=/tmp/hypatiax_test_outputs

# Create test output directory
RUN mkdir -p /tmp/hypatiax_test_outputs

# Run tests by default
CMD ["pytest", "tests/", "-v", "--cov=hypatiax", "--cov-report=html", "--cov-report=term"]

# ==============================================================================
# PRODUCTION STAGE - Optimized for deployment
# ==============================================================================

FROM dependencies as production

# Copy only necessary application files
COPY hypatiax/ /workspace/hypatiax/hypatiax/
COPY setup.py pyproject.toml README.md ./ 2>/dev/null || true
COPY setup_environment.sh ./ 2>/dev/null || true

# Install package in production mode
RUN pip install --no-cache-dir -e . && \
    rm -rf ~/.cache/pip

# Run setup script if exists
RUN if [ -f setup_environment.sh ]; then \
    chmod +x setup_environment.sh && \
    bash setup_environment.sh || echo "Setup completed with warnings"; \
    fi

# Set production environment variables
ENV HYPATIAX_ROOT=/workspace/hypatiax \
    PYTHONPATH=/workspace/hypatiax:$PYTHONPATH \
    HYPATIAX_OUTPUT_DIR=/tmp/hypatiax_outputs \
    HYPATIAX_ENV=production

# Create necessary directories
RUN mkdir -p /tmp/hypatiax_outputs

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash hypatiax && \
    chown -R hypatiax:hypatiax /workspace/hypatiax /tmp/hypatiax_outputs

# Switch to non-root user
USER hypatiax

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "from hypatiax.config import config; import sys; sys.exit(0)" || exit 1

# Default production command
CMD ["python", "-m", "hypatiax"]

# ==============================================================================
# API STAGE - For serving HypatiaX as an API
# ==============================================================================

FROM production as api

# Switch back to root to install additional packages
USER root

# Install API framework
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic

# Copy API code if exists
COPY api/ /workspace/hypatiax/api/ 2>/dev/null || echo "No API directory found"

# Switch back to non-root user
USER hypatiax

# Expose API port
EXPOSE 8000

# Health check for API
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ==============================================================================
# NOTEBOOK STAGE - For Jupyter notebook server
# ==============================================================================

FROM development as notebook

# Expose Jupyter port
EXPOSE 8888

# Set working directory
WORKDIR /workspace/hypatiax

# Start Jupyter notebook
CMD ["jupyter", "notebook", \
     "--ip=0.0.0.0", \
     "--port=8888", \
     "--no-browser", \
     "--allow-root", \
     "--NotebookApp.token=''", \
     "--NotebookApp.password=''"]

# ==============================================================================
# BUILD & RUN INSTRUCTIONS
# ==============================================================================

# Build with specific Python version:
#   docker build --target development -t hypatiax:dev-py312 --build-arg PYTHON_VERSION=3.12 .
#   docker build --target development -t hypatiax:dev-py313 --build-arg PYTHON_VERSION=3.13 .
#
# Development (with volume mounting for live code updates):
#   docker run -v $(pwd):/workspace/hypatiax -it hypatiax:dev-py312 bash
#   docker run -v $(pwd):/workspace/hypatiax -p 8888:8888 -it hypatiax:dev-py312
#
# Testing (run all tests - both Python versions):
#   docker build --target testing -t hypatiax:test-py312 --build-arg PYTHON_VERSION=3.12 .
#   docker build --target testing -t hypatiax:test-py313 --build-arg PYTHON_VERSION=3.13 .
#   docker run hypatiax:test-py312
#   docker run hypatiax:test-py313
#
# Production (optimized, no dev tools):
#   docker build --target production -t hypatiax:prod --build-arg PYTHON_VERSION=3.12 .
#   docker run hypatiax:prod
#   docker run -v /host/data:/tmp/hypatiax_outputs hypatiax:prod
#
# API Server:
#   docker build --target api -t hypatiax:api --build-arg PYTHON_VERSION=3.12 .
#   docker run -p 8000:8000 hypatiax:api
#
# Jupyter Notebook:
#   docker build --target notebook -t hypatiax:notebook --build-arg PYTHON_VERSION=3.12 .
#   docker run -p 8888:8888 -v $(pwd):/workspace/hypatiax hypatiax:notebook
#
# Security scanning:
#   docker run hypatiax:dev-py312 pip-audit
#   docker run hypatiax:dev-py312 safety check
#
# With custom environment variables:
#   docker run -e HYPATIAX_OUTPUT_DIR=/data \
#              -v /host/path:/data \
#              hypatiax:prod
#
# Docker Compose usage (recommended - see docker-compose.yml):
#   docker-compose build
#   docker-compose run --rm hypatiax-py312
#   docker-compose run --rm hypatiax-test-py312
#   docker-compose run --rm hypatiax-test-py313
#   docker-compose up hypatiax-notebook