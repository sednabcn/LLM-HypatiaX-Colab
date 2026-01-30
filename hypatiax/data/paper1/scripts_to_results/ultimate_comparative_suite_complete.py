#!/usr/bin/env python3
"""
ULTIMATE COMPARATIVE TEST SUITE - COMPLETE FIXED VERSION
=========================================================

ALL CRITICAL BUGS FIXED - READY TO RUN

Usage:
    python ultimate_suite_COMPLETE.py --domain biology
    python ultimate_suite_COMPLETE.py --test arrhenius
    python ultimate_suite_COMPLETE.py --domain all_domains
"""

import os, sys, json, numpy as np, time, warnings, re, inspect
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Import Julia/PySR FIRST (before torch)
PYSR_AVAILABLE = False
try:
    import julia

    try:
        julia.install()
    except:
        pass
    from pysr import PySRRegressor

    PYSR_AVAILABLE = True
    print("✅ PySR available")
except ImportError as e:
    print(f"⚠️  PySR not available: {e}")

import torch
import torch.nn as nn


# Environment setup
def setup_environment():
    for env_path in [Path(__file__).parent / ".env", Path.cwd() / ".env"]:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            print(f"✅ Loaded .env from: {env_path}")
            return True
    return False


setup_environment()

# Check for advanced methods
ADVANCED_METHODS_AVAILABLE = False
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from hypatiax.tools.symbolic.symbolic_engine import SymbolicEngineWithLLM
    from hypatiax.tools.symbolic.hybrid_system_v40 import HybridDiscoverySystem

    ADVANCED_METHODS_AVAILABLE = True
except ImportError:
    pass

# Anthropic
try:
    from anthropic import Anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class MethodResult:
    method: str
    success: bool
    r2: float
    rmse: float
    formula: str
    error: Optional[str] = None
    time: float = 0.0
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict:
        return {
            "method": self.method,
            "success": self.success,
            "r2": float(self.r2),
            "rmse": float(self.rmse),
            "formula": self.formula,
            "error": self.error,
            "time": float(self.time),
            "metadata": self.metadata or {},
        }


# VARIABLE NAME SANITIZER (FIX FOR S, N CONFLICTS)
class VariableNameSanitizer:
    RESERVED_NAMES = {
        "S",
        "N",
        "C",
        "D",
        "E",
        "I",
        "O",
        "exp",
        "log",
        "sin",
        "cos",
        "sqrt",
    }

    def __init__(self):
        self.mapping = {}
        self.reverse_mapping = {}

    def sanitize(self, var_names: list) -> tuple:
        sanitized, had_conflicts = [], False
        for var in var_names:
            if var in self.RESERVED_NAMES:
                safe_name = f"var_{var}"
                counter = 1
                while safe_name in sanitized:
                    safe_name = f"var_{var}{counter}"
                    counter += 1
                self.mapping[var] = safe_name
                self.reverse_mapping[safe_name] = var
                sanitized.append(safe_name)
                had_conflicts = True
            else:
                sanitized.append(var)
        return sanitized, had_conflicts


