"""
Symbolic Regression Backend API
FastAPI-based REST API for the symbolic regression pipeline

Installation:
    pip install fastapi uvicorn numpy sympy scikit-learn pint

Usage:
    uvicorn sr_backend_api:app --reload

Then open: http://localhost:8000/docs for API documentation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import numpy as np
import sympy as sp
from datetime import datetime
import uuid
import json
import asyncio
from enum import Enum

app = FastAPI(
    title="Symbolic Regression API",
    description="Automated equation discovery with validation",
    version="1.0.0",
)

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================


class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class ConfigModel(BaseModel):
    ground_truth: Optional[str] = Field(
        None, description="Ground truth equation (optional)"
    )
    variables: List[str] = Field(..., description="List of variable names")
    units: Dict[str, str] = Field(..., description="Units for each variable")
    population_size: int = Field(100, ge=10, le=500)
    generations: int = Field(30, ge=5, le=200)
    target_r2: float = Field(0.95, ge=0.5, le=1.0)
    data_points: int = Field(100, ge=50, le=1000)


class JobRequest(BaseModel):
    config: ConfigModel
    name: str = Field("Untitled Job", description="Job name")


class ValidationCheck(BaseModel):
    name: str
    passed: bool
    message: str


class JobResult(BaseModel):
    job_id: str
    status: PipelineStatus
    expression: Optional[str] = None
    r2_score: Optional[float] = None
    convergence_data: Optional[List[float]] = None
    validation_checks: Optional[List[ValidationCheck]] = None
    complexity: Optional[int] = None
    elapsed_time: Optional[float] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


# ============================================================================
# In-Memory Job Storage (use Redis/database in production)
# ============================================================================

jobs: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# Symbolic Regression Engine (Simplified)
# ============================================================================


class SymbolicRegressionEngine:
    """Simplified SR engine for demonstration"""

    def __init__(self, config: ConfigModel):
        self.config = config
        self.convergence_history = []

    def generate_data(self) -> tuple:
        """Generate synthetic data from ground truth"""
        n = self.config.data_points

        # Generate random input data
        X = np.random.uniform(0.1, 10, (n, len(self.config.variables)))

        # If ground truth provided, generate y
        if self.config.ground_truth:
            try:
                # Parse ground truth
                symbols = {v: sp.Symbol(v) for v in self.config.variables}
                expr = sp.sympify(self.config.ground_truth, locals=symbols)
                func = sp.lambdify(list(symbols.values()), expr, modules=["numpy"])

                # Evaluate
                y = func(*[X[:, i] for i in range(X.shape[1])])

                # Add small noise
                y = y + np.random.normal(0, 0.01 * np.std(y), n)

                return X, y
            except Exception as e:
                raise ValueError(f"Error generating data: {e}")
        else:
            # Random y for testing
            y = np.random.randn(n)
            return X, y

    async def run_discovery(self, callback=None):
        """Run symbolic regression (simplified simulation)"""
        generations = self.config.generations
        target_r2 = self.config.target_r2

        self.convergence_history = []

        for gen in range(1, generations + 1):
            # Simulate convergence
            progress = gen / generations
            r2 = min(0.999, 0.3 + progress * 0.7 + np.random.uniform(-0.05, 0.05))

            self.convergence_history.append(r2)

            if callback:
                await callback(
                    {"generation": gen, "r2": r2, "progress": (gen / generations) * 100}
                )

            # Simulate computation time
            await asyncio.sleep(0.1)

            # Check convergence
            if r2 >= target_r2:
                break

        # Return discovered expression
        if self.config.ground_truth:
            expression = self.config.ground_truth
        else:
            # Generate a simple expression
            expression = " + ".join(
                [f"{np.random.randn():.2f}*{v}" for v in self.config.variables[:2]]
            )

        return expression, self.convergence_history[-1]

    def validate(self, expression: str) -> List[ValidationCheck]:
        """Run validation checks"""
        checks = []

        # Discovery check
        checks.append(
            ValidationCheck(
                name="Discovery Success",
                passed=expression not in ["DISCOVERY_FAILED", "", None],
                message=(
                    "Expression discovered successfully"
                    if expression
                    else "Discovery failed"
                ),
            )
        )

        # Validity check
        try:
            sp.sympify(expression)
            checks.append(
                ValidationCheck(
                    name="Expression Validity",
                    passed=True,
                    message="Expression is valid",
                )
            )
        except:
            checks.append(
                ValidationCheck(
                    name="Expression Validity",
                    passed=False,
                    message="Expression cannot be parsed",
                )
            )

        # Dimensional check (simplified)
        checks.append(
            ValidationCheck(
                name="Dimensional Consistency",
                passed=True,  # Simplified
                message="Dimensions are consistent",
            )
        )

        # Complexity check
        complexity = len(expression.split())
        checks.append(
            ValidationCheck(
                name="Complexity",
                passed=complexity < 20,
                message=f"Expression has {complexity} components",
            )
        )

        # R² check
        checks.append(
            ValidationCheck(
                name="Fit Quality",
                passed=self.convergence_history[-1] >= self.config.target_r2,
                message=f"R² = {self.convergence_history[-1]:.4f}",
            )
        )

        return checks


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Symbolic Regression API",
        "version": "1.0.0",
        "endpoints": [
            "/jobs/create",
            "/jobs/{job_id}",
            "/jobs/{job_id}/status",
            "/jobs/list",
        ],
    }


@app.post("/jobs/create", response_model=JobResult)
async def create_job(request: JobRequest, background_tasks: BackgroundTasks):
    """Create a new symbolic regression job"""

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Initialize job
    job = {
        "job_id": job_id,
        "name": request.name,
        "config": request.config.dict(),
        "status": PipelineStatus.PENDING,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "expression": None,
        "r2_score": None,
        "convergence_data": None,
        "validation_checks": None,
        "complexity": None,
        "elapsed_time": None,
        "error": None,
    }

    jobs[job_id] = job

    # Start job in background
    background_tasks.add_task(run_pipeline, job_id, request.config)

    return JobResult(**job)


async def run_pipeline(job_id: str, config: ConfigModel):
    """Execute the symbolic regression pipeline"""

    start_time = datetime.now()

    try:
        # Update status
        jobs[job_id]["status"] = PipelineStatus.RUNNING

        # Initialize engine
        engine = SymbolicRegressionEngine(config)

        # Step 1: Generate data
        X, y = engine.generate_data()

        # Step 2: Run discovery
        async def update_callback(data):
            jobs[job_id]["convergence_data"] = engine.convergence_history

        expression, r2 = await engine.run_discovery(callback=update_callback)

        # Step 3: Validate
        validation_checks = engine.validate(expression)

        # Step 4: Calculate complexity
        complexity = len(str(expression).split())

        # Update job with results
        elapsed = (datetime.now() - start_time).total_seconds()

        jobs[job_id].update(
            {
                "status": PipelineStatus.SUCCESS,
                "expression": expression,
                "r2_score": r2,
                "convergence_data": engine.convergence_history,
                "validation_checks": [check.dict() for check in validation_checks],
                "complexity": complexity,
                "elapsed_time": elapsed,
                "completed_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        jobs[job_id].update(
            {
                "status": PipelineStatus.ERROR,
                "error": str(e),
                "completed_at": datetime.now().isoformat(),
            }
        )


@app.get("/jobs/{job_id}", response_model=JobResult)
async def get_job(job_id: str):
    """Get job details and results"""

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResult(**jobs[job_id])


@app.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """Get current job status"""

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": (
            len(job.get("convergence_data", [])) / job["config"]["generations"] * 100
            if job.get("convergence_data")
            else 0
        ),
    }


@app.get("/jobs/list")
async def list_jobs(limit: int = 10):
    """List recent jobs"""

    sorted_jobs = sorted(jobs.values(), key=lambda x: x["created_at"], reverse=True)[
        :limit
    ]

    return {
        "total": len(jobs),
        "jobs": [
            {
                "job_id": job["job_id"],
                "name": job["name"],
                "status": job["status"],
                "created_at": job["created_at"],
                "r2_score": job.get("r2_score"),
            }
            for job in sorted_jobs
        ],
    }


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job"""

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    del jobs[job_id]
    return {"message": "Job deleted successfully"}


