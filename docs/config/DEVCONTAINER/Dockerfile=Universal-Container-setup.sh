# Dockerfile for HypatiaX
# Works with universal configuration system

FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCKER_CONTAINER=1 \
    HYPATIAX_ROOT=/app \
    PYTHONPATH=/app \
    HYPATIAX_OUTPUT_DIR=/app/outputs

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f requirements-py312.txt ]; then \
        pip install --no-cache-dir -r requirements-py312.txt; \
    elif [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Copy project files
COPY . .

# Install package in editable mode
RUN pip install -e .

# Create outputs directory
RUN mkdir -p /app/outputs && chmod 777 /app/outputs

# Verify installation
RUN python -c "from hypatiax.config import config; config.print_config()" && \
    python -c "import hypatiax; print(f'HypatiaX {hypatiax.__version__} installed successfully')"

# Default command
CMD ["python", "-c", "from hypatiax.config import show_config; show_config()"]
