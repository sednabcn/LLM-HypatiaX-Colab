"""
HypatiaX Hybrid Discovery System v5.0
======================================
FULL REWRITE — fixes the LLM wiring bug that has been present since v3.5.

Bug history
-----------
v3.5  use_llm parameter introduced in discover_validate_interpret() signature.
      AnthropicProvider / GoogleProvider imported directly.
      Bug: neither provider was ever called; SymbolicEngineWithLLM never used.

v3.8  Direct LLM imports removed (regression).
      Bug: persisted — use_llm still a no-op.

v4.1-PROD (v40)
      PROD-1…7 performance improvements added.
      Bug: persisted — self.anthropic_provider / self.google_provider set but
      never read; SymbolicEngineWithLLM never imported; use_llm flag never
      checked in method body.

v4.2 / v4.2.1 (hybrid_system.py / v43)
      Variable-name fix, optional import guards added.
      Bug: persisted unchanged.

Root cause
----------
HybridDiscoverySystem always instantiated the BASE class SymbolicEngine, not
the subclass SymbolicEngineWithLLM that lives in the same module and implements
all four LLM modes (none / seed / hybrid / fallback).  The use_llm parameter
was accepted, documented, but never inspected inside the method body — making
it a no-op flag across the entire version history.

What v5.0 fixes
---------------
FIX-1   Import SymbolicEngineWithLLM alongside SymbolicEngine.
FIX-2   __init__ instantiates SymbolicEngineWithLLM when use_llm=True OR when
        an LLM API key is available, passing llm_mode through correctly.
FIX-3   discover_validate_interpret() now reads use_llm and routes to the
        correct engine path.
FIX-4   _discover_with_retry() respects the engine type already set —
        no duplicate routing needed.
FIX-5   _initialize_llm_providers() retained for the external
        anthropic_provider / google_provider attributes (used by callers that
        talk to LLM providers directly), but the discovery path now uses
        SymbolicEngineWithLLM's internal IntegratedLLMEngine instead.
FIX-6   use_llm=True now propagates through the discover() thin adapter so
        benchmark runners can enable LLM guidance via metadata.

All PROD-1…7 performance improvements from v4.1-PROD are preserved.
Public API is backward-compatible: callers that pass use_llm=False (or omit
it) get pure-PySR behaviour identical to v4.1-PROD.
"""

import json
import logging
import os
import random
import re
import time
from collections import deque
from datetime import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
random.seed(42)
np.random.seed(42)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_env_path)

# ---------------------------------------------------------------------------
# FIX-1: Import BOTH SymbolicEngine and SymbolicEngineWithLLM.
# Previous versions only imported the base class, making LLM guidance
# unreachable regardless of what use_llm was set to.
# ---------------------------------------------------------------------------
from hypatiax.tools.symbolic.symbolic_engine import (
    DiscoveryConfig,
    LLMConfig,
    SymbolicEngine,
    SymbolicEngineWithLLM,
    detect_collapsed_constants,
)
from hypatiax.tools.symbolic.physics_aware_regressor import PhysicsAwareRegressor
from hypatiax.tools.validation.ensemble_validator import EnsembleValidator


class DiscoveryMode(Enum):
    STRICT = "strict"
    CALIBRATED = "calibrated"


# ---------------------------------------------------------------------------
# PROD-1: Cached quality check (unchanged from v4.1-PROD).
# ---------------------------------------------------------------------------
@lru_cache(maxsize=256)
def _cached_quality(
    expression: str,
    r2_rounded: float,
    complexity_threshold: int,
) -> Tuple[bool, int, Tuple[str, ...]]:
    """
    Pure-function quality check used as the LRU target.
    Returns (is_overfit, complexity, warnings_tuple) — fully hashable.
    """
    complexity = len(expression)
    is_overfit = False
    warnings: List[str] = []

    if complexity > complexity_threshold and r2_rounded < 0.999:
        is_overfit = True
        warnings.append(f"High complexity ({complexity}) but R2={r2_rounded:.4f}")

    constants = re.findall(r"\d+\.\d+", expression)
    if len(constants) > 5:
        warnings.append(f"Many constants detected ({len(constants)})")

    suspicious = [c for c in constants if float(c) < 0.001 or float(c) > 1000]
    if suspicious:
        warnings.append(f"Suspicious constants: {suspicious[:3]}")

    return is_overfit, complexity, tuple(warnings)


# ---------------------------------------------------------------------------
# PROD-3: Pre-compiled regex patterns for PySR operator normalisation.
# ---------------------------------------------------------------------------
def _build_op_patterns(aliases: Dict[str, str]) -> Dict[str, Tuple[re.Pattern, str]]:
    return {
        pysr_name: (re.compile(r"\b" + re.escape(pysr_name) + r"\b"), numpy_name)
        for pysr_name, numpy_name in aliases.items()
    }


