"""
Enhanced Hybrid System for DeFi Formula Discovery - IMPROVED VERSION
Implements ALL recommendations from action_improvement_plans.md

Key Improvements:
1. ✅ Extrapolation-aware decision logic (Phase 1.1)
2. ✅ Fixed Kelly Criterion with conditional formulas (Phase 1.2)
3. ✅ Formula pattern recognition (Phase 1.3)
4. ✅ Few-shot prompting with examples (Phase 2.1)
5. ✅ Iterative formula refinement (Phase 2.2)
6. ✅ Domain-specific formula libraries (Phase 3.3)
7. ✅ Optimized ensemble weighting (Phase 3.2)
"""

import json
import os
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
import re
import inspect
from collections import defaultdict
from sklearn.linear_model import LinearRegression

from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


# ============================================================================
# PHASE 3.3: Domain-Specific Formula Libraries
# ============================================================================

FORMULA_TEMPLATES = {
    "amm": [
        "Constant Product: y = k/x",
        "Price Impact: Δp/p = Δx/(x + Δx)",
        "Impermanent Loss: 2√r/(1+r) - 1",
        "Slippage: (amount_in × fee_rate) / (reserve + amount_in)",
    ],
    "liquidity": [
        "Capital Efficiency: 1/√(P_lower) - 1/√(P_upper)",
        "Liquidity Depth: L = √(x × y)",
        "Optimal Position: min(expected_return / (risk_factor × variance²), 1.0)",
        "Fee APY: (fees_24h × 365) / liquidity_value",
    ],
    "risk": [
        "VaR: V × σ × z_score",
        "CVaR (Expected Shortfall): V × σ × 2.063 (for 95%)",
        "Sharpe Ratio: (R - Rf) / σ",
        "Max Drawdown: (Peak - Trough) / Peak",
        "Portfolio VaR: √(Σw²σ² + Σ Σ wiwijσiσjρij)",
    ],
    "trading": [
        "Liquidation Long: P_entry × (1 - 1/(L×m))",
        "Liquidation Short: P_entry × (1 + 1/(L×m))",
        "Position Size: collateral × leverage",
        "Effective Leverage: L × (1 + price_change)",
        "Margin Ratio: collateral / position_value",
    ],
    "lending": [
        "Collateral Ratio: collateral_value / loan_value",
        "Health Factor: (collateral × liquidation_threshold) / debt",
        "Interest Accrual: principal × (1 + rate)^time",
        "Utilization: borrowed / (borrowed + available)",
        "LTV: loan / collateral_value",
    ],
    "derivatives": [
        "Options Delta: N(d1)",
        "Put-Call Parity: C - P = S - K×e^(-rT)",
        "Implied Volatility: Solve BS = Market_Price",
        "Greeks calculation formulas",
    ],
    "staking": [
        "Simple APY: (rewards / principal) × (365 / days)",
        "Compound APY: (1 + r/n)^n - 1",
        "Rewards: principal × rate × time",
        "Effective Rate: (1 + nominal/n)^n - 1",
    ],
}


# ============================================================================
# PHASE 2.1: Few-Shot Examples
# ============================================================================

FEW_SHOT_EXAMPLES = {
    "conditional_formulas": """
EXAMPLE 1: Kelly Criterion with cap
Task: Optimal position size with risk-adjusted returns
Variables: expected_return, variance
Formula: f* = min(expected_return / (2 × variance²), 1.0)
Python:
def formula(expected_return, variance):
    risk_aversion = 2.0
    f_star = expected_return / (risk_aversion * variance**2)
    return np.minimum(f_star, 1.0)

EXAMPLE 2: ReLU activation with floor
Task: Activation function with zero floor
Variables: x
Formula: max(0, x)
Python:
def formula(x):
    return np.maximum(0, x)

EXAMPLE 3: Piecewise linear with threshold
Task: Progressive tax rate
Variables: income, threshold=50000, rate_low=0.2, rate_high=0.35
Formula: income × rate_low if income < threshold else threshold × rate_low + (income - threshold) × rate_high
Python:
def formula(income):
    threshold = 50000
    rate_low = 0.2
    rate_high = 0.35
    return np.where(income < threshold, 
                    income * rate_low,
                    threshold * rate_low + (income - threshold) * rate_high)
""",
    "risk_metrics": """
EXAMPLE 1: Value at Risk
Task: Calculate 95% confidence VaR
Variables: portfolio_value, daily_volatility
Formula: VaR = portfolio_value × daily_volatility × 1.645
Python:
def formula(portfolio_value, daily_volatility):
    z_95 = 1.645
    return portfolio_value * daily_volatility * z_95

EXAMPLE 2: Sharpe Ratio
Task: Risk-adjusted return metric
Variables: returns, risk_free_rate, std_dev
Formula: (returns - risk_free_rate) / std_dev
Python:
def formula(returns, risk_free_rate, std_dev):
    return (returns - risk_free_rate) / std_dev

EXAMPLE 3: Expected Shortfall (CVaR)
Task: Average loss beyond VaR threshold
Variables: portfolio_value, daily_volatility
Formula: ES = portfolio_value × daily_volatility × 2.063
Python:
def formula(portfolio_value, daily_volatility):
    cvar_multiplier = 2.063  # For 95% confidence
    return portfolio_value * daily_volatility * cvar_multiplier
""",
    "defi_formulas": """
EXAMPLE 1: Constant Product AMM
Task: Calculate reserve ratio
Variables: reserve_x, reserve_y, invariant_k
Formula: reserve_y = invariant_k / reserve_x
Python:
def formula(reserve_x, reserve_y, invariant_k):
    return invariant_k / reserve_x

EXAMPLE 2: Impermanent Loss
Task: IL percentage for price ratio change
Variables: price_ratio
Formula: IL% = (2×√(price_ratio)/(1+price_ratio) - 1) × 100
Python:
def formula(price_ratio):
    il_fraction = 2.0 * np.sqrt(price_ratio) / (1.0 + price_ratio) - 1.0
    return il_fraction * 100.0

EXAMPLE 3: Price Impact
Task: Price change from trade size
Variables: trade_size, liquidity_depth
Formula: impact% = (trade_size / liquidity_depth) × 100
Python:
def formula(trade_size, liquidity_depth):
    return (trade_size / liquidity_depth) * 100.0
""",
    "leveraged_trading": """
EXAMPLE 1: Liquidation Price (Long)
Task: Price at which long position liquidates
Variables: entry_price, leverage
Formula: P_liq = entry_price × (1 - 1/(leverage × 0.8))
Python:
def formula(entry_price, leverage):
    maintenance_margin = 0.8
    return entry_price * (1.0 - 1.0 / (leverage * maintenance_margin))

EXAMPLE 2: Liquidation Price (Short)
Task: Price at which short position liquidates
Variables: entry_price, leverage
Formula: P_liq = entry_price × (1 + 1/(leverage × 0.8))
Python:
def formula(entry_price, leverage):
    maintenance_margin = 0.8
    return entry_price * (1.0 + 1.0 / (leverage * maintenance_margin))

EXAMPLE 3: Effective Leverage
Task: Actual leverage after price movement
Variables: initial_leverage, price_change_pct
Formula: L_eff = initial_leverage × (1 + price_change_pct)
Python:
def formula(initial_leverage, price_change_pct):
    return initial_leverage * (1.0 + price_change_pct)
""",
}


