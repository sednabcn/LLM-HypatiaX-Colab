# api/main.py (updated)
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from formula_registry import REGISTRY
from pydantic import BaseModel, create_model

app = FastAPI(title="QuantAPI", version="1.0.0")


@app.post("/calculate/{formula_id}")
async def calculate(formula_id: str, inputs: Dict[str, float]):
    """
    Universal calculation endpoint.

    Example:
        POST /calculate/defi_il_basic
        {"price_ratio": 2.0}

        POST /calculate/risk_var_95
        {"mu": 0.05, "sigma": 0.2, "t": 1}
    """
    try:
        # Get formula from registry
        formula = REGISTRY.get(formula_id)

        # Validate inputs
        for input_def in formula.inputs:
            if input_def.required and input_def.name not in inputs:
                raise ValueError(f"Missing required input: {input_def.name}")

            if input_def.name in inputs:
                value = inputs[input_def.name]
                if input_def.min_value and value < input_def.min_value:
                    raise ValueError(f"{input_def.name} must be >= {input_def.min_value}")
                if input_def.max_value and value > input_def.max_value:
                    raise ValueError(f"{input_def.name} must be <= {input_def.max_value}")

        # Execute formula
        result = formula.implementation(**inputs)

        return {
            "formula_id": formula_id,
            "formula_name": formula.name,
            "result": float(result),
            "unit": formula.output_unit,
            "formula_used": formula.formula_latex,
            "inputs_used": inputs,
        }

    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/formulas/search")
async def search_formulas(q: str):
    """Search formulas by description."""
    results = REGISTRY.search(q)
    return [{"id": f.id, "name": f.name, "description": f.description, "category": f.category} for f in results]


@app.get("/formulas/{formula_id}")
async def get_formula_details(formula_id: str):
    """Get complete formula metadata."""
    formula = REGISTRY.get(formula_id)
    return {
        "id": formula.id,
        "name": formula.name,
        "description": formula.description,
        "category": formula.category,
        "formula_latex": formula.formula_latex,
        "formula_python": formula.formula_python,
        "inputs": [inp.dict() for inp in formula.inputs],
        "output_unit": formula.output_unit,
        "examples": formula.examples,
        "constraints": formula.constraints,
    }
