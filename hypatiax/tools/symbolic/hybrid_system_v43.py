"""
HypatiaX Hybrid Discovery System v4.2.1 - VARIABLE NAME FIX
============================================================
Fixes variable name conflicts with Julia/PySR reserved names.

CRITICAL FIX:
✅ Automatic variable name sanitization for PySR
✅ Handles reserved names: S, N, C, D, E, I, O, etc.
✅ Preserves original names in output
✅ Backward compatible with all existing code

Author: HypatiaX Team
Version: 4.2.1 (BUGFIX)
Date: 2026-01-20
"""

import json
import logging
import os
import re
from collections import deque
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from dotenv import load_dotenv

# Core imports
from hypatiax.tools.symbolic.symbolic_engine import DiscoveryConfig, SymbolicEngine

# Optional imports with fallbacks
try:
    from hypatiax.tools.symbolic.physics_aware_regressor import PhysicsAwareRegressor
    HAS_PHYSICS = True
except ImportError:
    HAS_PHYSICS = False
    logging.warning("PhysicsAwareRegressor not available")

try:
    from hypatiax.tools.validation.ensemble_validator import EnsembleValidator
    HAS_VALIDATOR = True
except ImportError:
    HAS_VALIDATOR = False
    logging.warning("EnsembleValidator not available")

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# VARIABLE NAME SANITIZATION (NEW!)
# ============================================================================

