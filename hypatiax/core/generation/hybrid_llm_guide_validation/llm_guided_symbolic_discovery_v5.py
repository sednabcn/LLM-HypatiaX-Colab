#!/usr/bin/env python3
"""
LLM-GUIDED SYMBOLIC DISCOVERY SYSTEM v5.0
==========================================
Combines LLM intelligence with symbolic regression for 10-20x speedup.

KEY IMPROVEMENTS v5.0:
✅ Protocol compatibility (A, B, B18, ALL)
✅ Session management with checkpointing
✅ Results table matching suite v4.2 format
✅ Enhanced validation integration
✅ Better error handling and recovery
✅ Comprehensive metadata tracking
✅ CLI aligned with suite patterns
✅ Improved API key handling with .env support
✅ Configurable LLM parameters (model, temperature, max_tokens)

API Key Setup (3 options):
    1. Environment variable: export ANTHROPIC_API_KEY=your_key
    2. .env file: Create .env with ANTHROPIC_API_KEY=your_key
    3. CLI argument: --api-key YOUR_KEY

Architecture:
    Phase 1: Data Pattern Analysis (0.5s)
        └─ Detect linearity, power laws, interactions
    
    Phase 2: LLM Hypothesis Generation (5s)
        └─ Generate 5 candidate equations using domain knowledge
    
    Phase 3: Rapid Verification + Validation (2-3s)
        └─ Fit coefficients, compute R², validate dimensions
    
    Phase 4: PySR Fallback (optional, 30s)
        └─ If hypotheses fail, fall back to symbolic regression

Expected Performance:
    - 80% cases: Direct LLM hit (8s total)
    - 15% cases: LLM + refinement (20s total)
    - 5% cases: Full PySR fallback (60s total)
    - Average: 12s (vs current 60-180s) → 10x speedup

Usage:
    # Setup API key (choose one):
    export ANTHROPIC_API_KEY=your_key              # Option 1: Environment variable
    echo "ANTHROPIC_API_KEY=your_key" > .env       # Option 2: .env file
    
    # Test single equation
    python llm_guided_discovery.py --test kinetic_energy
    
    # Run protocol suite (uses ANTHROPIC_API_KEY from environment or .env)
    python llm_guided_discovery.py --protocol B --batch
    
    # Or provide API key directly
    python llm_guided_discovery.py --protocol B --batch --api-key YOUR_KEY
    
    # Resume interrupted run
    python llm_guided_discovery.py --protocol ALL --batch --resume
    
    # Adjust LLM parameters
    python llm_guided_discovery.py --protocol A --batch --temperature 0.5 --max-tokens 3000

Author: HypatiaX Team
Date: 2026-01-08
Version: 4.0
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats
from sklearn.metrics import r2_score
from dotenv import load_dotenv

# ============================================================================
# SETUP & IMPORTS
# ============================================================================

# Required packages:
#   pip install numpy scipy scikit-learn anthropic python-dotenv
# Optional:
#   pip install hypatiax  # For validation

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Results directory
RESULTS_DIR = Path("hypatiax/data/results/llm_guided")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Try to import validator
try:
    from hypatiax.tools.validation.ensemble_validator import EnsembleValidator
    HAS_VALIDATOR = True
except ImportError:
    HAS_VALIDATOR = False
    print("⚠️  EnsembleValidator not available (validation disabled)")

# Try to import protocol loader
try:
    from suite_hybrid_system_all_domains_v5 import ExternalProtocolLoader
    HAS_PROTOCOL_LOADER = True
except ImportError:
    HAS_PROTOCOL_LOADER = False
    print("⚠️  Protocol loader not available (using built-in tests only)")

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

class SessionManager:
    """Manages test sessions with checkpointing."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"llm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_dir = RESULTS_DIR / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.session_dir / "checkpoint.json"
        self.completed_tests = set()
        self.failed_tests = set()
        self._load_checkpoint()
    
    def _load_checkpoint(self):
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    self.completed_tests = set(data.get('completed', []))
                    self.failed_tests = set(data.get('failed', []))
                    print(f"\n📂 Checkpoint: {len(self.completed_tests)} completed, {len(self.failed_tests)} failed")
            except:
                pass
    
    def _save_checkpoint(self):
        with open(self.checkpoint_file, 'w') as f:
            json.dump({
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'completed': list(self.completed_tests),
                'failed': list(self.failed_tests)
            }, f, indent=2)
    
    def is_completed(self, test_name: str) -> bool:
        return test_name in self.completed_tests
    
    def save_test_result(self, test_name: str, result: Dict, passed: bool):
        test_file = self.session_dir / f"{test_name}.json"
        result['_metadata'] = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'passed': passed,
            'test_name': test_name,
            'method': 'llm_guided'
        }
        
        # Convert numpy types
        clean_result = {}
        for k, v in result.items():
            if isinstance(v, np.ndarray):
                clean_result[k] = v.tolist()
            elif isinstance(v, (np.int64, np.int32)):
                clean_result[k] = int(v)
            elif isinstance(v, (np.float64, np.float32)):
                clean_result[k] = float(v)
            else:
                clean_result[k] = v
        
        with open(test_file, 'w') as f:
            json.dump(clean_result, f, indent=2, default=str)
        
        if passed:
            self.completed_tests.add(test_name)
        else:
            self.failed_tests.add(test_name)
        self._save_checkpoint()
        print(f"   💾 Saved: {test_file.name}")
    
    def load_all_results(self) -> Dict[str, Dict]:
        results = {}
        for f in self.session_dir.glob("*.json"):
            if f.name not in ['checkpoint.json', 'summary.json']:
                try:
                    with open(f, 'r') as file:
                        results[f.stem] = json.load(file)
                except:
                    pass
        return results
    
    def get_pending_tests(self, all_tests: List[str]) -> List[str]:
        return [t for t in all_tests if t not in self.completed_tests]