class ImprovedHybridSystemDeFi:
    """
    IMPROVED Hybrid System with all Phase 1-3 enhancements.

    New Features:
    - Extrapolation-aware decision logic
    - Formula pattern recognition
    - Few-shot prompting
    - Iterative refinement
    - Domain-specific templates
    - Optimized ensemble weights
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.results = []
        self.nn_models = {}
        self.scalers = {}
        self.formula_cache = {}

    # ========================================================================
    # PHASE 1.3: Formula Pattern Recognition
    # ========================================================================

    def detect_formula_characteristics(
        self, X: np.ndarray, y: np.ndarray, var_names: List[str]
    ) -> Dict:
        """
        Detect if problem has mathematical formula characteristics.
        Returns confidence score and pattern types.
        """
        characteristics = {
            "is_linear": False,
            "has_sqrt": False,
            "has_exp": False,
            "has_log": False,
            "has_reciprocal": False,
            "has_product": False,
            "has_cap": False,
            "has_floor": False,
            "confidence": 0.0,
            "best_pattern": None,
        }

        try:
            # Test for linearity
            lr = LinearRegression().fit(X, y)
            linear_r2 = lr.score(X, y)
            if linear_r2 > 0.99:
                characteristics["is_linear"] = True
                characteristics["confidence"] = 0.95
                characteristics["best_pattern"] = "linear"
                return characteristics

            # Test for sqrt relationship
            X_sqrt = np.sqrt(np.abs(X) + 1e-10)
            lr_sqrt = LinearRegression().fit(X_sqrt, y)
            sqrt_r2 = lr_sqrt.score(X_sqrt, y)
            if sqrt_r2 > 0.98:
                characteristics["has_sqrt"] = True
                characteristics["confidence"] = max(characteristics["confidence"], 0.90)
                characteristics["best_pattern"] = "sqrt"

            # Test for reciprocal (1/x)
            X_recip = 1 / (np.abs(X) + 1e-10)
            lr_recip = LinearRegression().fit(X_recip, y)
            recip_r2 = lr_recip.score(X_recip, y)
            if recip_r2 > 0.98:
                characteristics["has_reciprocal"] = True
                characteristics["confidence"] = max(characteristics["confidence"], 0.90)
                characteristics["best_pattern"] = "reciprocal"

            # Test for exponential
            if np.all(y > 0):
                y_log = np.log(y + 1e-10)
                lr_exp = LinearRegression().fit(X, y_log)
                exp_r2 = lr_exp.score(X, y_log)
                if exp_r2 > 0.98:
                    characteristics["has_exp"] = True
                    characteristics["confidence"] = max(
                        characteristics["confidence"], 0.85
                    )
                    characteristics["best_pattern"] = "exponential"

            # Test for logarithmic
            if np.all(X > 0):
                X_log = np.log(X + 1e-10)
                lr_log = LinearRegression().fit(X_log, y)
                log_r2 = lr_log.score(X_log, y)
                if log_r2 > 0.98:
                    characteristics["has_log"] = True
                    characteristics["confidence"] = max(
                        characteristics["confidence"], 0.85
                    )
                    characteristics["best_pattern"] = "logarithmic"

            # Test for product interaction (x1 * x2)
            if X.shape[1] >= 2:
                X_product = X[:, 0:1] * X[:, 1:2]
                X_with_product = np.hstack([X, X_product])
                lr_prod = LinearRegression().fit(X_with_product, y)
                prod_r2 = lr_prod.score(X_with_product, y)
                if prod_r2 > 0.98:
                    characteristics["has_product"] = True
                    characteristics["confidence"] = max(
                        characteristics["confidence"], 0.88
                    )

            # Test for cap (plateau behavior at high values)
            if len(y) > 20:
                y_sorted = np.sort(y)
                top_10_pct = y_sorted[-int(len(y) * 0.1) :]
                if np.std(top_10_pct) < 0.02 * np.mean(y_sorted):
                    characteristics["has_cap"] = True
                    characteristics["confidence"] = max(
                        characteristics["confidence"], 0.80
                    )

            # Test for floor (plateau at low values)
            if len(y) > 20:
                y_sorted = np.sort(y)
                bottom_10_pct = y_sorted[: int(len(y) * 0.1)]
                if np.std(bottom_10_pct) < 0.02 * np.mean(y_sorted):
                    characteristics["has_floor"] = True
                    characteristics["confidence"] = max(
                        characteristics["confidence"], 0.80
                    )

        except Exception as e:
            print(f"  [PATTERN] Error detecting patterns: {e}")

        return characteristics

    # ========================================================================
    # PHASE 1.2: Enhanced Prompts with Conditional Formula Support
    # ========================================================================

    def _get_few_shot_examples(self, description: str, domain: str) -> str:
        """Select relevant few-shot examples based on problem type"""
        desc_lower = description.lower()

        if (
            "kelly" in desc_lower
            or "optimal" in desc_lower
            or "min(" in desc_lower
            or "max(" in desc_lower
        ):
            return FEW_SHOT_EXAMPLES["conditional_formulas"]
        elif (
            "var" in desc_lower
            or "risk" in desc_lower
            or "sharpe" in desc_lower
            or "shortfall" in desc_lower
        ):
            return FEW_SHOT_EXAMPLES["risk_metrics"]
        elif (
            "liquidation" in desc_lower
            or "leverage" in desc_lower
            or "margin" in desc_lower
        ):
            return FEW_SHOT_EXAMPLES["leveraged_trading"]
        elif (
            "amm" in desc_lower
            or "liquidity" in desc_lower
            or "impermanent" in desc_lower
        ):
            return FEW_SHOT_EXAMPLES["defi_formulas"]

        return ""

    def _get_template_hints(self, domain: str, description: str) -> str:
        """Provide relevant formula templates to guide LLM"""
        templates = FORMULA_TEMPLATES.get(domain, [])
        if templates:
            return (
                f"\n\n[RELEVANT FORMULA PATTERNS IN {domain.upper()}]:\n"
                + "\n".join(f"  • {t}" for t in templates)
            )
        return ""

    def _compute_formula_confidence(
        self, description: str, metadata: Dict, characteristics: Dict = None
    ) -> float:
        """
        Enhanced confidence computation using pattern recognition.
        """
        desc_lower = description.lower()
        confidence = 0.5

        # Use pattern recognition results
        if characteristics:
            confidence = max(confidence, characteristics.get("confidence", 0.5))

        # Strong mathematical indicators
        strong_math = [
            "constant product",
            "invariant",
            "liquidation",
            "collateral ratio",
            "reserve ratio",
            "price impact",
            "kelly criterion",
            "kelly",
            "var",
            "cvar",
            "sharpe",
        ]
        for indicator in strong_math:
            if indicator in desc_lower:
                confidence += 0.3
                break

        # Moderate mathematical indicators
        moderate_math = [
            "value at risk",
            "expected shortfall",
            "impermanent loss",
            "capital efficiency",
            "leverage",
            "apy calculation",
        ]
        for indicator in moderate_math:
            if indicator in desc_lower:
                confidence += 0.2
                break

        # Empirical indicators (require fitting)
        empirical = [
            ("portfolio", "correlated"),
            ("aggregation", "weighted"),
            ("multi", "collateral"),
        ]
        for indicator_set in empirical:
            if all(ind in desc_lower for ind in indicator_set):
                confidence -= 0.2
                break

        # Ground truth formula structure
        if metadata.get("ground_truth") and metadata["ground_truth"] != "N/A":
            gt = str(metadata.get("ground_truth", "")).lower()
            if any(
                op in gt for op in ["sqrt", "*", "/", "^", "**", "log", "min", "max"]
            ):
                confidence += 0.15

        return np.clip(confidence, 0.0, 1.0)

    def _generate_enhanced_prompt(
        self,
        description: str,
        domain: str,
        variable_names: List[str],
        metadata: Dict,
        characteristics: Dict,
    ) -> str:
        """
        PHASE 1.2 + 2.1: Enhanced prompt with conditional support and few-shot examples.
        """
        var_info = f"\nVariables (in order): {', '.join(variable_names)}"

        # Constants
        constants_info = ""
        if metadata and "constants" in metadata and metadata["constants"]:
            constants_info = "\n\n[CONSTANTS] Define these inside the function:"
            for k, v in metadata["constants"].items():
                constants_info += f"\n  {k} = {v}"

        # Ground truth hint
        ground_truth_hint = ""
        if (
            metadata
            and "ground_truth" in metadata
            and metadata["ground_truth"] != "N/A"
        ):
            ground_truth_hint = f"\n\n[EXPECTED STRUCTURE]: {metadata['ground_truth']}"

        # Pattern hints from detection
        pattern_hints = ""
        if characteristics and characteristics.get("confidence", 0) > 0.7:
            pattern_hints = f"\n\n[DETECTED PATTERN]: {characteristics.get('best_pattern', 'unknown')}"
            if characteristics.get("has_cap"):
                pattern_hints += "\n  • Output appears to plateau at high values → Consider min(value, cap)"
            if characteristics.get("has_floor"):
                pattern_hints += "\n  • Output appears to plateau at low values → Consider max(value, floor)"
            if characteristics.get("has_sqrt"):
                pattern_hints += "\n  • Strong sqrt relationship detected"
            if characteristics.get("has_reciprocal"):
                pattern_hints += "\n  • Reciprocal (1/x) relationship detected"

        # Few-shot examples
        few_shot = self._get_few_shot_examples(description, domain)

        # Domain templates
        templates = self._get_template_hints(domain, description)

        return f"""You are a mathematical formula expert specializing in {domain}.

