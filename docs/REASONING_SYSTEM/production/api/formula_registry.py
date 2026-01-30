# api/formula_registry.py
"""
Formula Registry - Maps descriptions to executable functions
Bridges dataset generators with API endpoints
"""

import sys
from typing import Any, Callable, Dict, List

import numpy as np
from pydantic import BaseModel, Field

sys.path.append("../tools")

# Import YOUR existing implementations
from domains.finance.defi.uniswap_v2.uniswap_v2_formulas import *
from domains.finance.defi.uniswap_v3.uniswap_v3_formulas import *
from domains.finance.risk.risk_formulas import *


class FormulaInput(BaseModel):
    """Input parameter definition."""

    name: str
    description: str
    unit: str
    type: str  # "float", "int", "bool"
    min_value: float = None
    max_value: float = None
    default: Any = None
    required: bool = True


class FormulaMetadata(BaseModel):
    """Complete formula definition."""

    id: str  # "defi_il_basic"
    name: str  # "Impermanent Loss (Basic)"
    description: str  # From your generator
    category: str
    formula_latex: str  # "IL = 2\sqrt{p}/(1+p) - 1"
    formula_python: str  # "2*np.sqrt(p)/(p+1) - 1"

    inputs: List[FormulaInput]
    output_unit: str

    # The actual Python function
    implementation: Callable

    # Validation rules
    domain: str  # "defi" or "risk"
    constraints: List[str]  # ["price_ratio > 0"]

    # Examples
    examples: List[Dict]  # [{"inputs": {...}, "output": 0.0572}]

    class Config:
        arbitrary_types_allowed = True  # Allow Callable