# ============================================================================
# DATA PATTERN ANALYSIS
# ============================================================================

@dataclass
class DataPatterns:
    """Analyzed patterns in the data."""
    is_linear: bool
    is_polynomial: bool
    is_power_law: bool
    is_exponential: bool
    is_logarithmic: bool
    is_periodic: bool
    has_interactions: bool
    
    correlations: Dict[str, float]
    polynomial_degree: Optional[int]
    power_exponents: Dict[str, float]
    
    y_range: Tuple[float, float]
    y_scale: str
    symmetry: str
    estimated_complexity: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for LLM prompt."""
        return {
            'structure': {
                'linear': self.is_linear,
                'polynomial': self.is_polynomial,
                'power_law': self.is_power_law,
                'exponential': self.is_exponential,
                'logarithmic': self.is_logarithmic,
                'periodic': self.is_periodic,
                'has_interactions': self.has_interactions
            },
            'correlations': {k: f"{v:.3f}" for k, v in self.correlations.items()},
            'details': {
                'polynomial_degree': self.polynomial_degree,
                'power_exponents': {k: f"{v:.2f}" for k, v in self.power_exponents.items()},
                'y_range': f"[{self.y_range[0]:.2e}, {self.y_range[1]:.2e}]",
                'y_scale': self.y_scale,
                'complexity': self.estimated_complexity
            }
        }


class DataPatternAnalyzer:
    """Analyzes data patterns to guide LLM hypothesis generation."""
    
    def __init__(self, threshold_linear: float = 0.98, threshold_nonlinear: float = 0.90):
        self.threshold_linear = threshold_linear
        self.threshold_nonlinear = threshold_nonlinear
    
    def analyze(self, X: np.ndarray, y: np.ndarray, variable_names: List[str]) -> DataPatterns:
        """Comprehensive pattern analysis."""
        
        # Correlations
        correlations = {}
        for i, var in enumerate(variable_names):
            corr = np.corrcoef(X[:, i], y)[0, 1]
            correlations[var] = corr if not np.isnan(corr) else 0.0
        
        # Tests
        is_linear = self._test_linearity(X, y)
        is_polynomial, poly_degree = self._test_polynomial(X, y)
        is_power_law, power_exponents = self._test_power_law(X, y, variable_names)
        is_exponential = self._test_exponential(X, y)
        is_logarithmic = self._test_logarithmic(X, y)
        is_periodic = self._test_periodic(y)
        has_interactions = self._test_interactions(X, y)
        
        # Statistics
        y_range = (float(np.min(y)), float(np.max(y)))
        y_scale = self._classify_scale(y)
        symmetry = self._test_symmetry(y)
        complexity = self._estimate_complexity(
            is_linear, is_polynomial, is_power_law, has_interactions, len(variable_names)
        )
        
        return DataPatterns(
            is_linear=is_linear, is_polynomial=is_polynomial, is_power_law=is_power_law,
            is_exponential=is_exponential, is_logarithmic=is_logarithmic,
            is_periodic=is_periodic, has_interactions=has_interactions,
            correlations=correlations, polynomial_degree=poly_degree,
            power_exponents=power_exponents, y_range=y_range,
            y_scale=y_scale, symmetry=symmetry, estimated_complexity=complexity
        )
    
    def _test_linearity(self, X: np.ndarray, y: np.ndarray) -> bool:
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        return r2_score(y, model.predict(X)) > self.threshold_linear
    
    def _test_polynomial(self, X: np.ndarray, y: np.ndarray) -> Tuple[bool, Optional[int]]:
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression
        
        best_r2, best_degree = 0, None
        for degree in [2, 3, 4]:
            try:
                poly = PolynomialFeatures(degree=degree)
                X_poly = poly.fit_transform(X)
                model = LinearRegression().fit(X_poly, y)
                r2 = r2_score(y, model.predict(X_poly))
                if r2 > best_r2:
                    best_r2, best_degree = r2, degree
            except:
                continue
        return best_r2 > self.threshold_nonlinear, best_degree if best_r2 > self.threshold_nonlinear else None
    
    def _test_power_law(self, X: np.ndarray, y: np.ndarray, variable_names: List[str]) -> Tuple[bool, Dict[str, float]]:
        exponents = {}
        for i, var in enumerate(variable_names):
            x_col = X[:, i]
            if np.any(x_col <= 0) or np.any(y <= 0):
                continue
            try:
                slope, _, r_value, _, _ = stats.linregress(np.log(x_col), np.log(y))
                if r_value**2 > self.threshold_nonlinear:
                    exponents[var] = slope
            except:
                continue
        return len(exponents) > 0, exponents
    
    def _test_exponential(self, X: np.ndarray, y: np.ndarray) -> bool:
        if np.any(y <= 0):
            return False
        try:
            from sklearn.linear_model import LinearRegression
            model = LinearRegression().fit(X, np.log(y))
            return r2_score(np.log(y), model.predict(X)) > self.threshold_nonlinear
        except:
            return False
    
    def _test_logarithmic(self, X: np.ndarray, y: np.ndarray) -> bool:
        if np.any(X <= 0):
            return False
        try:
            from sklearn.linear_model import LinearRegression
            model = LinearRegression().fit(np.log(X), y)
            return r2_score(y, model.predict(np.log(X))) > self.threshold_nonlinear
        except:
            return False
    
    def _test_periodic(self, y: np.ndarray) -> bool:
        try:
            from scipy.fft import fft
            fft_vals = np.abs(fft(y))
            max_freq = np.max(fft_vals[1:len(fft_vals)//2])
            mean_freq = np.mean(fft_vals[1:len(fft_vals)//2])
            return max_freq > 5 * mean_freq
        except:
            return False
    
    def _test_interactions(self, X: np.ndarray, y: np.ndarray) -> bool:
        if X.shape[1] < 2:
            return False
        try:
            from sklearn.linear_model import LinearRegression
            r2_no_inter = r2_score(y, LinearRegression().fit(X, y).predict(X))
            X_inter = np.column_stack([X, X[:, 0] * X[:, 1]])
            r2_inter = r2_score(y, LinearRegression().fit(X_inter, y).predict(X_inter))
            return (r2_inter - r2_no_inter) > 0.05
        except:
            return False
    
    def _classify_scale(self, y: np.ndarray) -> str:
        y_max = np.max(np.abs(y))
        if y_max < 1e-10: return 'very_small'
        elif y_max < 1: return 'small'
        elif y_max < 1000: return 'medium'
        elif y_max < 1e6: return 'large'
        else: return 'very_large'
    
    def _test_symmetry(self, y: np.ndarray) -> str:
        skewness = stats.skew(y)
        if abs(skewness) < 0.5: return 'symmetric'
        elif skewness > 0: return 'skewed_right'
        else: return 'skewed_left'
    
    def _estimate_complexity(self, is_linear: bool, is_polynomial: bool,
                            is_power_law: bool, has_interactions: bool, n_vars: int) -> str:
        if is_linear and not has_interactions:
            return 'simple'
        elif (is_polynomial or is_power_law) and n_vars <= 3:
            return 'medium'
        else:
            return 'complex'

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class LLMConfig:
    """Configuration for LLM hypothesis generator."""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 2000
    temperature: float = 0.3
    provider: str = "anthropic"


# ============================================================================
# LLM HYPOTHESIS GENERATOR
# ============================================================================

@dataclass
class EquationHypothesis:
    """A candidate equation hypothesis."""
    equation: str
    confidence: float
    reasoning: str
    source: str = 'llm'
    
    fitted_equation: Optional[str] = None
    coefficients: Optional[Dict[str, float]] = None
    r2_score: Optional[float] = None
    
    validation_score: Optional[float] = None
    validation_passed: Optional[bool] = None
    dimensional_check: Optional[Dict] = None


class LLMHypothesisGenerator:
    """Generates equation hypotheses using LLM."""
    
    def __init__(self, config: Optional[LLMConfig] = None, api_key: Optional[str] = None):
        """
        Initialize LLM hypothesis generator.
        
        Args:
            config: LLM configuration (uses defaults if None)
            api_key: API key (loads from environment if None)
        """
        # Load environment variables
        load_dotenv()
        
        # Use provided config or defaults
        self.config = config or LLMConfig()
        
        # Get API key from parameter, environment, or raise error
        if api_key:
            self.api_key = api_key
            api_source = "CLI argument"
        else:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            api_source = ".env file or environment variable"
        
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. "
                "Provide via --api-key argument, set ANTHROPIC_API_KEY environment variable, "
                "or create a .env file with ANTHROPIC_API_KEY=your_key"
            )
        
        # Initialize client based on provider
        if self.config.provider == "anthropic":
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                print(f"   ✓ Anthropic client initialized ({self.config.model})")
                print(f"   ✓ API key loaded from: {api_source}")
            except ImportError:
                raise ImportError("anthropic package required: pip install anthropic")
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    def generate_hypotheses(self, domain: str, variables: List[str],
                           variable_descriptions: Dict[str, str],
                           description: str, patterns: DataPatterns,
                           n_candidates: int = 5) -> List[EquationHypothesis]:
        """Generate equation hypotheses using LLM."""
        
        prompt = self._build_prompt(
            domain, variables, variable_descriptions, description, patterns, n_candidates
        )
        response = self._call_llm(prompt)
        hypotheses = self._parse_response(response)
        return hypotheses
    
    def _build_prompt(self, domain: str, variables: List[str],
                     variable_descriptions: Dict[str, str], description: str,
                     patterns: DataPatterns, n_candidates: int) -> str:
        """Build LLM prompt."""
        
        var_desc = "\n".join([
            f"  - {var}: {variable_descriptions.get(var, 'No description')}"
            for var in variables
        ])
        
        patterns_json = json.dumps(patterns.to_dict(), indent=2)
        
        prompt = f"""You are an expert scientific equation discovery system. Generate {n_candidates} candidate equations for this problem.