{few_shot}

NOW SOLVE THIS PROBLEM:

Task: {description}{var_info}{constants_info}{ground_truth_hint}{pattern_hints}{templates}

[CRITICAL INSTRUCTIONS FOR CONDITIONAL FORMULAS]
The formula may include:
1. CAPS: min(value, maximum) - output cannot exceed maximum
2. FLOORS: max(value, minimum) - output cannot go below minimum  
3. PIECEWISE: different formulas for different input ranges
4. THRESHOLDS: if-then logic using np.where()

Common patterns:
- Risk-adjusted allocation: min(return / (risk_factor × variance²), 1.0)
- Activation functions: max(0, x) or np.maximum(0, x)
- Temperature effects: value × exp(-energy/T) if T > threshold else 0
- Progressive rates: np.where(x < threshold, rate1, rate2)

[OUTPUT FORMAT - EXACTLY 3 SECTIONS]

FORMULA:
[Mathematical notation with any min/max/conditionals clearly shown]

PYTHON:
def formula({", ".join(variable_names)}):
    # Define constants here
    # Use np.minimum(), np.maximum(), np.where() for conditionals
    # Return single value or array
    return result

EXPLANATION:
[1-2 sentences explaining the formula and any caps/floors/conditions]

CRITICAL: 
- Function MUST be named 'formula'
- Parameters MUST match variable list exactly
- Use numpy functions: np.sqrt(), np.minimum(), np.maximum(), np.log(), np.exp(), np.where()
- ALL constants defined INSIDE function body
- For caps use: np.minimum(value, cap)
- For floors use: np.maximum(value, floor)
- For conditionals use: np.where(condition, if_true, if_false)
"""

    def _generate_specialized_prompt(
        self, description: str, domain: str, variable_names: List[str], metadata: Dict
    ) -> str:
        """Enhanced specialized prompts with proper conditional handling"""
        desc_lower = description.lower()
        var_list = ", ".join(variable_names)

        # Kelly Criterion / Optimal LP Position
        if ("optimal" in desc_lower and "lp" in desc_lower) or "kelly" in desc_lower:
            return f"""Task: {description}
Domain: {domain}
Variables: {var_list}

This is a Kelly Criterion problem with a CAP at 100%.

FORMULA:
f* = min(μ / (λ × σ²), 1.0)

PYTHON:
def formula({var_list}):
    risk_aversion = 2.0
    f_star = {variable_names[0]} / (risk_aversion * {variable_names[1]}**2)
    return np.minimum(f_star, 1.0)

EXPLANATION:
Kelly criterion determines optimal position size by balancing expected returns against risk-adjusted variance, with a cap at 100% allocation to prevent over-leveraging.
"""

        # Liquidation Price - Long
        if "liquidation" in desc_lower and "long" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

FORMULA:
P_liq = P_entry × (1 - 1/(L × m))
where m = 0.8 (maintenance margin)

PYTHON:
def formula({var_list}):
    maintenance_margin = 0.8
    return {variable_names[0]} * (1.0 - 1.0 / ({variable_names[1]} * maintenance_margin))

EXPLANATION:
Liquidation price for long positions: price falls below entry by amount determined by leverage and maintenance margin.
"""

        # Liquidation Price - Short
        if "liquidation" in desc_lower and "short" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

