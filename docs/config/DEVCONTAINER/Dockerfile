# Multi-stage Dockerfile for HypatiaX

# Stage 1: Python 3.10 (Colab-like)
FROM python:3.10-slim as py310
WORKDIR /app
COPY requirements-py310.txt .
RUN pip install --no-cache-dir -r requirements-py310.txt && \
    python -m spacy download en_core_web_sm
COPY . .
RUN pip install -e .

# Stage 2: Python 3.11 (Stable)
FROM python:3.11-slim as py311
WORKDIR /app
COPY requirements-py311.txt .
RUN pip install --no-cache-dir -r requirements-py311.txt && \
    python -m spacy download en_core_web_sm
COPY . .
RUN pip install -e .

# Stage 3: Python 3.13 (Latest)
FROM python:3.13-slim as py313
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm
COPY . .
RUN pip install -e .

# Default stage (Python 3.13)
FROM py313
CMD ["bash"]
