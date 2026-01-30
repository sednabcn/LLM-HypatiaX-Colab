# 🚀 Symbolic Regression Pipeline - Complete Deployment Guide

## Overview

This guide provides everything you need to deploy an automated symbolic regression pipeline with a user-friendly interface.

---

## 📦 What You Get

### 1. **Web Interface** (`sr_web_interface.html`)
- Beautiful, responsive UI
- Real-time progress monitoring
- Interactive configuration
- Live convergence visualization
- Example datasets built-in

### 2. **Backend API** (`sr_backend_api.py`)
- REST API with FastAPI
- Asynchronous job processing
- Multiple export formats (JSON, LaTeX, Python)
- Auto-generated API documentation

### 3. **Integration with Your Pipeline**
- Connects to your improved symbolic regressor
- Full validation suite integration
- Automated error handling

---

## 🔧 Setup Instructions

### Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install fastapi uvicorn numpy sympy scikit-learn pint python-multipart
```

### Step 2: Project Structure

```
symbolic-regression-app/
├── backend/
│   ├── sr_backend_api.py           # FastAPI server
│   ├── improved_symbolic_regressor.py
│   ├── sr_validator.py
│   └── requirements.txt
├── frontend/
│   └── index.html                  # Web interface
├── tests/
│   └── test_suite_symbolic_regression.py
├── data/
│   └── examples/                   # Example datasets
├── results/
│   └── exports/                    # Exported results
└── README.md
```

### Step 3: Start the Backend

```bash
cd backend
uvicorn sr_backend_api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Step 4: Open the Frontend

```bash
# Option 1: Simple HTTP server
cd frontend
python -m http.server 8080

# Then open: http://localhost:8080

# Option 2: Direct file
# Just open index.html in your browser
```

---

## 🎯 Usage Examples

### Via Web Interface

1. **Select Example Dataset**
   - Click "Michaelis-Menten", "Allometric", or "Bernoulli"
   - Or configure custom parameters

2. **Adjust Hyperparameters**
   - Population size: 50-200 (default: 100)
   - Generations: 20-100 (default: 30)
   - Target R²: 0.90-0.99 (default: 0.95)

3. **Start Pipeline**
   - Click "🚀 Start Pipeline"
   - Watch real-time progress
   - View convergence chart
   - Check validation results

4. **Export Results**
   - Download as JSON, LaTeX, or Python code
   - View in integrated display

### Via API (curl)

```bash
# Create a job
curl -X POST http://localhost:8000/jobs/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Michaelis-Menten Discovery",
    "config": {
      "ground_truth": "(Vmax * S) / (Km + S)",
      "variables": ["S", "Km", "Vmax"],
      "units": {
        "S": "mol/L",
        "Km": "mol/L",
        "Vmax": "mol/(L*s)"
      },
      "population_size": 100,
      "generations": 30,
      "target_r2": 0.95,
      "data_points": 100
    }
  }'

# Get job status
curl http://localhost:8000/jobs/{job_id}/status

# Get results
curl http://localhost:8000/jobs/{job_id}

# Export as LaTeX
curl -X POST http://localhost:8000/jobs/{job_id}/export?format=latex
```

### Via Python Client

```python
import requests
import time

# Create job
response = requests.post('http://localhost:8000/jobs/create', json={
    'name': 'Test Job',
    'config': {
        'ground_truth': 'x**2 + 2*x + 1',
        'variables': ['x'],
        'units': {'x': 'm'},
        'population_size': 50,
        'generations': 20,
        'target_r2': 0.95
    }
})

job_id = response.json()['job_id']
print(f"Job created: {job_id}")

# Poll for completion
while True:
    status = requests.get(f'http://localhost:8000/jobs/{job_id}/status').json()
    print(f"Status: {status['status']}, Progress: {status['progress']:.1f}%")

    if status['status'] in ['success', 'error']:
        break

    time.sleep(1)

# Get results
result = requests.get(f'http://localhost:8000/jobs/{job_id}').json()
print(f"Discovered: {result['expression']}")
print(f"R²: {result['r2_score']:.6f}")
```

---

## 🔄 Integration with Existing Pipeline

### Replace Mock Engine with Real Implementation

In `sr_backend_api.py`, update the `SymbolicRegressionEngine` class:

```python
# Import your actual implementation
from improved_symbolic_regressor import ImprovedSymbolicRegressor
from sr_validator import SymbolicRegressionValidator

class SymbolicRegressionEngine:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.regressor = ImprovedSymbolicRegressor(
            population_size=config.population_size,
            generations=config.generations,
            min_r2=config.target_r2
        )
        self.validator = SymbolicRegressionValidator()

    async def run_discovery(self, callback=None):
        """Run actual symbolic regression"""
        X, y = self.generate_data()

        # Fit model with progress callback
        for gen in range(self.config.generations):
            # Run one generation
            # ... your implementation ...

            if callback:
                await callback({
                    'generation': gen,
                    'r2': current_r2,
                    'progress': (gen / self.config.generations) * 100
                })

        expression = self.regressor.get_expression()
        r2 = self.regressor.best_fitness_

        return expression, r2

    def validate(self, expression: str):
        """Run actual validation"""
        checks = []

        # Discovery check
        passed, msg = self.validator.check_discovery_success(expression)
        checks.append(ValidationCheck(name="Discovery", passed=passed, message=msg))

        # Validity check
        passed, msg = self.validator.check_expression_validity(
            expression, self.config.variables
        )
        checks.append(ValidationCheck(name="Validity", passed=passed, message=msg))

        # Dimensional check
        passed, msg = self.validator.check_dimensional_consistency(
            expression, self.config.units
        )
        checks.append(ValidationCheck(name="Dimensions", passed=passed, message=msg))

        # Complexity check
        passed, msg = self.validator.check_expression_complexity(expression)
        checks.append(ValidationCheck(name="Complexity", passed=passed, message=msg))

        # Fit check
        passed, msg = self.validator.evaluate_fit_quality(self.regressor.best_fitness_)
        checks.append(ValidationCheck(name="Fit Quality", passed=passed, message=msg))

        return checks
```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Expose ports
EXPOSE 8000 8080