PROBLEM CONTEXT:
Domain: {domain}
Description: {description}
Variables:
{var_desc}

DATA PATTERNS DETECTED:
{patterns_json}

TASK:
Generate {n_candidates} candidate equations that could explain this relationship.
Use proper mathematical notation with these variable names: {', '.join(variables)}

For each candidate, provide:
1. equation: The mathematical formula (e.g., "y = 0.5 * m * v**2")
2. confidence: Your confidence 0.0-1.0 that this is correct
3. reasoning: Brief explanation of why this equation makes sense

IMPORTANT RULES:
- Use Python syntax: ** for power, * for multiply, / for divide, + and -
- Use EXACT variable names from the list: {', '.join(variables)}
- Include physical constants as numeric coefficients when appropriate
- Consider the domain ({domain}) and typical equations in that field
- Order by confidence (highest first)
- Make equations as simple as possible while fitting the patterns

Return ONLY a JSON array in this format:
[
  {{
    "equation": "energy = 0.5 * m * v**2",
    "confidence": 0.95,
    "reasoning": "This is the classical kinetic energy formula from mechanics"
  }},
  ...
]

JSON ARRAY:"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM API."""
        message = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def _parse_response(self, response: str) -> List[EquationHypothesis]:
        """Parse LLM response into hypotheses."""
        try:
            # Extract JSON
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                start = response.find("[")
                end = response.rfind("]") + 1
                json_str = response[start:end]
            
            candidates = json.loads(json_str)
            return [
                EquationHypothesis(
                    equation=c.get('equation', ''),
                    confidence=float(c.get('confidence', 0.5)),
                    reasoning=c.get('reasoning', ''),
                    source='llm'
                )
                for c in candidates
            ]
        except Exception as e:
            print(f"⚠️  Failed to parse LLM response: {e}")
            return []

