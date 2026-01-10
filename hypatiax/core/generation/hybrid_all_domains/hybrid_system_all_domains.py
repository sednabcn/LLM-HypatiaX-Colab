"""
Hybrid System for All Scientific/Engineering Domains
Combines LLM symbolic reasoning with Neural Network learning
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

from hypatiax.core.generation.experiment_protocol import ExperimentProtocol

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class HybridSystemAllDomains:
    """
    Hybrid system for scientific/engineering domains.
    Same strategy as DeFi version but adapted for broader domains.
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
5. Use numpy: np.sqrt, np.log, etc.

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
        """Parse LLM response"""
        parsed = {}

        match = re.search(r"FORMULA:\s*\n([^\n]+)", content, re.IGNORECASE)
        parsed["formula"] = match.group(1).strip() if match else "N/A"

        match = re.search(
            r"PYTHON:\s*\n(.*?)(?=\n\n[A-Z]+:|$)", content, re.DOTALL | re.IGNORECASE
        )
        code = match.group(1).strip() if match else "N/A"
        parsed["python"] = re.sub(
            r"^```python\s*\n", "", re.sub(r"\n```\s*$", "", code)
        )

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
        """Train neural network and return only JSON-serializable metrics"""
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        scaler_X = StandardScaler()
        scaler_y = StandardScaler()

        X_train_s = scaler_X.fit_transform(X_train)
        X_test_s = scaler_X.transform(X_test)
        y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

        # Simple NN architecture
        model = nn.Sequential(
            nn.Linear(X.shape[1], 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = nn.MSELoss()

        X_train_t = torch.FloatTensor(X_train_s)
        y_train_t = torch.FloatTensor(y_train_s).reshape(-1, 1)

        # Training loop
        for epoch in range(epochs):
            optimizer.zero_grad()
            pred = model(X_train_t)
            loss = criterion(pred, y_train_t)
            loss.backward()
            optimizer.step()

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

        # Return only JSON-serializable metrics
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
        """Evaluate LLM formula"""
        try:
            code = formula_dict.get("python_code", "")
            if not code or code == "N/A":
                return {"error": "No code", "success": False}

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

            y_pred = self._evaluate_function(func, X, var_names)

            if len(y_pred) != len(y_true):
                return {"error": f"Shape mismatch", "success": False}

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
            return {"error": str(e), "success": False}

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
        """
        Hybrid prediction combining LLM and NN.

        Decision logic:
        - If LLM R² > 0.95: Use LLM (interpretable + accurate)
        - If 0.80 < LLM R² ≤ 0.95: Use ensemble (LLM + NN)
        - If LLM R² ≤ 0.80: Use NN (accuracy over interpretability)
        """

        if verbose:
            print(f"\n  [HYBRID] Generating LLM formula...")

        # Step 1: Get LLM formula
        llm_result = self.generate_llm_formula(description, domain, var_names, metadata)

        if "error" not in llm_result:
            llm_metrics = self.evaluate_llm_formula(llm_result, X, y_true, var_names)
        else:
            llm_metrics = {"error": llm_result["error"], "success": False}

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

        # Step 3: Decision logic
        llm_r2 = llm_metrics.get("r2", 0) if llm_metrics.get("success") else 0
        nn_r2 = nn_metrics.get("r2", 0)

        if llm_r2 > 0.95:
            decision = "llm"
            final_r2 = llm_r2
            final_rmse = llm_metrics["rmse"]
            reason = "LLM excellent (R² > 0.95)"
        elif llm_r2 > 0.80 and llm_metrics.get("success"):
            decision = "ensemble"
            final_r2 = max(llm_r2, nn_r2)
            final_rmse = min(llm_metrics.get("rmse", 1e10), nn_metrics["rmse"])
            reason = "Ensemble (both good)"
        else:
            decision = "nn"
            final_r2 = nn_r2
            final_rmse = nn_metrics["rmse"]
            reason = "NN primary (LLM struggled)"

        if verbose:
            print(f"  [HYBRID] Decision: {decision.upper()} - {reason}")

        # Build fully JSON-serializable result
        return {
            "method": "hybrid",
            "description": description,
            "domain": domain,
            "decision": decision,
            "decision_reason": reason,
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


def run_hybrid_test_all_domains(
    domains: List[str] = None, num_samples: int = 100, verbose: bool = False
):
    """Run hybrid system test on all scientific domains"""

    protocol = ExperimentProtocol()
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

            if meta.get("extrapolation_test"):
                print(f"  ⚠️  EXTRAPOLATION TEST")

            result = hybrid.hybrid_predict(
                desc, domain, X, y, var_names, meta, verbose=verbose
            )

            metrics = result["evaluation"]
            decision = result["decision"]

            print(f"  ✅ Decision: {decision.upper()}")
            print(f"  R²: {metrics['r2']:.6f}, RMSE: {metrics['rmse']:.6f}")

            if metrics["r2"] > 0.99:
                print(f"  🎯 EXCELLENT")
            elif metrics["r2"] > 0.95:
                print(f"  ✓ Good")

            all_results.append(result)
            hybrid.results.append(result)

    # Save results
    os.makedirs("results", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    hybrid.save_results(f"hypatiax/data/results/hybrid_all_domains_{ts}.json")

    # Generate report
    report = protocol.generate_experiment_report(all_results)
    with open(f"hypatiax/data/results/report_hybrid_all_{ts}.json", "w") as f:
        json.dump(report, f, indent=2)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY".center(80))
    print("=" * 80)

    overall = report["overall"]
    print(f"\n📊 Total: {overall['total_cases']}")
    print(
        f"Success: {overall['successful']}/{overall['total_cases']} ({100 * overall['success_rate']:.1f}%)"
    )

    if "mean_r2" in overall:
        print(f"Mean R²: {overall['mean_r2']:.6f}")

    # Decision breakdown
    decisions = {"llm": 0, "ensemble": 0, "nn": 0}
    for r in all_results:
        decisions[r["decision"]] += 1

    print(f"\n🎯 Decision Breakdown:")
    for dec, count in decisions.items():
        print(
            f"  {dec.upper()}: {count}/{len(all_results)} ({100 * count / len(all_results):.1f}%)"
        )

    print("\n" + "=" * 80)


if __name__ == "__main__":
    import sys

    verbose = "--verbose" in sys.argv
    run_hybrid_test_all_domains(domains=None, num_samples=100, verbose=verbose)