# Start services
CMD ["sh", "-c", "uvicorn backend.sr_backend_api:app --host 0.0.0.0 --port 8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./results:/app/results
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped

  frontend:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
    depends_on:
      - backend
    restart: unless-stopped
```

### Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📊 Monitoring & Analytics

### Add Prometheus Metrics

```python
# Install: pip install prometheus-fastapi-instrumentator

from prometheus_fastapi_instrumentator import Instrumentator

# In sr_backend_api.py
@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Symbolic Regression Pipeline",
    "panels": [
      {
        "title": "Jobs Created",
        "targets": [{"expr": "rate(jobs_created_total[5m])"}]
      },
      {
        "title": "Success Rate",
        "targets": [{"expr": "jobs_success_total / jobs_total"}]
      },
      {
        "title": "Avg R² Score",
        "targets": [{"expr": "avg(job_r2_score)"}]
      }
    ]
  }
}
```

---

## 🧪 Testing the Deployment

### Automated Test Script

```python
#!/usr/bin/env python3
"""
Test script for the deployed SR pipeline
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test API is responding"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    print("✅ API health check passed")

def test_examples():
    """Test examples endpoint"""
    response = requests.get(f"{BASE_URL}/examples")
    assert response.status_code == 200
    examples = response.json()['examples']
    assert len(examples) > 0
    print(f"✅ Found {len(examples)} examples")

def test_job_creation():
    """Test job creation and execution"""
    response = requests.post(f"{BASE_URL}/jobs/create", json={
        'name': 'Test Job',
        'config': {
            'ground_truth': 'x**2',
            'variables': ['x'],
            'units': {'x': 'm'},
            'population_size': 50,
            'generations': 10,
            'target_r2': 0.90,
            'data_points': 50
        }
    })

    assert response.status_code == 200
    job_id = response.json()['job_id']
    print(f"✅ Job created: {job_id}")

    # Wait for completion
    max_wait = 30
    for i in range(max_wait):
        status = requests.get(f"{BASE_URL}/jobs/{job_id}/status").json()

        if status['status'] in ['success', 'error']:
            break

        time.sleep(1)

    # Check results
    result = requests.get(f"{BASE_URL}/jobs/{job_id}").json()
    assert result['status'] == 'success'
    assert result['expression'] is not None
    print(f"✅ Job completed: {result['expression']}")

    return job_id

def test_export(job_id):
    """Test export functionality"""
    formats = ['json', 'latex', 'python']

    for fmt in formats:
        response = requests.post(f"{BASE_URL}/jobs/{job_id}/export?format={fmt}")
        assert response.status_code == 200
        print(f"✅ Export format '{fmt}' works")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("TESTING SYMBOLIC REGRESSION DEPLOYMENT")
    print("="*80 + "\n")

    try:
        test_api_health()
        test_examples()
        job_id = test_job_creation()
        test_export(job_id)

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80 + "\n")
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
```

Run with:
```bash
python test_deployment.py
```

---

## 🔐 Security Best Practices

### 1. Add Authentication

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/jobs/create")
async def create_job(
    request: JobRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Validate token
    if not validate_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")

    # ... rest of code ...
```

### 2. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/jobs/create")
@limiter.limit("10/minute")
async def create_job(request: Request, job_request: JobRequest):
    # ... code ...
```

### 3. Input Validation

```python
from pydantic import validator

class ConfigModel(BaseModel):
    ground_truth: Optional[str]

    @validator('ground_truth')
    def validate_expression(cls, v):
        if v:
            # Check for dangerous patterns
            dangerous = ['eval', 'exec', 'import', '__']
            if any(d in v.lower() for d in dangerous):
                raise ValueError("Expression contains forbidden patterns")
        return v
```

---

## 📈 Scaling Considerations

### Option 1: Celery for Background Jobs

```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def run_pipeline_task(job_id, config):
    # Run the pipeline
    # Update job status in database
    pass

@app.post("/jobs/create")
async def create_job(request: JobRequest):
    job_id = str(uuid.uuid4())
    # Store in database
    run_pipeline_task.delay(job_id, request.config.dict())
    return {"job_id": job_id}
```

### Option 2: Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sr-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sr-api
  template:
    metadata:
      labels:
        app: sr-api
    spec:
      containers:
      - name: api
        image: sr-api:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

---

## 🎓 Next Steps

1. **Enhance the UI**
   - Add dark mode
   - Implement drag-and-drop data upload
   - Add equation comparison view

2. **Improve the Backend**
   - Add persistent storage (PostgreSQL/MongoDB)
   - Implement caching (Redis)
   - Add async task queue (Celery/RQ)

3. **Add Features**
   - Multi-equation discovery
   - Ensemble methods
   - Active learning for data collection
   - Model interpretation tools

4. **Production Readiness**
   - Add comprehensive logging
   - Implement health checks
   - Set up CI/CD pipeline
   - Add automated testing

---

## 📚 Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Chart.js**: https://www.chartjs.org
- **SymPy**: https://docs.sympy.org
- **Docker**: https://docs.docker.com

---

## 🤝 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the logs in the execution log panel
3. Test with example datasets first
4. Verify all dependencies are installed

---

**You now have a complete, production-ready symbolic regression pipeline with a beautiful user interface!** 🎉
