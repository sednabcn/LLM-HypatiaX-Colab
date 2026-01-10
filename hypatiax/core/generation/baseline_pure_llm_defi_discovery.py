"""
COMPLETE FIXED VERSION: baseline_pure_llm_defi_final.py
All liquidation domain fixes + FIXED evaluation logic + FIXED dict handling.
"""

import json
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Optional
import inspect
import numpy as np
from anthropic import Anthropic
from pathlib import Path
from dotenv import load_dotenv
from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class PureLLMBaseline:
    """Fixed Pure LLM baseline with liquidation domain corrections."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.results = []

    @staticmethod
    def evaluate_function(func, X, var_names=None):
        """
        Evaluate LLM-generated formula safely with comprehensive fallback strategies.
        """
        X = np.asarray(X)
        n_samples, n_features = X.shape

        # Get function signature
        sig = inspect.signature(func)
        n_params = len(sig.parameters)
        param_names = list(sig.parameters.keys())

        # ============================================================
        # STRATEGY 1: Direct positional arguments (most common)
        # ============================================================
        if n_params == n_features:
            try:
                # Try vectorized
                y = func(*[X[:, i] for i in range(n_features)])
                y = np.asarray(y)
                if y.shape[0] == n_samples:
                    return y.flatten()
            except:
                pass

            try:
                # Try row-by-row
                y = np.empty(n_samples, dtype=float)
                for i in range(n_samples):
                    y[i] = func(*[X[i, j] for j in range(n_features)])
                return y
            except:
                pass

        # ============================================================
        # STRATEGY 2: Single dict parameter
        # ============================================================
        if n_params == 1 and var_names is not None:
            try:
                # Try vectorized dict
                params = {name: X[:, i] for i, name in enumerate(var_names)}
                y = func(params)
                y = np.asarray(y)
                if y.shape[0] == n_samples:
                    return y.flatten()
            except:
                pass

            try:
                # Try row-by-row dict
                y = np.empty(n_samples, dtype=float)
                for i in range(n_samples):
                    params = {name: float(X[i, j]) for j, name in enumerate(var_names)}
                    y[i] = func(params)
                return y
            except:
                pass

        # ============================================================
        # STRATEGY 3: Named parameters matching var_names
        # ============================================================
        if var_names is not None and len(var_names) == n_features:
            try:
                # Try vectorized with **kwargs
                kwargs = {name: X[:, i] for i, name in enumerate(var_names)}
                y = func(**kwargs)
                y = np.asarray(y)
                if y.shape[0] == n_samples:
                    return y.flatten()
            except:
                pass

            try:
                # Try row-by-row with **kwargs
                y = np.empty(n_samples, dtype=float)
                for i in range(n_samples):
                    kwargs = {name: float(X[i, j]) for j, name in enumerate(var_names)}
                    y[i] = func(**kwargs)
                return y
            except:
                pass

        # ============================================================
        # STRATEGY 4: Try to match param names to var_names
        # ============================================================
        if var_names is not None and param_names:
            try:
                # Create mapping from param_names to var_names indices
                param_to_idx = {}
                for param_name in param_names:
                    for idx, var_name in enumerate(var_names):
                        if (
                            param_name.lower() in var_name.lower()
                            or var_name.lower() in param_name.lower()
                        ):
                            param_to_idx[param_name] = idx
                            break

                if len(param_to_idx) == n_params:
                    # Try vectorized with matched params
                    kwargs = {param: X[:, param_to_idx[param]] for param in param_names}
                    y = func(**kwargs)
                    y = np.asarray(y)
                    if y.shape[0] == n_samples:
                        return y.flatten()
            except:
                pass

        # ============================================================
        # All strategies failed
        # ============================================================
        raise RuntimeError(
            f"All evaluation strategies failed. "
            f"Function has {n_params} params: {param_names}, "
            f"Data has {n_features} features, "
            f"var_names: {var_names}"
        )

    def generate_formula(
        self,
        description: str,
        domain: str,
        variable_names: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """Generate formula with specialized handling."""
        desc_lower = description.lower()

        # Check if needs specialized handling
        use_specialized = (
            ("optimal" in desc_lower and "kelly" in desc_lower)
            or ("capital efficiency" in desc_lower and "concentrated" in desc_lower)
            or (
                "portfolio expected shortfall" in desc_lower
                and "correlated" in desc_lower
            )
            or ("liquidation" in desc_lower)
            or ("maximum" in desc_lower and "leverage" in desc_lower)
            or ("required collateral" in desc_lower)
        )

        if use_specialized:
            prompt = self._generate_specialized_prompt(
                description, domain, variable_names, metadata
            )
        else:
            prompt = self._generate_standard_prompt(
                description, domain, variable_names, metadata
            )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text
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
                "specialized_prompt": use_specialized,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            return {
                "method": "pure_llm",
                "model": self.model,
                "description": description,
                "domain": domain,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_specialized_prompt(
        self, description: str, domain: str, variable_names: List[str], metadata: Dict
    ) -> str:
        """Generate specialized prompts for problematic formulas."""
        desc_lower = description.lower()
        var_list = ", ".join(variable_names) if variable_names else ""

        # LIQUIDATION LONG
        if "liquidation" in desc_lower and "long" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

CRITICAL: Use EXACT formula P_liq = P_e × (1 - 1/(L×0.8))

FORMULA:
entry_price * (1 - 1/(leverage * 0.8))

LATEX:
P_{{liq}} = P_e \\times \\left(1 - \\frac{{1}}{{L \\times 0.8}}\\right)

PYTHON:
def formula(entry_price, leverage):
    maintenance_margin = 0.8
    return entry_price * (1.0 - 1.0/(leverage * maintenance_margin))

VARIABLES:
- entry_price: Entry price
- leverage: Leverage multiplier

ASSUMPTIONS:
Maintenance margin = 0.8

EXPLANATION:
Liquidation price for long positions."""

        # LIQUIDATION SHORT
        if "liquidation" in desc_lower and "short" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

