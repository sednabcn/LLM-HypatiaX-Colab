import json
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
from anthropic import Anthropic


class PureLLMBaseline:
    """
    Pure LLM baseline for formula discovery.
    Uses Claude to generate formulas from text descriptions without symbolic regression.
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize Pure LLM baseline.

        Args:
            model: Claude model to use
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.results = []

    def generate_formula(self, description: str, domain: str, variable_names: Optional[List[str]] = None) -> Dict:
        """
        Generate a mathematical formula using LLM.

        Args:
            description: Natural language description of the formula
            domain: Domain (e.g., 'defi', 'risk', 'physics')
            variable_names: Optional list of variable names to use

        Returns:
            Dictionary containing formula, implementation, and metadata
        """
        # Build enhanced prompt
        var_info = ""
        if variable_names:
            var_info = f"\nUse these variable names: {', '.join(variable_names)}"

        prompt = f"""You are a mathematical formula expert. Generate a precise mathematical formula for the following:

Description: {description}
Domain: {domain}{var_info}

Provide your response in this EXACT format:

FORMULA:
[Write the formula in standard mathematical notation]

LATEX:
[Write the formula in LaTeX notation]

PYTHON:
[Write a Python function that implements the formula]

VARIABLES:
[List each variable with its meaning and units]

ASSUMPTIONS:
[List any assumptions made in the formula]

EXPLANATION:
[Brief explanation of the formula and when to use it]

Be mathematically precise and use standard conventions for the {domain} domain."""

        try:
            response = self.client.messages.create(
                model=self.model, max_tokens=2000, messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            # Parse the structured response
            parsed = self._parse_response(content)

            return {
                "method": "pure_llm",
                "model": self.model,
                "description": description,
                "domain": domain,
                "formula": parsed.get("formula", "N/A"),
                "latex": parsed.get("latex", "N/A"),
                "python_code": parsed.get("python", "N/A"),
                "variables": parsed.get("variables", "N/A"),
                "assumptions": parsed.get("assumptions", "N/A"),
                "explanation": parsed.get("explanation", "N/A"),
                "raw_response": content,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "method": "pure_llm",
                "model": self.model,
                "description": description,
                "domain": domain,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _parse_response(self, content: str) -> Dict[str, str]:
        """
        Parse structured response from LLM.

        Args:
            content: Raw LLM response

        Returns:
            Dictionary of parsed sections
        """
        sections = {
            "formula": r"FORMULA:\s*\n(.*?)(?=\n\n|\nLATEX:|\Z)",
            "latex": r"LATEX:\s*\n(.*?)(?=\n\n|\nPYTHON:|\Z)",
            "python": r"PYTHON:\s*\n(.*?)(?=\n\n|\nVARIABLES:|\Z)",
            "variables": r"VARIABLES:\s*\n(.*?)(?=\n\n|\nASSUMPTIONS:|\Z)",
            "assumptions": r"ASSUMPTIONS:\s*\n(.*?)(?=\n\n|\nEXPLANATION:|\Z)",
            "explanation": r"EXPLANATION:\s*\n(.*?)(?=\Z)",
        }

        parsed = {}
        for key, pattern in sections.items():
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                parsed[key] = match.group(1).strip()
            else:
                parsed[key] = "N/A"

        return parsed

    def test_formula_accuracy(self, formula_dict: Dict, X: np.ndarray, y_true: np.ndarray) -> Dict:
        """
        Test formula accuracy against ground truth data.

        Args:
            formula_dict: Dictionary containing formula information
            X: Input features
            y_true: True output values

        Returns:
            Dictionary of evaluation metrics
        """
        try:
            # Extract Python code
            python_code = formula_dict.get("python_code", "")

            # Try to execute the Python function
            # This is a simplified approach - in practice you'd need more robust execution
            local_vars = {}
            exec(python_code, {"np": np}, local_vars)

            # Find the function (assume it's the first function defined)
            func = None
            for var in local_vars.values():
                if callable(var):
                    func = var
                    break

            if func is None:
                return {"error": "No callable function found in Python code"}

            # Evaluate on data
            if X.shape[1] == 1:
                y_pred = func(X[:, 0])
            elif X.shape[1] == 2:
                y_pred = func(X[:, 0], X[:, 1])
            elif X.shape[1] == 3:
                y_pred = func(X[:, 0], X[:, 1], X[:, 2])
            else:
                # Generic approach
                y_pred = func(*[X[:, i] for i in range(X.shape[1])])

            y_pred = np.array(y_pred)

            # Calculate metrics
            mse = np.mean((y_pred - y_true) ** 2)
            mae = np.mean(np.abs(y_pred - y_true))

            # R² score
            ss_res = np.sum((y_true - y_pred) ** 2)
            ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            # RMSE
            rmse = np.sqrt(mse)

            return {"mse": float(mse), "mae": float(mae), "rmse": float(rmse), "r2": float(r2), "success": True}

        except Exception as e:
            return {"error": str(e), "success": False}

    def save_results(self, filepath: str):
        """Save results to JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to: {filepath}")