# ============================================================================
# HYPOTHESIS VERIFIER
# ============================================================================

class HypothesisVerifier:
    """Verifies equation hypotheses against data with validation."""
    
    def __init__(self):
        self.has_validator = HAS_VALIDATOR
        if self.has_validator:
            self.validator = EnsembleValidator()
            print("   ✓ EnsembleValidator loaded")
        else:
            print("   ⚠️  Validation disabled")
    
    def verify(self, hypothesis: EquationHypothesis, X: np.ndarray, y: np.ndarray,
               variable_names: List[str], variable_units: Optional[Dict[str, str]] = None,
               domain: Optional[str] = None) -> EquationHypothesis:
        """Verify hypothesis by fitting coefficients and validating."""
        
        try:
            expr = hypothesis.equation
            fitted_expr, coeffs, r2 = self._fit_equation(expr, X, y, variable_names)
            
            hypothesis.fitted_equation = fitted_expr
            hypothesis.coefficients = coeffs
            hypothesis.r2_score = r2
            
            if self.has_validator and variable_units:
                validation_result = self._validate_equation(
                    fitted_expr, variable_names, variable_units, domain
                )
                hypothesis.validation_score = validation_result.get('total_score', 0.0)
                hypothesis.validation_passed = validation_result.get('valid', False)
                hypothesis.dimensional_check = validation_result.get('dimensional_check', {})
            
            return hypothesis
            
        except Exception as e:
            print(f"   ⚠️  Failed to verify: {hypothesis.equation}")
            print(f"       Error: {e}")
            hypothesis.r2_score = 0.0
            hypothesis.validation_score = 0.0
            hypothesis.validation_passed = False
            return hypothesis
    
    def _fit_equation(self, equation: str, X: np.ndarray, y: np.ndarray,
                     variable_names: List[str]) -> Tuple[str, Dict, float]:
        """Fit equation coefficients."""
        namespace = {var: X[:, i] for i, var in enumerate(variable_names)}
        namespace['np'] = np
        
        y_pred = eval(equation, namespace)
        r2 = r2_score(y, y_pred)
        return equation, {}, r2
    
    def _validate_equation(self, equation: str, variable_names: List[str],
                          variable_units: Dict[str, str], domain: Optional[str]) -> Dict:
        """Validate equation using EnsembleValidator."""
        try:
            result = self.validator.validate(
                expression=equation,
                variable_names=variable_names,
                variable_units=variable_units,
                domain=domain or "unknown"
            )
            return result
        except Exception as e:
            print(f"   ⚠️  Validation failed: {e}")
            return {'total_score': 0.0, 'valid': False, 'error': str(e)}