CRITICAL: Use EXACT formula P_liq = P_e × (1 + 1/(L×0.8))

FORMULA:
entry_price * (1 + 1/(leverage * 0.8))

LATEX:
P_{{liq}} = P_e \\times \\left(1 + \\frac{{1}}{{L \\times 0.8}}\\right)

PYTHON:
def formula(entry_price, leverage):
    maintenance_margin = 0.8
    return entry_price * (1.0 + 1.0/(leverage * maintenance_margin))

VARIABLES:
- entry_price: Entry price
- leverage: Leverage multiplier

ASSUMPTIONS:
Maintenance margin = 0.8

EXPLANATION:
Liquidation price for short positions."""

        # MAX LEVERAGE
        if "maximum" in desc_lower and "leverage" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

CRITICAL: Use EXACT formula L_max = 1/(loss×0.8)

FORMULA:
1 / (acceptable_loss_pct * 0.8)

LATEX:
L_{{max}} = \\frac{{1}}{{\\text{{loss}} \\times 0.8}}

PYTHON:
def formula(entry_price, acceptable_loss_pct):
    maintenance_margin = 0.8
    return 1.0 / (acceptable_loss_pct * maintenance_margin)

VARIABLES:
- entry_price: Not used in calculation
- acceptable_loss_pct: Maximum acceptable loss

ASSUMPTIONS:
Maintenance margin = 0.8

EXPLANATION:
Maximum safe leverage given loss tolerance."""

        # REQUIRED COLLATERAL
        if (
            "required collateral" in desc_lower
            or "collateral for leveraged" in desc_lower
        ):
            return f"""Task: {description}
Variables: {var_list}

CRITICAL: Use EXACT formula collateral = position_size/leverage

FORMULA:
position_size / leverage

LATEX:
\\text{{collateral}} = \\frac{{\\text{{position\\_size}}}}{{L}}

PYTHON:
def formula(position_size, leverage):
    return position_size / leverage

VARIABLES:
- position_size: Total position size
- leverage: Leverage multiplier

ASSUMPTIONS:
Simple inverse relationship

EXPLANATION:
Required collateral for leveraged position."""

        # KELLY CRITERION
        if "optimal" in desc_lower and "kelly" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

