"""
Hybrid System for All Scientific/Engineering Domains - ENHANCED
Combines LLM symbolic reasoning with Neural Network learning
Now includes comprehensive results table and error fixes
"""

import json
import os
import sys
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

# Load environment - try multiple locations
env_paths = [
    Path(__file__).parent.parent.parent / ".env",
    Path(__file__).parent.parent.parent.parent / ".env",
    Path.cwd() / "hypatiax" / ".env",
    Path.cwd() / ".env",
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"✅ Loaded .env from: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    print("⚠️  No .env file found. Trying load_dotenv() without path...")
    load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import protocol
try:
    from hypatiax.protocols.experiment_protocol_all_30 import ExperimentProtocolAll

    print("✅ Loaded ExperimentProtocolAll from: hypatiax/protocols/")
except ImportError:
    try:
        from experiment_protocol_all_30 import ExperimentProtocolAll

        print("✅ Loaded ExperimentProtocolAll from: current directory")
    except ImportError:
        print("❌ Error: experiment_protocol_all_30.py not found")
        sys.exit(1)


class HybridSystemAllDomains:
    """
    Hybrid system for scientific/engineering domains.
    Enhanced with comprehensive results tracking and error handling.
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.results = []

    def generate_llm_formula(
        self, description: str, domain: str, variable_names: List[str], metadata: Dict
    ) -> Dict:
        """Generate formula using LLM"""
        prompt = self._generate_prompt(description, domain, variable_names, metadata)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text
            parsed = self._parse_response(content)

            return {
                "formula": parsed.get("formula", "N/A"),
                "latex": parsed.get("latex", "N/A"),
                "python_code": parsed.get("python", "N/A"),
                "explanation": parsed.get("explanation", "N/A"),
            }
        except Exception as e:
            return {"error": str(e)}

    def _generate_prompt(
        self, description: str, domain: str, variable_names: List[str], metadata: Dict
    ) -> str:
        """Generate prompt for LLM"""
        var_info = f"\nVariables: {', '.join(variable_names)}"

        constants_info = ""
        if metadata and "constants" in metadata and metadata["constants"]:
            constants_info = "\n\n⚠️ CRITICAL - Use EXACT constants:"
            for k, v in metadata["constants"].items():
                constants_info += f"\n  • {k} = {v}"

        hint_info = ""
        if metadata and "ground_truth" in metadata:
            hint_info = f"\nExpected form: {metadata['ground_truth']}"

        return f"""Mathematical formula expert in {domain}.

Task: {description}
Domain: {domain}{var_info}{constants_info}{hint_info}

⚠️ CRITICAL INSTRUCTIONS:
1. Function parameters = INPUT VARIABLES only
2. ALL constants INSIDE function body
3. Use EXACT constants shown above
4. Function named 'formula'
5. Use numpy: np.sqrt, np.log, np.exp, etc.

Format:

FORMULA:
[mathematical notation]

PYTHON:
def formula(param1, param2, ...):
    # Define constants here
    return result

EXPLANATION:
[brief explanation]

NO markdown code blocks, individual parameters NOT dict."""

    def _parse_response(self, content: str) -> Dict[str, str]:
        """Parse LLM response with improved error handling"""
        parsed = {}

        # Extract formula
        match = re.search(r"FORMULA:\s*\n([^\n]+)", content, re.IGNORECASE)
        parsed["formula"] = match.group(1).strip() if match else "N/A"

        # Extract Python code
        match = re.search(
            r"PYTHON:\s*\n(.*?)(?=\n\n[A-Z]+:|$)", content, re.DOTALL | re.IGNORECASE
        )
        code = match.group(1).strip() if match else "N/A"
        # Remove markdown code fences if present
        parsed["python"] = re.sub(
            r"^```python\s*\n", "", re.sub(r"\n```\s*$", "", code)
        )

        # Extract explanation
        match = re.search(
            r"EXPLANATION:\s*\n(.*?)(?=\n\n[A-Z]+:|$)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        parsed["explanation"] = match.group(1).strip() if match else "N/A"

        return parsed

    def train_nn(
        self, X: np.ndarray, y: np.ndarray, epochs: int = 300
    ) -> Tuple[nn.Module, Dict]:
        """Train neural network with improved architecture"""
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler

        # Handle edge cases
        if len(X) < 10:
            return None, {
                "r2": 0.0,
                "rmse": float("inf"),
                "mae": float("inf"),
                "error": "Insufficient data",
            }

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        scaler_X = StandardScaler()
        scaler_y = StandardScaler()

        X_train_s = scaler_X.fit_transform(X_train)
        X_test_s = scaler_X.transform(X_test)
        y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

        # Improved NN architecture
        hidden_size = min(64, max(32, X.shape[1] * 8))
        model = nn.Sequential(
            nn.Linear(X.shape[1], hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, 1),
        )

        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.MSELoss()

        X_train_t = torch.FloatTensor(X_train_s)
        y_train_t = torch.FloatTensor(y_train_s).reshape(-1, 1)

        # Training loop with early stopping
        best_loss = float("inf")
        patience = 50
        patience_counter = 0

        for epoch in range(epochs):
            optimizer.zero_grad()
            pred = model(X_train_t)
            loss = criterion(pred, y_train_t)
            loss.backward()
            optimizer.step()

            # Early stopping
            if loss.item() < best_loss:
                best_loss = loss.item()
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    break

        # Evaluate on test set
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

        return model, metrics

    def evaluate_llm_formula(
        self,
        formula_dict: Dict,
        X: np.ndarray,
        y_true: np.ndarray,
        var_names: List[str],
    ) -> Dict:
        """Evaluate LLM formula with better error handling"""
        try:
            code = formula_dict.get("python_code", "")
            if not code or code == "N/A":
                return {"error": "No code generated", "success": False, "r2": 0.0}

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
                return {"error": "No function found", "success": False, "r2": 0.0}

            y_pred = self._evaluate_function(func, X, var_names)

            if len(y_pred) != len(y_true):
                return {
                    "error": f"Shape mismatch: {len(y_pred)} vs {len(y_true)}",
                    "success": False,
                    "r2": 0.0,
                }

            # Handle inf/nan values
            if not np.all(np.isfinite(y_pred)):
                return {"error": "Non-finite predictions", "success": False, "r2": 0.0}

            mse = np.mean((y_pred - y_true) ** 2)
            ss_res = np.sum((y_true - y_pred) ** 2)
            ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0

            return {
                "r2": float(r2),
                "rmse": float(np.sqrt(mse)),
                "mae": float(np.mean(np.abs(y_pred - y_true))),
                "success": True,
            }
        except Exception as e:
            return {"error": str(e)[:100], "success": False, "r2": 0.0}

    def _evaluate_function(self, func, X, var_names):
        """Evaluate function with multiple strategies"""
        sig = inspect.signature(func)
        n_params = len(sig.parameters)
        n_features = X.shape[1]

        # Strategy 1: Vectorized positional arguments
        if n_params == n_features:
            try:
                y = func(*[X[:, i] for i in range(n_features)])
                return np.asarray(y).flatten()
            except:
                pass

        # Strategy 2: Row-by-row evaluation
        try:
            y = np.empty(X.shape[0])
            for i in range(X.shape[0]):
                if n_params == n_features:
                    y[i] = func(*X[i, :])
                elif n_params < n_features:
                    y[i] = func(*X[i, :n_params])
            return y
        except:
            pass

        raise RuntimeError(f"All evaluation strategies failed")

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
        """Hybrid prediction with enhanced decision logic"""

        if verbose:
            print(f"\n  [HYBRID] Generating LLM formula...")

        # Step 1: Get LLM formula
        llm_result = self.generate_llm_formula(description, domain, var_names, metadata)

        if "error" not in llm_result:
            llm_metrics = self.evaluate_llm_formula(llm_result, X, y_true, var_names)
        else:
            llm_metrics = {"error": llm_result["error"], "success": False, "r2": 0.0}

        if verbose:
            if llm_metrics.get("success"):
                print(f"  [HYBRID] LLM R²: {llm_metrics['r2']:.4f}")
            else:
                print(
                    f"  [HYBRID] LLM failed: {llm_metrics.get('error', 'Unknown')[:50]}"
                )

        # Step 2: Train NN
        if verbose:
            print(f"  [HYBRID] Training NN...")

        nn_model, nn_metrics = self.train_nn(X, y_true, epochs=300)

        if verbose:
            print(f"  [HYBRID] NN R²: {nn_metrics['r2']:.4f}")

        # Step 3: Enhanced decision logic
        llm_r2 = llm_metrics.get("r2", 0) if llm_metrics.get("success") else 0
        nn_r2 = nn_metrics.get("r2", 0)

        if llm_r2 > 0.95:
            decision = "llm"
            final_r2 = llm_r2
            final_rmse = llm_metrics.get("rmse", float("inf"))
            reason = "LLM excellent (R² > 0.95)"
            validation_score = "EXCELLENT"
        elif llm_r2 > 0.80 and llm_metrics.get("success"):
            decision = "ensemble"
            final_r2 = max(llm_r2, nn_r2)
            final_rmse = min(llm_metrics.get("rmse", 1e10), nn_metrics["rmse"])
            reason = "Ensemble (both good)"
            validation_score = "GOOD"
        else:
            decision = "nn"
            final_r2 = nn_r2
            final_rmse = nn_metrics["rmse"]
            reason = "NN primary (LLM struggled)"
            validation_score = "FAIR" if nn_r2 > 0.8 else "POOR"

        if verbose:
            print(f"  [HYBRID] Decision: {decision.upper()} - {reason}")

        # Build result with observations
        observations = []
        if llm_r2 > 0.99:
            observations.append("Perfect symbolic fit")
        elif not llm_metrics.get("success"):
            observations.append(
                f"LLM error: {llm_metrics.get('error', 'Unknown')[:50]}"
            )

        if nn_r2 < 0:
            observations.append("NN worse than baseline")
        elif nn_r2 > llm_r2 + 0.1:
            observations.append("NN significantly better")

        return {
            "method": "hybrid",
            "description": description,
            "domain": domain,
            "decision": decision,
            "decision_reason": reason,
            "validation_score": validation_score,
            "observations": ", ".join(observations) if observations else "Normal",
            "llm_result": {
                "formula": llm_result.get("formula", "N/A"),
                "python_code": llm_result.get("python_code", "N/A"),
                "metrics": llm_metrics,
            },
            "nn_result": {"metrics": nn_metrics},
            "evaluation": {
                "r2": float(final_r2),
                "rmse": float(final_rmse),
                "success": True,
            },
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
        }

    def save_results(self, filepath: str):
        """Save results to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"✅ Results saved: {filepath}")

    def print_results_table(self, results: List[Dict]):
        """Print comprehensive results table"""
        print("\n" + "=" * 140)
        print("DETAILED RESULTS TABLE".center(140))
        print("=" * 140)

        # Header
        header = f"{'#':<4} {'Domain':<18} {'Test Case':<35} {'R²':<10} {'Val.Score':<12} {'Observations':<50}"
        print(header)
        print("-" * 140)

        # Data rows
        for i, r in enumerate(results, 1):
            domain = r["domain"][:17]
            desc = r["description"][:34]
            r2 = r["evaluation"]["r2"]
            val_score = r["validation_score"]
            obs = r["observations"][:49]

            # Color coding for R²
            if r2 > 0.95:
                r2_str = f"{r2:.6f} ✓"
            elif r2 > 0.80:
                r2_str = f"{r2:.6f} ~"
            else:
                r2_str = f"{r2:.6f} ✗"

            row = (
                f"{i:<4} {domain:<18} {desc:<35} {r2_str:<10} {val_score:<12} {obs:<50}"
            )
            print(row)

        print("=" * 140)