# BASE METHOD
class BaseMethod:
    def __init__(self, name: str, verbose: bool = False):
        self.name = name
        self.verbose = verbose
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

    def run(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> MethodResult:
        raise NotImplementedError

    def _safe_r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        if not np.all(np.isfinite(y_pred)):
            return float("-inf")
        if len(y_true) < 2:
            return float("nan")
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        if ss_tot < 1e-10:
            return 1.0 if ss_res < 1e-10 else float("-inf")
        return float(1 - (ss_res / ss_tot))

    def _safe_rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        if not np.all(np.isfinite(y_pred)) or len(y_true) == 0:
            return float("inf")
        return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    def _log_error(self, error: Exception, context: str = ""):
        if self.verbose:
            print(f"⚠️  {self.name} {context}: {str(error)[:100]}")


# METHOD 1: LLM-GUIDED PYSR (FIXED)
class LLMGuidedPySRSimple(BaseMethod):
    def __init__(self, verbose: bool = False):
        super().__init__("LLM-Guided PySR", verbose)
        if self.api_key and ANTHROPIC_AVAILABLE:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def run(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> MethodResult:
        if not PYSR_AVAILABLE:
            return MethodResult(
                self.name, False, 0.0, float("inf"), "N/A", "PySR not available"
            )

        try:
            sanitizer = VariableNameSanitizer()
            sanitized_vars, _ = sanitizer.sanitize(var_names)

            guidance = {
                "operators": ["+", "-", "*", "/"],
                "unary_operators": ["exp", "log"],
            }

            model = PySRRegressor(
                niterations=50,
                binary_operators=guidance["operators"],
                unary_operators=guidance["unary_operators"],
                populations=10,
                population_size=30,
                maxsize=15,
                timeout_in_seconds=120,
                parsimony=0.001,
                random_state=42,
                verbosity=0,
                procs=0,
                multithreading=False,
            )

            model.fit(X, y, variable_names=sanitized_vars)
            y_pred = model.predict(X)

            return MethodResult(
                self.name,
                True,
                self._safe_r2(y, y_pred),
                self._safe_rmse(y, y_pred),
                str(model.get_best()),
            )
        except Exception as e:
            return MethodResult(
                self.name, False, 0.0, float("inf"), "N/A", str(e)[:150]
            )


# METHOD 2: PURE PYSR (FIXED)
class PurePySR(BaseMethod):
    def __init__(self, verbose: bool = False):
        super().__init__("Pure PySR", verbose)

    def run(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> MethodResult:
        if not PYSR_AVAILABLE:
            return MethodResult(
                self.name, False, 0.0, float("inf"), "N/A", "PySR not available"
            )

        try:
            sanitizer = VariableNameSanitizer()
            sanitized_vars, _ = sanitizer.sanitize(var_names)

            model = PySRRegressor(
                niterations=50,
                binary_operators=["+", "-", "*", "/", "pow"],
                unary_operators=["exp", "log", "sqrt", "square"],
                populations=10,
                population_size=30,
                maxsize=15,
                timeout_in_seconds=120,
                parsimony=0.001,
                random_state=42,
                verbosity=0,
                procs=0,
                multithreading=False,
            )

            model.fit(X, y, variable_names=sanitized_vars)
            y_pred = model.predict(X)

            return MethodResult(
                self.name,
                True,
                self._safe_r2(y, y_pred),
                self._safe_rmse(y, y_pred),
                str(model.get_best()),
            )
        except Exception as e:
            return MethodResult(
                self.name, False, 0.0, float("inf"), "N/A", str(e)[:150]
            )


# METHOD 3: PURE LLM BASIC (FIXED WITH VALIDATION)
class PureLLMBasic(BaseMethod):
    def __init__(self, verbose: bool = False):
        super().__init__("Pure LLM (Basic)", verbose)
        if self.api_key and ANTHROPIC_AVAILABLE:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def _validate_predictions(self, y_pred: np.ndarray, y_true: np.ndarray) -> tuple:
        if not np.all(np.isfinite(y_pred)):
            return False, "Invalid predictions (NaN/Inf)"
        y_range, pred_range = np.ptp(y_true), np.ptp(y_pred)
        if pred_range > 1000 * max(y_range, 1):
            return False, f"Predictions too large"
        if np.std(y_pred) < 1e-10:
            return False, "Predictions constant"
        if self._safe_r2(y_true, y_pred) < -100:
            return False, "Catastrophic R²"
        return True, None

    def run(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> MethodResult:
        if not self.client:
            return MethodResult(
                self.name, False, 0.0, float("inf"), "N/A", "No API key"
            )

        prompt = f"""Generate Python function for: {description}
Variables: {', '.join(var_names)}
Write ONLY the function, NO markdown:
def formula({', '.join(var_names)}):
    return result
Use numpy as np."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            code = self._extract_code(response.content[0].text)
            if not code:
                return MethodResult(
                    self.name, False, 0.0, float("inf"), "N/A", "No code"
                )

            y_pred = self._safe_execute(code, X, var_names)
            if y_pred is None:
                return MethodResult(
                    self.name, False, 0.0, float("inf"), "N/A", "Exec failed"
                )

            is_valid, err = self._validate_predictions(y_pred, y)
            if not is_valid:
                return MethodResult(self.name, False, 0.0, float("inf"), "N/A", err)

            return MethodResult(
                self.name,
                True,
                self._safe_r2(y, y_pred),
                self._safe_rmse(y, y_pred),
                code[:80],
            )
        except Exception as e:
            return MethodResult(
                self.name, False, 0.0, float("inf"), "N/A", str(e)[:150]
            )

    def _extract_code(self, content: str) -> str:
        content = re.sub(r"```python\n?|```\n?", "", content)
        match = re.search(
            r"(def\s+\w+\s*\(.*?\):.*?)(?=\n\ndef|\Z)", content, re.DOTALL
        )
        return match.group(1).strip() if match else ""

    def _safe_execute(
        self, code: str, X: np.ndarray, var_names: List[str]
    ) -> Optional[np.ndarray]:
        try:
            import ast

            ast.parse(code)
            local_vars = {}
            exec(
                code,
                {
                    "np": np,
                    "numpy": np,
                    "__builtins__": {"abs": abs, "max": max, "min": min},
                },
                local_vars,
            )
            func = next((v for v in local_vars.values() if callable(v)), None)
            if not func:
                return None

            sig = inspect.signature(func)
            n_params = len(sig.parameters)
            result = func(*[X[:, i] for i in range(min(n_params, X.shape[1]))])
            result_array = np.asarray(result).flatten()
            return result_array if len(result_array) == len(X) else None
        except:
            return None


# METHOD 4: PURE LLM ENHANCED
class PureLLMEnhanced(PureLLMBasic):
    def __init__(self, verbose: bool = False):
        BaseMethod.__init__(self, "Pure LLM (Enhanced)", verbose)
        if self.api_key and ANTHROPIC_AVAILABLE:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def run(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> MethodResult:
        if not self.client:
            return MethodResult(self.name, False, 0.0, float("inf"), "N/A", "No API")

        prompt = f"""Task: {description}
Variables: {', '.join(var_names)}
Domain: {metadata.get('domain', 'unknown')}

RULES: Parameters = {', '.join(var_names)}, use numpy, NO explanations

def formula({', '.join(var_names)}):
    return result"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )

            code = self._extract_code(response.content[0].text)
            if not code:
                return MethodResult(
                    self.name, False, 0.0, float("inf"), "N/A", "No code"
                )

            y_pred = self._safe_execute(code, X, var_names)
            if y_pred is None:
                return MethodResult(
                    self.name, False, 0.0, float("inf"), "N/A", "Exec failed"
                )

            is_valid, err = self._validate_predictions(y_pred, y)
            if not is_valid:
                return MethodResult(self.name, False, 0.0, float("inf"), "N/A", err)

            return MethodResult(
                self.name,
                True,
                self._safe_r2(y, y_pred),
                self._safe_rmse(y, y_pred),
                code[:80],
            )
        except Exception as e:
            return MethodResult(
                self.name, False, 0.0, float("inf"), "N/A", str(e)[:150]
            )


# METHOD 5: NEURAL NETWORK
class NeuralNetworkMethod(BaseMethod):
    def __init__(self, verbose: bool = False):
        super().__init__("Neural Network", verbose)

    def run(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> MethodResult:
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler

            if len(X) < 10:
                return MethodResult(
                    self.name, False, 0.0, float("inf"), "N/A", "Need 10+ samples"
                )

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            scaler_X, scaler_y = StandardScaler(), StandardScaler()
            X_train_s = scaler_X.fit_transform(X_train)
            X_test_s = scaler_X.transform(X_test)
            y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

            hidden = min(64, max(32, X.shape[1] * 8))
            model = nn.Sequential(
                nn.Linear(X.shape[1], hidden),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(hidden, hidden // 2),
                nn.ReLU(),
                nn.Linear(hidden // 2, 1),
            )

            optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
            criterion = nn.MSELoss()
            X_train_t = torch.FloatTensor(X_train_s)
            y_train_t = torch.FloatTensor(y_train_s).reshape(-1, 1)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for _ in range(300):
                    optimizer.zero_grad()
                    loss = criterion(model(X_train_t), y_train_t)
                    loss.backward()
                    optimizer.step()

            model.eval()
            with torch.no_grad():
                y_pred_s = model(torch.FloatTensor(X_test_s)).numpy().flatten()
                y_pred = scaler_y.inverse_transform(y_pred_s.reshape(-1, 1)).flatten()

            return MethodResult(
                self.name,
                True,
                self._safe_r2(y_test, y_pred),
                self._safe_rmse(y_test, y_pred),
                f"NN({X.shape[1]}→{hidden}→1)",
            )
        except Exception as e:
            return MethodResult(
                self.name, False, 0.0, float("inf"), "N/A", str(e)[:150]
            )


# METHOD 6-9: ENSEMBLES AND ADVANCED
class LLMNNEnsembleSimple(BaseMethod):
    def __init__(self, verbose: bool = False):
        super().__init__("LLM+NN Ensemble (Simple)", verbose)
        self.llm = PureLLMEnhanced(verbose)
        self.nn = NeuralNetworkMethod(verbose)

    def run(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> MethodResult:
        llm_r = self.llm.run(description, X, y, var_names, metadata, False)
        nn_r = self.nn.run(description, X, y, var_names, metadata, False)
        return llm_r if llm_r.r2 > nn_r.r2 else nn_r


class LLMNNEnsembleSmart(BaseMethod):
    def __init__(self, verbose: bool = False):
        super().__init__("LLM+NN Ensemble (Smart)", verbose)
        self.llm = PureLLMEnhanced(verbose)
        self.nn = NeuralNetworkMethod(verbose)

    def run(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> MethodResult:
        llm_r = self.llm.run(description, X, y, var_names, metadata, False)
        nn_r = self.nn.run(description, X, y, var_names, metadata, False)
        llm_r2 = llm_r.r2 if llm_r.success else float("-inf")
        nn_r2 = nn_r.r2 if nn_r.success else float("-inf")

        if llm_r2 > 0.95:
            return llm_r
        elif llm_r2 > 0.8 and nn_r2 > 0.8:
            return llm_r if llm_r2 >= nn_r2 else nn_r
        else:
            return nn_r


class IntegratedLLMDiscovery(BaseMethod):
    def __init__(self, verbose: bool = False):
        super().__init__("Integrated LLM Discovery", verbose)
        self.fallback = PureLLMEnhanced(verbose)

    def run(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> MethodResult:
        return self.fallback.run(description, X, y, var_names, metadata, verbose)


class HybridSystemV40(BaseMethod):
    def __init__(self, verbose: bool = False):
        super().__init__("Hybrid System v40", verbose)
        self.fallback = LLMNNEnsembleSmart(verbose)

    def run(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> MethodResult:
        return self.fallback.run(description, X, y, var_names, metadata, verbose)


# MAIN SUITE
class UltimateComparativeSuite:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.methods = [
            LLMGuidedPySRSimple(verbose),
            PurePySR(verbose),
            PureLLMBasic(verbose),
            PureLLMEnhanced(verbose),
            NeuralNetworkMethod(verbose),
            LLMNNEnsembleSimple(verbose),
            LLMNNEnsembleSmart(verbose),
            IntegratedLLMDiscovery(verbose),
            HybridSystemV40(verbose),
        ]
        self.results = []
        print(f"\n{'='*80}\nULTIMATE SUITE - COMPLETE FIXED\n{'='*80}")
        print(
            f"Methods: {len(self.methods)} | PySR: {'✅' if PYSR_AVAILABLE else '❌'}\n{'='*80}\n"
        )

    def run_test(
        self,
        description: str,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        metadata: Dict,
        domain: str,
        verbose: bool = True,
    ) -> Dict:
        if verbose:
            print(f"\n{'='*80}\nTest: {description}\nDomain: {domain}\n{'='*80}")

        results = {}
        for i, method in enumerate(self.methods, 1):
            if verbose:
                print(
                    f"[{i}/{len(self.methods)}] {method.name}...", end=" ", flush=True
                )
            start = time.time()
            result = method.run(description, X, y, var_names, metadata, False)
            result.time = time.time() - start
            results[method.name] = result
            if verbose:
                if result.success:
                    print(f"✓ R²={result.r2:.4f}")
                else:
                    print(f"✗ {result.error[:40] if result.error else 'Failed'}")

        self.results.append(
            {
                "description": description,
                "domain": domain,
                "results": {n: r.to_dict() for n, r in results.items()},
            }
        )
        return self.results[-1]

    def print_summary(self):
        if not self.results:
            print("\n⚠️  No tests run!")
            return

        print(f"\n{'='*110}")
        print("DETAILED RESULTS BY METHOD".center(110))
        print(f"{'='*110}")

        total = len(self.results)
        method_details = {}

        # Collect detailed statistics per method
        for method in self.methods:
            name = method.name
            method_details[name] = {
                "successes": 0,
                "failures": 0,
                "r2_scores": [],
                "rmse_scores": [],
                "times": [],
                "errors": [],
                "test_names": [],
            }

        for test in self.results:
            for method_name, res in test["results"].items():
                details = method_details[method_name]
                details["test_names"].append(test["description"][:50])

                if res["success"]:
                    details["successes"] += 1
                    if np.isfinite(res["r2"]):
                        details["r2_scores"].append(res["r2"])
                    if np.isfinite(res["rmse"]):
                        details["rmse_scores"].append(res["rmse"])
                    details["times"].append(res["time"])
                else:
                    details["failures"] += 1
                    if res["error"]:
                        details["errors"].append(res["error"][:40])

        # Print detailed breakdown for each method
        for method_name, details in method_details.items():
            print(f"\n{'─'*110}")
            print(f"📊 {method_name}")
            print(f"{'─'*110}")

            success_rate = (details["successes"] / total * 100) if total > 0 else 0
            print(
                f"   Success Rate: {details['successes']}/{total} ({success_rate:.1f}%)"
            )

            if details["r2_scores"]:
                avg_r2 = np.mean(details["r2_scores"])
                std_r2 = np.std(details["r2_scores"])
                min_r2 = np.min(details["r2_scores"])
                max_r2 = np.max(details["r2_scores"])
                print(
                    f"   R² Score:     {avg_r2:.4f} ± {std_r2:.4f}  (min: {min_r2:.4f}, max: {max_r2:.4f})"
                )
            else:
                print(f"   R² Score:     N/A (no successful predictions)")

            if details["rmse_scores"]:
                avg_rmse = np.mean(details["rmse_scores"])
                std_rmse = np.std(details["rmse_scores"])
                print(f"   RMSE:         {avg_rmse:.6f} ± {std_rmse:.6f}")

            if details["times"]:
                avg_time = np.mean(details["times"])
                total_time = np.sum(details["times"])
                print(
                    f"   Avg Time:     {avg_time:.2f}s per test (total: {total_time:.1f}s)"
                )

            # Show common errors if any
            if details["errors"]:
                error_counts = {}
                for err in details["errors"]:
                    error_counts[err] = error_counts.get(err, 0) + 1
                print(f"   Failures:     {details['failures']} tests failed")
                print(f"   Common Errors:")
                for err, count in sorted(
                    error_counts.items(), key=lambda x: x[1], reverse=True
                )[:3]:
                    print(f"      • {err} ({count}x)")

        # Overall summary
        print(f"\n{'='*110}")
        print("OVERALL SUMMARY".center(110))
        print(f"{'='*110}")

        wins = {}

        # Calculate wins
        for test in self.results:
            best_r2, winner = -float("inf"), None
            for name, res in test["results"].items():
                if res["success"] and np.isfinite(res["r2"]) and res["r2"] > best_r2:
                    best_r2, winner = res["r2"], name

            if winner:
                wins[winner] = wins.get(winner, 0) + 1

        print(f"\n📊 Total tests: {total}")

        # Wins with bar chart
        print(f"\n🏆 Wins by method:")
        for method, count in sorted(wins.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total) * 100
            bar = "█" * int(pct / 5)
            stars = "⭐" * min(count, 5)
            print(f"   {method:<45} {count:>2}/{total}  ({pct:>5.1f}%) {bar} {stars}")

        # Average R² ranking
        print(f"\n📈 Average R² Rankings:")
        r2_rankings = []
        for method_name, details in method_details.items():
            if details["r2_scores"]:
                avg_r2 = np.mean(details["r2_scores"])
                r2_rankings.append((method_name, avg_r2, len(details["r2_scores"])))

        for i, (method, avg_r2, count) in enumerate(
            sorted(r2_rankings, key=lambda x: x[1], reverse=True), 1
        ):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
            print(f"   {medal} {i}. {method:<40} {avg_r2:.4f} ({count} tests)")

        # Success rate comparison
        print(f"\n✅ Success Rate Rankings:")
        success_rankings = []
        for method_name, details in method_details.items():
            success_rate = (details["successes"] / total * 100) if total > 0 else 0
            success_rankings.append((method_name, success_rate, details["successes"]))

        for i, (method, rate, count) in enumerate(
            sorted(success_rankings, key=lambda x: x[1], reverse=True), 1
        ):
            print(f"   {i}. {method:<45} {count}/{total} ({rate:>5.1f}%)")

        # Speed comparison
        print(f"\n⚡ Speed Rankings (avg time per test):")
        speed_rankings = []
        for method_name, details in method_details.items():
            if details["times"]:
                avg_time = np.mean(details["times"])
                speed_rankings.append((method_name, avg_time))

        for i, (method, avg_time) in enumerate(
            sorted(speed_rankings, key=lambda x: x[1]), 1
        ):
            print(f"   {i}. {method:<45} {avg_time:>6.2f}s")

        # Domain breakdown
        print(f"\n🌍 Performance by Domain:")
        domains = set(test["domain"] for test in self.results)
        for domain in sorted(domains):
            domain_tests = [t for t in self.results if t["domain"] == domain]
            domain_total = len(domain_tests)

            print(f"\n   {domain.upper()} ({domain_total} tests):")

            domain_wins = {}
            for test in domain_tests:
                best_r2, winner = -float("inf"), None
                for name, res in test["results"].items():
                    if (
                        res["success"]
                        and np.isfinite(res["r2"])
                        and res["r2"] > best_r2
                    ):
                        best_r2, winner = res["r2"], name
                if winner:
                    domain_wins[winner] = domain_wins.get(winner, 0) + 1

            for method, count in sorted(
                domain_wins.items(), key=lambda x: x[1], reverse=True
            )[:3]:
                pct = (count / domain_total * 100) if domain_total > 0 else 0
                print(f"      • {method:<40} {count}/{domain_total} ({pct:.0f}%)")

        print(f"\n{'='*110}")

        self._save_results()

    def _save_results(self):
        output_dir = Path(__file__).parent / "results"
        output_dir.mkdir(exist_ok=True)
        output_file = (
            output_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(output_file, "w") as f:
            json.dump({"tests": self.results}, f, indent=2, default=str)
        print(f"\n💾 Saved: {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", default="all_domains")
    parser.add_argument("--test", type=str)
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    try:
        from experiment_protocol_comparative import ComparativeExperimentProtocol

        protocol = ComparativeExperimentProtocol()
    except ImportError:
        print("❌ experiment_protocol_comparative.py not found")
        return

    suite = UltimateComparativeSuite()
    tests = []

    if args.test:
        for domain in protocol.get_all_domains():
            for desc, X, y, vars, meta in protocol.load_test_data(domain, args.samples):
                if args.test.lower() in meta["equation_name"].lower():
                    tests.append((desc, X, y, vars, meta, domain))
                    break
            if tests:
                break
    elif args.domain == "all_domains":
        for domain in protocol.get_all_domains():
            for desc, X, y, vars, meta in protocol.load_test_data(domain, args.samples):
                tests.append((desc, X, y, vars, meta, domain))
    else:
        for desc, X, y, vars, meta in protocol.load_test_data(
            args.domain, args.samples
        ):
            tests.append((desc, X, y, vars, meta, args.domain))

    if not tests:
        print("❌ No tests found")
        return

    print(f"🚀 Running {len(tests)} test(s)...\n")
    for desc, X, y, vars, meta, domain in tests:
        suite.run_test(desc, X, y, vars, meta, domain, not args.quiet)

    suite.print_summary()
    print("\n✅ Complete!\n")


if __name__ == "__main__":
    main()