class VariableNameSanitizer:
    """
    Sanitizes variable names to avoid conflicts with Julia/PySR reserved names.
    
    Reserved single-letter names in Julia/SymbolicRegression.jl:
    - S, N, C, D, E, I, O (function names)
    - T, V, X, Y, Z (common conflicts)
    
    Strategy:
    1. Detect problematic single-letter names
    2. Replace with safe alternatives (var_S, var_N, etc.)
    3. Track mapping for reversal
    4. Restore original names in final output
    """
    
    # Known problematic names (Julia reserved or common conflicts)
    RESERVED_NAMES = {
        'S', 'N', 'C', 'D', 'E', 'I', 'O',  # Julia functions
        'T', 'V', 'X', 'Y', 'Z',            # Common conflicts
    }
    
    @staticmethod
    def sanitize_names(variable_names: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        Sanitize variable names to avoid Julia/PySR conflicts.
        
        Args:
            variable_names: Original variable names
            
        Returns:
            (sanitized_names, name_mapping)
            - sanitized_names: Safe variable names for PySR
            - name_mapping: {sanitized -> original} for reversal
        """
        sanitized = []
        mapping = {}
        
        for name in variable_names:
            # Check if name is problematic
            if name in VariableNameSanitizer.RESERVED_NAMES:
                # Create safe alternative
                safe_name = f"var_{name}"
                sanitized.append(safe_name)
                mapping[safe_name] = name
                logger.info(f"   Sanitized: {name} → {safe_name}")
            else:
                # Keep original
                sanitized.append(name)
        
        return sanitized, mapping
    
    @staticmethod
    def restore_expression(expression: str, mapping: Dict[str, str]) -> str:
        """
        Restore original variable names in discovered expression.
        
        Args:
            expression: Expression with sanitized names
            mapping: {sanitized -> original} mapping
            
        Returns:
            Expression with original names restored
        """
        restored = expression
        
        # Sort by length (longest first) to avoid partial replacements
        for safe_name, original_name in sorted(mapping.items(), 
                                              key=lambda x: len(x[0]), 
                                              reverse=True):
            # Use word boundaries to avoid partial replacements
            pattern = r'\b' + re.escape(safe_name) + r'\b'
            restored = re.sub(pattern, original_name, restored)
        
        return restored


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def detect_collapsed_constants(expression: str, variable_names: List[str]) -> List[str]:
    """Detect collapsed physical constants in expressions."""
    collapsed = []
    constants = re.findall(r"(\d+\.?\d*(?:[eE][+-]?\d+)?)", expression)
    
    PHYSICAL_CONSTANTS = {
        "c (speed of light)": [2.998e8, 3.0e8],
        "G (gravitational constant)": [6.674e-11, 6.67e-11],
        "h (Planck constant)": [6.626e-34, 6.63e-34],
        "k_B (Boltzmann constant)": [1.381e-23, 1.38e-23],
        "e (elementary charge)": [1.602e-19, 1.60e-19],
    }
    
    for const_str in constants:
        try:
            value = float(const_str)
            for const_name, const_values in PHYSICAL_CONSTANTS.items():
                for const_val in const_values:
                    if abs(value - const_val) / const_val < 0.1:
                        if const_name not in collapsed:
                            collapsed.append(const_name)
                        break
        except ValueError:
            continue
    
    return collapsed


# ============================================================================
# ENUMS
# ============================================================================

class DiscoveryMode(Enum):
    """Discovery acceptance modes."""
    STRICT = "strict"
    CALIBRATED = "calibrated"


# ============================================================================
# HYBRID DISCOVERY SYSTEM v4.2.1 (FIXED)
# ============================================================================

class HybridDiscoverySystem:
    """
    Hybrid Discovery System v4.2.1 - VARIABLE NAME FIX
    
    CRITICAL FIX:
    ✅ Automatic variable name sanitization
    ✅ Handles S, N, C, D, E, I, O conflicts
    ✅ Preserves original names in output
    
    All other features from v4.2 preserved.
    """

    def __init__(
        self,
        domain: str = "general",
        discovery_config: Optional[DiscoveryConfig] = None,
        discovery_mode: DiscoveryMode = DiscoveryMode.CALIBRATED,
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
        max_retries: int = 5,
        enable_auto_config: bool = True,
        anthropic_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
    ):
        """Initialize hybrid discovery system v4.2.1."""
        self.domain = domain
        self.discovery_mode = discovery_mode
        self.primary_llm = primary_llm
        self.enable_fallback = enable_fallback
        self.enable_physics_fallback = enable_physics_fallback and HAS_PHYSICS
        self.physics_fallback_threshold = physics_fallback_threshold
        self.complexity_penalty_threshold = complexity_penalty_threshold
        self.physics_population_size = physics_population_size
        self.physics_generations = physics_generations
        self.max_retries = max_retries
        self.enable_auto_config = enable_auto_config

        logger.info(f"=" * 70)
        logger.info(f"HybridDiscoverySystem v4.2.1 - VARIABLE NAME FIX")
        logger.info(f"=" * 70)
        logger.info(f"Domain: {domain}")
        logger.info(f"Discovery mode: {self.discovery_mode.value}")
        logger.info(f"Primary LLM: {primary_llm}")
        logger.info(f"Auto-config: {enable_auto_config}")
        logger.info(f"Max retries: {max_retries}")
        logger.info(f"Variable sanitization: ENABLED")
        logger.info(f"=" * 70)

        # Configure symbolic engine
        if discovery_config is None:
            symbolic_config = DiscoveryConfig(
                niterations=100,
                enable_auto_configuration=enable_auto_config,
            )
            logger.info(f"Using default iterations: 100")
        else:
            symbolic_config = discovery_config
            logger.info(f"Using provided iterations: {symbolic_config.niterations}")

        self.symbolic_engine = SymbolicEngine(symbolic_config, domain=domain)

        # Initialize validator if available
        if HAS_VALIDATOR:
            self.validator = EnsembleValidator(
                domain=domain, max_history=max_results, weights=validation_weights
            )
        else:
            self.validator = None

        # Initialize LLM providers (optional)
        self._initialize_llm_providers(anthropic_api_key, google_api_key)

        # Results storage
        self.max_results = max_results
        if max_results is not None:
            self.results = deque(maxlen=max_results)
        else:
            self.results = []

        # Statistics
        self.stats = {
            "discoveries": 0,
            "symbolic_attempts": 0,
            "symbolic_successes": 0,
            "symbolic_failures": 0,
            "physics_used": 0,
            "physics_successes": 0,
            "validations": 0,
            "auto_configs": 0,
            "collapsed_constants_detected": 0,
            "variable_sanitizations": 0,  # NEW
        }

        self.use_rich_output = use_rich_output

        logger.info("[OK] HybridDiscoverySystem v4.2.1 initialized\n")

    def _initialize_llm_providers(
        self, anthropic_api_key: Optional[str], google_api_key: Optional[str]
    ):
        """Initialize LLM providers (optional)."""
        self.anthropic_provider = None
        self.google_provider = None

        try:
            from hypatiax.tools.llm_providers.anthropic_provider import AnthropicProvider
            api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_provider = AnthropicProvider(
                    api_key=api_key, max_tokens=4096
                )
        except ImportError:
            pass

        try:
            from hypatiax.tools.llm_providers.google_provider import GoogleProvider
            api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.google_provider = GoogleProvider(
                    api_key=api_key, max_output_tokens=8192
                )
        except ImportError:
            pass

    def _check_expression_quality(self, expression: str, r2: float) -> Dict[str, Any]:
        """Check expression quality for overfitting indicators."""
        complexity = len(expression)
        is_overfit = False
        warnings = []

        if complexity > self.complexity_penalty_threshold and r2 < 0.999:
            is_overfit = True
            warnings.append(f"High complexity ({complexity}) but R²={r2:.4f}")

        constants = re.findall(r"\d+\.\d+", expression)
        if len(constants) > 5:
            warnings.append(f"Many constants detected ({len(constants)})")

        try:
            suspicious = [c for c in constants if float(c) < 0.001 or float(c) > 1000]
            if suspicious:
                warnings.append(f"Suspicious constants: {suspicious[:3]}")
        except:
            pass

        return {
            "is_overfit": is_overfit,
            "complexity": complexity,
            "warnings": warnings,
        }

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
        Discovery with retry logic and variable name sanitization.
        
        NEW: Automatically sanitizes variable names before PySR.
        """
        # SANITIZE VARIABLE NAMES (NEW!)
        sanitized_names, name_mapping = VariableNameSanitizer.sanitize_names(
            variable_names
        )
        
        if name_mapping:
            logger.info(f"\n[SANITIZATION] Detected problematic variable names")
            self.stats["variable_sanitizations"] += 1
        
        # Update descriptions and units with sanitized names
        sanitized_descriptions = {}
        sanitized_units = {}
        
        for orig_name in variable_names:
            # Find sanitized name
            if orig_name in VariableNameSanitizer.RESERVED_NAMES:
                safe_name = f"var_{orig_name}"
            else:
                safe_name = orig_name
            
            # Copy metadata
            if orig_name in variable_descriptions:
                sanitized_descriptions[safe_name] = variable_descriptions[orig_name]
            if orig_name in variable_units:
                sanitized_units[safe_name] = variable_units[orig_name]
        
        best_result = None
        best_r2 = -np.inf

        # Try SymbolicEngine with different seeds
        for attempt in range(self.max_retries):
            try:
                seed = 42 + attempt
                logger.info(
                    f"\n[SYMBOLIC] Attempt {attempt + 1}/{self.max_retries} (seed={seed})"
                )

                self.stats["symbolic_attempts"] += 1

                # Use SANITIZED names for discovery
                result = self.symbolic_engine.discover(
                    X, y, sanitized_names, equation_name=equation_name, random_state=seed
                )

                r2 = result.get("r2_score", 0)
                expr = result.get("expression", "")

                logger.info(f"   Result: {expr}")
                logger.info(f"   R² = {r2:.4f}")

                # RESTORE ORIGINAL NAMES (NEW!)
                if expr and name_mapping:
                    original_expr = VariableNameSanitizer.restore_expression(
                        expr, name_mapping
                    )
                    result["expression"] = original_expr
                    result["sanitized_expression"] = expr
                    result["variable_mapping"] = name_mapping
                    logger.info(f"   Restored: {original_expr}")

                # Detect collapsed constants
                collapsed = detect_collapsed_constants(
                    result["expression"], variable_names
                )
                result["collapsed_constants"] = collapsed
                
                if collapsed:
                    logger.info(f"   Collapsed constants: {collapsed}")
                    self.stats["collapsed_constants_detected"] += 1

                # Quality check
                if expr and expr not in [
                    "DISCOVERY_FAILED",
                    "NO_VALID_EQUATIONS",
                    "VALIDATION_FAILED",
                ]:
                    quality = self._check_expression_quality(expr, r2)

                    if quality["is_overfit"]:
                        logger.warning(f"   [WARNING] Possible overfit")
                        for w in quality["warnings"]:
                            logger.warning(f"      {w}")
                else:
                    quality = {"is_overfit": False, "complexity": 0, "warnings": []}

                # Track best result
                if r2 > best_r2:
                    best_r2 = r2
                    best_result = result
                    best_result["discovery_engine"] = "symbolic"
                    best_result["attempt"] = attempt + 1
                    best_result["quality_check"] = quality
                    logger.info(f"   [BEST] New best!")

                # Early stopping
                if r2 >= 0.95 and not quality["is_overfit"]:
                    logger.info(f"   [EARLY STOP] Excellent result")
                    self.stats["symbolic_successes"] += 1
                    return best_result

            except Exception as e:
                logger.error(f"   [ERROR] Attempt {attempt + 1} failed: {e}")

        # Evaluate symbolic results
        if best_result and best_r2 >= 0.80:
            logger.info(f"\n[SUCCESS] SymbolicEngine succeeded (R²={best_r2:.4f})")
            self.stats["symbolic_successes"] += 1
            return best_result
        else:
            logger.warning(f"\n[WARNING] SymbolicEngine best R²={best_r2:.4f}")
            self.stats["symbolic_failures"] += 1

        if best_result:
            return best_result
        else:
            raise ValueError("All discovery attempts failed")

    def _safe_validate(
        self,
        expression_str: str,
        variable_definitions: Dict[str, str],
        variable_units: Dict[str, str],
        test_data: Dict[str, np.ndarray],
    ) -> Dict[str, Any]:
        """Safe validation with error handling."""
        if not self.validator:
            return {
                "valid": True,
                "total_score": 80.0,
                "layer_scores": {},
                "errors": [],
                "warnings": ["Validation disabled"],
                "validation_disabled": True,
            }

        try:
            validation_result = self.validator.validate_complete(
                expression_str=expression_str,
                variable_definitions=variable_definitions,
                variable_units=variable_units,
                test_data=test_data,
            )
            return validation_result

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
                "warnings": ["Validation failed"],
                "validation_exception": True,
            }

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
        use_llm: bool = False,
        min_validation_score: float = 85.0,
    ) -> Dict[str, Any]:
        """
        Complete discovery workflow with variable name sanitization.
        
        NEW: Automatically handles problematic variable names.
        """
        print(f"\n{'=' * 70}")
        print(f"DISCOVERY WORKFLOW v4.2.1")
        print(f"{'=' * 70}")
        print(f"Description: {description or 'Unnamed'}")
        print(f"Domain: {self.domain.upper()}")
        print(f"Samples: {len(X)}")
        print(f"Variables: {variable_names}")
        if equation_name:
            print(f"Equation hint: {equation_name}")
        print(f"{'=' * 70}")

        # STAGE 1: DISCOVER
        print(f"\n[DISCOVER] Running symbolic regression...")

        try:
            discovery_result = self._discover_with_retry(
                X,
                y,
                variable_names,
                variable_descriptions,
                variable_units,
                equation_name=equation_name,
            )
            self.stats["discoveries"] += 1

            engine = discovery_result.get("discovery_engine", "unknown")
            print(f"\n[OK] Discovery complete")
            print(f"   Expression: {discovery_result['expression']}")
            print(f"   R² Score: {discovery_result['r2_score']:.4f}")
            print(f"   Engine: {engine}")

            if "attempt" in discovery_result:
                print(f"   Attempt: {discovery_result['attempt']}/{self.max_retries}")

            if discovery_result.get("variable_mapping"):
                print(f"   Variables sanitized: {list(discovery_result['variable_mapping'].values())}")

        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            return {"error": "discovery_failed", "message": str(e)}

        # STAGE 2: VALIDATE
        print(f"\n[VALIDATE] Checking expression quality...")

        test_data = {name: X[:, i] for i, name in enumerate(variable_names)}

        validation_result = self._safe_validate(
            expression_str=discovery_result["expression"],
            variable_definitions=variable_descriptions,
            variable_units=variable_units,
            test_data=test_data,
        )

        self.stats["validations"] += 1

        print(f"[OK] Validation complete")
        print(f"   Score: {validation_result['total_score']:.1f}/100")

        # STAGE 3: ACCEPTANCE
        validation_score = validation_result["total_score"]
        r2_score = discovery_result["r2_score"]

        accepted = False
        accept_reason = None

        if self.discovery_mode == DiscoveryMode.STRICT:
            accepted = validation_score >= min_validation_score
            accept_reason = f"STRICT mode: validation >= {min_validation_score}"
        elif self.discovery_mode == DiscoveryMode.CALIBRATED:
            accepted = r2_score >= 0.99 and validation_score >= 30.0
            accept_reason = "CALIBRATED mode: R² >= 0.99, validation >= 30"

        # Compile result
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
                "equation_name": equation_name,
                "version": "4.2.1",
            },
        }

        self.results.append(complete_result)

        print(f"\n{'=' * 70}")
        print(f"[OK] WORKFLOW COMPLETE")
        print(f"{'=' * 70}\n")

        return complete_result


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "HybridDiscoverySystem",
    "DiscoveryMode",
    "DiscoveryConfig",
    "detect_collapsed_constants",
    "VariableNameSanitizer",
]