def load_test_data(domain: str) -> List[Tuple[str, np.ndarray, np.ndarray, List[str]]]:
    """
    Load test data for evaluation.

    Args:
        domain: Domain to load data for

    Returns:
        List of (description, X, y, variable_names) tuples
    """
    test_cases = []

    if domain == "defi":
        # Impermanent Loss
        price_ratio = np.random.uniform(0.5, 2.0, 100)
        X = price_ratio.reshape(-1, 1)
        y = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1
        test_cases.append(("Impermanent loss in constant product AMM", X, y, ["price_ratio"]))

        # Liquidation Price (Long)
        leverage = np.random.uniform(2, 20, 100)
        entry = np.random.uniform(1000, 5000, 100)
        maint = np.random.uniform(0.03, 0.10, 100)
        X = np.column_stack([leverage, entry, maint])
        y = entry * (1 - 1 / leverage + maint)
        test_cases.append(
            ("Liquidation price for leveraged long position", X, y, ["leverage", "entry_price", "maintenance_margin"])
        )

    elif domain == "risk":
        # VaR 95%
        mu = np.random.uniform(-0.1, 0.1, 100)
        sigma = np.random.uniform(0.1, 0.5, 100)
        X = np.column_stack([mu, sigma])
        y = mu - 1.96 * sigma
        test_cases.append(("Value at Risk at 95% confidence", X, y, ["mu", "sigma"]))

        # Sharpe Ratio
        returns = np.random.uniform(-0.1, 0.3, 100)
        rf = np.random.uniform(0.01, 0.05, 100)
        vol = np.random.uniform(0.1, 0.3, 100)
        X = np.column_stack([returns, rf, vol])
        y = (returns - rf) / vol
        test_cases.append(("Sharpe ratio for risk-adjusted returns", X, y, ["returns", "risk_free_rate", "volatility"]))

    return test_cases


def run_comprehensive_test(domains: List[str] = ["defi", "risk"]):
    """
    Run comprehensive test of pure LLM baseline.

    Args:
        domains: List of domains to test
    """
    baseline = PureLLMBaseline()

    print("=" * 70)
    print("Pure LLM Baseline Evaluation".center(70))
    print("=" * 70)

    all_results = []

    for domain in domains:
        print(f"\n{'Testing Domain: ' + domain.upper():^70}")
        print("-" * 70)

        test_cases = load_test_data(domain)

        for i, (description, X, y_true, var_names) in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {description}")

            # Generate formula
            start_time = time.time()
            result = baseline.generate_formula(description, domain, var_names)
            generation_time = time.time() - start_time

            result["generation_time"] = generation_time

            # Test accuracy
            print(f"  Generated formula in {generation_time:.2f}s")
            print(f"  Formula: {result.get('formula', 'N/A')[:80]}...")

            # Evaluate accuracy
            metrics = baseline.test_formula_accuracy(result, X, y_true)
            result["evaluation"] = metrics

            if metrics.get("success"):
                print(f"  R² Score: {metrics['r2']:.4f}")
                print(f"  RMSE: {metrics['rmse']:.6f}")
            else:
                print(f"  ⚠ Evaluation failed: {metrics.get('error', 'Unknown error')}")

            all_results.append(result)
            baseline.results.append(result)

            # Small delay to avoid rate limits
            time.sleep(1)

    # Save results
    os.makedirs("results", exist_ok=True)
    baseline.save_results("results/baseline_pure_llm.json")

    # Print summary
    print("\n" + "=" * 70)
    print("Summary".center(70))
    print("=" * 70)

    successful = sum(1 for r in all_results if r.get("evaluation", {}).get("success"))
    total = len(all_results)

    print(f"\nTotal test cases: {total}")
    print(f"Successfully evaluated: {successful}/{total} ({100*successful/total:.1f}%)")

    # Calculate average R² for successful cases
    r2_scores = [r["evaluation"]["r2"] for r in all_results if r.get("evaluation", {}).get("success")]
    if r2_scores:
        print(f"Average R² score: {np.mean(r2_scores):.4f}")
        print(f"Median R² score: {np.median(r2_scores):.4f}")

    print(f"\nResults saved to: results/baseline_pure_llm.json")
    print("=" * 70)


if __name__ == "__main__":
    # Run comprehensive test
    run_comprehensive_test(domains=["defi", "risk"])

    # Optional: Test individual formula
    # baseline = PureLLMBaseline()
    # result = baseline.generate_formula(
    #     "Expected Shortfall (CVaR) at 95%",
    #     "risk",
    #     variable_names=['mu', 'sigma']
    # )
    # print(json.dumps(result, indent=2))