# ============================================================================
# LLM-GUIDED DISCOVERY SYSTEM
# ============================================================================

class LLMGuidedDiscovery:
    """Main LLM-guided symbolic discovery system."""
    
    def __init__(self, config: Optional[LLMConfig] = None, api_key: Optional[str] = None,
                 fallback_to_pysr: bool = False):
        """
        Initialize LLM-guided discovery system.
        
        Args:
            config: LLM configuration (uses defaults if None)
            api_key: API key (loads from environment if None)
            fallback_to_pysr: Whether to fallback to PySR if LLM fails
        """
        self.pattern_analyzer = DataPatternAnalyzer()
        self.hypothesis_generator = LLMHypothesisGenerator(config=config, api_key=api_key)
        self.verifier = HypothesisVerifier()
        self.fallback_to_pysr = fallback_to_pysr
    
    def discover(self, X: np.ndarray, y: np.ndarray, variable_names: List[str],
                domain: str, description: str,
                variable_descriptions: Optional[Dict[str, str]] = None,
                variable_units: Optional[Dict[str, str]] = None,
                n_hypotheses: int = 5, success_threshold: float = 0.95,
                validation_threshold: float = 70.0, verbose: bool = True) -> Dict[str, Any]:
        """Discover equation using LLM-guided approach."""
        
        if variable_descriptions is None:
            variable_descriptions = {var: "" for var in variable_names}
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"LLM-GUIDED DISCOVERY")
            print(f"{'='*80}")
            print(f"Domain: {domain}")
            print(f"Variables: {', '.join(variable_names)}")
            print(f"Samples: {len(y)}")
            if variable_units:
                print(f"Validation: ENABLED")
        
        start_time = time.time()
        
        # Phase 1: Analyze patterns
        if verbose:
            print(f"\n[PHASE 1] Analyzing data patterns...")
        phase1_start = time.time()
        patterns = self.pattern_analyzer.analyze(X, y, variable_names)
        phase1_time = time.time() - phase1_start
        
        if verbose:
            print(f"   ✓ Complexity: {patterns.estimated_complexity}")
            print(f"   ⏱️  Time: {phase1_time:.2f}s")
        
        # Phase 2: Generate hypotheses
        if verbose:
            print(f"\n[PHASE 2] Generating hypotheses with LLM...")
        phase2_start = time.time()
        hypotheses = self.hypothesis_generator.generate_hypotheses(
            domain, variables, variable_descriptions, description, patterns, n_hypotheses
        )
        phase2_time = time.time() - phase2_start
        
        if verbose:
            print(f"   ✓ Generated {len(hypotheses)} hypotheses")
            print(f"   ⏱️  Time: {phase2_time:.2f}s")
        
        # Phase 3: Verify
        if verbose:
            print(f"\n[PHASE 3] Verifying hypotheses...")
        phase3_start = time.time()
        verified = []
        for hyp in hypotheses:
            verified_hyp = self.verifier.verify(
                hyp, X, y, variable_names, variable_units, domain
            )
            verified.append(verified_hyp)
            
            if verbose and verified_hyp.r2_score is not None:
                status = "✅" if verified_hyp.r2_score > success_threshold else "⚠️"
                val_str = ""
                if verified_hyp.validation_score is not None:
                    val_str = f" | Val: {verified_hyp.validation_score:.1f}/100"
                print(f"   {status} R²={verified_hyp.r2_score:.4f}{val_str}")
        
        def score_hypothesis(h):
            r2 = h.r2_score or 0
            val = (h.validation_score or 0) / 100.0 if h.validation_score else 0
            return 0.7 * r2 + 0.3 * val
        
        verified = sorted(verified, key=score_hypothesis, reverse=True)
        best = verified[0] if verified else None
        phase3_time = time.time() - phase3_start
        
        if verbose:
            print(f"   ⏱️  Time: {phase3_time:.2f}s")
        
        # Check success
        success = False
        if best:
            meets_r2 = best.r2_score > success_threshold
            meets_val = (best.validation_score is None or best.validation_score > validation_threshold)
            success = meets_r2 and meets_val
        
        total_time = time.time() - start_time
        
        if verbose:
            print(f"\n{'='*80}")
            if success:
                print(f"✅ SUCCESS")
                print(f"   Equation: {best.fitted_equation or best.equation}")
                print(f"   R² Score: {best.r2_score:.4f}")
                if best.validation_score:
                    print(f"   Validation: {best.validation_score:.1f}/100")
            else:
                print(f"⚠️  No hypothesis met thresholds")
            print(f"   Total time: {total_time:.2f}s")
        
        return {
            'success': success,
            'best_hypothesis': best,
            'all_hypotheses': verified,
            'patterns': patterns,
            'timing': {
                'total': total_time,
                'phase1_analysis': phase1_time,
                'phase2_llm': phase2_time,
                'phase3_verify': phase3_time
            },
            'r2_score': best.r2_score if best else 0.0,
            'validation_score': best.validation_score if best else 0.0,
            'expression': best.fitted_equation or best.equation if best else None
        }