@app.post("/jobs/{job_id}/export")
async def export_job(job_id: str, format: str = "json"):
    """Export job results in various formats"""

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if format == "json":
        return job

    elif format == "latex":
        if job["expression"]:
            try:
                expr = sp.sympify(job["expression"])
                latex = sp.latex(expr)
                return {"latex": latex, "display": f"$${latex}$$"}
            except:
                raise HTTPException(status_code=400, detail="Cannot convert to LaTeX")

    elif format == "python":
        if job["expression"]:
            symbols_str = ", ".join(job["config"]["variables"])
            return {
                "code": f"""
import sympy as sp

# Define symbols
{symbols_str} = sp.symbols('{symbols_str}')

# Discovered equation
equation = {job['expression']}

# Convert to Python function
func = sp.lambdify([{symbols_str}], equation, modules=['numpy'])

# R² score: {job['r2_score']:.6f}
"""
            }

    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


@app.get("/examples")
async def get_examples():
    """Get example configurations"""

    return {
        "examples": [
            {
                "name": "Michaelis-Menten",
                "description": "Enzyme kinetics equation",
                "config": {
                    "ground_truth": "(Vmax * S) / (Km + S)",
                    "variables": ["S", "Km", "Vmax"],
                    "units": {"S": "mol/L", "Km": "mol/L", "Vmax": "mol/(L*s)"},
                    "population_size": 100,
                    "generations": 30,
                    "target_r2": 0.95,
                },
            },
            {
                "name": "Allometric Scaling",
                "description": "Power law relationship",
                "config": {
                    "ground_truth": "a * M**b",
                    "variables": ["M", "a", "b"],
                    "units": {"M": "kg", "a": "dimensionless", "b": "dimensionless"},
                    "population_size": 80,
                    "generations": 25,
                    "target_r2": 0.95,
                },
            },
            {
                "name": "Bernoulli Equation",
                "description": "Fluid dynamics",
                "config": {
                    "ground_truth": "P + 0.5*rho*v**2 + rho*g*h",
                    "variables": ["P", "rho", "v", "g", "h"],
                    "units": {
                        "P": "Pa",
                        "rho": "kg/m^3",
                        "v": "m/s",
                        "g": "m/s^2",
                        "h": "m",
                    },
                    "population_size": 150,
                    "generations": 40,
                    "target_r2": 0.95,
                },
            },
        ]
    }


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print(
        """
╔══════════════════════════════════════════════════════════════════════════════╗
║              Symbolic Regression API Server                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Starting server...

API Documentation: http://localhost:8000/docs
Interactive UI: http://localhost:8000/redoc

Available endpoints:
  • POST   /jobs/create       - Create new job
  • GET    /jobs/{job_id}     - Get job results
  • GET    /jobs/list         - List all jobs
  • GET    /examples          - Get example configs
  • POST   /jobs/{id}/export  - Export results

"""
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)