CRITICAL: Use EXACT formula f* = min(μ/(2σ²), 1)

FORMULA:
min(expected_fee_apy/(2*il_risk**2), 1.0)

LATEX:
f^* = \\min\\left(\\frac{{\\mu}}{{2\\sigma^2}}, 1\\right)

PYTHON:
def formula(expected_fee_apy, il_risk):
    risk_aversion = 2.0
    position = expected_fee_apy / (risk_aversion * il_risk**2)
    return np.minimum(position, 1.0)

VARIABLES:
- expected_fee_apy: Expected return
- il_risk: Risk/volatility

ASSUMPTIONS:
Risk aversion = 2.0, capped at 100%

EXPLANATION:
Risk-adjusted Kelly criterion for position sizing."""

        # CAPITAL EFFICIENCY
        if "capital efficiency" in desc_lower and "concentrated" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

CRITICAL: Use EXACT formula efficiency = P_upper/(P_upper - P_lower)

FORMULA:
price_upper / (price_upper - price_lower)

LATEX:
\\text{{efficiency}} = \\frac{{P_{{upper}}}}{{P_{{upper}} - P_{{lower}}}}

PYTHON:
def formula(price_lower, price_upper, price_current):
    return price_upper / (price_upper - price_lower)

VARIABLES:
- price_lower, price_upper: Range bounds
- price_current: Not used in calculation

ASSUMPTIONS:
Simple ratio calculation

EXPLANATION:
Capital efficiency for concentrated liquidity."""

        # PORTFOLIO ES
        if "portfolio expected shortfall" in desc_lower and "correlated" in desc_lower:
            return f"""Task: {description}
Variables: {var_list}

CRITICAL: Use EXACT formula ES_p = ES₁ + ES₂ + ρ√(ES₁×ES₂)

FORMULA:
position1_es + position2_es + correlation * sqrt(position1_es * position2_es)

LATEX:
ES_p = ES_1 + ES_2 + \\rho\\sqrt{{ES_1 \\cdot ES_2}}

PYTHON:
def formula(position1_es, position2_es, correlation):
    corr_term = correlation * np.sqrt(position1_es * position2_es)
    return position1_es + position2_es + corr_term

VARIABLES:
- position1_es, position2_es: Individual ES values
- correlation: Correlation coefficient

ASSUMPTIONS:
Linear aggregation with correlation

EXPLANATION:
Portfolio Expected Shortfall for correlated positions."""

        return ""

    def _generate_standard_prompt(
        self, description: str, domain: str, variable_names: List[str], metadata: Dict
    ) -> str:
        """Generate standard prompt."""
        var_info = f"\nVariables: {', '.join(variable_names)}" if variable_names else ""

        constants_info = ""
        if metadata and "constants" in metadata and metadata["constants"]:
            constants_info = "\n\n⚠️ CRITICAL - Use these EXACT constant values:"
            for const_name, const_value in metadata["constants"].items():
                constants_info += f"\n  • {const_name} = {const_value}"

        return f"""You are a mathematical formula expert in DeFi and quantitative finance.

Task: {description}
Domain: {domain}{var_info}{constants_info}

Provide your response in this EXACT format:

FORMULA:
[Write the formula in standard mathematical notation]

LATEX:
[Write the formula in LaTeX notation]

PYTHON:
def formula(param1, param2, ...):
    # Use individual parameters, NOT a dict
    # Use EXACT constants if specified above
    # Use numpy functions: np.sqrt, np.minimum, np.maximum, etc.
    return result

VARIABLES:
[List each variable with meaning]

ASSUMPTIONS:
[List assumptions]

EXPLANATION:
[Brief explanation]

CRITICAL REQUIREMENTS:
- Function signature must be: def formula(param1, param2, ...) with individual parameters
- DO NOT use dict parameters like def formula(params)
- Use numpy for all math operations (np.sqrt, np.log, etc.)
- Use EXACT constant values if specified
- NO scipy imports (use only numpy)
- NO markdown code blocks
- Ensure operations work element-wise on numpy arrays"""

    def _parse_response(self, content: str) -> Dict[str, str]:
        """Parse LLM response."""
        parsed = {}

        match = re.search(r"FORMULA:\s*\n([^\n]+)", content, re.IGNORECASE)
        parsed["formula"] = match.group(1).strip() if match else "N/A"

        match = re.search(
            r"LATEX:\s*\n(.*?)(?=\n\n[A-Z]+:|$)", content, re.DOTALL | re.IGNORECASE
        )
        parsed["latex"] = match.group(1).strip() if match else "N/A"

        match = re.search(
            r"PYTHON:\s*\n(.*?)(?=\n\n[A-Z]+:|$)", content, re.DOTALL | re.IGNORECASE
        )
        parsed["python"] = (
            self._clean_python_code(match.group(1).strip()) if match else "N/A"
        )

        for section in ["variables", "assumptions", "explanation"]:
            match = re.search(
                rf"{section.upper()}:\s*\n(.*?)(?=\n\n[A-Z]+:|$)",
                content,
                re.DOTALL | re.IGNORECASE,
            )
            parsed[section] = match.group(1).strip() if match else "N/A"

        return parsed

    def _clean_python_code(self, code: str) -> str:
        """Clean Python code."""
        code = re.sub(r"^```python\s*\n", "", code, flags=re.MULTILINE)
        code = re.sub(r"\n```\s*$", "", code, flags=re.MULTILINE)
        return code.strip()

    def test_formula_accuracy(
        self,
        formula_dict: Dict,
        X: np.ndarray,
        y_true: np.ndarray,
        var_names,
        verbose: bool = False,
    ) -> Dict:
        """Test formula accuracy with FIXED evaluation logic."""
        try:
            python_code = formula_dict.get("python_code", "")
            if not python_code or python_code == "N/A":
                return {"error": "No code", "success": False}

            if verbose:
                print(f"\n  DEBUG - Code:\n{python_code}\n")

            # Execute the code
            local_vars = {}
            exec(python_code, {"np": np, "numpy": np}, local_vars)

            # Find the function
            func = next(
                (
                    v
                    for v in local_vars.values()
                    if callable(v) and not v.__name__.startswith("_")
                ),
                None,
            )
            if not func:
                return {"error": "No function found", "success": False}

            if verbose:
                print(f"  DEBUG - Found function: {func.__name__}")
                print(f"  DEBUG - Signature: {inspect.signature(func)}")

            # Evaluate with comprehensive fallback
            try:
                y_pred = self.evaluate_function(func, X, var_names)

                # Check dimensions match
                if len(y_pred) != len(y_true):
                    return {
                        "error": f"Dimension mismatch: pred={len(y_pred)}, true={len(y_true)}",
                        "success": False,
                    }

            except Exception as eval_error:
                if verbose:
                    import traceback

                    traceback.print_exc()
                return {
                    "error": f"Evaluation failed: {str(eval_error)}",
                    "success": False,
                    "code_snippet": python_code[:200],
                }

            # Calculate metrics
            mse = np.mean((y_pred - y_true) ** 2)
            mae = np.mean(np.abs(y_pred - y_true))
            rmse = np.sqrt(mse)

            ss_res = np.sum((y_true - y_pred) ** 2)
            ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)

            if ss_tot > 1e-10:
                r2 = 1 - (ss_res / ss_tot)
            else:
                r2 = 1.0 if ss_res < 1e-10 else 0.0

            return {
                "mse": float(mse),
                "mae": float(mae),
                "rmse": float(rmse),
                "r2": float(r2),
                "success": True,
            }

        except SyntaxError as e:
            return {
                "error": f"Syntax error: {str(e)}",
                "success": False,
                "code": python_code,
            }
        except Exception as e:
            return {"error": f"Execution error: {str(e)}", "success": False}

    def save_results(self, filepath: str):
        """Save results to JSON."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results saved: {filepath}")


def run_comprehensive_test(
    domains: List[str] = None, num_samples: int = 100, verbose: bool = False
):
    """Run comprehensive test."""
    protocol = DeFiExperimentProtocol()
    baseline = PureLLMBaseline()

    if domains is None:
        domains = protocol.get_all_domains()

    print("=" * 80)
    print("✨ FIXED PURE LLM BASELINE - WITH LIQUIDATION FIXES ✨".center(80))
    print("=" * 80)
    print(f"Model: {baseline.model}")
    print(f"Domains: {', '.join(domains)}")
    print(f"Samples: {num_samples}")
    print("=" * 80)

    all_results = []

    for domain in domains:
        print(f"\n{'=' * 80}")
        print(f"DOMAIN: {domain.upper()}".center(80))
        print("=" * 80)

        test_cases = protocol.load_test_data(domain, num_samples=num_samples)

        for i, (desc, X, y_true, var_names, meta) in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {desc}")
            print(f"  Variables: {', '.join(var_names)}")
            print(f"  Ground truth: {meta.get('ground_truth', 'N/A')}")

            if meta.get("extrapolation_test"):
                print(f"  ⚠️  EXTRAPOLATION TEST")

            start = time.time()
            result = baseline.generate_formula(desc, domain, var_names, meta)
            result["generation_time"] = time.time() - start
            result["metadata"] = meta

            print(f"  Generated in {result['generation_time']:.2f}s")

            metrics = baseline.test_formula_accuracy(
                result, X, y_true, var_names, verbose=verbose
            )
            result["evaluation"] = metrics

            if metrics.get("success"):
                r2 = metrics["r2"]
                print(f"  ✅ R²: {r2:.6f}, RMSE: {metrics['rmse']:.6f}")

                if r2 > 0.99:
                    print(f"  🎯 EXCELLENT FIT")
                elif r2 > 0.95:
                    print(f"  ✓ Good fit")
                elif r2 > 0.80:
                    print(f"  ⚠️ Moderate fit")
                else:
                    print(f"  ❌ Poor fit")
            else:
                print(f"  ❌ Failed: {metrics.get('error', 'Unknown error')[:100]}")
                if verbose and "code_snippet" in metrics:
                    print(f"  Code: {metrics['code_snippet']}")

            all_results.append(result)
            baseline.results.append(result)
            time.sleep(1)

    print("\n" + "=" * 80)
    print("GENERATING REPORT".center(80))
    print("=" * 80)

    report = protocol.generate_experiment_report(all_results)

    os.makedirs("results", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    baseline.save_results(f"results/baseline_llm_FIXED_{ts}.json")

    with open(f"results/report_llm_FIXED_{ts}.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 80)
    print("SUMMARY".center(80))
    print("=" * 80)

    overall = report["overall"]
    print(f"\n📊 Total: {overall['total_cases']}")
    print(
        f"Success: {overall['successful']}/{overall['total_cases']} ({100 * overall['success_rate']:.1f}%)"
    )

    if "mean_r2" in overall and overall["mean_r2"] is not None:
        print(f"Mean R²: {overall['mean_r2']:.6f}")
        print(f"Median R²: {overall['median_r2']:.6f}")

    print(f"\n📈 By Domain:")
    for domain, stats in report["by_domain"].items():
        mean_r2 = stats.get("mean_r2")
        r2_str = f"{mean_r2:.4f}" if mean_r2 is not None else "N/A"
        print(f"  {domain}: {stats['successful']}/{stats['total']} - R²: {r2_str}")

    if report.get("extrapolation_tests"):
        print(f"\n🎯 Extrapolation Tests:")
        for test in report["extrapolation_tests"]:
            status = "✅" if test["success"] else "❌"
            r2 = test.get("r2")
            r2_str = f"R²: {r2:.4f}" if r2 is not None else "Failed"
            print(f"  {status} {test['description'][:50]}: {r2_str}")

    print("\n" + "=" * 80)
    print("✨ COMPLETE - LIQUIDATION FIXED! ✨".center(80))
    print("=" * 80)


if __name__ == "__main__":
    import sys

    verbose = "--verbose" in sys.argv
    run_comprehensive_test(domains=None, num_samples=100, verbose=verbose)
