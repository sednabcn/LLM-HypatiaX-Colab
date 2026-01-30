# api/formula_metadata_mappings.py
"""
Mappings for units, constraints, and variable descriptions
"""

# Variable name → unit mapping
VARIABLE_UNITS = {
    # DeFi
    "price_ratio": "dimensionless",
    "reserve_x": "tokens",
    "reserve_y": "tokens",
    "reserve_in": "tokens",
    "reserve_out": "tokens",
    "amount_in": "tokens",
    "amount_out": "tokens",
    "liquidity": "tokens",
    "fee": "dimensionless",
    "slippage": "percentage",
    # Risk
    "mu": "percentage",
    "sigma": "percentage",
    "volatility": "percentage",
    "return": "percentage",
    "confidence": "dimensionless",
    "t": "days",
    "z": "dimensionless",
}

# Variable name → description mapping
VARIABLE_DESCRIPTIONS = {
    "price_ratio": "Current price / Initial price",
    "reserve_x": "Reserve of token X",
    "reserve_y": "Reserve of token Y",
    "mu": "Expected return (mean)",
    "sigma": "Volatility (standard deviation)",
    "confidence": "Confidence level (e.g., 0.95 for 95%)",
    "t": "Time horizon in days",
}

# Variable name → constraints
VARIABLE_CONSTRAINTS = {
    "price_ratio": (0.01, 100.0),
    "reserve_x": (0.0, float("inf")),
    "reserve_y": (0.0, float("inf")),
    "mu": (-1.0, 1.0),
    "sigma": (0.0, 1.0),
    "confidence": (0.5, 0.999),
    "t": (0.0, 365.0),
    "fee": (0.0, 0.1),
}


def enrich_inputs(inputs: List[FormulaInput]) -> List[FormulaInput]:
    """Add unit/description/constraint metadata to inputs."""
    for inp in inputs:
        if inp.name in VARIABLE_UNITS:
            inp.unit = VARIABLE_UNITS[inp.name]
        if inp.name in VARIABLE_DESCRIPTIONS:
            inp.description = VARIABLE_DESCRIPTIONS[inp.name]
        if inp.name in VARIABLE_CONSTRAINTS:
            inp.min_value, inp.max_value = VARIABLE_CONSTRAINTS[inp.name]

    return inputs