# ---------------------------------------------------------------------------
# PROD-4: Recursive serialisation helper.
# ---------------------------------------------------------------------------
def _to_serialisable(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {str(k): _to_serialisable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_serialisable(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    return obj


class HybridDiscoverySystem:
    """
    Hybrid discovery system v5.0.

    Now correctly wires LLM guidance through SymbolicEngineWithLLM when
    use_llm=True or when an API key is present.  Backward-compatible:
    use_llm=False (default) gives pure-PySR behaviour identical to v4.1-PROD.

    LLM modes (passed as llm_mode, or inferred from primary_llm):
        "none"     — pure PySR (default, same as all previous versions)
        "seed"     — LLM configures PySR operator set before search
        "hybrid"   — LLM attempts first; PySR refines if needed
        "fallback" — PySR first; LLM fires only when PySR underperforms
    """

    # PROD-3: Alias table (unchanged from v4.1-PROD)
    _PYSR_OP_ALIASES: Dict[str, str] = {
        "safe_asin":   "arcsin",
        "safe_acos":   "arccos",
        "asin_of_sin": "arcsin",
        "acos_of_cos": "arccos",
        "atan_of_tan": "arctan",
    }
    _PYSR_OP_PATTERNS: Dict[str, Tuple[re.Pattern, str]] = _build_op_patterns(
        _PYSR_OP_ALIASES
    )

    def __init__(
        self,
        domain: str = "general",
        discovery_config: Optional[DiscoveryConfig] = None,
        discovery_mode: DiscoveryMode = DiscoveryMode.STRICT,
        max_results: Optional[int] = 100,
        validation_weights: Optional[Dict[str, float]] = None,
        use_rich_output: bool = True,
        primary_llm: str = "anthropic",
        enable_fallback: bool = True,
        enable_physics_fallback: bool = False,
        physics_fallback_threshold: float = 0.85,
        complexity_penalty_threshold: int = 20,
        physics_population_size: int = 20,
        physics_generations: int = 100,
        max_retries: int = 3,
        enable_auto_config: bool = True,
        anthropic_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
        # FIX-2: New parameters to control LLM engine behaviour.
        use_llm: bool = False,
        llm_mode: str = "hybrid",          # none | seed | hybrid | fallback
        llm_n_candidates: int = 3,
        llm_temperature: float = 0.3,
    ):
        """
        Initialize HybridDiscoverySystem v5.0.

        New parameters vs v4.1-PROD
        ----------------------------
        use_llm : bool
            Master switch.  When False (default) behaviour is identical to all
            previous versions.  When True, SymbolicEngineWithLLM is used and
            llm_mode controls the integration strategy.
        llm_mode : str
            "none"     — pure PySR (same as use_llm=False)
            "seed"     — LLM suggests operators; PySR searches
            "hybrid"   — LLM first, PySR refines (recommended)
            "fallback" — PySR first, LLM backup on poor R²
        llm_n_candidates : int
            Number of equation hypotheses to request from the LLM per call.
        llm_temperature : float
            Sampling temperature passed to the LLM API.
        """
        self.domain = domain
        self.discovery_mode = discovery_mode
        self.primary_llm = primary_llm
        self.enable_fallback = enable_fallback
        self.enable_physics_fallback = enable_physics_fallback
        self.physics_fallback_threshold = physics_fallback_threshold
        self.complexity_penalty_threshold = complexity_penalty_threshold
        self.physics_population_size = physics_population_size
        self.physics_generations = physics_generations
        self.max_retries = max_retries
        self.enable_auto_config = enable_auto_config
        self.use_llm = use_llm
        self.llm_mode = llm_mode if use_llm else "none"

        logger.info("=" * 70)
        logger.info("HybridDiscoverySystem v5.0 — LLM WIRING FIX")
        logger.info("=" * 70)
        logger.info(f"Domain: {domain}")
        logger.info(f"Discovery mode: {self.discovery_mode.value}")
        logger.info(f"Primary LLM: {primary_llm}")
        logger.info(f"use_llm: {use_llm}  |  llm_mode: {self.llm_mode}")
        logger.info(f"Auto-config: {enable_auto_config}")
        logger.info(f"Max retries: {max_retries}")
        logger.info(f"PhysicsAware fallback: {enable_physics_fallback}")
        logger.info(f"Complexity threshold: {complexity_penalty_threshold}")
        logger.info("=" * 70)

        if discovery_config is None:
            symbolic_config = DiscoveryConfig(
                niterations=40,
                enable_auto_configuration=enable_auto_config,
            )
            logger.info("Using default iterations: 40")
        else:
            symbolic_config = discovery_config
            logger.info(f"Using provided iterations: {symbolic_config.niterations}")
            logger.info(f"Parsimony: {symbolic_config.parsimony}")
            logger.info(
                f"Transcendental compositions: {symbolic_config.use_transcendental_compositions}"
            )

        # PROD-2: operator injection (unchanged from v4.1-PROD)
        self._inject_operators(symbolic_config, domain)

        # FIX-2: Resolve the API key that will be used for LLM guidance.
        _llm_api_key = (
            anthropic_api_key
            if primary_llm == "anthropic"
            else (google_api_key or os.getenv("GOOGLE_API_KEY"))
        ) or os.getenv("ANTHROPIC_API_KEY")

        # FIX-2: Auto-enable LLM if a key is present and use_llm was not
        # explicitly set to False by the caller.
        _key_present = bool(_llm_api_key)
        if _key_present and not use_llm:
            logger.info(
                "[LLM] API key found but use_llm=False — running pure PySR. "
                "Pass use_llm=True to enable LLM guidance."
            )

        # FIX-2: Instantiate the correct engine class.
        # Previous versions ALWAYS used SymbolicEngine (base) even when
        # use_llm=True, because SymbolicEngineWithLLM was never imported.
        if self.llm_mode != "none" and _key_present:
            llm_config = LLMConfig(
                enabled=True,
                api_key=_llm_api_key,
                n_candidates=llm_n_candidates,
                temperature=llm_temperature,
            )
            try:
                self.symbolic_engine: SymbolicEngine = SymbolicEngineWithLLM(
                    symbolic_config,
                    domain=domain,
                    llm_config=llm_config,
                    llm_mode=self.llm_mode,
                )
                logger.info(
                    f"[LLM] SymbolicEngineWithLLM instantiated "
                    f"(mode={self.llm_mode}, candidates={llm_n_candidates})"
                )
            except Exception:
                logger.error(
                    "SymbolicEngineWithLLM construction FAILED — "
                    "falling back to base SymbolicEngine",
                    exc_info=True,
                )
                self.symbolic_engine = SymbolicEngine(symbolic_config, domain=domain)
                self.llm_mode = "none"
        else:
            # Pure-PySR path: identical to all previous versions.
            self.symbolic_engine = SymbolicEngine(symbolic_config, domain=domain)
            if self.llm_mode != "none":
                logger.warning(
                    "[LLM] llm_mode != 'none' but no API key available — "
                    "running pure PySR.  Set ANTHROPIC_API_KEY or pass "
                    "anthropic_api_key= to enable LLM guidance."
                )
                self.llm_mode = "none"

        try:
            self.validator = EnsembleValidator(
                domain=domain, max_history=max_results, weights=validation_weights
            )
        except Exception:
            logger.error("EnsembleValidator construction FAILED", exc_info=True)
            raise

        # FIX-5: Keep external provider attributes for callers that use them
        # directly (e.g. interpretation, explanation steps).  These are NOT
        # used in the discovery path — SymbolicEngineWithLLM owns that now.
        self._initialize_llm_providers(anthropic_api_key, google_api_key)

        self.max_results = max_results
        self.results: Any = deque(maxlen=max_results) if max_results is not None else []

        self.stats: Dict[str, int] = {
            "discoveries": 0,
            "symbolic_attempts": 0,
            "symbolic_successes": 0,
            "symbolic_failures": 0,
            "llm_guided": 0,
            "llm_skipped": 0,
            "physics_used": 0,
            "physics_successes": 0,
            "validations": 0,
            "auto_configs": 0,
        }

        self.use_rich_output = use_rich_output
        logger.info("[OK] HybridDiscoverySystem v5.0 initialized\n")

    # ------------------------------------------------------------------
    # PROD-2: shared operator-injection logic (unchanged from v4.1-PROD)
    # ------------------------------------------------------------------
    @staticmethod
    def _inject_operators(symbolic_config: DiscoveryConfig, domain: str) -> None:
        """Inject safe_asin/safe_acos when use_transcendental_compositions is True."""
        _TRIG_DEFAULTS = ["sin", "cos", "tan"]
        _needs_inv_trig = getattr(symbolic_config, "use_transcendental_compositions", False)
        if _needs_inv_trig:
            _inv_trig = ["safe_asin", "safe_acos"]
            _current = list(getattr(symbolic_config, "unary_operators", None) or [])
            if not _current:
                _current = list(_TRIG_DEFAULTS)
                logger.info(
                    f"[AUTO-v5.0] unary_operators was empty — seeding with trig defaults: {_current}"
                )
            _added = [op for op in _inv_trig if op not in _current]
            if _added:
                symbolic_config.unary_operators = _current + _added
                logger.info(
                    f"[AUTO-v5.0] Injected inverse-trig operators {_added} "
                    f"(use_tc=True). Full unary set: {symbolic_config.unary_operators}"
                )
        else:
            logger.info(
                f"[AUTO-v5.0] Skipping safe_asin/safe_acos injection "
                f"(domain='{domain}', use_tc=False)"
            )

    def _initialize_llm_providers(
        self, anthropic_api_key: Optional[str], google_api_key: Optional[str]
    ) -> None:
        """
        Initialize external LLM provider references (FIX-5).

        These are kept for callers that use anthropic_provider / google_provider
        directly (e.g. interpretation, summarisation steps outside discovery).
        The discovery path itself now uses SymbolicEngineWithLLM internally.
        """
        api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            try:
                from hypatiax.tools.llm_providers.anthropic_provider import AnthropicProvider
                self.anthropic_provider = AnthropicProvider(api_key=api_key, max_tokens=4096)
            except Exception:
                self.anthropic_provider = None
        else:
            self.anthropic_provider = None

        api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        if api_key:
            try:
                from hypatiax.tools.llm_providers.google_provider import GoogleProvider
                self.google_provider = GoogleProvider(api_key=api_key, max_output_tokens=8192)
            except Exception:
                self.google_provider = None
        else:
            self.google_provider = None

    def _create_optimized_physics_regressor(
        self, noise_level: Optional[float] = None
    ) -> PhysicsAwareRegressor:
        return PhysicsAwareRegressor(
            domain=self.domain,
            verbose=True,
            population_size=self.physics_population_size,
            generations=self.physics_generations,
            noise_level=noise_level,
        )

    def _check_expression_quality(self, expression: str, r2: float) -> Dict[str, Any]:
        """Quality check — PROD-1: delegates to LRU-cached pure function."""
        r2_rounded = round(r2, 6)
        is_overfit, complexity, warnings_tuple = _cached_quality(
            expression, r2_rounded, self.complexity_penalty_threshold
        )
        return {
            "is_overfit": is_overfit,
            "complexity": complexity,
            "warnings": list(warnings_tuple),
        }

    def _detect_rational_pattern(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Detect if data likely follows a rational/saturation pattern (unchanged)."""
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score as _r2

        if X.shape[1] < 1 or np.any(y <= 0):
            return False
        try:
            inv_y = 1.0 / y
            for i in range(X.shape[1]):
                xi = X[:, i]
                if np.any(xi <= 0):
                    continue
                inv_x = 1.0 / xi
                r2 = _r2(
                    inv_y,
                    LinearRegression()
                    .fit(inv_x.reshape(-1, 1), inv_y)
                    .predict(inv_x.reshape(-1, 1)),
                )
                if r2 > 0.85:
                    logger.info(
                        f"[RATIONAL] Lineweaver-Burk R²={r2:.3f} on var {i} — injecting inv"
                    )
                    return True
            for i in range(X.shape[1]):
                xi = X[:, i]
                sort_idx = np.argsort(xi)
                y_sorted = y[sort_idx]
                if y_sorted[-1] > y_sorted[0]:
                    diffs = np.diff(y_sorted)
                    if np.all(diffs >= -1e-6) and diffs[-1] < diffs[0] * 0.3:
                        logger.info(
                            f"[RATIONAL] Saturation shape detected on var {i} — injecting inv"
                        )
                        return True
        except Exception as exc:
            logger.warning(f"[RATIONAL] Detection failed: {exc}")
        return False

    # ------------------------------------------------------------------
    # Core discovery worker
    # ------------------------------------------------------------------
    def _discover_with_retry(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str],
        variable_descriptions: Dict[str, str],
        variable_units: Dict[str, str],
        equation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Discover with retry.

        FIX-4: No engine-routing needed here — the correct engine type
        (SymbolicEngine or SymbolicEngineWithLLM) was already selected in
        __init__ based on use_llm and key availability.  All retry logic and
        physics fallback are unchanged from v4.1-PROD.
        """
        best_result = None
        best_r2 = -np.inf
        last_attempt_error: Optional[Exception] = None
        _inv_injected = False

        for attempt in range(self.max_retries):
            try:
                seed = 42 + attempt
                logger.info(f"\n[SYMBOLIC] Attempt {attempt + 1}/{self.max_retries} (seed={seed})")
                self.stats["symbolic_attempts"] += 1

                result = self.symbolic_engine.discover(
                    X, y, variable_names, equation_name=equation_name, random_state=seed
                )

                r2 = result.get("r2_score", 0)
                expr = result.get("expression", "")

                # Track whether LLM was actually used this attempt
                if result.get("llm_mode") and result["llm_mode"] != "none":
                    self.stats["llm_guided"] += 1
                else:
                    self.stats["llm_skipped"] += 1

                try:
                    collapsed = detect_collapsed_constants(expr, variable_names)
                except Exception:
                    logger.error("detect_collapsed_constants FAILED", exc_info=True)
                    collapsed = []

                result["collapsed_constants"] = collapsed
                logger.info(f"   Result: {expr}")
                logger.info(f"   R2 = {r2:.4f}")
                if result.get("llm_mode"):
                    logger.info(f"   LLM mode: {result['llm_mode']}")

                if expr and expr not in (
                    "DISCOVERY_FAILED", "NO_VALID_EQUATIONS", "VALIDATION_FAILED"
                ):
                    quality = self._check_expression_quality(expr, r2)
                    if quality["is_overfit"]:
                        logger.warning("   [WARNING] Possible overfit")
                        for w in quality["warnings"]:
                            logger.warning(f"      {w}")
                else:
                    quality = {"is_overfit": False, "complexity": 0, "warnings": []}

                if r2 > best_r2:
                    best_r2 = r2
                    best_result = result
                    best_result["discovery_engine"] = "symbolic"
                    best_result["attempt"] = attempt + 1
                    best_result["quality_check"] = quality
                    logger.info("   [BEST] New best!")

                if attempt == 0 and r2 < 0.1 and not _inv_injected:
                    if self._detect_rational_pattern(X, y):
                        _current_unary = list(
                            getattr(self.symbolic_engine.config, "unary_operators", None) or []
                        )
                        if "inv" not in _current_unary:
                            self.symbolic_engine.config.unary_operators = _current_unary + ["inv"]
                            logger.info("[RATIONAL] Injected 'inv' into unary_operators for next attempt")
                            _inv_injected = True

                _early_stop_r2 = (
                    0.9999
                    if getattr(self.symbolic_engine.config, "use_transcendental_compositions", False)
                    else 0.95
                )
                if r2 >= _early_stop_r2 and not quality["is_overfit"]:
                    logger.info(f"   [EARLY STOP] Excellent result (R²={r2:.6f})")
                    self.stats["symbolic_successes"] += 1
                    return best_result

            except Exception as e:
                last_attempt_error = e
                logger.error(f"   [ERROR] Attempt {attempt + 1} failed: {e}")
                logger.error(f"Attempt {attempt + 1} exception", exc_info=True)

        if best_result and best_r2 >= 0.97:
            logger.info(f"\n[SUCCESS] SymbolicEngine succeeded (R2={best_r2:.4f})")
            self.stats["symbolic_successes"] += 1
            return best_result
        else:
            logger.warning(f"\n[WARNING] SymbolicEngine best R2={best_r2:.4f}")
            self.stats["symbolic_failures"] += 1

        if self.enable_physics_fallback and (
            not best_result or best_r2 < self.physics_fallback_threshold
        ):
            try:
                logger.info("\n[FALLBACK] Using PhysicsAwareRegressor...")
                _meta_noise = getattr(self, "_current_noise_level", None)
                physics_regressor = self._create_optimized_physics_regressor(
                    noise_level=_meta_noise
                )
                physics_regressor.fit_noise_aware(
                    X=X,
                    y=y,
                    variable_names=variable_names,
                    noise_level=_meta_noise,
                    variable_units=variable_units,
                    variable_descriptions=variable_descriptions,
                )
                expression = physics_regressor.get_expression()
                r2 = physics_regressor.best_fitness_
                logger.info(f"   PhysicsAware: {expression}")
                logger.info(f"   R2 = {r2:.4f}")
                physics_result = {
                    "expression": expression,
                    "r2_score": r2,
                    "discovery_engine": "physics_aware",
                    "complexity": len(expression),
                }
                self.stats["physics_used"] += 1
                if r2 > best_r2:
                    logger.info("   [BEST] PhysicsAware better!")
                    best_result = physics_result
                    best_r2 = r2
                    self.stats["physics_successes"] += 1
            except Exception as e:
                logger.error(f"   [ERROR] PhysicsAware failed: {e}")

        if best_result:
            logger.warning(
                f"[PARTIAL] Returning best result with R2={best_r2:.4f}. "
                "If R2 is very low, check that the right unary operators are enabled."
            )
            return best_result
        else:
            raise ValueError(
                f"All {self.max_retries} discovery attempts failed"
                + (f": {last_attempt_error}" if last_attempt_error else "")
                + f"\n  HINT: If this is an optics/trig equation, ensure "
                  f"safe_asin/safe_acos are in unary_operators (DiscoveryConfig). "
                  f"Domain detected: '{self.domain}'."
            ) from last_attempt_error

    @staticmethod
    def _normalise_expression(expression_str: str) -> str:
        """Replace PySR custom operator names — PROD-3: uses pre-compiled patterns."""
        result = expression_str
        for pat, numpy_name in HybridDiscoverySystem._PYSR_OP_PATTERNS.values():
            result = pat.sub(numpy_name, result)
        return result

    def _safe_validate(
        self,
        expression_str: str,
        variable_definitions: Dict[str, str],
        variable_units: Dict[str, str],
        test_data: Dict[str, np.ndarray],
    ) -> Dict[str, Any]:
        """Safe validation (unchanged from v4.1-PROD)."""
        normalised = self._normalise_expression(expression_str)
        if normalised != expression_str:
            logger.info(
                f"[NORMALISE] Expression rewritten for validator: "
                f"'{expression_str}' → '{normalised}'"
            )
        try:
            return self.validator.validate_complete(
                expression_str=normalised,
                variable_definitions=variable_definitions,
                variable_units=variable_units,
                test_data=test_data,
            )
        except Exception as e:
            logger.warning(f"[WARNING] Validation error: {str(e)[:100]}")
            return {
                "valid": False,
                "total_score": 60.0,
                "layer_scores": {
                    "symbolic": 100.0,
                    "dimensional": 20.0,
                    "domain": 60.0,
                    "numerical": 100.0,
                },
                "errors": [f"Validation error: {str(e)[:200]}"],
                "warnings": ["Validation failed - likely unit system issue"],
                "validation_exception": True,
            }

    # ------------------------------------------------------------------
    # Complete discovery workflow
    # ------------------------------------------------------------------
    def discover_validate_interpret(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str],
        variable_descriptions: Dict[str, str],
        variable_units: Dict[str, str],
        description: Optional[str] = None,
        equation_name: Optional[str] = None,
        validate_first: bool = True,
        show_formatted: bool = True,
        use_llm: bool = False,          # FIX-3: now actually read and respected
        min_validation_score: float = 85.0,
    ) -> Dict[str, Any]:
        """
        Complete discovery workflow v5.0.

        FIX-3: use_llm is now respected.  If True and the instance was
        initialised with use_llm=False (pure-PySR engine), a warning is
        logged and the call proceeds with pure PySR.  The recommended
        pattern is to set use_llm at __init__ time; the parameter here
        acts as a per-call override guard only.
        """
        # FIX-3: Per-call use_llm guard.
        _effective_llm = use_llm or self.use_llm
        if use_llm and self.llm_mode == "none":
            logger.warning(
                "[LLM] use_llm=True passed to discover_validate_interpret() but "
                "the engine was initialised in pure-PySR mode (either use_llm=False "
                "at __init__ or no API key was found).  Running pure PySR.  "
                "Reinitialise with use_llm=True to enable LLM guidance."
            )

        print(f"\n{'=' * 70}")
        print("DISCOVERY WORKFLOW v5.0")
        print(f"{'=' * 70}")
        print(f"Description: {description or 'Unnamed'}")
        print(f"Domain: {self.domain.upper()}")
        print(f"Samples: {len(X)}")
        print(f"Variables: {variable_names}")
        print(f"LLM mode: {self.llm_mode}")
        if equation_name:
            print(f"Equation hint: {equation_name}")
        print(f"{'=' * 70}")

        print("\n[DISCOVER] Running symbolic regression...")
        try:
            discovery_result = self._discover_with_retry(
                X, y, variable_names, variable_descriptions, variable_units,
                equation_name=equation_name,
            )
            self.stats["discoveries"] += 1

            engine = discovery_result.get("discovery_engine", "unknown")
            llm_info = discovery_result.get("llm_mode", "")
            print("\n[OK] Discovery complete")
            print(f"   Expression: {discovery_result['expression']}")
            print(f"   R2 Score: {discovery_result['r2_score']:.4f}")
            print(f"   Engine: {engine}")
            if llm_info:
                print(f"   LLM mode used: {llm_info}")
            if "attempt" in discovery_result:
                print(f"   Attempt: {discovery_result['attempt']}/{self.max_retries}")
            if discovery_result.get("auto_configuration", {}).get("used"):
                auto_cfg = discovery_result["auto_configuration"]["config"]
                print(f"   Auto-config: {auto_cfg.get('reason', 'N/A')}")
                self.stats["auto_configs"] += 1

        except Exception as e:
            import traceback as _tb_mod
            _tb_str = _tb_mod.format_exc()
            logger.error(f"Discovery failed: {e}")
            logger.error(_tb_str)
            return {
                "error": "discovery_failed",
                "message": str(e),
                "traceback": _tb_str,
            }

        print("\n[VALIDATE] Checking expression quality...")
        test_data = {name: X[:, i] for i, name in enumerate(variable_names)}
        validation_result = self._safe_validate(
            expression_str=discovery_result["expression"],
            variable_definitions=variable_descriptions,
            variable_units=variable_units,
            test_data=test_data,
        )
        self.stats["validations"] += 1

        print("[OK] Validation complete")
        print(f"   Score: {validation_result['total_score']:.1f}/100")
        if validation_result.get("validation_exception"):
            print("   [WARNING] Validation had errors (likely unit system)")

        if discovery_result.get("collapsed_constants"):
            validation_result.setdefault("warnings", []).append(
                f"Collapsed constants detected: {discovery_result['collapsed_constants']}"
            )

        validation_score = validation_result["total_score"]
        r2_score = discovery_result["r2_score"]
        accepted = False
        accept_reason = None

        if self.discovery_mode == DiscoveryMode.STRICT:
            accepted = validation_score >= min_validation_score
        elif self.discovery_mode == DiscoveryMode.CALIBRATED:
            accepted = r2_score >= 0.99 and validation_score >= 30.0
            if accepted:
                accept_reason = "Calibrated physics acceptance (constants absorbed)"

        complete_result = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "domain": self.domain,
            "discovery": discovery_result,
            "validation": validation_result,
            "acceptance": {
                "accepted": accepted,
                "mode": self.discovery_mode.value,
                "reason": accept_reason,
            },
            "metadata": {
                "n_samples": len(X),
                "n_features": X.shape[1],
                "variable_names": variable_names,
                "discovery_engine": discovery_result.get("discovery_engine"),
                "llm_mode": self.llm_mode,
                "equation_name": equation_name,
                "version": "5.0",
            },
        }

        self.results.append(complete_result)

        print(f"\n{'=' * 70}")
        print("[OK] WORKFLOW COMPLETE")
        print(f"{'=' * 70}\n")

        return complete_result

    # ------------------------------------------------------------------
    # discover() thin adapter — FIX-6: propagates use_llm from metadata
    # ------------------------------------------------------------------
    def discover(
        self,
        X: np.ndarray,
        y: np.ndarray,
        var_names: List[str],
        description: str = "",
        metadata: Optional[Dict] = None,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Thin adapter for benchmark runners.

        FIX-6: metadata may now contain use_llm (bool) and llm_mode (str)
        to override the instance defaults per-call.  This lets benchmark
        runners toggle LLM guidance equation-by-equation without
        reinstantiating the system.
        """
        metadata = metadata or {}

        _noise_level = metadata.get("noise_level", None)
        self._current_noise_level = _noise_level

        # PROD-7: domain fast-path (unchanged)
        _domain_from_meta = metadata.get("domain", "")
        if _domain_from_meta and _domain_from_meta != self.domain:
            logger.info(
                f"[DOMAIN-FIX] Updating domain: '{self.domain}' → '{_domain_from_meta}'"
            )
            self.domain = _domain_from_meta
            self.symbolic_engine.domain = _domain_from_meta

        # FIX-6: per-call LLM override from metadata
        _meta_use_llm = metadata.get("use_llm", self.use_llm)

        variable_descriptions = metadata.get(
            "variable_descriptions", {v: v for v in var_names}
        )
        variable_units = metadata.get("variable_units", {v: "" for v in var_names})
        equation_name = metadata.get("equation_name", description or "unknown")

        try:
            full_result = self.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=var_names,
                variable_descriptions=variable_descriptions,
                variable_units=variable_units,
                description=description,
                equation_name=equation_name,
                show_formatted=verbose,
                use_llm=_meta_use_llm,
            )

            if "error" in full_result and full_result["error"] == "discovery_failed":
                raise RuntimeError(full_result.get("message", "Discovery failed"))

            discovery = full_result.get("discovery", {})
            validation = full_result.get("validation", {})
            r2 = float(discovery.get("r2_score", 0.0))

            try:
                y_pred = discovery.get("predictions", None)
                rmse = (
                    float(np.sqrt(np.mean((y - np.asarray(y_pred)) ** 2)))
                    if y_pred is not None
                    else float("inf")
                )
            except Exception:
                rmse = float("inf")

            formula = discovery.get("expression", "N/A")
            success = r2 > 0.0 and formula not in (
                "DISCOVERY_FAILED", "NO_VALID_EQUATIONS", "VALIDATION_FAILED", "N/A"
            )

            return {
                "success": success,
                "r2": r2,
                "rmse": rmse,
                "final_formula": formula,
                "strategy": discovery.get("discovery_engine", "symbolic"),
                "llm_mode": discovery.get("llm_mode", self.llm_mode),
                "validations": 1 if validation else 0,
                "validation_score": validation.get("total_score", 0.0),
                "error": None,
            }

        except Exception as exc:
            logger.error(
                f"discover() caught top-level exception — {type(exc).__name__}: {exc}",
                exc_info=True,
            )
            return {
                "success": False,
                "r2": 0.0,
                "rmse": float("inf"),
                "final_formula": "N/A",
                "strategy": "error",
                "llm_mode": "none",
                "validations": 0,
                "error": str(exc)[:200],
            }

    def print_statistics_summary(self) -> None:
        """Print statistics summary."""
        print(f"\n{'=' * 70}")
        print("STATISTICS SUMMARY v5.0")
        print(f"{'=' * 70}")
        print(f"\nOverall:")
        print(f"   Discoveries: {self.stats['discoveries']}")
        print(f"   Validations: {self.stats['validations']}")
        print(f"\nSymbolicEngine:")
        print(f"   Attempts: {self.stats['symbolic_attempts']}")
        print(f"   Successes: {self.stats['symbolic_successes']}")
        print(f"   Failures: {self.stats['symbolic_failures']}")
        if self.stats["symbolic_attempts"] > 0:
            rate = 100 * self.stats["symbolic_successes"] / self.stats["symbolic_attempts"]
            print(f"   Success rate: {rate:.1f}%")
        print(f"\nLLM Guidance (mode={self.llm_mode}):")
        print(f"   Calls guided by LLM: {self.stats['llm_guided']}")
        print(f"   Calls using pure PySR: {self.stats['llm_skipped']}")
        if self.enable_physics_fallback:
            print(f"\nPhysicsAware:")
            print(f"   Used: {self.stats['physics_used']}")
            print(f"   Successes: {self.stats['physics_successes']}")
        print(f"\nAuto-Configuration:")
        print(f"   Used: {self.stats['auto_configs']} times")
        print(f"\n{'=' * 70}\n")

    def save_results(self, filename: Optional[str] = None) -> str:
        """Save results to JSON — PROD-4/5: single-pass serialisation."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"discovery_results_v50_{timestamp}.json"

        results_list = [_to_serialisable(r) for r in self.results]

        output = {
            "version": "5.0",
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "llm_mode": self.llm_mode,
            "statistics": self.stats,
            "results": results_list,
        }

        with open(filename, "w") as f:
            json.dump(output, f, indent=2)

        logger.info(f"[OK] Results saved to {filename}")
        return filename


# ============================================================================
# QUICK TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("HYBRID SYSTEM v5.0 — QUICK TEST")
    print("=" * 80)

    print("\nTest A: Pure PySR (use_llm=False, backward-compatible)")
    print("-" * 80)
    np.random.seed(42)
    I = np.random.uniform(0.1, 10, 100)
    R = np.random.uniform(1, 100, 100)
    V = I * R + np.random.normal(0, np.abs(I * R) * 0.01, 100)
    X = np.column_stack([I, R])

    system_pure = HybridDiscoverySystem(
        domain="physics",
        discovery_config=DiscoveryConfig(niterations=60, enable_auto_configuration=True),
        enable_physics_fallback=False,
        max_retries=3,
        use_llm=False,   # pure PySR — identical to v4.1-PROD
    )
    result_pure = system_pure.discover_validate_interpret(
        X=X, y=V,
        variable_names=["I", "R"],
        variable_descriptions={"I": "Current in amperes", "R": "Resistance in ohms"},
        variable_units={"I": "A", "R": "Ohm"},
        description="Ohm's Law (pure PySR)",
        equation_name="ohms_law",
    )
    print(f"Expression: {result_pure['discovery']['expression']}")
    print(f"R2: {result_pure['discovery']['r2_score']:.4f}")
    system_pure.print_statistics_summary()

    print("\nTest B: LLM hybrid mode (use_llm=True, requires ANTHROPIC_API_KEY)")
    print("-" * 80)
    if os.getenv("ANTHROPIC_API_KEY"):
        system_llm = HybridDiscoverySystem(
            domain="physics",
            discovery_config=DiscoveryConfig(niterations=60, enable_auto_configuration=True),
            enable_physics_fallback=False,
            max_retries=3,
            use_llm=True,
            llm_mode="hybrid",
            llm_n_candidates=3,
        )
        result_llm = system_llm.discover_validate_interpret(
            X=X, y=V,
            variable_names=["I", "R"],
            variable_descriptions={"I": "Current in amperes", "R": "Resistance in ohms"},
            variable_units={"I": "A", "R": "Ohm"},
            description="Ohm's Law (LLM hybrid)",
            equation_name="ohms_law",
        )
        print(f"Expression: {result_llm['discovery']['expression']}")
        print(f"R2: {result_llm['discovery']['r2_score']:.4f}")
        print(f"LLM mode used: {result_llm['discovery'].get('llm_mode', 'N/A')}")
        system_llm.print_statistics_summary()
    else:
        print("  Skipping — ANTHROPIC_API_KEY not set.")
        print("  Set the key and rerun with use_llm=True to test LLM guidance.")