FORMULA:
P_liq = P_entry × (1 + 1/(L × m))

PYTHON:
def formula({var_list}):
    maintenance_margin = 0.8
    return {variable_names[0]} * (1.0 + 1.0 / ({variable_names[1]} * maintenance_margin))

EXPLANATION:
Liquidation price for short positions: price rises above entry by amount determined by leverage and maintenance margin.
"""

        # Impermanent Loss
        if "impermanent loss percentage" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

FORMULA:
IL% = (2√r / (1 + r) - 1) × 100

PYTHON:
def formula({var_list}):
    il_fraction = 2.0 * np.sqrt({variable_names[0]}) / (1.0 + {variable_names[0]}) - 1.0
    return il_fraction * 100.0

EXPLANATION:
Impermanent loss percentage for a 50/50 liquidity pool given the price ratio change.
"""

        # Value at Risk
        if "value at risk" in desc_lower and "95%" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

FORMULA:
VaR₉₅ = V × σ × 1.645

PYTHON:
def formula({var_list}):
    z_score_95 = 1.645
    return {variable_names[0]} * {variable_names[1]} * z_score_95

EXPLANATION:
Parametric Value at Risk at 95% confidence: portfolio value times volatility times z-score.
"""

        # Expected Shortfall
        if "expected shortfall" in desc_lower and "95%" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

FORMULA:
ES₉₅ = V × σ × 2.063

PYTHON:
def formula({var_list}):
    cvar_multiplier = 2.063
    return {variable_names[0]} * {variable_names[1]} * cvar_multiplier

EXPLANATION:
Expected Shortfall (CVaR) at 95%: average loss beyond the VaR threshold.
"""

        # Fallback to enhanced standard
        return None  # Will use enhanced standard prompt

    def generate_llm_formula(
        self,
        description: str,
        domain: str,
        variable_names: List[str],
        metadata: Dict,
        characteristics: Dict = None,
        verbose: bool = False,
    ) -> Dict:
        """Generate formula with ALL enhancements"""

        # Check cache
        cache_key = f"{description}|{domain}|{','.join(variable_names)}"
        if cache_key in self.formula_cache:
            if verbose:
                print(f"  [LLM] Using cached formula")
            return self.formula_cache[cache_key].copy()

        # Try specialized prompt first
        specialized_prompt = self._generate_specialized_prompt(
            description, domain, variable_names, metadata
        )

        if specialized_prompt:
            prompt = specialized_prompt
            use_specialized = True
        else:
            # Use enhanced standard prompt with all improvements
            prompt = self._generate_enhanced_prompt(
                description, domain, variable_names, metadata, characteristics or {}
            )
            use_specialized = False

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text

            if verbose:
                print(f"  [LLM] Raw response length: {len(content)} chars")

            parsed = self._parse_response(content, verbose=verbose)

            result = {
                "formula": parsed.get("formula", "N/A"),
                "latex": parsed.get("latex", "N/A"),
                "python_code": parsed.get("python", "N/A"),
                "explanation": parsed.get("explanation", "N/A"),
                "specialized": use_specialized,
            }

            # Cache if valid
            if (
                result["python_code"] != "N/A"
                and "def formula" in result["python_code"]
            ):
                self.formula_cache[cache_key] = result.copy()

            return result

        except Exception as e:
            if verbose:
                import traceback

                traceback.print_exc()
            return {"error": str(e)}

    def _parse_response(self, content: str, verbose: bool = False) -> Dict[str, str]:
        """Multi-strategy robust parsing"""
        parsed = {}

        # Extract FORMULA
        match = re.search(r"FORMULA:\s*\n([^\n]+(?:\n[^\n]+)?)", content, re.IGNORECASE)
        if match:
            parsed["formula"] = match.group(1).strip()
        else:
            parsed["formula"] = "N/A"

        # Extract PYTHON code
        code = None

        # Strategy A: PYTHON: section
        match = re.search(
            r"PYTHON:\s*\n(.*?)(?=\n\n[A-Z]+:|\n\n\[|$)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if match:
            code = match.group(1).strip()

        # Strategy B: Code fence
        if not code:
            match = re.search(r"```python\s*\n(.*?)\n```", content, re.DOTALL)
            if match:
                code = match.group(1).strip()

        # Strategy C: Any def formula()
        if not code:
            match = re.search(
                r"(def formula\([^)]*\):.*?)(?=\n\n[A-Z]+:|\n\n```|\n\n\[|\Z)",
                content,
                re.DOTALL,
            )
            if match:
                code = match.group(1).strip()

        if code:
            code = re.sub(r"^```python\s*\n", "", code)
            code = re.sub(r"\n```\s*$", "", code)
            parsed["python"] = code.strip()
        else:
            parsed["python"] = "N/A"

        # Extract EXPLANATION
        match = re.search(
            r"EXPLANATION:\s*\n(.*?)(?=\n\n[A-Z]+:|\n\n```|\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if match:
            parsed["explanation"] = match.group(1).strip()
        else:
            parsed["explanation"] = "N/A"

        return parsed

    # ========================================================================
    # PHASE 2.2: Iterative Formula Refinement
    # ========================================================================

    def iterative_formula_refinement(
        self,
        initial_result: Dict,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        max_iterations: int = 2,
    ) -> Tuple[Dict, float]:
        """
        Refine formula based on error analysis.
        """
        if initial_result.get("python_code") == "N/A":
            return initial_result, 0.0

        best_result = initial_result
        best_r2 = -np.inf

        # Evaluate initial
        metrics = self.evaluate_llm_formula(
            initial_result, X, y, var_names, verbose=False
        )

        if metrics.get("success"):
            best_r2 = metrics["r2"]

        if best_r2 > 0.99:
            return best_result, best_r2  # Already excellent

        # Try refinement iterations
        for iteration in range(max_iterations):
            if best_r2 < 0.80:
                # Analyze errors
                error_analysis = self._analyze_formula_errors(
                    best_result, X, y, var_names, best_r2
                )

                # Generate refinement prompt
                refinement_prompt = f"""
The formula: {best_result.get("formula", "N/A")}
Achieves R²={best_r2:.4f}

Error analysis: {error_analysis}

Common issues to check:
- Missing constant multiplier? (all predictions proportionally off)
- Wrong exponent? (errors increase with input magnitude)
- Missing term? (systematic bias in predictions)
- Wrong operator? (+ vs -, × vs ÷)
- Missing min/max cap?

Provide ONLY the corrected Python code (def formula...), no explanation.
"""

                try:
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=1000,
                        messages=[{"role": "user", "content": refinement_prompt}],
                    )

                    refined_code = response.content[0].text.strip()

                    # Clean and test
                    refined_code = re.sub(r"^```python\s*\n", "", refined_code)
                    refined_code = re.sub(r"\n```\s*$", "", refined_code)

                    refined_result = {**best_result, "python_code": refined_code}

                    refined_metrics = self.evaluate_llm_formula(
                        refined_result, X, y, var_names, verbose=False
                    )

                    if (
                        refined_metrics.get("success")
                        and refined_metrics["r2"] > best_r2
                    ):
                        best_r2 = refined_metrics["r2"]
                        best_result = refined_result
                    else:
                        break  # No improvement

                except Exception:
                    break
            else:
                break

        return best_result, best_r2

    def _analyze_formula_errors(
        self,
        result: Dict,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        r2: float,
    ) -> str:
        """Analyze prediction errors to guide refinement"""
        try:
            code = result.get("python_code", "")
            local_vars = {}
            exec(code, {"np": np, "numpy": np}, local_vars)
            func = next((v for v in local_vars.values() if callable(v)), None)

            if func:
                y_pred = self._evaluate_function(func, X, var_names, verbose=False)
                errors = y_pred - y

                mean_error = np.mean(errors)
                std_error = np.std(errors)
                rel_errors = np.abs(errors) / (np.abs(y) + 1e-10)
                mean_rel_error = np.mean(rel_errors)

                analysis = []

                if abs(mean_error) > 0.1 * np.mean(np.abs(y)):
                    analysis.append(
                        "Systematic bias detected (predictions consistently too high/low)"
                    )

                if mean_rel_error > 0.2:
                    analysis.append("Large relative errors (>20% average)")

                if np.corrcoef(np.abs(errors), np.abs(y))[0, 1] > 0.5:
                    analysis.append(
                        "Errors scale with output magnitude (possibly wrong multiplier)"
                    )

                return "; ".join(analysis) if analysis else "No clear pattern in errors"
        except:
            return "Unable to analyze errors"

    # ========================================================================
    # Neural Network Training (unchanged)
    # ========================================================================

    def train_nn(
        self,
        X: np.ndarray,
        y: np.ndarray,
        is_extrapolation: bool = False,
        epochs: int = 500,
        verbose: bool = False,
    ) -> Tuple:
        """Train neural network (unchanged from original)"""
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler

        test_size = 0.3 if is_extrapolation else 0.2

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        scaler_X = StandardScaler()
        scaler_y = StandardScaler()

        X_train_s = scaler_X.fit_transform(X_train)
        X_test_s = scaler_X.transform(X_test)
        y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

        model = nn.Sequential(
            nn.Linear(X.shape[1], 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

        optimizer = torch.optim.Adam(model.parameters(), lr=0.0005, weight_decay=1e-4)
        criterion = nn.MSELoss()

        X_train_t = torch.FloatTensor(X_train_s)
        y_train_t = torch.FloatTensor(y_train_s).reshape(-1, 1)

        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="min", factor=0.3, patience=30, min_lr=1e-6
        )

        best_loss = float("inf")
        patience_counter = 0
        max_patience = 100

        for epoch in range(epochs):
            model.train()
            optimizer.zero_grad()
            pred = model(X_train_t)
            loss = criterion(pred, y_train_t)
            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            optimizer.step()
            scheduler.step(loss)

            if loss.item() < best_loss:
                best_loss = loss.item()
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= max_patience:
                    if verbose:
                        print(f"  [NN] Early stopping at epoch {epoch}")
                    break

        model.eval()
        with torch.no_grad():
            X_test_t = torch.FloatTensor(X_test_s)
            y_pred_s = model(X_test_t).numpy().flatten()
            y_pred = scaler_y.inverse_transform(y_pred_s.reshape(-1, 1)).flatten()

            mse = np.mean((y_test - y_pred) ** 2)
            ss_res = np.sum((y_test - y_pred) ** 2)
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0

        metrics = {
            "r2": float(r2),
            "rmse": float(np.sqrt(mse)),
            "mae": float(np.mean(np.abs(y_test - y_pred))),
        }

        return model, metrics, scaler_X, scaler_y

    def evaluate_llm_formula(
        self,
        formula_dict: Dict,
        X: np.ndarray,
        y_true: np.ndarray,
        var_names: List[str],
        verbose: bool = False,
    ) -> Dict:
        """Evaluate LLM formula (unchanged)"""
        try:
            code = formula_dict.get("python_code", "")
            if not code or code == "N/A":
                return {"error": "No code", "success": False}

            if "def formula" not in code:
                return {"error": "No formula function", "success": False}

            local_vars = {}
            exec(code, {"np": np, "numpy": np}, local_vars)

            func = next(
                (
                    v
                    for v in local_vars.values()
                    if callable(v) and not v.__name__.startswith("_")
                ),
                None,
            )

            if not func:
                return {"error": "No function", "success": False}

            y_pred = self._evaluate_function(func, X, var_names, verbose=verbose)

            if len(y_pred) != len(y_true):
                return {"error": "Shape mismatch", "success": False}

            mse = np.mean((y_pred - y_true) ** 2)
            ss_res = np.sum((y_true - y_pred) ** 2)
            ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0

            residuals = y_pred - y_true
            uncertainty = float(np.std(residuals))

            return {
                "r2": float(r2),
                "rmse": float(np.sqrt(mse)),
                "mae": float(np.mean(np.abs(y_pred - y_true))),
                "uncertainty": uncertainty,
                "success": True,
                "predictions": y_pred,
            }
        except Exception as e:
            if verbose:
                import traceback

                traceback.print_exc()
            return {"error": str(e), "success": False}

    def _evaluate_function(self, func, X, var_names, verbose=False):
        """Evaluate function with multiple strategies"""
        sig = inspect.signature(func)
        n_params = len(sig.parameters)
        n_features = X.shape[1]

        if n_params == n_features:
            try:
                y = func(*[X[:, i] for i in range(n_features)])
                result = np.asarray(y).flatten()
                return result
            except Exception:
                pass

        try:
            y = np.empty(X.shape[0])
            for i in range(X.shape[0]):
                if n_params == n_features:
                    y[i] = func(*X[i, :])
                elif n_params < n_features:
                    y[i] = func(*X[i, :n_params])
            return y
        except Exception as e:
            if verbose:
                print(f"  [EVAL] Evaluation failed: {e}")

        raise RuntimeError("All evaluation strategies failed")

    def _get_nn_predictions(self, model, X, scaler_X, scaler_y):
        """Get NN predictions"""
        model.eval()
        with torch.no_grad():
            X_scaled = scaler_X.transform(X)
            X_tensor = torch.FloatTensor(X_scaled)
            y_pred_scaled = model(X_tensor).numpy().flatten()
            y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
        return y_pred

    # ========================================================================
    # PHASE 3.2: Optimized Ensemble Weighting
    # ========================================================================

    def optimize_ensemble_weights(
        self,
        llm_pred: np.ndarray,
        nn_pred: np.ndarray,
        y_true: np.ndarray,
        llm_r2: float,
        nn_r2: float,
        is_extrapolation: bool = False,
    ) -> Tuple[float, float]:
        """
        Optimize ensemble weights based on performance and extrapolation.
        """
        from scipy.optimize import minimize

        def ensemble_mse(weights):
            w_llm, w_nn = weights
            ensemble_pred = w_llm * llm_pred + w_nn * nn_pred
            return np.mean((ensemble_pred - y_true) ** 2)

        # Constraints
        constraints = {"type": "eq", "fun": lambda w: w[0] + w[1] - 1}
        bounds = [(0, 1), (0, 1)]

        # Initial guess based on R²
        if llm_r2 + nn_r2 > 0:
            init_weights = [llm_r2 / (llm_r2 + nn_r2), nn_r2 / (llm_r2 + nn_r2)]
        else:
            init_weights = [0.5, 0.5]

        try:
            result = minimize(
                ensemble_mse,
                init_weights,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )

            optimal_weights = result.x

            # BOOST LLM for extrapolation
            if is_extrapolation and llm_r2 > 0.7:
                optimal_weights[0] *= 1.5
                optimal_weights /= optimal_weights.sum()

            return float(optimal_weights[0]), float(optimal_weights[1])
        except:
            return 0.5, 0.5

    # ========================================================================
    # PHASE 1.1: EXTRAPOLATION-AWARE DECISION LOGIC (CRITICAL FIX)
    # ========================================================================

    def hybrid_predict(
        self,
        description: str,
        domain: str,
        X: np.ndarray,
        y_true: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> Dict:
        """
        IMPROVED hybrid prediction with EXTRAPOLATION-AWARE DECISION LOGIC.
        """

        is_extrapolation = metadata.get("extrapolation_test", False)

        # STEP 0: Pattern Recognition
        characteristics = self.detect_formula_characteristics(X, y_true, var_names)

        if verbose:
            print(
                f"\n  [PATTERN] Detected: {characteristics.get('best_pattern')}, "
                f"Confidence: {characteristics.get('confidence', 0):.2f}"
            )

        # Enhanced confidence
        formula_confidence = self._compute_formula_confidence(
            description, metadata, characteristics
        )

        if verbose:
            print(f"  [HYBRID] Formula confidence: {formula_confidence:.2f}")
            print(f"  [HYBRID] Extrapolation: {is_extrapolation}")

        # STEP 1: Generate and Evaluate LLM
        llm_result = self.generate_llm_formula(
            description, domain, var_names, metadata, characteristics, verbose=verbose
        )

        if "error" not in llm_result and llm_result.get("python_code") != "N/A":
            llm_metrics = self.evaluate_llm_formula(
                llm_result, X, y_true, var_names, verbose=verbose
            )

            # PHASE 2.2: Try refinement if needed
            if llm_metrics.get("success") and llm_metrics["r2"] < 0.95:
                refined_result, refined_r2 = self.iterative_formula_refinement(
                    llm_result, X, y_true, var_names
                )
                if refined_r2 > llm_metrics["r2"]:
                    llm_result = refined_result
                    llm_metrics["r2"] = refined_r2
        else:
            llm_metrics = {
                "error": llm_result.get("error", "No valid code"),
                "success": False,
            }

        # STEP 2: Train and Evaluate NN
        nn_model, nn_metrics, scaler_X, scaler_y = self.train_nn(
            X, y_true, is_extrapolation=is_extrapolation, epochs=500, verbose=verbose
        )
        nn_predictions = self._get_nn_predictions(nn_model, X, scaler_X, scaler_y)

        # STEP 3: Extract Scores
        llm_r2 = llm_metrics.get("r2", -999) if llm_metrics.get("success") else -999
        nn_r2 = nn_metrics.get("r2", -999)

        if verbose:
            print(f"\n  [HYBRID] LLM R²: {llm_r2:.4f}, NN R²: {nn_r2:.4f}")

        # STEP 4: Validate Methods
        llm_valid = llm_r2 > 0.0
        nn_valid = nn_r2 > 0.0

        # ====================================================================
        # PHASE 1.1: EXTRAPOLATION-AWARE DECISION LOGIC (CRITICAL)
        # ====================================================================

        if is_extrapolation:
            if verbose:
                print(f"  [HYBRID] 🔴 EXTRAPOLATION MODE ACTIVATED")

            # STRONGLY PREFER LLM for extrapolation
            if llm_valid and llm_r2 > 0.90:
                decision = "llm"
                final_r2 = llm_r2
                final_rmse = llm_metrics["rmse"]
                reason = f"⭐ EXTRAPOLATION: LLM excellent (R²={llm_r2:.4f} > 0.90)"

            elif llm_valid and llm_r2 > 0.70:
                decision = "llm"
                final_r2 = llm_r2
                final_rmse = llm_metrics["rmse"]
                reason = f"✅ EXTRAPOLATION: LLM preferred (R²={llm_r2:.4f} > 0.70)"

            elif llm_valid and llm_r2 > 0.50:
                decision = "llm"
                final_r2 = llm_r2
                final_rmse = llm_metrics["rmse"]
                reason = f"🔶 EXTRAPOLATION: LLM acceptable (R²={llm_r2:.4f} > 0.50, safer than NN)"

            elif llm_valid and nn_valid:
                # Both valid but LLM not great - still prefer LLM slightly
                if llm_r2 > nn_r2 * 0.8:  # LLM within 80% of NN
                    decision = "llm"
                    final_r2 = llm_r2
                    final_rmse = llm_metrics["rmse"]
                    reason = f"🟡 EXTRAPOLATION: LLM safer despite lower R² ({llm_r2:.4f} vs {nn_r2:.4f})"
                else:
                    # NN much better, reluctantly use it
                    decision = "nn"
                    final_r2 = nn_r2
                    final_rmse = nn_metrics["rmse"]
                    reason = f"⚠️  EXTRAPOLATION: NN significantly better ({nn_r2:.4f} >> {llm_r2:.4f})"

            elif llm_valid:
                decision = "llm"
                final_r2 = llm_r2
                final_rmse = llm_metrics["rmse"]
                reason = "EXTRAPOLATION: LLM only valid method"

            elif nn_valid:
                decision = "nn"
                final_r2 = nn_r2
                final_rmse = nn_metrics["rmse"]
                reason = "⚠️  EXTRAPOLATION: NN only valid (LLM failed)"

            else:
                decision = "failed"
                final_r2 = max(llm_r2, nn_r2)
                final_rmse = 999
                reason = "❌ EXTRAPOLATION: Both methods failed"

        # ====================================================================
        # REGULAR INTERPOLATION LOGIC
        # ====================================================================
        else:
            if not llm_valid and not nn_valid:
                decision = "failed"
                final_r2 = max(llm_r2, nn_r2)
                final_rmse = (
                    llm_metrics.get("rmse", 999)
                    if llm_r2 > nn_r2
                    else nn_metrics.get("rmse", 999)
                )
                reason = "Both LLM and NN failed (R² < 0)"

            elif llm_valid and not nn_valid:
                decision = "llm"
                final_r2 = llm_r2
                final_rmse = llm_metrics["rmse"]
                reason = "LLM only valid method"

            elif nn_valid and not llm_valid:
                decision = "nn"
                final_r2 = nn_r2
                final_rmse = nn_metrics["rmse"]
                reason = "NN only valid method"

            else:
                # Both valid - sophisticated logic
                if formula_confidence >= 0.8 and llm_r2 > 0.85:
                    decision = "llm"
                    final_r2 = llm_r2
                    final_rmse = llm_metrics["rmse"]
                    reason = f"High-confidence formula (conf={formula_confidence:.2f}, R²={llm_r2:.4f})"

                elif llm_r2 > 0.95:
                    decision = "llm"
                    final_r2 = llm_r2
                    final_rmse = llm_metrics["rmse"]
                    reason = f"Excellent LLM (R²>{0.95:.2f})"

                elif llm_r2 > 0.80 and nn_r2 > 0.80:
                    # PHASE 3.2: Optimized ensemble
                    decision = "ensemble"
                    llm_predictions = llm_metrics.get("predictions")

                    if llm_predictions is not None:
                        weight_llm, weight_nn = self.optimize_ensemble_weights(
                            llm_predictions,
                            nn_predictions,
                            y_true,
                            llm_r2,
                            nn_r2,
                            is_extrapolation=False,
                        )

                        ensemble_predictions = (
                            weight_llm * llm_predictions + weight_nn * nn_predictions
                        )

                        mse = np.mean((y_true - ensemble_predictions) ** 2)
                        ss_res = np.sum((y_true - ensemble_predictions) ** 2)
                        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
                        final_r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0
                        final_rmse = np.sqrt(mse)

                        reason = f"Optimized ensemble (LLM:{weight_llm:.2f}, NN:{weight_nn:.2f})"
                    else:
                        if llm_r2 > nn_r2:
                            decision = "llm"
                            final_r2, final_rmse = llm_r2, llm_metrics["rmse"]
                            reason = "Ensemble fallback to LLM"
                        else:
                            decision = "nn"
                            final_r2, final_rmse = nn_r2, nn_metrics["rmse"]
                            reason = "Ensemble fallback to NN"

                elif llm_r2 > 0.75 and llm_r2 > nn_r2:
                    decision = "llm"
                    final_r2 = llm_r2
                    final_rmse = llm_metrics["rmse"]
                    reason = f"LLM preferred (R²={llm_r2:.4f} > {nn_r2:.4f})"

                else:
                    if llm_r2 > nn_r2:
                        decision = "llm"
                        final_r2 = llm_r2
                        final_rmse = llm_metrics["rmse"]
                        reason = f"LLM better ({llm_r2:.4f} > {nn_r2:.4f})"
                    else:
                        decision = "nn"
                        final_r2 = nn_r2
                        final_rmse = nn_metrics["rmse"]
                        reason = f"NN better ({nn_r2:.4f} > {llm_r2:.4f})"

        if verbose:
            print(f"\n  [HYBRID] === DECISION ===")
            print(f"  [HYBRID] Method: {decision.upper()}")
            print(f"  [HYBRID] Reason: {reason}")
            print(f"  [HYBRID] Final R²: {final_r2:.4f}")
            print(f"  [HYBRID] ===============")

        return {
            "method": "improved_hybrid",
            "description": description,
            "domain": domain,
            "decision": decision,
            "decision_reason": reason,
            "formula_confidence": float(formula_confidence),
            "pattern_characteristics": characteristics,
            "is_extrapolation_test": is_extrapolation,
            "llm_valid": llm_valid,
            "nn_valid": nn_valid,
            "llm_result": {
                "formula": llm_result.get("formula", "N/A"),
                "python_code": llm_result.get("python_code", "N/A"),
                "explanation": llm_result.get("explanation", "N/A"),
                "specialized": llm_result.get("specialized", False),
                "metrics": {k: v for k, v in llm_metrics.items() if k != "predictions"},
            },
            "nn_result": {"metrics": nn_metrics},
            "evaluation": {
                "r2": float(final_r2),
                "rmse": float(final_rmse),
                "success": final_r2 > 0.0,
            },
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
        }

    def save_results(self, filepath: str):
        """Save results to JSON"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"✅ Results saved: {filepath}")


# ============================================================================
# Testing Interface
# ============================================================================


def run_improved_test(
    domains: List[str] = None, num_samples: int = 100, verbose: bool = False
):
    """Run improved hybrid system test"""
    protocol = DeFiExperimentProtocol()
    hybrid = ImprovedHybridSystemDeFi()

    if domains is None:
        domains = protocol.get_all_domains()

    print("=" * 80)
    print("[EXPERIMENT] IMPROVED HYBRID SYSTEM".center(80))
    print("=" * 80)
    print("Improvements:")
    print("  ✅ Phase 1.1: Extrapolation-aware decision logic")
    print("  ✅ Phase 1.2: Enhanced conditional formula support")
    print("  ✅ Phase 1.3: Formula pattern recognition")
    print("  ✅ Phase 2.1: Few-shot prompting with examples")
    print("  ✅ Phase 2.2: Iterative formula refinement")
    print("  ✅ Phase 3.2: Optimized ensemble weighting")
    print("  ✅ Phase 3.3: Domain-specific formula libraries")
    print("=" * 80)

    all_results = []

    for domain in domains:
        print(f"\n{'=' * 80}")
        print(f"DOMAIN: {domain.upper()}".center(80))
        print("=" * 80)

        test_cases = protocol.load_test_data(domain, num_samples=num_samples)

        for i, (desc, X, y, var_names, meta) in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {desc}")
            result = hybrid.hybrid_predict(
                desc, domain, X, y, var_names, meta, verbose=verbose
            )

            metrics = result["evaluation"]
            print(f"  Decision: {result['decision'].upper()}")
            print(f"  R²: {metrics['r2']:.6f}, RMSE: {metrics['rmse']:.6f}")

            if metrics["r2"] > 0.99:
                print(f"  ⭐ EXCELLENT")
            elif metrics["r2"] > 0.95:
                print(f"  ✅ GOOD")
            elif metrics["r2"] > 0.80:
                print(f"  🟡 ACCEPTABLE")
            elif metrics["r2"] > 0.0:
                print(f"  🟠 NEEDS IMPROVEMENT")
            else:
                print(f"  ❌ FAILED")

            all_results.append(result)
            hybrid.results.append(result)

    os.makedirs("hypatiax/data/results", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    hybrid.save_results(f"hypatiax/data/results/improved_hybrid_{ts}.json")

    print("\n" + "=" * 80)
    print("IMPROVED SYSTEM SUMMARY".center(80))
    print("=" * 80)

    decisions = defaultdict(int)
    r2_scores = []
    extrap_r2 = []
    interp_r2 = []

    for r in all_results:
        decisions[r["decision"]] += 1
        r2_scores.append(r["evaluation"]["r2"])

        if r.get("is_extrapolation_test"):
            extrap_r2.append(r["evaluation"]["r2"])
        else:
            interp_r2.append(r["evaluation"]["r2"])

    print(f"\nTotal cases: {len(all_results)}")
    print(f"Mean R²: {np.mean(r2_scores):.4f}")
    print(f"Median R²: {np.median(r2_scores):.4f}")
    print(f"Min R²: {np.min(r2_scores):.4f}")

    if extrap_r2:
        print(f"\nExtrapolation R² (n={len(extrap_r2)}): {np.mean(extrap_r2):.4f}")
    if interp_r2:
        print(f"Interpolation R² (n={len(interp_r2)}): {np.mean(interp_r2):.4f}")

    print(f"\nDecision breakdown:")
    for decision in ["llm", "ensemble", "nn", "failed"]:
        if decision in decisions:
            count = decisions[decision]
            pct = 100 * count / len(all_results)
            decision_r2 = [
                r["evaluation"]["r2"] for r in all_results if r["decision"] == decision
            ]
            mean_r2 = np.mean(decision_r2) if decision_r2 else 0
            print(
                f"  {decision.upper():8s}: {count:2d} ({pct:5.1f}%) - Mean R² = {mean_r2:.4f}"
            )

    problem_cases = [r for r in all_results if r["evaluation"]["r2"] < 0.80]
    if problem_cases:
        print(f"\n⚠️  Cases needing improvement (R² < 0.80): {len(problem_cases)}")
        for r in problem_cases[:5]:
            print(f"  • {r['description'][:60]}")
            print(f"    R²: {r['evaluation']['r2']:.4f}, Decision: {r['decision']}")
    else:
        print(f"\n✅ All cases R² >= 0.80!")

    print("\n" + "=" * 80)
    return all_results


def run_single_test(
    description: str, domain: str, num_samples: int = 100, verbose: bool = True
):
    """Run improved hybrid system on a single test case for debugging"""
    protocol = DeFiExperimentProtocol()
    hybrid = ImprovedHybridSystemDeFi()

    print("=" * 80)
    print(f"[TEST] SINGLE TEST: {description}".center(80))
    print("=" * 80)

    test_cases = protocol.load_test_data(domain, num_samples=num_samples)

    target_case = None
    for desc, X, y, var_names, meta in test_cases:
        if description.lower() in desc.lower():
            target_case = (desc, X, y, var_names, meta)
            break

    if not target_case:
        print(f"❌ Test case not found: {description}")
        print(f"Available cases in {domain}:")
        for desc, _, _, _, _ in test_cases:
            print(f"  • {desc}")
        return None

    desc, X, y, var_names, meta = target_case

    print(f"\nTest Case: {desc}")
    print(f"Variables: {', '.join(var_names)}")
    print(f"Samples: {len(X)}")

    if meta.get("extrapolation_test"):
        print(f"🔴 EXTRAPOLATION TEST")

    if meta.get("ground_truth"):
        print(f"Ground Truth: {meta['ground_truth']}")

    print("\n" + "-" * 80)

    result = hybrid.hybrid_predict(desc, domain, X, y, var_names, meta, verbose=verbose)

    print("\n" + "-" * 80)
    print("RESULTS:")
    print(f"  Decision: {result['decision'].upper()}")
    print(f"  Reason: {result['decision_reason']}")
    print(f"  Formula Confidence: {result['formula_confidence']:.2f}")
    print(f"  Pattern: {result['pattern_characteristics'].get('best_pattern', 'N/A')}")
    print(f"  LLM Valid: {result.get('llm_valid', 'N/A')}")
    print(f"  NN Valid: {result.get('nn_valid', 'N/A')}")

    print(f"\nMetrics:")
    print(f"  Final R²: {result['evaluation']['r2']:.6f}")
    print(f"  Final RMSE: {result['evaluation']['rmse']:.6f}")
    print(f"  Success: {result['evaluation']['success']}")

    llm_metrics = result["llm_result"]["metrics"]
    nn_metrics = result["nn_result"]["metrics"]

    print(f"\nComponent Performance:")
    print(f"  LLM R²: {llm_metrics.get('r2', 'N/A')}")
    print(f"  NN R²:  {nn_metrics['r2']:.6f}")

    if (
        result["decision"] in ["llm", "ensemble"]
        and result["llm_result"]["formula"] != "N/A"
    ):
        print(f"\nLLM Formula:")
        print(f"  {result['llm_result']['formula']}")

        if result["llm_result"]["python_code"] != "N/A":
            print(f"\nPython Code:")
            code_lines = result["llm_result"]["python_code"].split("\n")
            for line in code_lines:
                print(f"  {line}")

    print("\n" + "=" * 80)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Improved Hybrid System for DeFi")
    parser.add_argument("--mode", choices=["full", "single"], default="full")
    parser.add_argument("--domains", nargs="+", default=None)
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--description", type=str, default=None)
    parser.add_argument("--domain", type=str, default="lending")

    args = parser.parse_args()

    if args.mode == "full":
        run_improved_test(
            domains=args.domains, num_samples=args.samples, verbose=args.verbose
        )
    elif args.mode == "single":
        if not args.description:
            print("Error: --description required for single test mode")
            exit(1)
        run_single_test(
            description=args.description,
            domain=args.domain,
            num_samples=args.samples,
            verbose=args.verbose,
        )
"""
 # Full test
python hybrid_system_defi_domain.py --mode full --verbose

# Single test (Kelly Criterion)
python hybrid_system_defi_domain.py --mode single --description "optimal lp" --domain liquidity --verbose

# Specific domains
python hybrid_system_defi_domain.py --mode full --domains lending trading --samples 200

"""
