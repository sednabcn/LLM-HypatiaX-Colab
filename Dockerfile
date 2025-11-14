# Multi-stage Dockerfile for HypatiaX - Integrated Version
# Supports Python 3.12 (Stable) and 3.13 (Latest)
# Version: 3.0

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim as base

LABEL maintainer="HypatiaX Team"
LABEL description="HypatiaX - Advanced NLP and Agent System"
LABEL version="3.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DOCKER_CONTAINER=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/hypatiax

# ==============================================================================
# DEPENDENCIES STAGE
# ==============================================================================

FROM base as dependencies

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# DEVELOPMENT STAGE
# ==============================================================================

FROM dependencies as development

RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    nano \
    tmux \
    htop \
    && rm -rf /var/lib/apt/lists/*

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

COPY . .

ENV HYPATIAX_ROOT=/workspace/hypatiax \
    PYTHONPATH=/workspace/hypatiax:$PYTHONPATH \
    HYPATIAX_OUTPUT_DIR=/workspace/hypatiax/outputs \
    HYPATIAX_ENV=docker

RUN if [ -f setup_environment.sh ]; then \
    chmod +x setup_environment.sh && \
    bash setup_environment.sh || echo Setup completed with warnings; \
    fi

RUN mkdir -p /workspace/hypatiax/outputs /tmp/hypatiax_outputs

RUN python -c "from hypatiax.config import config; print('Config loaded successfully')" || \
    echo Config validation skipped

EXPOSE 8888 8000

CMD ["bash"]

# ==============================================================================
# TESTING STAGE
# ==============================================================================

FROM development as testing

RUN pip install --no-cache-dir \
    pytest-xdist \
    pytest-timeout \
    coverage[toml]

ENV HYPATIAX_ENV=testing \
    HYPATIAX_OUTPUT_DIR=/tmp/hypatiax_test_outputs

RUN mkdir -p /tmp/hypatiax_test_outputs

CMD ["pytest", "tests/", "-v", "--cov=hypatiax", "--cov-report=html", "--cov-report=term"]

# ==============================================================================
# PRODUCTION STAGE
# ==============================================================================

FROM dependencies as production

COPY hypatiax/ /workspace/hypatiax/hypatiax/

RUN pip install --no-cache-dir -e . && \
    rm -rf ~/.cache/pip

ENV HYPATIAX_ROOT=/workspace/hypatiax \
    PYTHONPATH=/workspace/hypatiax:$PYTHONPATH \
    HYPATIAX_OUTPUT_DIR=/tmp/hypatiax_outputs \
    HYPATIAX_ENV=production

RUN mkdir -p /tmp/hypatiax_outputs

RUN useradd -m -u 1000 -s /bin/bash hypatiax && \
    chown -R hypatiax:hypatiax /workspace/hypatiax /tmp/hypatiax_outputs

USER hypatiax

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "from hypatiax.config import config; import sys; sys.exit(0)" || exit 1

CMD ["python", "-m", "hypatiax"]

# ==============================================================================
# API STAGE
# ==============================================================================

FROM production as api

USER root

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic

USER hypatiax

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ==============================================================================
# NOTEBOOK STAGE
# ==============================================================================

FROM development as notebook

EXPOSE 8888

WORKDIR /workspace/hypatiax

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=", "--NotebookApp.password="]