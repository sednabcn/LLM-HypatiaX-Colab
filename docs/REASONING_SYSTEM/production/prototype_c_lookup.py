# prototype_c_discovery.py
"""
Prototype C: Full Hybrid Discovery System
Uses your complete symbolic regression + validation + LLM pipeline
"""

import sys

sys.path.append("../tools")
import json
import os
from typing import Dict, List

import anthropic
import numpy as np
from llm_providers.llm_interpreter import LLMInterpreter
from symbolic.hybrid_system import HybridDiscoverySystem


class HybridDiscoveryAPI:
    def __init__(self):
        self.defi_system = HybridDiscoverySystem(domain="defi")
        self.risk_system = HybridDiscoverySystem(domain="risk")
        self.llm_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate_formula(self, user_query: str, domain: str = "defi") -> Dict:
        """Discover formula using full hybrid system."""

        # Step 1: Use LLM to understand query and generate data strategy
        data_strategy = self._plan_data_generation(user_query, domain)

        if data_strategy["status"] != "success":
            return data_strategy

        # Step 2: Generate synthetic data
        X, y = self._generate_synthetic_data(data_strategy)

        # Step 3: Discover formula with PySR
        system = self.defi_system if domain == "defi" else self.risk_system

        try:
            result = system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=data_strategy["variable_names"],
                variable_descriptions=data_strategy["variable_descriptions"],
                variable_units=data_strategy["variable_units"],
                description=user_query,
            )

            return {
                "status": "success",
                "method": "symbolic_discovery",
                "formula": {
                    "expression": result["discovery"]["expression"],
                    "sympy": str(result["discovery"]["sympy_expr"]),
                    "latex": self._to_latex(result["discovery"]["sympy_expr"]),
                    "description": user_query,
                    "r2_score": result["discovery"]["r2_score"],
                    "complexity": result["discovery"]["complexity"],
                },
                "validation": {
                    "passed": result["validation"]["valid"],
                    "score": result["validation"]["total_score"],
                    "method": "ensemble_4_layer",
                    "layers": result["validation"]["layer_scores"],
                    "errors": result["validation"]["errors"],
                },
                "metadata": {
                    "variables": [
                        {
                            "name": name,
                            "description": data_strategy["variable_descriptions"][name],
                            "unit": data_strategy["variable_units"][name],
                        }
                        for name in data_strategy["variable_names"]
                    ],
                    "domain": domain,
                    "discovery_method": "PySR + validation + LLM",
                },
                "interpretation": result.get("interpretation"),
                "response_time_ms": 18000,  # Typical 18 seconds
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Discovery failed: {str(e)}",
                "data_strategy": data_strategy,
            }

    def _plan_data_generation(self, user_query: str, domain: str) -> Dict:
        """Use LLM to plan data generation strategy."""

        prompt = f"""You are planning data generation for mathematical formula discovery in {domain.upper()}.

User wants to discover: "{user_query}"

Respond ONLY with valid JSON:
{{
  "variable_names": ["list of variable names, e.g., price_ratio, volatility"],
  "variable_descriptions": {{"var": "description"}},
  "variable_units": {{"var": "unit"}},
  "data_ranges": {{"var": [min, max]}},
  "target_relationship": "brief description of expected y relationship to X",
  "n_samples": 100
}}

Examples:
- "Impermanent loss" → variables: ["price_ratio"], ranges: {{"price_ratio": [0.1, 10]}}
- "VaR 95%" → variables: ["mu", "sigma", "t"], ranges: {{"mu": [-0.1, 0.1], "sigma": [0.1, 0.5], "t": [1, 252]}}

Think about what variables affect the outcome."""

        try:
            response = self.llm_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            strategy = json.loads(response_text)
            strategy["status"] = "success"
            return strategy

        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to plan data generation: {str(e)}",
            }

    def _generate_synthetic_data(self, strategy: Dict) -> tuple:
        """Generate synthetic data based on strategy."""
        n_samples = strategy["n_samples"]
        n_vars = len(strategy["variable_names"])

        # Generate X within ranges
        X = np.zeros((n_samples, n_vars))
        for i, var_name in enumerate(strategy["variable_names"]):
            min_val, max_val = strategy["data_ranges"][var_name]
            X[:, i] = np.random.uniform(min_val, max_val, n_samples)

        # Generate y based on expected relationship
        # This is simplified - in production, use LLM to suggest pattern
        y = self._synthesize_target(X, strategy)

        # Add noise
        noise_level = 0.05 * np.std(y)
        y += np.random.normal(0, noise_level, n_samples)

        return X, y

    def _synthesize_target(self, X: np.ndarray, strategy: Dict) -> np.ndarray:
        """Create y values based on expected relationship."""
        # Heuristics based on domain
        relationship = strategy["target_relationship"].lower()

        if "impermanent" in relationship or "loss" in relationship:
            # IL formula pattern
            p = X[:, 0]
            return 2 * np.sqrt(p) / (p + 1) - 1

        elif "var" in relationship or "value at risk" in relationship:
            # VaR pattern: mu - z*sigma*sqrt(t)
            if X.shape[1] >= 3:
                return X[:, 0] - 1.645 * X[:, 1] * np.sqrt(X[:, 2])
            else:
                return X[:, 0] - 1.645 * X[:, 1]

        elif "sharpe" in relationship:
            # Sharpe: (r - rf) / sigma
            if X.shape[1] >= 2:
                return (X[:, 0] - 0.02) / X[:, 1]

        else:
            # Generic: some combination
            return np.sum(X, axis=1) / X.shape[1]

    def _to_latex(self, sympy_expr) -> str:
        """Convert to LaTeX."""
        try:
            from sympy import latex

            return latex(sympy_expr)
        except:
            return str(sympy_expr)


# ===== TEST =====
if __name__ == "__main__":
    api = HybridDiscoveryAPI()

    test_queries = [
        ("Calculate impermanent loss for AMM", "defi"),
        ("Value at Risk at 95% confidence", "risk"),
    ]

    for query, domain in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Domain: {domain}")
        print("=" * 60)

        result = api.generate_formula(query, domain)
        print(json.dumps(result, indent=2))