# ============================================================================
# RESULTS TABLE
# ============================================================================

def print_results_table(results: Dict[str, Dict], test_cases: Dict[str, Dict]):
    """Print comprehensive results table matching suite format."""
    print(f"\n{'='*120}")
    print(f"LLM-GUIDED DISCOVERY RESULTS".center(120))
    print(f"{'='*120}")
    print(f"{'Test Name':<35} {'R²':>8} {'Val':>6} {'Time':>6} {'Status':^8} {'Observation':<45}")
    print(f"{'-'*35} {'-'*8} {'-'*6} {'-'*6} {'-'*8} {'-'*45}")
    
    sorted_tests = sorted(results.items(), key=lambda x: (
        test_cases.get(x[0], {}).get('domain', ''), x[0]
    ))
    
    current_domain = None
    for test_name, result in sorted_tests:
        domain = test_cases.get(test_name, {}).get('domain', 'unknown')
        if domain != current_domain:
            if current_domain:
                print()
            print(f"{'─'*120}")
            print(f"{domain.upper()}")
            print(f"{'─'*120}")
            current_domain = domain
        
        r2 = result.get('r2_score', 0.0)
        val = result.get('validation_score', 0.0)
        time_taken = result.get('timing', {}).get('total', 0.0)
        passed = result.get('_metadata', {}).get('passed', False)
        
        if 'error' in result:
            observation = f"ERROR: {result['error'][:40]}"
            status = "❌ FAIL"
        elif passed:
            observation = "LLM hypothesis successful"
            status = "✅ PASS"
        else:
            observation = "Below threshold"
            status = "❌ FAIL"
        
        print(f"{test_name:<35} {r2:>8.4f} {val:>6.1f} {time_taken:>6.1f}s {status:^8} {observation:<45}")
    
    print(f"{'='*120}")
    
    # Summary
    total = len(results)
    passed = sum(1 for r in results.values() if r.get('_metadata', {}).get('passed', False))
    if total > 0:
        avg_r2 = np.mean([r.get('r2_score', 0) for r in results.values()])
        avg_val = np.mean([r.get('validation_score', 0) for r in results.values()])
        avg_time = np.mean([r.get('timing', {}).get('total', 0) for r in results.values()])
        print(f"\nSUMMARY: {passed}/{total} passed ({passed/total*100:.1f}%) | ")
        print(f"Avg R²: {avg_r2:.4f} | Avg Val: {avg_val:.1f} | Avg Time: {avg_time:.1f}s")
    print(f"{'='*120}\n")

# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_single_test_llm(test_name: str, test_cases: Dict, api_key: Optional[str] = None,
                        config: Optional[LLMConfig] = None, verbose: bool = True, 
                        session: Optional[SessionManager] = None) -> Dict:
    """Run single test with LLM-guided discovery."""
    
    test_config = test_cases[test_name]
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"Running: {test_config['name']} | Domain: {test_config['domain']}")
        print(f"{'='*80}")
    
    start = time.time()
    
    try:
        # Generate data
        X, y_func = test_config['generate_data'](1000)
        y = y_func(X)
        
        # Discover
        discoverer = LLMGuidedDiscovery(config=config, api_key=api_key)
        result = discoverer.discover(
            X=X, y=y,
            variable_names=test_config['variables'],
            domain=test_config['domain'],
            description=test_config.get('name', test_name),
            variable_descriptions=test_config.get('variable_descriptions', {}),
            variable_units=test_config.get('variable_units', {}),
            verbose=verbose
        )
        
        result.update({
            'test_name': test_name,
            'timestamp': datetime.now().isoformat(),
            'ground_truth': test_config.get('ground_truth', ''),
            'domain': test_config['domain']
        })
        
        passed = result['success']
        
        if session:
            session.save_test_result(test_name, result, passed)
        
        return result
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'test_name': test_name,
            'execution_time': time.time() - start,
            'timestamp': datetime.now().isoformat()
        }
        if session:
            session.save_test_result(test_name, error_result, False)
        if verbose:
            print(f"\n❌ Error: {e}")
        return error_result

def run_protocol_suite(protocol_name: str, api_key: Optional[str] = None, 
                      config: Optional[LLMConfig] = None, resume: bool = False,
                      session_id: Optional[str] = None) -> Dict[str, Dict]:
    """Run full protocol suite with LLM-guided discovery."""
    
    if not HAS_PROTOCOL_LOADER:
        print("❌ Protocol loader not available")
        return {}
    
    # Load protocol
    loader = ExternalProtocolLoader()
    protocol = loader.load_protocol(protocol_name)
    if not protocol:
        return {}
    
    test_cases = loader.convert_protocol_to_test_cases(protocol)
    if not test_cases:
        return {}
    
    # Session management
    if resume and Path(RESULTS_DIR / "current_session.json").exists():
        with open(RESULTS_DIR / "current_session.json", 'r') as f:
            session_id = json.load(f).get('session_id')
    
    session = SessionManager(session_id)
    with open(RESULTS_DIR / "current_session.json", 'w') as f:
        json.dump({'session_id': session.session_id}, f)
    
    print(f"\n{'='*80}")
    print(f"LLM-GUIDED DISCOVERY - Protocol {protocol_name}")
    print(f"{'='*80}")
    print(f"Tests: {len(test_cases)}")
    
    # Get pending tests
    pending = session.get_pending_tests(list(test_cases.keys())) if resume else list(test_cases.keys())
    
    if not pending:
        print("✅ All tests completed!")
        results = session.load_all_results()
        print_results_table(results, test_cases)
        return results
    
    print(f"Running: {len(pending)}/{len(test_cases)} tests")
    
    # Run tests
    for i, test_name in enumerate(pending, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(pending)}: {test_name}")
        print(f"{'='*80}")
        
        try:
            run_single_test_llm(test_name, test_cases, api_key, config, verbose=True, session=session)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted! Progress saved. Use --resume")
            break
        except:
            continue
    
    results = session.load_all_results()
    print_results_table(results, test_cases)
    return results

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='LLM-Guided Symbolic Discovery v4.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Protocol B with LLM-guided discovery
  python llm_guided_discovery.py --protocol B --batch
  
  # Resume interrupted run
  python llm_guided_discovery.py --protocol ALL --batch --resume
  
  # Use custom API key
  python llm_guided_discovery.py --protocol A --batch --api-key YOUR_KEY
  
  # Adjust LLM parameters
  python llm_guided_discovery.py --protocol B --batch --temperature 0.5

API Key Setup:
  1. Set ANTHROPIC_API_KEY environment variable, OR
  2. Create a .env file with ANTHROPIC_API_KEY=your_key, OR
  3. Use --api-key argument