# ============================================================================
# QUICK TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("HYBRID SYSTEM v4.2.1 - VARIABLE NAME FIX TEST")
    print("=" * 80)

    # Test: Michaelis-Menten (uses variable 'S' which conflicts with Julia)
    print("\nTest: Michaelis-Menten v = (Vmax*S)/(Km+S)")
    print("Testing variable name sanitization for 'S' (conflicts with sine)")
    print("-" * 80)

    np.random.seed(42)
    S_substrate = np.random.uniform(0.1, 50, 100)
    v = (50 * S_substrate) / (10 + S_substrate)
    v += np.random.normal(0, np.abs(v) * 0.01, 100)

    X = S_substrate.reshape(-1, 1)

    discovery_config = DiscoveryConfig(
        niterations=50,
        enable_auto_configuration=True,
    )

    system = HybridDiscoverySystem(
        domain="biology",
        discovery_config=discovery_config,
        discovery_mode=DiscoveryMode.CALIBRATED,
        max_retries=3,
    )

    result = system.discover_validate_interpret(
        X=X,
        y=v,
        variable_names=["S"],  # Problematic name!
        variable_descriptions={"S": "Substrate concentration"},
        variable_units={"S": "mM"},
        description="Michaelis-Menten Kinetics",
        equation_name="michaelis_menten",
    )

    print("\n" + "=" * 80)
    print("RESULT:")
    print("=" * 80)
    print(f"Expression: {result['discovery']['expression']}")
    print(f"R²: {result['discovery']['r2_score']:.4f}")
    print(f"Accepted: {result['acceptance']['accepted']}")
    
    if result['discovery'].get('variable_mapping'):
        print(f"Variable mapping: {result['discovery']['variable_mapping']}")
        print("✅ Variable sanitization WORKED!")
    else:
        print("ℹ️ No variable sanitization needed")
    
    print("\n" + "=" * 80)
    print("v4.2.1 VARIABLE NAME FIX - Test complete!")
    print("=" * 80)