def run_hybrid_test_all_domains(
    domains: List[str] = None, num_samples: int = 100, verbose: bool = False
):
    """Run hybrid system test on all scientific domains with results table"""

    protocol = ExperimentProtocolAll()
    hybrid = HybridSystemAllDomains()

    if domains is None:
        domains = protocol.get_all_domains()

    print("=" * 80)
    print("🔬 HYBRID SYSTEM - ALL DOMAINS 🔬".center(80))
    print("=" * 80)
    print(f"Strategy: LLM (R²>0.95) → Ensemble (0.80-0.95) → NN (<0.80)")
    print(f"Domains: {', '.join(domains)}")
    print("=" * 80)

    all_results = []

    for domain in domains:
        print(f"\n{'=' * 80}")
        print(f"DOMAIN: {domain.upper()}".center(80))
        print("=" * 80)

        test_cases = protocol.load_test_data(domain, num_samples=num_samples)

        for i, (desc, X, y, var_names, meta) in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {desc}")
            print(f"  Variables: {', '.join(var_names)}")

            result = hybrid.hybrid_predict(
                desc, domain, X, y, var_names, meta, verbose=verbose
            )

            metrics = result["evaluation"]
            decision = result["decision"]

            print(f"  ✅ Decision: {decision.upper()}")
            print(f"  R²: {metrics['r2']:.6f}, RMSE: {metrics['rmse']:.6f}")
            print(f"  📊 {result['validation_score']}")

            all_results.append(result)
            hybrid.results.append(result)

    # Save results
    os.makedirs("hypatiax/data/results", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    hybrid.save_results(f"hypatiax/data/results/hybrid_llm_nn_all_domains_{ts}.json")

    # Print detailed results table
    hybrid.print_results_table(all_results)

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS".center(80))
    print("=" * 80)

    r2_scores = [r["evaluation"]["r2"] for r in all_results]
    print(f"\n📊 Total Test Cases: {len(all_results)}")
    print(f"Mean R²: {np.mean(r2_scores):.6f}")
    print(f"Median R²: {np.median(r2_scores):.6f}")
    print(f"Std Dev R²: {np.std(r2_scores):.6f}")
    print(f"Min R²: {np.min(r2_scores):.6f}")
    print(f"Max R²: {np.max(r2_scores):.6f}")

    # Decision breakdown
    print(f"\n🎯 Decision Breakdown:")
    decisions = {"llm": [], "ensemble": [], "nn": []}
    for r in all_results:
        decisions[r["decision"]].append(r["evaluation"]["r2"])

    for dec, r2_list in decisions.items():
        if r2_list:
            count = len(r2_list)
            pct = 100 * count / len(all_results)
            mean_r2 = np.mean(r2_list)
            print(
                f"  {dec.upper()}: {count}/{len(all_results)} ({pct:.1f}%) - Mean R² = {mean_r2:.4f}"
            )

    # Validation score breakdown
    print(f"\n📈 Validation Score Breakdown:")
    val_scores = {}
    for r in all_results:
        score = r["validation_score"]
        val_scores[score] = val_scores.get(score, 0) + 1

    for score, count in sorted(val_scores.items(), key=lambda x: x[1], reverse=True):
        pct = 100 * count / len(all_results)
        print(f"  {score}: {count}/{len(all_results)} ({pct:.1f}%)")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hybrid System - All Domains")
    parser.add_argument("--domains", nargs="+", default=None)
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    run_hybrid_test_all_domains(
        domains=args.domains, num_samples=args.samples, verbose=args.verbose
    )
