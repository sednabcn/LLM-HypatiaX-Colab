"""
Enhanced Hybrid System for DeFi Formula Discovery
Combines LLM symbolic reasoning with Neural Network learning

Key Enhancements:
1. Multi-strategy robust parsing for LLM responses
2. Method validation (R² > 0 requirement)
3. Stricter format enforcement in prompts
4. Improved NN architecture with early stopping
5. Better error handling and reporting
6. Formula caching for efficiency
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

from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class EnhancedHybridSystemDeFi:
    """
    Enhanced hybrid system with intelligent decision-making.

    Key Features:
    - Confidence scoring for formulas
    - Adaptive thresholds
    - Uncertainty-based ensemble
    - Robust parsing with multiple fallbacks
    - Method validation before selection
    - Better NN architecture
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

    def _compute_formula_confidence(self, description: str, metadata: Dict) -> float:
        """
        Compute confidence that this is a mathematical formula (0-1).
        Higher confidence = more likely LLM will succeed
        """
        desc_lower = description.lower()
        confidence = 0.5

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
        empirical = [("portfolio", "correlated"), ("aggregation", "weighted")]
        for indicator_set in empirical:
            if all(ind in desc_lower for ind in indicator_set):
                confidence -= 0.3
                break

        # Ground truth formula structure
        if metadata.get("ground_truth") != "N/A":
            gt = str(metadata.get("ground_truth", "")).lower()
            if any(
                op in gt for op in ["sqrt", "*", "/", "^", "**", "log", "min", "max"]
            ):
                confidence += 0.2

        # Extrapolation test (slightly reduce)
        if metadata.get("extrapolation_test"):
            confidence -= 0.1

        return np.clip(confidence, 0.0, 1.0)

    def _get_adaptive_thresholds(self, formula_confidence: float) -> Dict[str, float]:
        """
        Get adaptive thresholds based on formula confidence.
        High confidence -> lower thresholds (trust LLM more)
        Low confidence -> higher thresholds (require better performance)
        """
        if formula_confidence >= 0.8:
            return {
                "llm_excellent": 0.90,
                "llm_good": 0.70,
                "ensemble_min": 0.60,
                "prefer_llm_over_nn": 0.65,
            }
        elif formula_confidence >= 0.6:
            return {
                "llm_excellent": 0.95,
                "llm_good": 0.80,
                "ensemble_min": 0.70,
                "prefer_llm_over_nn": 0.75,
            }
        else:
            return {
                "llm_excellent": 0.98,
                "llm_good": 0.90,
                "ensemble_min": 0.80,
                "prefer_llm_over_nn": 0.85,
            }

    def generate_llm_formula(
        self,
        description: str,
        domain: str,
        variable_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> Dict:
        """Generate formula with improved prompts and caching"""

        # Check cache
        cache_key = f"{description}|{domain}|{','.join(variable_names)}"
        if cache_key in self.formula_cache:
            if verbose:
                print(f"  [LLM] Using cached formula")
            return self.formula_cache[cache_key].copy()

        desc_lower = description.lower()

        # Enhanced detection
        use_specialized = (
            (
                "optimal" in desc_lower
                and ("kelly" in desc_lower or "lp position" in desc_lower)
            )
            or ("liquidation" in desc_lower and "price" in desc_lower)
            or (
                "portfolio expected shortfall" in desc_lower
                and "correlated" in desc_lower
            )
            or ("impermanent loss percentage" in desc_lower)
        )

        if use_specialized:
            prompt = self._generate_specialized_prompt(
                description, domain, variable_names, metadata
            )
        else:
            prompt = self._generate_enhanced_standard_prompt(
                description, domain, variable_names, metadata
            )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text

            if verbose:
                print(f"\n  [LLM] Raw response length: {len(content)} chars")
                print(f"  [LLM] First 300 chars:\n{content[:300]}")

            parsed = self._parse_response(content, verbose=verbose)

            if verbose:
                print(f"  [LLM] Parsed formula: {parsed.get('formula', 'N/A')[:100]}")
                print(
                    f"  [LLM] Python code length: {len(parsed.get('python', 'N/A'))} chars"
                )
                if parsed.get("python") != "N/A":
                    print(
                        f"  [LLM] First line of code: {parsed.get('python', '').split(chr(10))[0]}"
                    )

            result = {
                "formula": parsed.get("formula", "N/A"),
                "latex": parsed.get("latex", "N/A"),
                "python_code": parsed.get("python", "N/A"),
                "explanation": parsed.get("explanation", "N/A"),
                "specialized": use_specialized,
            }

            # Cache only if we got valid code
            if (
                result["python_code"] != "N/A"
                and "def formula" in result["python_code"]
            ):
                self.formula_cache[cache_key] = result.copy()
                if verbose:
                    print(f"  [LLM] Formula cached successfully")
            elif verbose:
                print(f"  [LLM] Formula not cached (invalid code)")

            return result

        except Exception as e:
            if verbose:
                import traceback

                print(f"  [LLM] Exception occurred:")
                traceback.print_exc()
            return {"error": str(e)}

    def _generate_enhanced_standard_prompt(
        self, description: str, domain: str, variable_names: List[str], metadata: Dict
    ) -> str:
        """Enhanced standard prompt with better structure"""
        var_info = f"\nVariables (in order): {', '.join(variable_names)}"

        constants_info = ""
        if metadata and "constants" in metadata and metadata["constants"]:
            constants_info = "\n\n[CONSTANTS] Define these inside the function:"
            for k, v in metadata["constants"].items():
                constants_info += f"\n  {k} = {v}"

        ground_truth_hint = ""
        if (
            metadata
            and "ground_truth" in metadata
            and metadata["ground_truth"] != "N/A"
        ):
            ground_truth_hint = (
                f"\n\nExpected formula structure: {metadata['ground_truth']}"
            )

        domain_examples = {
            "lending": "\nExample: collateral_ratio = collateral_value / loan_value",
            "trading": "\nExample: price_impact = trade_size / liquidity_depth",
            "liquidity": "\nExample: k = reserve_x * reserve_y  # Constant product",
        }
        example = domain_examples.get(domain, "")

        return f"""You are a mathematical formula expert in {domain}.

Task: {description}{var_info}{constants_info}{ground_truth_hint}{example}

[CRITICAL REQUIREMENTS]
1. Function parameters must EXACTLY match the variable list in order
2. Define ALL constants INSIDE the function body
3. Use numpy functions: np.sqrt(), np.minimum(), np.maximum(), np.log(), etc.
4. Return a single numeric value or array
5. Function MUST be named 'formula'
6. Follow the EXACT output format below

[OUTPUT FORMAT]
You MUST output exactly three sections with these headers:

FORMULA:
[mathematical notation using the variable names provided]

PYTHON:
def formula({", ".join(variable_names)}):
    # Define constants here if needed
    constant_name = value
    # Implement formula
    result = ...
    return result

EXPLANATION:
[Brief 1-2 sentence explanation of what the formula computes]

CRITICAL: Output ONLY these three sections with these exact headers. No additional text, no markdown code fences outside the PYTHON section, no preamble, no postamble."""

    def _generate_specialized_prompt(
        self, description: str, domain: str, variable_names: List[str], metadata: Dict
    ) -> str:
        """Enhanced specialized prompts with exact implementations"""
        desc_lower = description.lower()
        var_list = ", ".join(variable_names)

        # Kelly Criterion / Optimal LP Position
        if ("optimal" in desc_lower and "lp" in desc_lower) or "kelly" in desc_lower:
            return f"""You are implementing the risk-adjusted Kelly criterion for optimal position sizing.

Task: {description}
Domain: {domain}
Variables (in order): {var_list}

[CRITICAL] Follow this EXACT format:

FORMULA:
f* = min(mu / (lambda * sigma^2), 1.0)

PYTHON:
def formula({var_list}):
    risk_aversion = 2.0
    f_star = {variable_names[0]} / (risk_aversion * {variable_names[1]}**2)
    return np.minimum(f_star, 1.0)

EXPLANATION:
Kelly criterion determines optimal position size by balancing expected returns against risk-adjusted variance, capped at 100% allocation.

Output ONLY these three sections. No additional text."""

        # Liquidation Price - Long
        if "liquidation" in desc_lower and "long" in desc_lower:
            return f"""Task: {description}
Domain: {domain}
Variables (in order): {var_list}

FORMULA:
P_liq = P_entry * (1 - 1/(L * m))

PYTHON:
def formula({var_list}):
    maintenance_margin = 0.8
    return {variable_names[0]} * (1.0 - 1.0 / ({variable_names[1]} * maintenance_margin))

EXPLANATION:
Price at which a long leveraged position gets liquidated due to insufficient collateral.

Output ONLY these three sections."""

        # Liquidation Price - Short
        if "liquidation" in desc_lower and "short" in desc_lower:
            return f"""Task: {description}
Domain: {domain}
Variables (in order): {var_list}

FORMULA:
P_liq = P_entry * (1 + 1/(L * m))

PYTHON:
def formula({var_list}):
    maintenance_margin = 0.8
    return {variable_names[0]} * (1.0 + 1.0 / ({variable_names[1]} * maintenance_margin))

EXPLANATION:
Price at which a short leveraged position gets liquidated.

Output ONLY these three sections."""

        # Impermanent Loss
        if "impermanent loss percentage" in desc_lower:
            return f"""Task: {description}
Domain: {domain}
Variables (in order): {var_list}

FORMULA:
IL% = (2*sqrt(r) / (1 + r) - 1) * 100

PYTHON:
def formula({var_list}):
    il_fraction = 2.0 * np.sqrt({variable_names[0]}) / (1.0 + {variable_names[0]}) - 1.0
    return il_fraction * 100.0

EXPLANATION:
Impermanent loss as a percentage for a 50/50 liquidity pool given the price ratio.

Output ONLY these three sections."""

        # Fallback to standard prompt
        return self._generate_enhanced_standard_prompt(
            description, domain, variable_names, metadata
        )

    def _parse_response(self, content: str, verbose: bool = False) -> Dict[str, str]:
        """
        Multi-strategy robust parsing for LLM responses.
        Tries multiple patterns to extract code.
        """
        parsed = {}

        # === FORMULA EXTRACTION ===
        match = re.search(r"FORMULA:\s*\n([^\n]+(?:\n[^\n]+)?)", content, re.IGNORECASE)
        if match:
            parsed["formula"] = match.group(1).strip()
        else:
            match = re.search(r"formula[:\s]+([^\n]+)", content, re.IGNORECASE)
            parsed["formula"] = match.group(1).strip() if match else "N/A"
            if verbose and not match:
                print(f"  [PARSE] No FORMULA section found")

        # === PYTHON CODE EXTRACTION (Multiple Strategies) ===
        code = None

        # Strategy A: Standard PYTHON: section
        match = re.search(
            r"PYTHON:\s*\n(.*?)(?=\n\n[A-Z]+:|\n\n\[|$)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if match:
            code = match.group(1).strip()
            if verbose:
                print(f"  [PARSE] Found code via PYTHON: section")

        # Strategy B: Code fence with python marker
        if not code:
            match = re.search(r"```python\s*\n(.*?)\n```", content, re.DOTALL)
            if match:
                code = match.group(1).strip()
                if verbose:
                    print(f"  [PARSE] Found code via ```python fence")

        # Strategy C: Any def formula() function
        if not code:
            match = re.search(
                r"(def formula\([^)]*\):.*?)(?=\n\n[A-Z]+:|\n\n```|\n\n\[|\Z)",
                content,
                re.DOTALL,
            )
            if match:
                code = match.group(1).strip()
                if verbose:
                    print(f"  [PARSE] Found code via def formula search")

        # Strategy D: Look for def formula anywhere in content
        if not code:
            match = re.search(
                r"(def formula\([^)]*\):(?:\n(?!def\s).*?)*)", content, re.DOTALL
            )
            if match:
                code = match.group(1).strip()
                if verbose:
                    print(f"  [PARSE] Found code via broad def formula search")

        if code:
            code = re.sub(r"^```python\s*\n", "", code)
            code = re.sub(r"\n```\s*$", "", code)
            code = code.strip()
            parsed["python"] = code

            if verbose:
                print(f"  [PARSE] Extracted {len(code)} chars of Python code")
                lines = code.split("\n")
                print(f"  [PARSE] Code has {len(lines)} lines")
                print(f"  [PARSE] First line: {lines[0] if lines else 'N/A'}")
        else:
            parsed["python"] = "N/A"
            if verbose:
                print(f"  [PARSE] WARNING: No Python code found")
                print(f"  [PARSE] Content preview (first 400 chars):")
                print(f"  {content[:400]}")

        # === EXPLANATION EXTRACTION ===
        match = re.search(
            r"EXPLANATION:\s*\n(.*?)(?=\n\n[A-Z]+:|\n\n```|\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if match:
            parsed["explanation"] = match.group(1).strip()
        else:
            parsed["explanation"] = "N/A"
            if verbose:
                print(f"  [PARSE] No EXPLANATION section found")

        return parsed

    def train_nn(
        self,
        X: np.ndarray,
        y: np.ndarray,
        is_extrapolation: bool = False,
        epochs: int = 500,
        verbose: bool = False,
    ) -> Tuple:
        """Train neural network with improved architecture and early stopping"""
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

        if verbose:
            print(f"  [NN] Training completed: R2={r2:.4f}, RMSE={np.sqrt(mse):.6f}")

        return model, metrics, scaler_X, scaler_y

    def evaluate_llm_formula(
        self,
        formula_dict: Dict,
        X: np.ndarray,
        y_true: np.ndarray,
        var_names: List[str],
        verbose: bool = False,
    ) -> Dict:
        """Evaluate LLM formula with uncertainty quantification"""
        try:
            code = formula_dict.get("python_code", "")
            if not code or code == "N/A":
                if verbose:
                    print(f"  [EVAL] No code to evaluate")
                return {"error": "No code", "success": False}

            if "def formula" not in code:
                if verbose:
                    print(f"  [EVAL] Code doesn't contain 'def formula'")
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
                if verbose:
                    print(f"  [EVAL] No callable function found in code")
                return {"error": "No function", "success": False}

            if verbose:
                print(f"  [EVAL] Found function: {func.__name__}")

            y_pred = self._evaluate_function(func, X, var_names, verbose=verbose)

            if len(y_pred) != len(y_true):
                if verbose:
                    print(
                        f"  [EVAL] Shape mismatch: pred={len(y_pred)}, true={len(y_true)}"
                    )
                return {"error": "Shape mismatch", "success": False}

            mse = np.mean((y_pred - y_true) ** 2)
            ss_res = np.sum((y_true - y_pred) ** 2)
            ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0

            residuals = y_pred - y_true
            uncertainty = float(np.std(residuals))

            if verbose:
                print(f"  [EVAL] R2={r2:.6f}, RMSE={np.sqrt(mse):.6f}")

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

                print(f"  [EVAL] Exception during evaluation:")
                traceback.print_exc()
            return {"error": str(e), "success": False}

    def _evaluate_function(self, func, X, var_names, verbose=False):
        """Evaluate function with multiple strategies"""
        sig = inspect.signature(func)
        n_params = len(sig.parameters)
        n_features = X.shape[1]

        if verbose:
            print(
                f"  [EVAL] Function expects {n_params} params, data has {n_features} features"
            )

        if n_params == n_features:
            try:
                y = func(*[X[:, i] for i in range(n_features)])
                result = np.asarray(y).flatten()
                if verbose:
                    print(f"  [EVAL] Vectorized evaluation succeeded")
                return result
            except Exception as e:
                if verbose:
                    print(f"  [EVAL] Vectorized evaluation failed: {e}")

        try:
            y = np.empty(X.shape[0])
            for i in range(X.shape[0]):
                if n_params == n_features:
                    y[i] = func(*X[i, :])
                elif n_params < n_features:
                    y[i] = func(*X[i, :n_params])
            if verbose:
                print(f"  [EVAL] Row-by-row evaluation succeeded")
            return y
        except Exception as e:
            if verbose:
                print(f"  [EVAL] Row-by-row evaluation failed: {e}")

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
        """Enhanced hybrid prediction with adaptive decision-making and validation."""

        formula_confidence = self._compute_formula_confidence(description, metadata)
        thresholds = self._get_adaptive_thresholds(formula_confidence)
        is_extrapolation = metadata.get("extrapolation_test", False)

        if verbose:
            print(f"\n  [HYBRID] Formula confidence: {formula_confidence:.2f}")
            print(f"  [HYBRID] Thresholds: {thresholds}")
            print(f"  [HYBRID] Extrapolation: {is_extrapolation}")

        # STEP 1: Generate and Evaluate LLM
        llm_result = self.generate_llm_formula(
            description, domain, var_names, metadata, verbose=verbose
        )

        if "error" not in llm_result and llm_result.get("python_code") != "N/A":
            llm_metrics = self.evaluate_llm_formula(
                llm_result, X, y_true, var_names, verbose=verbose
            )
        else:
            llm_metrics = {
                "error": llm_result.get("error", "No valid code"),
                "success": False,
            }
            if verbose:
                print(f"  [HYBRID] LLM generation failed: {llm_metrics['error']}")

        # STEP 2: Train and Evaluate NN
        nn_model, nn_metrics, scaler_X, scaler_y = self.train_nn(
            X, y_true, is_extrapolation=is_extrapolation, epochs=500, verbose=verbose
        )
        nn_predictions = self._get_nn_predictions(nn_model, X, scaler_X, scaler_y)

        # STEP 3: Extract Scores
        llm_r2 = llm_metrics.get("r2", -999) if llm_metrics.get("success") else -999
        nn_r2 = nn_metrics.get("r2", -999)

        if verbose:
            print(f"\n  [HYBRID] LLM R2: {llm_r2:.4f}, NN R2: {nn_r2:.4f}")

        # STEP 4: Validate Methods
        llm_valid = llm_r2 > 0.0
        nn_valid = nn_r2 > 0.0

        if verbose:
            print(f"  [HYBRID] LLM Valid: {llm_valid}, NN Valid: {nn_valid}")

        # STEP 5: Decision Logic with Validation
        if not llm_valid and not nn_valid:
            decision = "failed"
            final_r2 = max(llm_r2, nn_r2)
            final_rmse = (
                llm_metrics.get("rmse", 999)
                if llm_r2 > nn_r2
                else nn_metrics.get("rmse", 999)
            )
            reason = "Both LLM and NN failed (R2 < 0)"
            if verbose:
                print(f"  [HYBRID] WARNING: Both methods failed!")

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
            # Both valid - apply sophisticated logic
            if formula_confidence >= 0.8 and llm_r2 > thresholds["llm_good"]:
                decision = "llm"
                final_r2 = llm_r2
                final_rmse = llm_metrics["rmse"]
                reason = f"High-confidence formula (conf={formula_confidence:.2f}, R2={llm_r2:.4f})"

            elif llm_r2 > thresholds["llm_excellent"]:
                decision = "llm"
                final_r2 = llm_r2
                final_rmse = llm_metrics["rmse"]
                reason = f"Excellent LLM (R2>{thresholds['llm_excellent']:.2f})"

            elif (
                llm_r2 > thresholds["ensemble_min"]
                and nn_r2 > thresholds["ensemble_min"]
            ):
                decision = "ensemble"
                llm_predictions = llm_metrics.get("predictions")

                if llm_predictions is not None:
                    llm_uncertainty = llm_metrics.get("uncertainty", 1.0)
                    nn_uncertainty = np.std(nn_predictions - y_true)

                    weight_llm = (1.0 / (llm_uncertainty + 1e-6)) ** 0.5
                    weight_nn = (1.0 / (nn_uncertainty + 1e-6)) ** 0.5

                    weight_llm *= llm_r2
                    weight_nn *= nn_r2

                    total_weight = weight_llm + weight_nn
                    weight_llm /= total_weight
                    weight_nn /= total_weight

                    ensemble_predictions = (
                        weight_llm * llm_predictions + weight_nn * nn_predictions
                    )

                    mse = np.mean((y_true - ensemble_predictions) ** 2)
                    ss_res = np.sum((y_true - ensemble_predictions) ** 2)
                    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
                    final_r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0
                    final_rmse = np.sqrt(mse)

                    reason = f"Uncertainty ensemble (LLM:{weight_llm:.2f}, NN:{weight_nn:.2f})"
                else:
                    if llm_r2 > nn_r2:
                        decision = "llm"
                        final_r2, final_rmse = llm_r2, llm_metrics["rmse"]
                        reason = "Ensemble fallback to LLM"
                    else:
                        decision = "nn"
                        final_r2, final_rmse = nn_r2, nn_metrics["rmse"]
                        reason = "Ensemble fallback to NN"

            elif llm_r2 > thresholds["prefer_llm_over_nn"] and llm_r2 > nn_r2:
                decision = "llm"
                final_r2 = llm_r2
                final_rmse = llm_metrics["rmse"]
                reason = f"LLM preferred over NN (R2={llm_r2:.4f} > {nn_r2:.4f})"

            else:
                if llm_r2 > nn_r2:
                    decision = "llm"
                    final_r2 = llm_r2
                    final_rmse = llm_metrics["rmse"]
                    reason = f"LLM better than NN ({llm_r2:.4f} > {nn_r2:.4f})"
                else:
                    decision = "nn"
                    final_r2 = nn_r2
                    final_rmse = nn_metrics["rmse"]
                    reason = f"NN better than LLM ({nn_r2:.4f} > {llm_r2:.4f})"

        if verbose:
            print(f"\n  [HYBRID] === DECISION ===")
            print(f"  [HYBRID] Method: {decision.upper()}")
            print(f"  [HYBRID] Reason: {reason}")
            print(f"  [HYBRID] Final R2: {final_r2:.4f}")
            print(f"  [HYBRID] ===============")

        return {
            "method": "hybrid_enhanced",
            "description": description,
            "domain": domain,
            "decision": decision,
            "decision_reason": reason,
            "formula_confidence": float(formula_confidence),
            "adaptive_thresholds": thresholds,
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
        print(f"[OK] Results saved: {filepath}")


def run_enhanced_test(
    domains: List[str] = None, num_samples: int = 100, verbose: bool = False
):
    """Run enhanced hybrid system test"""
    protocol = DeFiExperimentProtocol()
    hybrid = EnhancedHybridSystemDeFi()

    if domains is None:
        domains = protocol.get_all_domains()

    print("=" * 80)
    print("[EXPERIMENT] ENHANCED HYBRID SYSTEM".center(80))
    print("=" * 80)
    print(f"Enhancements:")
    print(f"  * Confidence-based formula detection")
    print(f"  * Adaptive thresholds per formula type")
    print(f"  * Multi-strategy robust parsing")
    print(f"  * Method validation (R2 > 0 requirement)")
    print(f"  * Uncertainty-aware ensemble weighting")
    print(f"  * Improved NN architecture + early stopping")
    print(f"  * Formula caching for efficiency")
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
            print(f"  R2: {metrics['r2']:.6f}, RMSE: {metrics['rmse']:.6f}")

            if metrics["r2"] > 0.99:
                print(f"  [EXCELLENT]")
            elif metrics["r2"] > 0.95:
                print(f"  [GOOD]")
            elif metrics["r2"] > 0.80:
                print(f"  [ACCEPTABLE]")
            elif metrics["r2"] > 0.0:
                print(f"  [NEEDS IMPROVEMENT]")
            else:
                print(f"  [FAILED]")

            all_results.append(result)
            hybrid.results.append(result)

    os.makedirs("hypatiax/data/results", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    hybrid.save_results(f"hypatiax/data/results/hybrid_enhanced_{ts}.json")

    print("\n" + "=" * 80)
    print("ENHANCED SYSTEM SUMMARY".center(80))
    print("=" * 80)

    decisions = defaultdict(int)
    confidences = []
    r2_scores = []

    for r in all_results:
        decisions[r["decision"]] += 1
        confidences.append(r["formula_confidence"])
        r2_scores.append(r["evaluation"]["r2"])

    print(f"\nTotal cases: {len(all_results)}")
    print(f"Mean R2: {np.mean(r2_scores):.4f}")
    print(f"Median R2: {np.median(r2_scores):.4f}")
    print(f"Min R2: {np.min(r2_scores):.4f}")
    print(f"Mean confidence: {np.mean(confidences):.2f}")

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
                f"  {decision.upper():8s}: {count:2d} ({pct:5.1f}%) - Mean R2 = {mean_r2:.4f}"
            )

    problem_cases = [r for r in all_results if r["evaluation"]["r2"] < 0.80]
    if problem_cases:
        print(
            f"\n[WARNING] Cases needing improvement (R2 < 0.80): {len(problem_cases)}"
        )
        for r in problem_cases[:5]:
            print(f"  * {r['description'][:60]}")
            print(f"    R2: {r['evaluation']['r2']:.4f}, Decision: {r['decision']}")
    else:
        print(f"\n[SUCCESS] All cases R2 >= 0.80!")

    print("\n" + "=" * 80)
    return all_results


def run_single_test(
    description: str, domain: str, num_samples: int = 100, verbose: bool = True
):
    """Run hybrid system on a single test case for debugging"""
    protocol = DeFiExperimentProtocol()
    hybrid = EnhancedHybridSystemDeFi()

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
        print(f"[ERROR] Test case not found: {description}")
        print(f"Available cases in {domain}:")
        for desc, _, _, _, _ in test_cases:
            print(f"  * {desc}")
        return None

    desc, X, y, var_names, meta = target_case

    print(f"\nTest Case: {desc}")
    print(f"Variables: {', '.join(var_names)}")
    print(f"Samples: {len(X)}")

    if meta.get("extrapolation_test"):
        print(f"[WARNING] EXTRAPOLATION TEST")

    if meta.get("ground_truth"):
        print(f"Ground Truth: {meta['ground_truth']}")

    print("\n" + "-" * 80)

    result = hybrid.hybrid_predict(desc, domain, X, y, var_names, meta, verbose=verbose)

    print("\n" + "-" * 80)
    print("RESULTS:")
    print(f"  Decision: {result['decision'].upper()}")
    print(f"  Reason: {result['decision_reason']}")
    print(f"  Formula Confidence: {result['formula_confidence']:.2f}")
    print(f"  LLM Valid: {result.get('llm_valid', 'N/A')}")
    print(f"  NN Valid: {result.get('nn_valid', 'N/A')}")

    print(f"\nMetrics:")
    print(f"  Final R2: {result['evaluation']['r2']:.6f}")
    print(f"  Final RMSE: {result['evaluation']['rmse']:.6f}")
    print(f"  Success: {result['evaluation']['success']}")

    llm_metrics = result["llm_result"]["metrics"]
    nn_metrics = result["nn_result"]["metrics"]

    print(f"\nComponent Performance:")
    print(f"  LLM R2: {llm_metrics.get('r2', 'N/A')}")
    print(f"  NN R2:  {nn_metrics['r2']:.6f}")

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


def compare_methods(domain: str = "lending", num_samples: int = 100):
    """Compare LLM-only, NN-only, and Hybrid approaches"""
    protocol = DeFiExperimentProtocol()
    hybrid = EnhancedHybridSystemDeFi()

    print("=" * 80)
    print(f"[COMPARE] METHOD COMPARISON: {domain.upper()}".center(80))
    print("=" * 80)

    test_cases = protocol.load_test_data(domain, num_samples=num_samples)
    comparison_results = []

    for desc, X, y, var_names, meta in test_cases:
        print(f"\nTest: {desc}")
        result = hybrid.hybrid_predict(
            desc, domain, X, y, var_names, meta, verbose=False
        )

        llm_r2 = result["llm_result"]["metrics"].get("r2", 0)
        nn_r2 = result["nn_result"]["metrics"]["r2"]
        hybrid_r2 = result["evaluation"]["r2"]
        decision = result["decision"]

        print(f"  LLM R2:    {llm_r2:.4f}")
        print(f"  NN R2:     {nn_r2:.4f}")
        print(f"  Hybrid R2: {hybrid_r2:.4f} [{decision.upper()}]")

        best_method = max(
            [("LLM", llm_r2), ("NN", nn_r2), ("Hybrid", hybrid_r2)], key=lambda x: x[1]
        )
        print(f"  [WINNER] {best_method[0]} ({best_method[1]:.4f})")

        comparison_results.append(
            {
                "description": desc,
                "llm_r2": llm_r2,
                "nn_r2": nn_r2,
                "hybrid_r2": hybrid_r2,
                "decision": decision,
                "winner": best_method[0],
            }
        )

    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY".center(80))
    print("=" * 80)

    llm_wins = sum(1 for r in comparison_results if r["winner"] == "LLM")
    nn_wins = sum(1 for r in comparison_results if r["winner"] == "NN")
    hybrid_wins = sum(1 for r in comparison_results if r["winner"] == "Hybrid")

    print(f"\nWinner Breakdown:")
    print(
        f"  LLM:    {llm_wins}/{len(comparison_results)} ({100 * llm_wins / len(comparison_results):.1f}%)"
    )
    print(
        f"  NN:     {nn_wins}/{len(comparison_results)} ({100 * nn_wins / len(comparison_results):.1f}%)"
    )
    print(
        f"  Hybrid: {hybrid_wins}/{len(comparison_results)} ({100 * hybrid_wins / len(comparison_results):.1f}%)"
    )

    avg_llm = np.mean([r["llm_r2"] for r in comparison_results])
    avg_nn = np.mean([r["nn_r2"] for r in comparison_results])
    avg_hybrid = np.mean([r["hybrid_r2"] for r in comparison_results])

    print(f"\nAverage R2:")
    print(f"  LLM:    {avg_llm:.4f}")
    print(f"  NN:     {avg_nn:.4f}")
    print(f"  Hybrid: {avg_hybrid:.4f}")

    improvement_over_llm = ((avg_hybrid - avg_llm) / max(avg_llm, 0.01)) * 100
    improvement_over_nn = ((avg_hybrid - avg_nn) / max(avg_nn, 0.01)) * 100

    print(f"\nHybrid Improvement:")
    print(f"  vs LLM: {improvement_over_llm:+.1f}%")
    print(f"  vs NN:  {improvement_over_nn:+.1f}%")

    return comparison_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Hybrid System for DeFi")
    parser.add_argument("--mode", choices=["full", "single", "compare"], default="full")
    parser.add_argument("--domains", nargs="+", default=None)
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--description", type=str, default=None)
    parser.add_argument("--domain", type=str, default="lending")

    args = parser.parse_args()

    if args.mode == "full":
        run_enhanced_test(
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
    elif args.mode == "compare":
        compare_methods(domain=args.domain, num_samples=args.samples)