class FormulaRegistry:
    """Central registry of all formulas."""

    def __init__(self):
        self.formulas: Dict[str, FormulaMetadata] = {}
        self._register_all()

    def register(self, formula: FormulaMetadata):
        """Register a formula."""
        self.formulas[formula.id] = formula

    def get(self, formula_id: str) -> FormulaMetadata:
        """Get formula by ID."""
        if formula_id not in self.formulas:
            raise ValueError(f"Formula {formula_id} not found")
        return self.formulas[formula_id]

    def search(self, query: str) -> List[FormulaMetadata]:
        """Search formulas by description."""
        results = []
        query_lower = query.lower()
        for formula in self.formulas.values():
            if (
                query_lower in formula.description.lower()
                or query_lower in formula.name.lower()
                or query_lower in formula.category.lower()
            ):
                results.append(formula)
        return results

    def list_by_category(self, category: str) -> List[FormulaMetadata]:
        """List all formulas in category."""
        return [f for f in self.formulas.values() if f.category == category]

    def _register_all(self):
        """Register all formulas from your implementations."""
        self._register_defi_formulas()
        self._register_risk_formulas()

    def _register_defi_formulas(self):
        """Register DeFi formulas."""

        # 1. Impermanent Loss - Basic
        self.register(
            FormulaMetadata(
                id="defi_il_basic",
                name="Impermanent Loss (Basic)",
                description="Calculate impermanent loss for 50/50 AMM pool",
                category="Impermanent Loss",
                formula_latex="IL = \\frac{2\\sqrt{p}}{1+p} - 1",
                formula_python="2*np.sqrt(price_ratio)/(price_ratio + 1) - 1",
                inputs=[
                    FormulaInput(
                        name="price_ratio",
                        description="Current price / Initial price",
                        unit="dimensionless",
                        type="float",
                        min_value=0.01,
                        max_value=100.0,
                        required=True,
                    )
                ],
                output_unit="percentage",
                implementation=lambda price_ratio: 2 * np.sqrt(price_ratio) / (price_ratio + 1) - 1,
                domain="defi",
                constraints=["price_ratio > 0"],
                examples=[
                    {"inputs": {"price_ratio": 1.0}, "output": 0.0},
                    {"inputs": {"price_ratio": 2.0}, "output": -0.0572},
                    {"inputs": {"price_ratio": 4.0}, "output": -0.2},
                ],
            )
        )

        # 2. Uniswap V2 Swap Output
        self.register(
            FormulaMetadata(
                id="defi_uniswap_v2_swap",
                name="Uniswap V2 Swap Output",
                description="Calculate swap output with 0.3% fee",
                category="Swap Output",
                formula_latex="\\Delta y = \\frac{\\Delta x \\cdot (1-fee) \\cdot y}{x + \\Delta x \\cdot (1-fee)}",
                formula_python="(amount_in * (1-fee) * reserve_out) / (reserve_in + amount_in*(1-fee))",
                inputs=[
                    FormulaInput(
                        name="amount_in",
                        description="Input token amount",
                        unit="tokens",
                        type="float",
                        min_value=0.0,
                        required=True,
                    ),
                    FormulaInput(
                        name="reserve_in",
                        description="Input token reserve",
                        unit="tokens",
                        type="float",
                        min_value=1.0,
                        required=True,
                    ),
                    FormulaInput(
                        name="reserve_out",
                        description="Output token reserve",
                        unit="tokens",
                        type="float",
                        min_value=1.0,
                        required=True,
                    ),
                    FormulaInput(
                        name="fee",
                        description="Fee percentage (0.003 = 0.3%)",
                        unit="dimensionless",
                        type="float",
                        min_value=0.0,
                        max_value=0.1,
                        default=0.003,
                        required=False,
                    ),
                ],
                output_unit="tokens",
                implementation=lambda amount_in, reserve_in, reserve_out, fee=0.003: (
                    amount_in * (1 - fee) * reserve_out
                )
                / (reserve_in + amount_in * (1 - fee)),
                domain="defi",
                constraints=["reserve_in > 0", "reserve_out > 0", "0 <= fee <= 0.1"],
                examples=[
                    {
                        "inputs": {"amount_in": 1.0, "reserve_in": 1000, "reserve_out": 2000, "fee": 0.003},
                        "output": 1.992,
                    }
                ],
            )
        )

        # 3. Constant Product (k=x*y)
        self.register(
            FormulaMetadata(
                id="defi_constant_product",
                name="Constant Product Invariant",
                description="Calculate constant product k for AMM",
                category="Constant Product",
                formula_latex="k = x \\cdot y",
                formula_python="reserve_x * reserve_y",
                inputs=[
                    FormulaInput(
                        name="reserve_x", description="Token X reserve", unit="tokens", type="float", min_value=0
                    ),
                    FormulaInput(
                        name="reserve_y", description="Token Y reserve", unit="tokens", type="float", min_value=0
                    ),
                ],
                output_unit="tokens^2",
                implementation=lambda reserve_x, reserve_y: reserve_x * reserve_y,
                domain="defi",
                constraints=["reserve_x > 0", "reserve_y > 0"],
                examples=[{"inputs": {"reserve_x": 1000, "reserve_y": 2000}, "output": 2000000}],
            )
        )

        # TODO: Add remaining 277 DeFi formulas...
        # Use your generators to auto-create these

    def _register_risk_formulas(self):
        """Register Risk Management formulas."""

        # 1. VaR 95%
        self.register(
            FormulaMetadata(
                id="risk_var_95",
                name="Value at Risk (95%)",
                description="Calculate VaR at 95% confidence level",
                category="Value at Risk",
                formula_latex="VaR_{95} = \\mu - 1.645 \\cdot \\sigma \\cdot \\sqrt{t}",
                formula_python="mu - 1.645 * sigma * np.sqrt(t)",
                inputs=[
                    FormulaInput(name="mu", description="Expected return", unit="percentage", type="float"),
                    FormulaInput(name="sigma", description="Volatility", unit="percentage", type="float", min_value=0),
                    FormulaInput(
                        name="t", description="Time horizon (days)", unit="days", type="float", min_value=0, default=1
                    ),
                ],
                output_unit="percentage",
                implementation=lambda mu, sigma, t=1: mu - 1.645 * sigma * np.sqrt(t),
                domain="risk",
                constraints=["sigma > 0", "t > 0"],
                examples=[{"inputs": {"mu": 0.05, "sigma": 0.2, "t": 1}, "output": -0.279}],
            )
        )

        # 2. Sharpe Ratio
        self.register(
            FormulaMetadata(
                id="risk_sharpe",
                name="Sharpe Ratio",
                description="Calculate Sharpe Ratio for portfolio performance",
                category="Sharpe Ratio",
                formula_latex="Sharpe = \\frac{R_p - R_f}{\\sigma_p}",
                formula_python="(return_portfolio - risk_free_rate) / volatility",
                inputs=[
                    FormulaInput(
                        name="return_portfolio", description="Portfolio return", unit="percentage", type="float"
                    ),
                    FormulaInput(
                        name="risk_free_rate",
                        description="Risk-free rate",
                        unit="percentage",
                        type="float",
                        default=0.02,
                    ),
                    FormulaInput(
                        name="volatility",
                        description="Portfolio volatility",
                        unit="percentage",
                        type="float",
                        min_value=0,
                    ),
                ],
                output_unit="ratio",
                implementation=lambda return_portfolio, risk_free_rate=0.02, volatility=1: (
                    (return_portfolio - risk_free_rate) / volatility if volatility > 0 else 0
                ),
                domain="risk",
                constraints=["volatility > 0"],
                examples=[
                    {"inputs": {"return_portfolio": 0.15, "risk_free_rate": 0.02, "volatility": 0.2}, "output": 0.65}
                ],
            )
        )

        # TODO: Add remaining 298 Risk formulas...


# Create global registry
REGISTRY = FormulaRegistry()
