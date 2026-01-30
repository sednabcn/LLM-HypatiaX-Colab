# Multi-stage Dockerfile for HypatiaX
# Supports development and production deployments

# ==============================================================================
# BASE STAGE - Common dependencies
# ==============================================================================

FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DOCKER_CONTAINER=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# ==============================================================================
# DEPENDENCIES STAGE - Install Python packages
# ==============================================================================

FROM base as dependencies

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy models if needed
# RUN python -m spacy download en_core_web_sm

# ==============================================================================
# DEVELOPMENT STAGE - For local development
# ==============================================================================

FROM dependencies as development

# Copy entire project
COPY . .

# Set HypatiaX environment variables
ENV HYPATIAX_ROOT=/app \
    PYTHONPATH=/app:$PYTHONPATH \
    HYPATIAX_OUTPUT_DIR=/app/outputs \
    HYPATIAX_ENV=docker

# Run setup script
RUN chmod +x setup_environment.sh && ./setup_environment.sh

# Create outputs directory
RUN mkdir -p /app/outputs /tmp/hypatiax_outputs

# Validate installation
RUN python -c "from hypatiax.config import config; config.print_config()"

# Default command for development
CMD ["python", "-c", "from hypatiax.config import config; config.print_config(); print('\\nDevelopment container ready!')"]

# ==============================================================================
# PRODUCTION STAGE - Optimized for deployment
# ==============================================================================

FROM dependencies as production

# Copy only necessary files
COPY hypatiax/ /app/hypatiax/
COPY setup.py pyproject.toml README.md ./

# Install package
RUN pip install --no-cache-dir -e .

# Set production environment variables
ENV HYPATIAX_ROOT=/app \
    PYTHONPATH=/app:$PYTHONPATH \
    HYPATIAX_OUTPUT_DIR=/tmp/hypatiax_outputs \
    HYPATIAX_ENV=production

# Create necessary directories
RUN mkdir -p /tmp/hypatiax_outputs

# Run as non-root user
RUN useradd -m -u 1000 hypatiax && \
    chown -R hypatiax:hypatiax /app /tmp/hypatiax_outputs
USER hypatiax

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "from hypatiax.config import config" || exit 1

# Default production command
CMD ["python", "-m", "hypatiax"]

# ==============================================================================
# TESTING STAGE - For CI/CD
# ==============================================================================

FROM development as testing

# Install test dependencies
RUN pip install --no-cache-dir pytest pytest-cov

# Copy tests
COPY tests/ /app/tests/

# Run tests by default
CMD ["pytest", "tests/", "-v", "--cov=hypatiax"]

# ==============================================================================
# BUILD INSTRUCTIONS
# ==============================================================================

# Development:
#   docker build --target development -t hypatiax:dev .
#   docker run -v $(pwd):/app -it hypatiax:dev bash
#
# Production:
#   docker build --target production -t hypatiax:prod .
#   docker run hypatiax:prod
#
# Testing:
#   docker build --target testing -t hypatiax:test .
#   docker run hypatiax:test
#
# With custom output directory:
#   docker run -v /host/path:/data -e HYPATIAX_OUTPUT_DIR=/data hypatiax:prod