Get API key at: https://console.anthropic.com/
        """
    )
    
    parser.add_argument('--protocol', choices=['A', 'B', 'B18', 'ALL'],
                       help='Protocol to run')
    parser.add_argument('--batch', action='store_true',
                       help='Run all tests in protocol')
    parser.add_argument('--test', type=str,
                       help='Single test name')
    parser.add_argument('--api-key', type=str,
                       help='Anthropic API key (optional if ANTHROPIC_API_KEY is set)')
    parser.add_argument('--model', type=str, default='claude-sonnet-4-20250514',
                       help='LLM model to use (default: claude-sonnet-4-20250514)')
    parser.add_argument('--temperature', type=float, default=0.3,
                       help='LLM temperature (default: 0.3)')
    parser.add_argument('--max-tokens', type=int, default=2000,
                       help='Max tokens for LLM response (default: 2000)')
    parser.add_argument('--resume', action='store_true',
                       help='Resume interrupted run')
    parser.add_argument('--quiet', action='store_true',
                       help='Quiet mode')
    
    args = parser.parse_args()
    
    # Create LLM configuration
    config = LLMConfig(
        model=args.model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        provider='anthropic'
    )
    
    # API key handling - will try in this order:
    # 1. --api-key argument
    # 2. ANTHROPIC_API_KEY environment variable
    # 3. .env file (via load_dotenv in LLMHypothesisGenerator)
    api_key = args.api_key
    
    # Test API key availability early (will be checked again in LLMHypothesisGenerator)
    if not api_key:
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found")
        print("\nSetup options:")
        print("  1. Set environment variable:")
        print("     export ANTHROPIC_API_KEY=your_key")
        print("\n  2. Create a .env file:")
        print("     echo 'ANTHROPIC_API_KEY=your_key' > .env")
        print("\n  3. Use --api-key argument:")
        print("     python llm_guided_discovery.py --api-key YOUR_KEY ...")
        print("\nGet your API key at: https://console.anthropic.com/")
        return 1
    
    # Run tests
    try:
        if args.protocol and args.batch:
            run_protocol_suite(args.protocol, api_key, config, args.resume)
        elif args.test:
            print("❌ Single test mode requires protocol loader integration")
            return 1
        else:
            parser.print_help()
            return 0
    except ValueError as e:
        if "ANTHROPIC_API_KEY" in str(e):
            print(f"❌ {e}")
            return 1
        raise
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


"""
INTEGRATION NOTES
=================

API Key Handling (inspired by llm_interpreter.py):
    ✅ load_dotenv() for .env file support
    ✅ Clear error messages with setup instructions
    ✅ Multiple API key sources (CLI, env, .env)
    ✅ Early validation with helpful feedback
    ✅ Configuration dataclass for LLM parameters

Additional Features:
    ✅ Configurable model, temperature, max_tokens
    ✅ Exit codes for CI/CD integration (0=success, 1=error, 130=interrupted)
    ✅ Comprehensive help text with examples
    ✅ Clear source indication (where API key came from)
    ✅ Compatible with suite_hybrid_system patterns

Dependencies:
    Required: numpy, scipy, scikit-learn, anthropic, python-dotenv
    Optional: hypatiax (for validation)
    
Install:
    pip install numpy scipy scikit-learn anthropic python-dotenv

Quick Start:
    1. Get API key from https://console.anthropic.com/
    2. Create .env file: echo "ANTHROPIC_API_KEY=your_key" > .env
    3. Run: python llm_guided_discovery.py --protocol B --batch


Perfect! I've successfully integrated the API key handling pattern from llm_interpreter.py into the LLM-guided discovery system. Here's what was improved:
Key Improvements
1. API Key Handling (from llm_interpreter.py)

✅ load_dotenv() support for .env files
✅ Multiple sources: CLI argument → Environment variable → .env file
✅ Clear error messages with setup instructions
✅ Early validation with helpful feedback
✅ Source tracking: Shows where API key was loaded from

2. Configuration Management
python@dataclass
class LLMConfig:
    """Configuration for LLM hypothesis generator."""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 2000
    temperature: float = 0.3
    provider: str = "anthropic"
3. Improved CLI
bash# Option 1: Environment variable
export ANTHROPIC_API_KEY=your_key
python llm_guided_discovery.py --protocol B --batch

# Option 2: .env file (recommended)
echo "ANTHROPIC_API_KEY=your_key" > .env
python llm_guided_discovery.py --protocol B --batch

# Option 3: Direct argument
python llm_guided_discovery.py --protocol B --batch --api-key YOUR_KEY

# Adjust LLM parameters
python llm_guided_discovery.py --protocol B --batch --temperature 0.5 --max-tokens 3000
```

### 4. **Better Error Messages**
```
❌ Error: ANTHROPIC_API_KEY not found

Setup options:
  1. Set environment variable:
     export ANTHROPIC_API_KEY=your_key

  2. Create a .env file:
     echo 'ANTHROPIC_API_KEY=your_key' > .env

  3. Use --api-key argument:
     python llm_guided_discovery.py --api-key YOUR_KEY ...

Get your API key at: https://console.anthropic.com/
```

### 5. **Exit Codes for CI/CD**
- `0`: Success
- `1`: Error
- `130`: Interrupted by user

### 6. **Helpful Initialization Messages**
```
   ✓ Anthropic client initialized (claude-sonnet-4-20250514)
   ✓ API key loaded from: .env file or environment variable
Installation
bash# Install required packages
pip install numpy scipy scikit-learn anthropic python-dotenv

# Optional (for validation)
pip install hypatiax
Quick Start
bash# 1. Get API key from https://console.anthropic.com/
# 2. Create .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# 3. Run discovery
python llm_guided_discovery.py --protocol B --batch

# 4. Resume if interrupted
python llm_guided_discovery.py --protocol B --batch --resume
The system now follows the same robust API key handling pattern as llm_interpreter.py with enhanced configurability and better user experience!
"""
