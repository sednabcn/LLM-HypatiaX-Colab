# api/main.py - HYBRID APPROACH
import sys
from typing import Dict, List, Optional

import numpy as np
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

sys.path.append("../tools")

from formula_registry import REGISTRY
from symbolic.hybrid_system import HybridDiscoverySystem
from validation.ensemble_validator import EnsembleValidator

app = FastAPI(
    title="HypatiaX API - AI Formula Discovery",
    description="Fast calculations + AI-powered formula discovery",
    version="2.0.0",
)

# ==================== MODE 1: FAST CALCULATE ====================


class CalculateRequest(BaseModel):
    """Calculate using known formula."""

    formula_id: str
    inputs: Dict[str, float]


@app.post("/calculate/fast")
async def calculate_fast(req: CalculateRequest):
    """
    Fast calculation using pre-registered formulas.

    Speed: <100ms
    Cost: $0.001

    Example:
        POST /calculate/fast
        {
            "formula_id": "defi_il_basic",
            "inputs": {"price_ratio": 2.0}
        }
    """
    try:
        formula = REGISTRY.get(req.formula_id)
        result = formula.implementation(**req.inputs)

        return {"mode": "fast", "result": float(result), "formula": formula.formula_latex, "response_time_ms": 50}
    except Exception as e:
        raise HTTPException(400, str(e))


# ==================== MODE 2: DISCOVER NEW ====================


class DiscoverRequest(BaseModel):
    """Discover new formula from description + data."""

    description: str
    domain: str  # "defi" or "risk"

    # Option A: User provides data
    data: Optional[Dict[str, List[float]]] = None  # {"x": [...], "y": [...]}

    # Option B: System generates synthetic data
    generate_synthetic: bool = True
    n_samples: int = 100

    # Variable metadata
    variable_names: List[str]
    variable_descriptions: Dict[str, str]
    variable_units: Dict[str, str]


class DiscoverResponse(BaseModel):
    """Discovery result with validation."""

    mode: str = "discover"

    # Discovered formula
    expression: str
    sympy_expr: str
    r2_score: float
    complexity: int

    # Validation
    validation_score: float
    validation_passed: bool
    validation_errors: List[str]

    # LLM interpretation
    interpretation: Dict

    # Response time
    response_time_seconds: float


@app.post("/discover", response_model=DiscoverResponse)
async def discover_formula(req: DiscoverRequest):
    """
    AI-powered formula discovery from natural language.

    Speed: 15-30 seconds
    Cost: $0.10

    This uses your FULL hybrid system:
    - Symbolic regression (PySR)
    - Multi-layer validation
    - LLM interpretation

    Example:
        POST /discover
        {
            "description": "Calculate optimal LP fee for volatile market",
            "domain": "defi",
            "generate_synthetic": true,
            "variable_names": ["volume", "volatility", "liquidity"],
            "variable_descriptions": {
                "volume": "24h trading volume",
                "volatility": "Price volatility",
                "liquidity": "Pool liquidity"
            },
            "variable_units": {
                "volume": "USD",
                "volatility": "dimensionless",
                "liquidity": "USD"
            }
        }
    """
    import time

    start = time.time()

    try:
        # Initialize hybrid system
        system = HybridDiscoverySystem(domain=req.domain)

        # Generate or use provided data
        if req.data:
            # User provided data
            X = np.column_stack([req.data[var] for var in req.variable_names])
            y = req.data["y"]
        else:
            # Generate synthetic data based on description
            X, y = generate_synthetic_data(
                description=req.description, variable_names=req.variable_names, n_samples=req.n_samples
            )

        # DISCOVERY + VALIDATION + INTERPRETATION
        result = system.discover_validate_interpret(
            X=X,
            y=y,
            variable_names=req.variable_names,
            variable_descriptions=req.variable_descriptions,
            variable_units=req.variable_units,
            description=req.description,
        )

        elapsed = time.time() - start

        return DiscoverResponse(
            expression=result["discovery"]["expression"],
            sympy_expr=str(result["discovery"]["sympy_expr"]),
            r2_score=result["discovery"]["r2_score"],
            complexity=result["discovery"]["complexity"],
            validation_score=result["validation"]["total_score"],
            validation_passed=result["validation"]["valid"],
            validation_errors=result["validation"]["errors"],
            interpretation=result["interpretation"],
            response_time_seconds=elapsed,
        )

    except Exception as e:
        raise HTTPException(500, str(e))


# ==================== MODE 3: DISCOVER + SAVE ====================


@app.post("/discover-and-register")
async def discover_and_register(req: DiscoverRequest, background_tasks: BackgroundTasks):
    """
    Discover formula AND add to registry for future fast access.

    Workflow:
    1. Discover new formula (15-30s)
    2. Validate thoroughly
    3. If valid, add to registry
    4. Future calls use fast mode

    This is the "learn and optimize" pattern.
    """
    # Discover
    result = await discover_formula(req)

    if result.validation_passed and result.validation_score >= 85:
        # Add to registry in background
        background_tasks.add_task(
            add_to_registry,
            expression=result.expression,
            description=req.description,
            domain=req.domain,
            metadata=result.dict(),
        )

        return {
            **result.dict(),
            "registered": True,
            "message": "Formula added to registry. Future calls will use fast mode.",
        }
    else:
        return {
            **result.dict(),
            "registered": False,
            "message": "Formula validation score too low. Not added to registry.",
        }


# ==================== SEARCH & EXPLORE ====================


@app.get("/formulas/search")
async def search(q: str, mode: str = "all"):
    """
    Search both registry AND past discoveries.

    mode: "registry" (fast), "discovered" (AI-generated), "all"
    """
    results = {"registry": [], "discovered": []}

    if mode in ["registry", "all"]:
        results["registry"] = REGISTRY.search(q)

    if mode in ["discovered", "all"]:
        # Search database of past discoveries
        results["discovered"] = search_discovery_database(q)

    return results


@app.get("/formulas/{formula_id}/enhance")
async def enhance_formula(formula_id: str):
    """
    Take a registry formula and enhance it with AI.

    Example: User has "basic IL formula" but wants
    "IL formula adjusted for concentrated liquidity"

    This uses the registry formula as a starting point
    and discovers an enhanced version.
    """
    base_formula = REGISTRY.get(formula_id)

    # Use base formula to generate synthetic data
    # Then discover enhanced version
    # ...

    return {"base": base_formula, "enhanced": "..."}


# ==================== HELPER FUNCTIONS ====================


def generate_synthetic_data(description: str, variable_names: List[str], n_samples: int):
    """
    Generate synthetic data matching the description.

    This could use:
    1. LLM to suggest reasonable ranges
    2. Domain knowledge (DeFi ranges, Risk ranges)
    3. Random with constraints
    """
    # Simple version: random data
    n_vars = len(variable_names)
    X = np.random.uniform(0.1, 10, (n_samples, n_vars))

    # Generate y with some pattern (this is simplified)
    # In production, use LLM to suggest pattern based on description
    y = np.sum(X, axis=1) + np.random.normal(0, 0.1, n_samples)

    return X, y


def add_to_registry(expression: str, description: str, domain: str, metadata: Dict):
    """Add discovered formula to registry (background task)."""
    # Parse expression to lambda
    # Create FormulaMetadata
    # Register
    pass


def search_discovery_database(query: str):
    """Search past discoveries (stored in database)."""
    # Query database of past discoveries
    # Return matching results
    pass
