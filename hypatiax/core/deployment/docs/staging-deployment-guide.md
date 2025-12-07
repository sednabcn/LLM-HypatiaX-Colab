# HypatiaX Staging Deployment Guide

## Week 3: Real System Integration & Testing

**Target:** Production-ready staging environment with comprehensive monitoring
**Timeline:** Week 3 (7 days)
**Success Criteria:** 99.9% uptime, < 500ms latency, 1,000+ operation load tests passing

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Day-by-Day Deployment Plan](#day-by-day-deployment-plan)
4. [Monitoring & Observability](#monitoring--observability)
5. [Testing Procedures](#testing-procedures)
6. [Rollback Procedures](#rollback-procedures)
7. [Post-Deployment Validation](#post-deployment-validation)

---

## Pre-Deployment Checklist

### ✅ Critical Requirements (Must Complete Before Deploy)

#### 1. Code Readiness

- [ ] All Week 2 critical fixes merged to `main` branch
- [ ] Edge case detection implemented and tested
- [ ] Ensemble validator calibrated (threshold: 85.0)
- [ ] Real LLM integration tested locally
- [ ] All unit tests passing (300+ tests)
- [ ] Integration tests passing (100+ tests)
- [ ] Code review completed and approved

#### 2. Infrastructure Requirements

- [ ] Staging environment provisioned (AWS/GCP/Azure)
- [ ] Database instances deployed (PostgreSQL/MongoDB)
- [ ] Redis cache configured
- [ ] Load balancer configured
- [ ] SSL certificates installed
- [ ] Domain/subdomain configured (staging.hypatiax.ai)

#### 3. API Credentials

- [ ] Anthropic API key (Tier 2+) validated
- [ ] Google Gemini API key validated
- [ ] API keys stored in secrets manager (AWS Secrets Manager/Vault)
- [ ] Rate limits confirmed (Anthropic: 50/min, Gemini: 60/min)
- [ ] Billing alerts configured

#### 4. Monitoring Setup

- [ ] Application logging configured (CloudWatch/Stackdriver)
- [ ] Error tracking enabled (Sentry/Rollbar)
- [ ] Performance monitoring (DataDog/New Relic)
- [ ] Uptime monitoring (Pingdom/UptimeRobot)
- [ ] Alert rules configured (PagerDuty/OpsGenie)

#### 5. Documentation

- [ ] Deployment runbook created
- [ ] Architecture diagrams updated
- [ ] API documentation published
- [ ] Rollback procedures documented
- [ ] Incident response plan ready

---

## Infrastructure Setup

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (NGINX)                   │
│                  (staging.hypatiax.ai)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
│  App Server  │    │ App Server  │    │ App Server  │
│   (Django)   │    │  (Django)   │    │  (Django)   │
│  Gunicorn    │    │  Gunicorn   │    │  Gunicorn   │
└───────┬──────┘    └──────┬──────┘    └──────┬──────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼──────┐                        ┌──────▼──────┐
│  PostgreSQL  │                        │    Redis    │
│  (Primary)   │                        │   (Cache)   │
└──────────────┘                        └─────────────┘
        │
┌───────▼──────┐
│  PostgreSQL  │
│  (Replica)   │
└──────────────┘

External Services:
├─ Anthropic Claude API
├─ Google Gemini API
├─ Sentry (Error Tracking)
└─ DataDog (Monitoring)
```

### Infrastructure as Code (Terraform)

```hcl
# terraform/staging/main.tf

provider "aws" {
  region = "us-east-1"
}

# VPC and Networking
resource "aws_vpc" "staging" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "hypatiax-staging-vpc"
    Environment = "staging"
  }
}

# Application Servers (EC2 Auto Scaling)
resource "aws_autoscaling_group" "app_servers" {
  name                 = "hypatiax-staging-asg"
  vpc_zone_identifier  = [aws_subnet.private.*.id]
  min_size             = 2
  max_size             = 6
  desired_capacity     = 3

  launch_template {
    id      = aws_launch_template.app_server.id
    version = "$Latest"
  }

  health_check_type = "ELB"
  health_check_grace_period = 300

  tag {
    key                 = "Name"
    value               = "hypatiax-staging-app"
    propagate_at_launch = true
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier           = "hypatiax-staging-db"
  engine               = "postgres"
  engine_version       = "14.7"
  instance_class       = "db.t3.medium"
  allocated_storage    = 100
  storage_encrypted    = true

  db_name  = "hypatiax_staging"
  username = "hypatiax_admin"
  password = var.db_password

  multi_az               = true
  backup_retention_period = 7

  tags = {
    Environment = "staging"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "hypatiax-staging-cache"
  engine               = "redis"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "hypatiax-staging-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public.*.id

  enable_deletion_protection = false

  tags = {
    Environment = "staging"
  }
}

# Secrets Manager for API Keys
resource "aws_secretsmanager_secret" "api_keys" {
  name = "hypatiax-staging-api-keys"

  tags = {
    Environment = "staging"
  }
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id
  secret_string = jsonencode({
    ANTHROPIC_API_KEY = var.anthropic_api_key
    GEMINI_API_KEY    = var.gemini_api_key
  })
}
```

### Docker Configuration

```dockerfile
# Dockerfile (production-ready)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install hypatiax in production mode
RUN pip install --no-cache-dir .

# Create non-root user
RUN useradd -m -u 1000 hypatiax && \
    chown -R hypatiax:hypatiax /app
USER hypatiax

# Environment
ENV PYTHONUNBUFFERED=1
ENV HYPATIAX_ENV=staging

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "hypatiax.wsgi:application"]
```

### Docker Compose (Local Staging Simulation)

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  app:
    build: .
    image: hypatiax:staging
    ports:
      - "8000:8000"
    environment:
      - HYPATIAX_ENV=staging
      - DATABASE_URL=postgresql://hypatiax:password@db:5432/hypatiax_staging
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env.staging
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    command: gunicorn --bind 0.0.0.0:8000 --workers 4 hypatiax.wsgi:application

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=hypatiax_staging
      - POSTGRES_USER=hypatiax
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/staging.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

---

## Day-by-Day Deployment Plan

### **Day 1: Infrastructure & Initial Deployment**

#### Morning (9 AM - 12 PM)

**9:00 AM - Infrastructure Provisioning**

```bash
# 1. Provision infrastructure with Terraform
cd terraform/staging
terraform init
terraform plan -out=staging.tfplan
terraform apply staging.tfplan

# 2. Verify infrastructure
terraform output

# 3. Note down critical IPs and endpoints
export STAGING_LB_DNS=$(terraform output -raw load_balancer_dns)
export STAGING_DB_ENDPOINT=$(terraform output -raw database_endpoint)
export STAGING_REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)
```

**10:00 AM - Database Setup**

```bash
# 1. Connect to database
psql -h $STAGING_DB_ENDPOINT -U hypatiax_admin -d hypatiax_staging

# 2. Run migrations
python manage.py migrate --database=staging

# 3. Create initial admin user
python manage.py createsuperuser --database=staging

# 4. Seed test data
python scripts/seed_staging_data.py
```

**11:00 AM - Application Deployment**

```bash
# 1. Build Docker image
docker build -t hypatiax:staging-v1.0 .

# 2. Push to container registry
docker tag hypatiax:staging-v1.0 $ECR_REPO/hypatiax:staging-v1.0
docker push $ECR_REPO/hypatiax:staging-v1.0

# 3. Deploy to ECS/Kubernetes
kubectl apply -f k8s/staging/deployment.yaml
kubectl apply -f k8s/staging/service.yaml
kubectl apply -f k8s/staging/ingress.yaml

# 4. Verify deployment
kubectl get pods -n staging
kubectl logs -f deployment/hypatiax-staging -n staging
```

#### Afternoon (1 PM - 5 PM)

**1:00 PM - Health Check Verification**

```bash
# 1. Basic health endpoint
curl https://staging.hypatiax.ai/health
# Expected: {"status": "healthy", "version": "2.0", "timestamp": "..."}

# 2. Database connectivity
curl https://staging.hypatiax.ai/health/db
# Expected: {"database": "connected", "latency_ms": 5}

# 3. Redis connectivity
curl https://staging.hypatiax.ai/health/cache
# Expected: {"cache": "connected", "latency_ms": 2}

# 4. API integrations
curl https://staging.hypatiax.ai/health/apis
# Expected: {
#   "anthropic": "available",
#   "gemini": "available",
#   "fallback": "enabled"
# }
```

**2:00 PM - Smoke Tests**

```bash
# Run critical path smoke tests
pytest tests/smoke/ -v --base-url=https://staging.hypatiax.ai

# Expected output:
# tests/smoke/test_discovery.py::test_basic_discovery PASSED
# tests/smoke/test_validation.py::test_basic_validation PASSED
# tests/smoke/test_llm_integration.py::test_anthropic PASSED
# tests/smoke/test_llm_integration.py::test_gemini PASSED
# tests/smoke/test_end_to_end.py::test_defi_workflow PASSED
# ==================== 5 passed in 12.34s ====================
```

**3:00 PM - Monitoring Setup**

```bash
# 1. Configure DataDog agent
kubectl create secret generic datadog-api-key \
  --from-literal=api-key=$DATADOG_API_KEY \
  -n staging

kubectl apply -f k8s/staging/datadog-agent.yaml

# 2. Configure Sentry
export SENTRY_DSN="https://...@sentry.io/..."
kubectl create secret generic sentry-dsn \
  --from-literal=dsn=$SENTRY_DSN \
  -n staging

# 3. Verify monitoring
curl https://api.datadoghq.com/api/v1/validate?api_key=$DATADOG_API_KEY

# 4. Test error tracking
python scripts/test_sentry_integration.py
```

**4:00 PM - Day 1 Checkpoint**

```bash
# Run Day 1 checkpoint script
./scripts/day1_checkpoint.sh

# Checklist:
# [x] Infrastructure deployed
# [x] Application running (3 instances)
# [x] Health checks passing
# [x] Monitoring active
# [x] Smoke tests passing
# [ ] Load tests (Day 2)
# [ ] Integration tests (Day 2)
```

---

### **Day 2: Integration Testing**

#### Morning (9 AM - 12 PM)

**9:00 AM - Real LLM Integration Tests**

```bash
# Set API keys in environment
export ANTHROPIC_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id hypatiax-staging-api-keys \
  --query SecretString --output text | jq -r .ANTHROPIC_API_KEY)

export GEMINI_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id hypatiax-staging-api-keys \
  --query SecretString --output text | jq -r .GEMINI_API_KEY)

# Run LLM integration tests against staging
pytest tests/integration/test_real_llm_integration.py \
  -v \
  --base-url=https://staging.hypatiax.ai \
  --run-integration

# Expected: 100+ tests passing
# Anthropic tests: 50+ passed
# Gemini tests: 50+ passed
# Fallback tests: 20+ passed
```

**10:00 AM - End-to-End Workflows**

```bash
# Run E2E tests for all domains
pytest tests/integration/test_hybrid_system_e2e.py \
  -v \
  --base-url=https://staging.hypatiax.ai \
  --run-integration

# Expected workflows:
# - DeFi IL calculation: PASSED
# - Physics formula discovery: PASSED
# - Chemistry rate equations: PASSED
# - Multi-provider fallback: PASSED
# - Error recovery: PASSED
```

**11:00 AM - Data Validation**

```bash
# Test with production-like data
python scripts/test_with_real_data.py \
  --environment=staging \
  --dataset=defi_production_sample \
  --runs=100

# Verify results
# Success rate: >= 95%
# Average latency: < 6.5s
# Validation pass rate: >= 90%
```

#### Afternoon (1 PM - 5 PM)

**1:00 PM - Load Testing Preparation**

```bash
# Install load testing tools
pip install locust pytest-xdist

# Configure load test
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class HypatiaXUser(HttpUser):
    wait_time = between(1, 3)
    host = "https://staging.hypatiax.ai"

    @task(3)
    def discover_formula(self):
        self.client.post("/api/v1/discover", json={
            "X": [[1.5, 0.03], [2.0, 0.05]],
            "y": [0.15, 0.25],
            "variable_names": ["r", "φ"],
            "domain": "defi"
        })

    @task(1)
    def validate_formula(self):
        self.client.post("/api/v1/validate", json={
            "expression": "sqrt(2*sqrt(r/(1+r))) - 1",
            "variables": {"r": {"domain": "(0, inf)"}},
            "constraints": ["r > 0"]
        })
EOF
```

**2:00 PM - Load Testing Execution (1,000+ Operations)**

```bash
# Ramp-up test (50 users over 5 minutes)
locust -f locustfile.py \
  --headless \
  --users 50 \
  --spawn-rate 10 \
  --run-time 5m \
  --html reports/day2_load_test.html

# Expected results:
# - Total requests: 1,000+
# - Failure rate: < 1%
# - Average response time: < 10s
# - P95 response time: < 15s
# - P99 response time: < 20s

# Sustained load test (100 users, 15 minutes)
locust -f locustfile.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 15m \
  --html reports/day2_sustained_load.html

# Spike test (200 users for 2 minutes)
locust -f locustfile.py \
  --headless \
  --users 200 \
  --spawn-rate 50 \
  --run-time 2m \
  --html reports/day2_spike_test.html
```

**3:00 PM - Performance Analysis**

```bash
# Generate performance report
python scripts/analyze_load_test.py \
  --report reports/day2_load_test.html \
  --output reports/performance_analysis.pdf

# Check metrics against targets:
# ✓ Throughput: >= 50 ops/min sequential
# ✓ Latency P50: < 6.5s
# ✓ Latency P95: < 15s
# ✓ Latency P99: < 20s
# ✓ Error rate: < 1%
# ✓ CPU usage: < 80%
# ✓ Memory usage: < 4GB per instance
```

**4:00 PM - Day 2 Checkpoint**

```bash
./scripts/day2_checkpoint.sh

# [x] LLM integration tests passed (100+)
# [x] E2E workflows passed (80+)
# [x] Load tests completed (1,000+ ops)
# [x] Performance targets met
# [x] Error rate < 1%
# [ ] Extended monitoring (Day 3-5)
```

---

### **Day 3-5: Extended Monitoring & Optimization**

*[Content continues with Days 3-7...]*

---

## Monitoring & Observability

### Key Metrics Dashboard

**Application Performance**

```
┌─────────────────────────────────────────────────────────┐
│             HypatiaX Staging Dashboard                  │
├─────────────────────────────────────────────────────────┤
│ Uptime:            99.95% ▓▓▓▓▓▓▓▓▓▓                   │
│ Request Rate:      58 req/min ▓▓▓▓▓▓▓░░░░              │
│ Error Rate:        0.2% ▓░░░░░░░░░                     │
│ Avg Latency:       6.2s ▓▓▓▓▓▓▓▓▓░                     │
│ P95 Latency:       12.8s ▓▓▓▓▓▓▓▓▓▓░░░                 │
│ P99 Latency:       18.2s ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░               │
├─────────────────────────────────────────────────────────┤
│ API Status:                                             │
│  - Anthropic:     ✓ Available (latency: 450ms)         │
│  - Gemini:        ✓ Available (latency: 340ms)         │
│  - Fallback:      ✓ Enabled (used 3 times today)       │
├─────────────────────────────────────────────────────────┤
│ Resources:                                              │
│  - CPU:           45% ▓▓▓▓▓░░░░░                        │
│  - Memory:        2.8GB / 8GB ▓▓▓▓░░░░░░               │
│  - DB Connections: 12 / 100 ▓░░░░░░░░░                 │
└─────────────────────────────────────────────────────────┘
```

### Alert Configuration

```yaml
# alerts.yaml
alerts:
  - name: High Error Rate
    condition: error_rate > 5%
    duration: 5m
    severity: critical
    notify: [pagerduty, slack]

  - name: High Latency
    condition: p95_latency > 15s
    duration: 10m
    severity: warning
    notify: [slack]

  - name: API Unavailable
    condition: api_health == 'down'
    duration: 1m
    severity: critical
    notify: [pagerduty, slack, email]

  - name: Low Throughput
    condition: request_rate < 30/min
    duration: 15m
    severity: warning
    notify: [slack]
```

---

## Rollback Procedures

### Immediate Rollback (< 5 minutes)

```bash
# If critical issues detected, rollback immediately
./scripts/rollback_staging.sh --version=previous

# Steps:
# 1. Stop current deployment
# 2. Deploy previous stable version
# 3. Verify health checks
# 4. Notify team
```

---

**Complete guide continues with Days 3-7, testing procedures, and validation...**
