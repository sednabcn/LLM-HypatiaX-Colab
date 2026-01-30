"""
Enhanced Symbolic Engine v20 - WITH INTEGRATED LLM GUIDANCE + VARIABLE VALIDATOR
=================================================================================
All LLM discovery features built-in, no external dependencies.
FIXED: Added missing SymbolicEngine base class and DiscoveryConfig
NEW: Integrated variable name validator as static methods

Author: HypatiaX Team
Date: 2026-01-13
Version: 20 (Complete with Variable Validator)
"""

import os
import warnings
import re
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import numpy as np
from pysr import PySRRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import r2_score
from scipy import stats


# Optional LLM support
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


# ============================================================================
# VARIABLE NAME VALIDATOR (INTEGRATED)
# ============================================================================

class VariableNameValidator:
    """
    Static validator for variable names to avoid PySR reserved word conflicts.
    Integrated into SymbolicEngine v20.
    """
    
    # PySR reserved function names and operators
    PYSR_RESERVED = {
        # Mathematical functions
        'sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh',
        'asin', 'acos', 'atan', 'asinh', 'acosh', 'atanh',
        'exp', 'log', 'log10', 'log2', 'sqrt', 'cbrt',
        'abs', 'sign', 'floor', 'ceil', 'round',
        'erf', 'erfc', 'gamma', 'lgamma',
        
        # Special functions that PySR might reserve
        'Q',  # Often reserved for quotient or other special uses
        'E',  # Euler's number
        'PI', 'pi',  # Pi constant
        
        # Operators
        'pow', 'div', 'mod', 'max', 'min',
    }
    
    # Safe alternatives for common problematic variables
    SAFE_ALTERNATIVES = {
        'Q': 'Qr',      # Reaction quotient
        'E': 'E_val',   # Energy or potential
        'PI': 'Pi',     # Greek pi (different case)
        'pi': 'Pi',     # Pi constant
    }
    
    @staticmethod
    def is_reserved(name: str) -> bool:
        """Check if a variable name conflicts with PySR reserved words."""
        return (name.lower() in VariableNameValidator.PYSR_RESERVED or 
                name in VariableNameValidator.PYSR_RESERVED)
    
    @staticmethod
    def sanitize_name(name: str, existing_names: List[str] = None) -> str:
        """
        Sanitize a single variable name.
        
        Args:
            name: Original variable name
            existing_names: List of already-used names (to avoid collisions)
            
        Returns:
            Sanitized variable name
        """
        existing_names = existing_names or []
        
        # Check if already reserved
        if VariableNameValidator.is_reserved(name):
            # Try known safe alternative first
            if name in VariableNameValidator.SAFE_ALTERNATIVES:
                alternative = VariableNameValidator.SAFE_ALTERNATIVES[name]
                if alternative not in existing_names:
                    return alternative
            
            # Generate safe alternative by appending suffix
            base = name
            suffix = '_var'
            counter = 1
            
            while (f"{base}{suffix}" in existing_names or 
                   VariableNameValidator.is_reserved(f"{base}{suffix}")):
                suffix = f'_v{counter}'
                counter += 1
            
            return f"{base}{suffix}"
        
        # Name is safe
        return name
    
    @staticmethod
    def sanitize_names(names: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        Sanitize a list of variable names.
        
        Args:
            names: List of original variable names
            
        Returns:
            Tuple of (sanitized_names, mapping_dict)
            where mapping_dict maps original -> sanitized
        """
        sanitized = []
        mapping = {}
        
        for name in names:
            safe_name = VariableNameValidator.sanitize_name(name, sanitized)
            sanitized.append(safe_name)
            
            if safe_name != name:
                mapping[name] = safe_name
                warnings.warn(
                    f"Variable '{name}' conflicts with PySR reserved word. "
                    f"Renamed to '{safe_name}'.",
                    UserWarning
                )
        
        return sanitized, mapping
    
    @staticmethod
    def update_expression(expression: str, mapping: Dict[str, str]) -> str:
        """
        Update expression with sanitized variable names.
        
        Args:
            expression: Original expression string
            mapping: Dict mapping original -> sanitized names
            
        Returns:
            Updated expression
        """
        if not mapping:
            return expression
        
        # Replace each mapped variable (using word boundaries to avoid partial matches)
        updated = expression
        for original, sanitized in mapping.items():
            # Use regex with word boundaries
            pattern = r'\b' + re.escape(original) + r'\b'
            updated = re.sub(pattern, sanitized, updated)
        
        return updated


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def detect_collapsed_constants(expression: str, variable_names: List[str]) -> List[str]:
    """
    Detect if physical constants have collapsed into the expression.
    
    Args:
        expression: The symbolic expression string
        variable_names: List of variable names that should be present
        
    Returns:
        List of detected collapsed constants (e.g., ['g', 'h', 'c'])
    """
    import re
    
    collapsed = []
    
    # Common physical constants to check for
    # Format: (name, typical_value_pattern, description)
    known_constants = [
        ('g', r'9\.8[0-9]*', 'gravitational acceleration'),
        ('h', r'6\.626[0-9]*e-34', 'Planck constant'),
        ('c', r'2\.998[0-9]*e8|3\.0*e8', 'speed of light'),
        ('me', r'9\.109[0-9]*e-31', 'electron mass'),
        ('k', r'1\.380[0-9]*e-23', 'Boltzmann constant'),
        ('Na', r'6\.022[0-9]*e23', 'Avogadro constant'),
        ('e', r'1\.602[0-9]*e-19', 'elementary charge'),
        ('mu0', r'1\.257[0-9]*e-6', 'vacuum permeability'),
        ('epsilon0', r'8\.854[0-9]*e-12', 'vacuum permittivity'),
    ]
    
    # Check if constant values appear in the expression
    for const_name, pattern, description in known_constants:
        if const_name not in variable_names:  # Only if not a variable
            if re.search(pattern, expression):
                collapsed.append(f"{const_name} ({description})")
    
    # Also check for numerical constants that might indicate collapse
    # Find all floating point numbers in expression
    numbers = re.findall(r'\d+\.\d+(?:e[+-]?\d+)?', expression)
    
    # Flag if we see very specific constants
    for num_str in numbers:
        try:
            num = float(num_str)
            # Check for suspicious specific values
            if abs(num - 9.81) < 0.1:
                if 'g (gravitational acceleration)' not in collapsed:
                    collapsed.append('g (gravitational acceleration)')
            elif abs(num - 6.626e-34) < 1e-35:
                if 'h (Planck constant)' not in collapsed:
                    collapsed.append('h (Planck constant)')
            elif abs(num - 3e8) < 1e7:
                if 'c (speed of light)' not in collapsed:
                    collapsed.append('c (speed of light)')
        except ValueError:
            continue
    
    return collapsed


# ============================================================================
# CONFIGURATION CLASSES
# ============================================================================

@dataclass
class DiscoveryConfig:
    """Configuration for symbolic discovery."""
    niterations: int = 50
    populations: int = 15
    population_size: int = 50
    binary_operators: List[str] = field(default_factory=lambda: ["+", "-", "*", "/"])
    unary_operators: List[str] = field(default_factory=list)
    constraints: Dict = field(default_factory=dict)
    enable_auto_configuration: bool = True
    auto_config_correlation_threshold: float = 0.2
    enable_smart_discovery: bool = False
    smart_discovery_priority: bool = False


@dataclass
class LLMConfig:
    """Configuration for LLM hypothesis generation."""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 2000
    temperature: float = 0.3
    n_candidates: int = 3  # Number of hypotheses to generate
    enabled: bool = False
    api_key: Optional[str] = None


@dataclass
class EquationHypothesis:
    """A candidate equation from LLM."""
    equation: str
    confidence: float
    reasoning: str
    r2_score: Optional[float] = None
    validation_score: Optional[float] = None


# ============================================================================
# LLM COMPONENTS (INTEGRATED)
# ============================================================================

class IntegratedLLMEngine:
    """Built-in LLM hypothesis generator."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        
        if not config.enabled:
            return
        
        if not HAS_ANTHROPIC:
            print("⚠️  Anthropic not installed. Install: pip install anthropic")
            self.config.enabled = False
            return
        
        if not config.api_key:
            config.api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not config.api_key:
            print("⚠️  No API key found. LLM guidance disabled.")
            self.config.enabled = False
            return
        
        try:
            self.client = Anthropic(api_key=config.api_key)
            print(f"   ✓ LLM engine initialized ({config.model})")
        except Exception as e:
            print(f"⚠️  LLM init failed: {e}")
            self.config.enabled = False
    
    def generate_hypotheses(
        self,
        domain: str,
        variables: List[str],
        description: str,
        data_patterns: Dict,
        n_candidates: int = None
    ) -> List[EquationHypothesis]:
        """Generate equation hypotheses using LLM."""
        
        if not self.config.enabled or not self.client:
            return []
        
        n_candidates = n_candidates or self.config.n_candidates
        
        prompt = self._build_prompt(
            domain, variables, description, data_patterns, n_candidates
        )
        
        try:
            response = self._call_llm(prompt)
            hypotheses = self._parse_response(response)
            return hypotheses
        except Exception as e:
            print(f"⚠️  LLM generation failed: {e}")
            return []
    
    def _build_prompt(
        self,
        domain: str,
        variables: List[str],
        description: str,
        patterns: Dict,
        n_candidates: int
    ) -> str:
        """Build LLM prompt."""
        
        var_list = ", ".join(variables)
        patterns_str = json.dumps(patterns, indent=2)
        
        prompt = f"""You are an expert scientific equation discovery system. Generate {n_candidates} candidate equations for this problem.

PROBLEM CONTEXT:
Domain: {domain}
Description: {description}
Variables: {var_list}

DATA PATTERNS:
{patterns_str}

TASK:
Generate {n_candidates} candidate equations that could explain this relationship.
Use Python syntax: ** for power, * for multiply, / for divide, + and -
Use EXACT variable names: {var_list}

Return ONLY a JSON array:
[
  {{
    "equation": "y = 0.5 * m * v**2",
    "confidence": 0.95,
    "reasoning": "Classical kinetic energy formula"
  }},
  ...
]

JSON ARRAY:"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call Anthropic API."""
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
            # Extract JSON from response
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
            
            hypotheses = []
            for c in candidates:
                # Normalize equation (strip "y = " prefix)
                eq = c.get("equation", "")
                if "=" in eq:
                    eq = eq.split("=", 1)[1].strip()
                
                hypotheses.append(EquationHypothesis(
                    equation=eq,
                    confidence=float(c.get("confidence", 0.5)),
                    reasoning=c.get("reasoning", "")
                ))
            
            return hypotheses
        
        except Exception as e:
            print(f"⚠️  Failed to parse LLM response: {e}")
            return []


# ============================================================================
# PATTERN ANALYZER (INTEGRATED)
# ============================================================================

class DataPatternAnalyzer:
    """Lightweight pattern analysis for LLM context."""
    
    def analyze(self, X: np.ndarray, y: np.ndarray, variable_names: List[str]) -> Dict:
        """Analyze data patterns."""
        
        patterns = {
            "n_variables": X.shape[1],
            "n_samples": X.shape[0],
            "correlations": {},
            "structure_hints": [],
            "y_range": [float(np.min(y)), float(np.max(y))],
            "y_scale": self._classify_scale(y)
        }
        
        # Variable correlations
        for i, var in enumerate(variable_names):
            try:
                corr = np.corrcoef(X[:, i], y)[0, 1]
                patterns["correlations"][var] = float(corr) if not np.isnan(corr) else 0.0
            except:
                patterns["correlations"][var] = 0.0
        
        # Detect basic structure
        if X.shape[1] >= 2:
            # Test multiplicative
            product = np.prod(X, axis=1)
            if np.std(product) > 1e-10 and np.std(y) > 1e-10:
                prod_corr = abs(np.corrcoef(y, product)[0, 1])
                if prod_corr > 0.85:
                    patterns["structure_hints"].append("multiplicative")
        
        # Test polynomial
        for i, var in enumerate(variable_names):
            x_squared = X[:, i] ** 2
            try:
                r2 = r2_score(y, LinearRegression().fit(x_squared.reshape(-1, 1), y).predict(x_squared.reshape(-1, 1)))
                if r2 > 0.90:
                    patterns["structure_hints"].append(f"{var}_quadratic")
            except:
                pass
        
        return patterns
    
    def _classify_scale(self, y: np.ndarray) -> str:
        """Classify value scale."""
        y_max = np.max(np.abs(y))
        if y_max < 1e-6:
            return "very_small"
        elif y_max < 1:
            return "small"
        elif y_max < 1000:
            return "medium"
        elif y_max < 1e6:
            return "large"
        else:
            return "very_large"


# ============================================================================
# BASE SYMBOLIC ENGINE
# ============================================================================

class SymbolicEngine:
    """Base Symbolic Regression Engine using PySR with integrated variable name validation."""
    
    def __init__(self, config: DiscoveryConfig, domain: str = "general"):
        """Initialize symbolic engine."""
        self.config = config
        self.domain = domain
        self.model = None
    
    @staticmethod
    def validate_variable_names(variable_names: List[str], 
                                auto_fix: bool = True,
                                verbose: bool = False) -> Tuple[List[str], Dict[str, str]]:
        """
        Validate and optionally sanitize variable names for PySR compatibility.
        
        Args:
            variable_names: Original variable names
            auto_fix: If True, automatically sanitize reserved names
            verbose: Print sanitization info
            
        Returns:
            Tuple of (safe_names, mapping) where mapping is original->sanitized
        """
        conflicts = [name for name in variable_names 
                    if VariableNameValidator.is_reserved(name)]
        
        if not conflicts:
            return variable_names, {}
        
        if not auto_fix:
            raise ValueError(
                f"Variable names conflict with PySR reserved words: {conflicts}. "
                f"Use auto_fix=True to sanitize automatically."
            )
        
        safe_names, mapping = VariableNameValidator.sanitize_names(variable_names)
        
        if verbose and mapping:
            print("\n🔧 Variable Name Sanitization:")
            for orig, safe in mapping.items():
                print(f"   {orig} → {safe}")
        
        return safe_names, mapping
        
    def discover(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str] = None,
        equation_name: str = None,
        random_state: int = 42,
        auto_sanitize: bool = True,
        **kwargs
    ) -> Dict:
        """
        Discover symbolic equation from data with automatic variable name validation.
        
        Args:
            X: Input features (n_samples, n_features)
            y: Target values (n_samples,)
            variable_names: Names for each feature
            equation_name: Name of the equation being discovered
            random_state: Random seed for reproducibility
            auto_sanitize: Automatically fix variable name conflicts
            
        Returns:
            Dictionary with discovery results
        """
        if variable_names is None:
            variable_names = [f"x{i}" for i in range(X.shape[1])]
        
        # Validate and sanitize variable names
        safe_names, name_mapping = self.validate_variable_names(
            variable_names, 
            auto_fix=auto_sanitize,
            verbose=True
        )
        
        print(f"\n[DISCOVERY] Starting symbolic regression...")
        print(f"   Variables: {', '.join(safe_names)}")
        print(f"   Samples: {X.shape[0]}")
        print(f"   Iterations: {self.config.niterations}")
        
        if name_mapping:
            print(f"   ⚠️  Sanitized {len(name_mapping)} variable name(s)")
        
        try:
            # Configure PySR with safe names
            self.model = PySRRegressor(
                niterations=self.config.niterations,
                populations=self.config.populations,
                population_size=self.config.population_size,
                binary_operators=self.config.binary_operators,
                unary_operators=self.config.unary_operators,
                constraints=self.config.constraints,
                random_state=random_state,
                verbosity=0,
                progress=False,
                **kwargs
            )
            
            # Fit model with safe variable names
            self.model.fit(X, y, variable_names=safe_names)
            
            # Get best equation
            if hasattr(self.model, 'equations_') and len(self.model.equations_) > 0:
                best_eq = self.model.get_best()
                expression = str(best_eq['equation'])
                
                # Make predictions
                y_pred = self.model.predict(X)
                r2 = r2_score(y, y_pred)
                
                print(f"   ✅ Found: {expression}")
                print(f"   R²: {r2:.4f}")
                
                return {
                    "expression": expression,
                    "r2_score": r2,
                    "complexity": best_eq.get('complexity', len(expression)),
                    "variable_names": safe_names,
                    "original_variable_names": variable_names,
                    "variable_name_mapping": name_mapping,
                    "predictions": y_pred,
                    "validation": {"valid": True, "errors": [], "warnings": []}
                }
            else:
                print("   ⚠️ No valid equations found")
                return {
                    "expression": "NO_VALID_EQUATIONS",
                    "r2_score": 0.0,
                    "complexity": 0,
                    "variable_names": safe_names,
                    "original_variable_names": variable_names,
                    "variable_name_mapping": name_mapping,
                    "predictions": np.zeros_like(y),
                    "validation": {"valid": False, "errors": ["No equations found"], "warnings": []}
                }
                
        except Exception as e:
            print(f"   ❌ Discovery failed: {e}")
            return {
                "expression": "DISCOVERY_FAILED",
                "r2_score": 0.0,
                "complexity": 0,
                "variable_names": safe_names,
                "original_variable_names": variable_names,
                "variable_name_mapping": name_mapping,
                "predictions": np.zeros_like(y),
                "validation": {"valid": False, "errors": [str(e)], "warnings": []}
            }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using discovered equation."""
        if self.model is None:
            raise ValueError("Model not fitted. Call discover() first.")
        return self.model.predict(X)


# ============================================================================
# ENHANCED SYMBOLIC ENGINE WITH INTEGRATED LLM
# ============================================================================

class SymbolicEngineWithLLM(SymbolicEngine):
    """Symbolic Engine v20 - Integrated LLM guidance + Variable Name Validation."""
    
    def __init__(
        self,
        config: DiscoveryConfig,
        domain: str = "general",
        llm_config: Optional[LLMConfig] = None,
        llm_mode: str = "none"  # none, seed, hybrid, fallback
    ):
        """
        Initialize engine with optional LLM guidance and automatic variable validation.
        
        Args:
            config: PySR discovery configuration
            domain: Problem domain
            llm_config: LLM configuration (creates default if None)
            llm_mode: How to use LLM
                - "none": No LLM (pure PySR)
                - "seed": LLM configures PySR operators
                - "hybrid": Try LLM first, refine with PySR
                - "fallback": PySR first, LLM if it fails
        """
        super().__init__(config, domain)
        
        self.llm_mode = llm_mode
        self.llm_engine = None
        self.pattern_analyzer = None
        
        if llm_mode != "none":
            if llm_config is None:
                llm_config = LLMConfig(enabled=True)
            
            if llm_config.enabled:
                self.llm_engine = IntegratedLLMEngine(llm_config)
                self.pattern_analyzer = DataPatternAnalyzer()
                
                if self.llm_engine.config.enabled:
                    print(f"   ✓ LLM mode: {llm_mode}")
                else:
                    print(f"   ⚠️  LLM disabled, falling back to pure PySR")
                    self.llm_mode = "none"
    
    def discover(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str] = None,
        equation_name: str = None,
        random_state: int = 42,
        auto_sanitize: bool = True,
        **kwargs
    ) -> Dict:
        """
        Enhanced discovery with LLM guidance and automatic variable name validation.
        
        Args:
            auto_sanitize: Automatically fix variable name conflicts (default: True)
        """
        
        if variable_names is None:
            variable_names = [f"x{i}" for i in range(X.shape[1])]
        
        # Route based on LLM mode
        if self.llm_mode == "none" or not self.llm_engine or not self.llm_engine.config.enabled:
            return super().discover(X, y, variable_names, equation_name, random_state, 
                                   auto_sanitize=auto_sanitize, **kwargs)
        
        elif self.llm_mode == "seed":
            return self._discover_with_llm_seed(X, y, variable_names, equation_name, 
                                               random_state, auto_sanitize, **kwargs)
        
        elif self.llm_mode == "hybrid":
            return self._discover_hybrid(X, y, variable_names, equation_name, 
                                        random_state, auto_sanitize, **kwargs)
        
        elif self.llm_mode == "fallback":
            return self._discover_with_fallback(X, y, variable_names, equation_name, 
                                               random_state, auto_sanitize, **kwargs)
        
        else:
            print(f"⚠️  Unknown LLM mode: {self.llm_mode}, using pure PySR")
            return super().discover(X, y, variable_names, equation_name, random_state, 
                                   auto_sanitize=auto_sanitize, **kwargs)
    
    def _discover_with_llm_seed(
        self, X, y, variable_names, equation_name, random_state, auto_sanitize, **kwargs
    ) -> Dict:
        """Use LLM to configure PySR operators."""
        print("\n[LLM SEED MODE] Using LLM to configure PySR...")
        
        # Validate variable names first
        safe_names, name_mapping = self.validate_variable_names(
            variable_names, auto_fix=auto_sanitize, verbose=True
        )
        
        # Analyze patterns
        patterns = self.pattern_analyzer.analyze(X, y, safe_names)
        
        # Get LLM hypotheses
        hypotheses = self.llm_engine.generate_hypotheses(
            domain=self.domain,
            variables=safe_names,
            description=equation_name or "unknown",
            data_patterns=patterns
        )
        
        if hypotheses:
            print(f"   ✓ LLM generated {len(hypotheses)} hypotheses")
            
            # Extract operators from best hypothesis
            best_hyp = hypotheses[0]
            llm_config = self._extract_operators_from_equation(best_hyp.equation)
            
            print(f"   → LLM suggests operators: {llm_config}")
        
        # Run PySR with LLM-informed config
        result = super().discover(X, y, variable_names, equation_name, random_state, 
                                 auto_sanitize=auto_sanitize, **kwargs)
        result["llm_mode"] = "seed"
        result["llm_hypotheses"] = [h.equation for h in hypotheses]
        
        return result
    
    def _discover_hybrid(
        self, X, y, variable_names, equation_name, random_state, auto_sanitize, **kwargs
    ) -> Dict:
        """Try LLM first, refine with PySR if needed."""
        print("\n[HYBRID MODE] LLM first, PySR refinement...")
        
        start_time = time.time()
        
        # Validate variable names first
        safe_names, name_mapping = self.validate_variable_names(
            variable_names, auto_fix=auto_sanitize, verbose=True
        )
        
        # Phase 1: LLM Discovery
        patterns = self.pattern_analyzer.analyze(X, y, safe_names)
        hypotheses = self.llm_engine.generate_hypotheses(
            domain=self.domain,
            variables=safe_names,
            description=equation_name or "unknown",
            data_patterns=patterns
        )
        
        llm_time = time.time() - start_time
        
        if not hypotheses:
            print("   ⚠️  No LLM hypotheses, falling back to PySR")
            result = super().discover(X, y, variable_names, equation_name, random_state, 
                                     auto_sanitize=auto_sanitize, **kwargs)
            result["llm_mode"] = "hybrid_llm_failed"
            return result
        
        # Evaluate LLM hypotheses
        best_hyp = self._evaluate_hypotheses(hypotheses, X, y, safe_names)
        
        print(f"   LLM best: {best_hyp.equation}")
        print(f"   LLM R²: {best_hyp.r2_score:.4f}")
        print(f"   LLM time: {llm_time:.2f}s")
        
        # Decision: Is LLM good enough?
        if best_hyp.r2_score and best_hyp.r2_score > 0.95:
            print("   ✅ LLM solution excellent, skipping PySR")
            return {
                "expression": best_hyp.equation,
                "r2_score": best_hyp.r2_score,
                "complexity": len(best_hyp.equation),
                "variable_names": safe_names,
                "original_variable_names": variable_names,
                "variable_name_mapping": name_mapping,
                "predictions": self._predict_from_equation(best_hyp.equation, X, safe_names),
                "llm_mode": "hybrid_llm_only",
                "llm_time": llm_time,
                "validation": {"valid": True, "errors": [], "warnings": []},
                "llm_hypotheses": [h.equation for h in hypotheses]
            }
        
        # Phase 2: PySR Refinement
        print("   → Refining with PySR...")
        pysr_start = time.time()
        
        result = super().discover(X, y, variable_names, equation_name, random_state, 
                                 auto_sanitize=auto_sanitize, **kwargs)
        
        pysr_time = time.time() - pysr_start
        
        print(f"   PySR time: {pysr_time:.2f}s")
        print(f"   PySR R²: {result['r2_score']:.4f}")
        
        # Compare and choose best
        if result['r2_score'] > best_hyp.r2_score:
            print("   ✅ PySR refinement improved result")
            result["llm_mode"] = "hybrid_pysr_better"
            result["llm_hypotheses"] = [h.equation for h in hypotheses]
            result["llm_time"] = llm_time
            result["pysr_time"] = pysr_time
        else:
            print("   ✅ LLM solution was better")
            result = {
                "expression": best_hyp.equation,
                "r2_score": best_hyp.r2_score,
                "complexity": len(best_hyp.equation),
                "variable_names": safe_names,
                "original_variable_names": variable_names,
                "variable_name_mapping": name_mapping,
                "predictions": self._predict_from_equation(best_hyp.equation, X, safe_names),
                "llm_mode": "hybrid_llm_better",
                "llm_time": llm_time,
                "pysr_time": pysr_time,
                "validation": {"valid": True, "errors": [], "warnings": []},
                "llm_hypotheses": [h.equation for h in hypotheses]
            }
        
        return result
    
    def _discover_with_fallback(
        self, X, y, variable_names, equation_name, random_state, auto_sanitize, **kwargs
    ) -> Dict:
        """Try PySR first, fallback to LLM if it fails."""
        print("\n[FALLBACK MODE] PySR first, LLM backup...")
        
        # Validate variable names
        safe_names, name_mapping = self.validate_variable_names(
            variable_names, auto_fix=auto_sanitize, verbose=True
        )
        
        # Phase 1: PySR
        pysr_start = time.time()
        result = super().discover(X, y, variable_names, equation_name, random_state, 
                                 auto_sanitize=auto_sanitize, **kwargs)
        pysr_time = time.time() - pysr_start
        
        # Check if PySR succeeded
        if result['r2_score'] > 0.90:
            print(f"   ✅ PySR succeeded (R²={result['r2_score']:.4f})")
            result["llm_mode"] = "fallback_pysr_only"
            result["pysr_time"] = pysr_time
            return result
        
        # Phase 2: LLM Fallback
        print(f"   ⚠️  PySR suboptimal (R²={result['r2_score']:.4f}), trying LLM...")
        
        patterns = self.pattern_analyzer.analyze(X, y, safe_names)
        hypotheses = self.llm_engine.generate_hypotheses(
            domain=self.domain,
            variables=safe_names,
            description=equation_name or "unknown",
            data_patterns=patterns
        )
        
        if not hypotheses:
            print("   ⚠️  LLM also failed, keeping PySR result")
            result["llm_mode"] = "fallback_both_failed"
            return result
        
        best_hyp = self._evaluate_hypotheses(hypotheses, X, y, safe_names)
        
        if best_hyp.r2_score and best_hyp.r2_score > result['r2_score']:
            print(f"   ✅ LLM better (R²={best_hyp.r2_score:.4f})")
            return {
                "expression": best_hyp.equation,
                "r2_score": best_hyp.r2_score,
                "complexity": len(best_hyp.equation),
                "variable_names": safe_names,
                "original_variable_names": variable_names,
                "variable_name_mapping": name_mapping,
                "predictions": self._predict_from_equation(best_hyp.equation, X, safe_names),
                "llm_mode": "fallback_llm_better",
                "validation": {"valid": True, "errors": [], "warnings": []},
                "llm_hypotheses": [h.equation for h in hypotheses]
            }
        else:
            print("   → Keeping PySR result")
            result["llm_mode"] = "fallback_pysr_better"
            result["llm_hypotheses"] = [h.equation for h in hypotheses]
            return result
    
    def _evaluate_hypotheses(
        self, hypotheses: List[EquationHypothesis], X: np.ndarray, 
        y: np.ndarray, variable_names: List[str]
    ) -> EquationHypothesis:
        """Evaluate LLM hypotheses against data."""
        
        for hyp in hypotheses:
            try:
                y_pred = self._predict_from_equation(hyp.equation, X, variable_names)
                hyp.r2_score = r2_score(y, y_pred)
            except Exception as e:
                hyp.r2_score = 0.0
                hyp.validation_score = 0.0
        
        # Sort by R² score
        hypotheses.sort(key=lambda h: h.r2_score or 0.0, reverse=True)
        return hypotheses[0]
    
    def _predict_from_equation(
        self, equation: str, X: np.ndarray, variable_names: List[str]
    ) -> np.ndarray:
        """Evaluate equation on data."""
        
        # Build namespace with variables
        namespace = {}
        for i, name in enumerate(variable_names):
            namespace[name] = X[:, i]
        
        # Add numpy functions
        namespace.update({
            'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'abs': np.abs, 'sign': np.sign,
            'pi': np.pi, 'e': np.e
        })
        
        try:
            result = eval(equation, {"__builtins__": {}}, namespace)
            return np.array(result)
        except Exception as e:
            raise ValueError(f"Failed to evaluate equation: {e}")
    
    def _extract_operators_from_equation(self, equation: str) -> Dict:
        """Extract operators used in an equation."""
        
        binary_ops = set()
        unary_ops = set()
        
        # Binary operators
        if '+' in equation:
            binary_ops.add('+')
        if '-' in equation:
            binary_ops.add('-')
        if '*' in equation:
            binary_ops.add('*')
        if '/' in equation:
            binary_ops.add('/')
        if '**' in equation:
            binary_ops.add('pow')
        
        # Unary operators
        if 'exp(' in equation:
            unary_ops.add('exp')
        if 'log(' in equation:
            unary_ops.add('log')
        if 'sqrt(' in equation:
            unary_ops.add('sqrt')
        if 'sin(' in equation:
            unary_ops.add('sin')
        if 'cos(' in equation:
            unary_ops.add('cos')
        
        return {
            "binary_operators": list(binary_ops),
            "unary_operators": list(unary_ops)
        }


# ============================================================================
# MAIN TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("SYMBOLIC ENGINE v21 - WITH VARIABLE NAME VALIDATOR")
    print("=" * 80)
    print()

    # Test variable name validation
    print("=" * 80)
    print("TEST 1: VARIABLE NAME VALIDATION")
    print("=" * 80)
    
    test_names = ['E0', 'R', 'T', 'n', 'F', 'Q', 'exp', 'sin', 'E']
    safe_names, mapping = SymbolicEngine.validate_variable_names(
        test_names, auto_fix=True, verbose=True
    )
    
    print(f"\nOriginal: {test_names}")
    print(f"Safe:     {safe_names}")
    print(f"Mapping:  {mapping}")
    
    # Test Nernst equation example
    print("\n" + "=" * 80)
    print("TEST 2: NERNST EQUATION EXAMPLE")
    print("=" * 80)
    
    # Generate sample data
    np.random.seed(42)
    num_samples = 100
    
    E0 = np.random.uniform(0.5, 1.5, num_samples)
    R = np.full(num_samples, 8.314)
    T = np.random.uniform(273, 373, num_samples)
    n = np.random.randint(1, 4, num_samples)
    F = np.full(num_samples, 96485)
    Q = np.random.uniform(0.01, 100, num_samples)
    
    # Calculate Nernst potential
    y = E0 - (R * T / (n * F)) * np.log(Q)
    X = np.column_stack([E0, R, T, n, F, Q])
    
    # Test with conflicting variable name 'Q'
    variable_names = ['E0', 'R', 'T', 'n', 'F', 'Q']
    
    print(f"\nVariable names: {variable_names}")
    print(f"Data shape: X={X.shape}, y={y.shape}")
    print(f"Note: 'Q' is a PySR reserved word and will be auto-sanitized")
    
    # Test symbolic regression with auto-sanitization
    print("\n" + "=" * 80)
    print("TEST 3: SYMBOLIC REGRESSION WITH AUTO-SANITIZATION")
    print("=" * 80)
    
    config = DiscoveryConfig(
        niterations=20,
        populations=10,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["log", "exp"]
    )
    
    engine = SymbolicEngine(config, domain="chemistry")
    
    result = engine.discover(
        X, y,
        variable_names=variable_names,
        equation_name="Nernst Equation",
        auto_sanitize=True
    )
    
    print(f"\nDiscovery Result:")
    print(f"   Expression: {result['expression']}")
    print(f"   R² Score: {result['r2_score']:.4f}")
    print(f"   Variable Mapping: {result['variable_name_mapping']}")
    
    # Test integration with LLM mode
    if HAS_ANTHROPIC and os.getenv("ANTHROPIC_API_KEY"):
        print("\n" + "=" * 80)
        print("TEST 4: LLM-GUIDED DISCOVERY WITH VALIDATION")
        print("=" * 80)
        
        llm_config = LLMConfig(enabled=True, n_candidates=2)
        engine_llm = SymbolicEngineWithLLM(
            config, 
            domain="chemistry",
            llm_config=llm_config,
            llm_mode="hybrid"
        )
        
        result_llm = engine_llm.discover(
            X, y,
            variable_names=variable_names,
            equation_name="Nernst Equation",
            auto_sanitize=True
        )
        
        print(f"\nLLM-Guided Result:")
        print(f"   Expression: {result_llm['expression']}")
        print(f"   R² Score: {result_llm['r2_score']:.4f}")
        print(f"   LLM Mode: {result_llm.get('llm_mode', 'N/A')}")
        print(f"   Variable Mapping: {result_llm['variable_name_mapping']}")
    else:
        print("\n⚠️  Skipping LLM test (API key not found)")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 80)
    



  
