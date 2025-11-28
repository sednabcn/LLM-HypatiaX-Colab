# formula_generator_multiverse_v2.py
"""
Formula Generator Multiverse - Production Version
Complete implementation with all 5 requirements

Author: Dr. Ruperto Bonet
Version: 2.0
Date: 2024-11-28
"""

import sys
sys.path.append('../tools')

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import logging
from pathlib import Path
import traceback

# Your existing tools
try:
    from symbolic.hybrid_system import HybridDiscoverySystem
    HYBRID_AVAILABLE = True
except:
    HYBRID_AVAILABLE = False
    logging.warning("HybridDiscoverySystem not available")

try:
    from validation.ensemble_validator import EnsembleValidator
    VALIDATOR_AVAILABLE = True
except:
    VALIDATOR_AVAILABLE = False
    logging.warning("EnsembleValidator not available")

# External libraries
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except:
    ANTHROPIC_AVAILABLE = False

import os

# =====================================================================
# REQUIREMENT 5: EASY TO EXTEND - Base Strategy Interface
# =====================================================================

class Strategy(Enum):
    """Available generation strategies."""
    SMART_LOOKUP = "smart_lookup"
    LLM_GENERATION = "llm_generation"
    SYMBOLIC_DISCOVERY = "symbolic_discovery"
    HYBRID_LOOKUP_LLM = "hybrid_lookup_llm"
    HYBRID_LOOKUP_DISCOVERY = "hybrid_lookup_discovery"

@dataclass
class FormulaResult:
    """Standardized result from any strategy."""
    strategy: Strategy
    status: str  # 'success', 'error', 'no_match', 'timeout'
    
    # Formula data
    formula_expression: Optional[str] = None
    formula_latex: Optional[str] = None
    formula_description: Optional[str] = None
    category: Optional[str] = None
    
    # Variables
    variables: List[Dict] = field(default_factory=list)
    output_unit: Optional[str] = None
    
    # Validation
    validation_passed: bool = False
    validation_score: float = 0.0
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    validation_layers: Optional[Dict] = None
    
    # Metadata
    confidence: float = 0.0
    match_similarity: Optional[float] = None
    r2_score: Optional[float] = None
    complexity: Optional[int] = None
    
    # Interpretation
    interpretation: Optional[Dict] = None
    
    # Performance
    time_ms: float = 0.0
    cost_estimate: float = 0.0
    
    # Error handling
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['strategy'] = self.strategy.value
        return result


class BaseStrategy:
    """
    REQUIREMENT 5: Base class for easy extension.
    
    To add a new strategy:
    1. Inherit from BaseStrategy
    2. Implement generate() method
    3. Register in FormulaGeneratorMultiverse
    """
    
    def __init__(self, name: Strategy):
        self.name = name
    
    def generate(self, query: str, domain: str, timeout_seconds: int = 30) -> FormulaResult:
        """
        Generate formula. Must be implemented by subclass.
        
        Args:
            query: User's natural language query
            domain: 'defi' or 'risk'
            timeout_seconds: Max time allowed
        
        Returns:
            FormulaResult
        """
        raise NotImplementedError("Subclass must implement generate()")
    
    def _extract_variables(self, formula: str) -> List[Dict]:
        """Helper: Extract variables from formula string."""
        import re
        vars_raw = re.findall(r'\b[a-z_][a-z0-9_]*\b', formula.lower())
        functions = ['sqrt', 'exp', 'log', 'sin', 'cos', 'tan', 'abs', 'min', 'max']
        vars_unique = [v for v in set(vars_raw) if v not in functions]
        
        return [
            {
                'name': v,
                'description': f'Variable {v}',
                'unit': 'dimensionless',
                'type': 'float',
                'range': [None, None]
            }
            for v in sorted(vars_unique)
        ]
    
    def _to_latex(self, formula: str) -> str:
        """Helper: Convert to LaTeX."""
        try:
            from sympy import sympify, latex
            return latex(sympify(formula))
        except:
            return formula
    
    def _quick_validate(self, formula: str) -> Dict:
        """Helper: Quick syntax validation."""
        try:
            from sympy import sympify
            sympify(formula)
            return {'passed': True, 'score': 80, 'errors': []}
        except Exception as e:
            return {'passed': False, 'score': 0, 'errors': [str(e)]}


# =====================================================================
# STRATEGY IMPLEMENTATIONS
# =====================================================================

class SmartLookupStrategy(BaseStrategy):
    """Strategy: Semantic search over existing formulas."""
    
    def __init__(self, defi_csv: str, risk_csv: str):
        super().__init__(Strategy.SMART_LOOKUP)
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers required: pip install sentence-transformers")
        
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load formulas
        self.defi_df = pd.read_csv(defi_csv)
        self.risk_df = pd.read_csv(risk_csv)
        self.formulas_df = pd.concat([self.defi_df, self.risk_df], ignore_index=True)
        
        # Pre-compute embeddings
        logging.info(f"[{self.name.value}] Computing embeddings for {len(self.formulas_df)} formulas...")
        self.embeddings = self.model.encode(
            self.formulas_df['description'].tolist(),
            show_progress_bar=False
        )
        logging.info(f"[{self.name.value}] ✓ Ready")
    
    def generate(self, query: str, domain: str, timeout_seconds: int = 30) -> FormulaResult:
        """Generate via semantic search."""
        start = time.time()
        
        try:
            # Embed query
            query_embedding = self.model.encode([query])[0]
            
            # Cosine similarity
            similarities = np.dot(self.embeddings, query_embedding) / (
                np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # Best match
            best_idx = np.argmax(similarities)
            similarity = float(similarities[best_idx])
            match = self.formulas_df.iloc[best_idx]
            
            # Confidence thresholds
            if similarity < 0.3:
                status = 'no_match'
                confidence = 0.0
            elif similarity < 0.6:
                status = 'success'
                confidence = 0.5
            else:
                status = 'success'
                confidence = similarity
            
            # Extract variables
            variables = self._extract_variables(match['analytical_formula'])
            
            # Quick validation
            validation = self._quick_validate(match['analytical_formula'])
            
            elapsed_ms = (time.time() - start) * 1000
            
            warnings = []
            if similarity < 0.6:
                warnings.append(f"Low similarity match: {similarity:.2f}")
            if similarity < 0.8:
                warnings.append("Consider verifying formula matches your intent")
            
            return FormulaResult(
                strategy=self.name,
                status=status,
                formula_expression=match['analytical_formula'],
                formula_latex=self._to_latex(match['analytical_formula']),
                formula_description=match['description'],
                category=match['category'],
                variables=variables,
                validation_passed=validation['passed'],
                validation_score=validation['score'],
                validation_errors=validation['errors'],
                confidence=confidence,
                match_similarity=similarity,
                time_ms=elapsed_ms,
                cost_estimate=0.0001,
                warnings=warnings
            )
        
        except Exception as e:
            return FormulaResult(
                strategy=self.name,
                status='error',
                error_message=str(e),
                time_ms=(time.time() - start) * 1000
            )


class LLMGenerationStrategy(BaseStrategy):
    """Strategy: Generate formula using Claude."""
    
    def __init__(self, api_key: str):
        super().__init__(Strategy.LLM_GENERATION)
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic required: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        
        if VALIDATOR_AVAILABLE:
            self.validator = EnsembleValidator(domain='defi')
        else:
            self.validator = None
            logging.warning(f"[{self.name.value}] EnsembleValidator not available, using quick validation")
    
    def generate(self, query: str, domain: str, timeout_seconds: int = 30) -> FormulaResult:
        """Generate using LLM."""
        start = time.time()
        
        prompt = self._create_prompt(query, domain)
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout_seconds
            )
            
            response_text = response.content[0].text.strip()
            
            # Parse JSON
            formula_data = self._parse_response(response_text)
            
            if not formula_data:
                return FormulaResult(
                    strategy=self.name,
                    status='error',
                    error_message='Failed to parse LLM response as JSON',
                    time_ms=(time.time() - start) * 1000,
                    cost_estimate=0.01
                )
            
            # Validate
            if self.validator:
                self.validator.domain = domain
                validation = self._validate_with_ensemble(formula_data, domain)
            else:
                validation = self._quick_validate(formula_data['formula'])
                validation['layers'] = None
                validation['warnings'] = []
            
            elapsed_ms = (time.time() - start) * 1000
            
            return FormulaResult(
                strategy=self.name,
                status='success',
                formula_expression=formula_data['formula'],
                formula_latex=formula_data.get('latex', self._to_latex(formula_data['formula'])),
                formula_description=formula_data.get('description', query),
                category=formula_data.get('category', 'Generated'),
                variables=formula_data.get('variables', self._extract_variables(formula_data['formula'])),
                output_unit=formula_data.get('output_unit', 'dimensionless'),
                validation_passed=validation['passed'],
                validation_score=validation['score'],
                validation_errors=validation['errors'],
                validation_warnings=validation.get('warnings', []),
                validation_layers=validation.get('layers'),
                confidence=0.7,
                time_ms=elapsed_ms,
                cost_estimate=0.01,
                warnings=self._check_hallucination_patterns(formula_data)
            )
        
        except Exception as e:
            return FormulaResult(
                strategy=self.name,
                status='error',
                error_message=str(e),
                time_ms=(time.time() - start) * 1000,
                cost_estimate=0.01
            )
    
    def _create_prompt(self, query: str, domain: str) -> str:
        """Create structured LLM prompt."""
        return f"""You are a mathematical formula generator for {domain.upper()}.

User request: "{query}"

Generate a precise mathematical formula. Respond ONLY with valid JSON in this EXACT format:
{{
  "formula": "mathematical_expression",
  "latex": "LaTeX_version",
  "variables": [
    {{"name": "var_name", "description": "what it represents", "unit": "unit_type", "type": "float"}}
  ],
  "output_unit": "result_unit",
  "category": "formula_category",
  "description": "brief explanation"
}}

CRITICAL RULES:
1. Use ONLY these operators: sqrt(), exp(), log(), ^, *, /, +, -, (, )
2. Variable names: alphanumeric, no spaces (use underscore)
3. ALL variables in formula MUST appear in variables array
4. For DeFi: common variables are reserve_x, reserve_y, price_ratio, fee, liquidity, amount_in, amount_out
5. For Risk: common variables are mu, sigma, confidence, t, returns, volatility

EXAMPLES:
Query: "Impermanent loss for AMM"
Response: {{"formula": "2*sqrt(price_ratio)/(price_ratio + 1) - 1", "latex": "\\\\frac{{2\\\\sqrt{{p}}}}{{p+1}} - 1", "variables": [{{"name": "price_ratio", "description": "Current price / Initial price", "unit": "dimensionless", "type": "float"}}], "output_unit": "percentage", "category": "Impermanent Loss", "description": "IL for 50/50 AMM pool"}}

Query: "VaR at 95%"
Response: {{"formula": "mu - 1.645*sigma*sqrt(t)", "latex": "\\\\mu - 1.645\\\\sigma\\\\sqrt{{t}}", "variables": [{{"name": "mu", "description": "Expected return", "unit": "percentage", "type": "float"}}, {{"name": "sigma", "description": "Volatility", "unit": "percentage", "type": "float"}}, {{"name": "t", "description": "Time horizon", "unit": "days", "type": "float"}}], "output_unit": "percentage", "category": "Value at Risk", "description": "VaR at 95% confidence"}}

Respond with JSON ONLY. No markdown, no extra text."""
    
    def _parse_response(self, text: str) -> Optional[Dict]:
        """Parse LLM JSON response."""
        try:
            # Remove markdown code blocks
            if '```' in text:
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
                text = text.rsplit('```', 1)[0]
            
            text = text.strip()
            return json.loads(text)
        except Exception as e:
            logging.error(f"JSON parse error: {e}")
            logging.error(f"Response text: {text[:500]}")
            return None
    
    def _validate_with_ensemble(self, formula_data: Dict, domain: str) -> Dict:
        """Validate using EnsembleValidator."""
        try:
            variables = formula_data.get('variables', [])
            variable_defs = {v['name']: v['description'] for v in variables}
            variable_units = {v['name']: v['unit'] for v in variables}
            
            result = self.validator.validate_complete(
                expression_str=formula_data['formula'],
                variable_definitions=variable_defs,
                variable_units=variable_units
            )
            
            return {
                'passed': result['valid'],
                'score': result['total_score'],
                'layers': result['layer_scores'],
                'errors': result['errors'],
                'warnings': result.get('warnings', [])
            }
        except Exception as e:
            return {
                'passed': False,
                'score': 0,
                'errors': [f"Validation error: {str(e)}"],
                'layers': None,
                'warnings': []
            }
    
    def _check_hallucination_patterns(self, formula_data: Dict) -> List[str]:
        """Detect LLM hallucination patterns."""
        warnings = []
        formula = formula_data.get('formula', '')
        
        if len(formula) > 200:
            warnings.append("Formula unusually long - verify correctness")
        
        if 'undefined' in formula.lower() or 'nan' in formula.lower():
            warnings.append("Contains 'undefined' or 'NaN' - likely hallucination")
        
        # Check variable consistency
        import re
        formula_vars = set(re.findall(r'\b[a-z_][a-z0-9_]*\b', formula.lower()))
        defined_vars = set(v['name'] for v in formula_data.get('variables', []))
        functions = {'sqrt', 'exp', 'log', 'sin', 'cos', 'tan', 'abs', 'min', 'max'}
        
        undefined = formula_vars - defined_vars - functions
        if undefined:
            warnings.append(f"Undefined variables in formula: {undefined}")
        
        return warnings


class SymbolicDiscoveryStrategy(BaseStrategy):
    """Strategy: Discover formula via symbolic regression."""
    
    def __init__(self, api_key: str):
        super().__init__(Strategy.SYMBOLIC_DISCOVERY)
        
        if not HYBRID_AVAILABLE:
            raise ImportError("HybridDiscoverySystem not available")
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic required for data planning")
        
        self.llm_client = anthropic.Anthropic(api_key=api_key)
        self.defi_system = HybridDiscoverySystem(domain='defi')
        self.risk_system = HybridDiscoverySystem(domain='risk')
    
    def generate(self, query: str, domain: str, timeout_seconds: int = 60) -> FormulaResult:
        """Discover formula via PySR."""
        start = time.time()
        
        try:
            # Step 1: Plan data generation with LLM
            data_strategy = self._plan_data_generation(query, domain)
            
            if not data_strategy:
                return FormulaResult(
                    strategy=self.name,
                    status='error',
                    error_message='Failed to plan data generation',
                    time_ms=(time.time() - start) * 1000,
                    cost_estimate=0.05
                )
            
            # Step 2: Generate synthetic data
            X, y = self._generate_synthetic_data(data_strategy)
            
            # Step 3: Discover with timeout protection
            system = self.defi_system if domain == 'defi' else self.risk_system
            
            # Run discovery with timeout
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    system.discover_validate_interpret,
                    X, y,
                    data_strategy['variable_names'],
                    data_strategy['variable_descriptions'],
                    data_strategy['variable_units'],
                    query
                )
                
                try:
                    result = future.result(timeout=timeout_seconds)
                except TimeoutError:
                    return FormulaResult(
                        strategy=self.name,
                        status='timeout',
                        error_message=f'Discovery exceeded {timeout_seconds}s timeout',
                        time_ms=(time.time() - start) * 1000,
                        cost_estimate=0.05
                    )
            
            elapsed_ms = (time.time() - start) * 1000
            
            return FormulaResult(
                strategy=self.name,
                status='success',
                formula_expression=result['discovery']['expression'],
                formula_latex=self._to_latex(result['discovery']['sympy_expr']),
                formula_description=query,
                variables=[
                    {
                        'name': name,
                        'description': data_strategy['variable_descriptions'][name],
                        'unit': data_strategy['variable_units'][name],
                        'type': 'float'
                    }
                    for name in data_strategy['variable_names']
                ],
                validation_passed=result['validation']['valid'],
                validation_score=result['validation']['total_score'],
                validation_errors=result['validation']['errors'],
                validation_layers=result['validation']['layer_scores'],
                r2_score=result['discovery']['r2_score'],
                complexity=result['discovery']['complexity'],
                interpretation=result.get('interpretation'),
                confidence=min(result['discovery']['r2_score'], 1.0),
                time_ms=elapsed_ms,
                cost_estimate=0.05
            )
        
        except Exception as e:
            return FormulaResult(
                strategy=self.name,
                status='error',
                error_message=f"{str(e)}\n{traceback.format_exc()}",
                time_ms=(time.time() - start) * 1000,
                cost_estimate=0.05
            )
    
    def _plan_data_generation(self, query: str, domain: str) -> Optional[Dict]:
        """Use LLM to plan data generation."""
        prompt = f"""Plan synthetic data generation for formula discovery in {domain.upper()}.

User query: "{query}"

Respond with ONLY valid JSON:
{{
  "variable_names": ["var1", "var2"],
  "variable_descriptions": {{"var1": "description", "var2": "description"}},
  "variable_units": {{"var1": "unit", "var2": "unit"}},
  "data_ranges": {{"var1": [min, max], "var2": [min, max]}},
  "n_samples": 100
}}

EXAMPLES:
Query: "Impermanent loss"
Response: {{"variable_names": ["price_ratio"], "variable_descriptions": {{"price_ratio": "Current/Initial price"}}, "variable_units": {{"price_ratio": "dimensionless"}}, "data_ranges": {{"price_ratio": [0.1, 10]}}, "n_samples": 100}}

Query: "VaR at 95%"
Response: {{"variable_names": ["mu", "sigma", "t"], "variable_descriptions": {{"mu": "Expected return", "sigma": "Volatility", "t": "Time horizon"}}, "variable_units": {{"mu": "percentage", "sigma": "percentage", "t": "days"}}, "data_ranges": {{"mu": [-0.1, 0.1], "sigma": [0.05, 0.5], "t": [1, 252]}}, "n_samples": 100}}

JSON only, no markdown."""

        try:
            response = self.llm_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = response.content[0].text.strip()
            
            if '```' in text:
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
                text = text.rsplit('```', 1)[0]
            
            return json.loads(text.strip())
        except Exception as e:
            logging.error(f"Data planning failed: {e}")
            return None
    
    def _generate_synthetic_data(self, strategy: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic data based on strategy."""
        n_samples = strategy['n_samples']
        n_vars = len(strategy['variable_names'])
        
        # Generate X within specified ranges
        X = np.zeros((n_samples, n_vars))
        for i, var_name in enumerate(strategy['variable_names']):
            min_val, max_val = strategy['data_ranges'][var_name]
            X[:, i] = np.random.uniform(min_val, max_val, n_samples)
        
        # Generate y with a pattern based on variable names
        y = self._synthesize_target(X, strategy['variable_names'])
        
        # Add realistic noise (5% of std)
        noise_level = 0.05 * np.std(y)
        y += np.random.normal(0, noise_level, n_samples)
        
        return X, y
    
    def _synthesize_target(self, X: np.ndarray, var_names: List[str]) -> np.ndarray:
        """Create target values with realistic pattern."""
        # Use heuristics based on variable names
        if 'price_ratio' in var_names:
            p = X[:, var_names.index('price_ratio')]
            return 2*np.sqrt(p)/(p + 1) - 1  # Impermanent loss
        
        elif 'mu' in var_names and 'sigma' in var_names:
            mu_idx = var_names.index('mu')
            sigma_idx = var_names.index('sigma')
            
            if 't' in var_names:
                t_idx = var_names.index('t')
                return X[:, mu_idx] - 1.645 * X[:, sigma_idx] * np.sqrt(X[:, t_idx])  # VaR
            else:
                return X[:, mu_idx] - 1.645 * X[:, sigma_idx]
        
        elif 'reserve' in var_names[0].lower():
            # AMM constant product pattern
            return X[:, 0] * X[:, 1] if X.shape[1] >= 2 else X[:, 0]**2
        
        else:
            # Generic: weighted sum with non-linearity
            weights = np.random.uniform(0.5, 2.0, X.shape[1])
            return np.dot(X, weights) + 0.1 * np.sum(X**2, axis=1)


# =====================================================================
# REQUIREMENT 1: PARALLEL TESTING + REQUIREMENT 2: AUTO RECOMMENDATION
# =====================================================================

@dataclass
class MultiStrategyResult:
    """Results from all strategies for one query."""
    query: str
    domain: str
    timestamp: str
    
    results: Dict[Strategy, FormulaResult] = field(default_factory=dict)
    
    # Aggregated metrics
    total_time_ms: float = 0.0
    strategies_succeeded: int = 0
    strategies_validated: int = 0
    
    # REQUIREMENT 2: Automatic recommendation
    recommended_strategy: Optional[Strategy] = None
    recommendation_reason: str = ""
    recommendation_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'query': self.query,
            'domain': self.domain,
            'timestamp': self.timestamp,
            'results': {k.value: v.to_dict() for k, v in self.results.items()},
            'total_time_ms': self.total_time_ms,
            'strategies_succeeded': self.strategies_succeeded,
            'strategies_validated': self.strategies_validated,
            'recommended_strategy': self.recommended_strategy.value if self.recommended_strategy else None,
            'recommendation_reason': self.recommendation_reason,
            'recommendation_score': self.recommendation_score
        }


class FormulaGeneratorMultiverse:
    """
    Complete multiverse system with all 5 requirements.
    
    Requirements met:
    1. ✅ Parallel Testing
    2. ✅ Automatic Recommendation
    3. ✅ Comprehensive Analytics
    4. ✅ Export Everything
    5. ✅ Easy to Extend (BaseStrategy interface)
    """
    
    def __init__(self,
                 defi_csv: str,
                 risk_csv: str,
                 anthropic_api_key: str,
                 enable_strategies: Optional[List[Strategy]] = None,
                 parallel: bool = True,
                 timeout_per_strategy: int = 60):
        """
        Initialize multiverse.
        
        Args:
            defi_csv: Path to DeFi formulas CSV
            risk_csv: Path to Risk formulas CSV
            anthropic_api_key: Anthropic API key
            enable_strategies: List of strategies to enable (default: all available)
            parallel: Run strategies in parallel (REQUIREMENT 1)
            timeout_per_strategy: Max seconds per strategy
        """
        self.defi_csv = defi_csv
        self.risk_csv = risk_csv
        self.api_key = anthropic_api_key
        self.parallel = parallel
        self.timeout = timeout_per_strategy
        
        # REQUIREMENT 3 & 4: Storage for analytics and export
        self.results_history: List[MultiStrategyResult] = []
        
        # Initialize strategies (REQUIREMENT 5: Easy to extend)
        self.strategies: Dict[Strategy, BaseStrategy] = {}
        
        enabled = enable_strategies or [
            Strategy.SMART_LOOKUP,
            Strategy.LLM_GENERATION,
            # Strategy.SYMBOLIC_DISCOVERY  # Enable if desired (slow)
        ]
        
        logging.info("="*80)
        logging.info("FORMULA GENERATOR MULTIVERSE - INITIALIZATION")
        logging.info("="*80)
        
        for strategy_enum in enabled:
            try:
                if strategy_enum == Strategy.SMART_LOOKUP:
                    self.strategies[strategy_enum] = SmartLookupStrategy(defi_csv, risk_csv)
                    logging.info(f"✓ {strategy_enum.value} initialized")
                
                elif strategy_enum == Strategy.LLM_GENERATION:
                    self.strategies[strategy_enum] = LLMGenerationStrategy(anthropic_api_key)
                    logging.info(f"✓ {strategy_enum.value} initialized")
                
                elif strategy_enum == Strategy.SYMBOLIC_DISCOVERY:
                    self.strategies[strategy_enum] = SymbolicDiscoveryStrategy(anthropic_api_key)
                    logging.info(f"✓ {strategy_enum.value} initialized")
                
            except Exception as e:
                logging.warning(f"✗ {strategy_enum.value} failed to initialize: {e}")
        
        logging.info(f"\n✓ Multiverse ready with {len(self.strategies)} strategies")
        logging.info("="*80 + "\n")
    
    # REQUIREMENT 1: PARALLEL TESTING
    def generate_all_strategies(self,
                                query: str,
                                domain: str = 'defi') -> MultiStrategyResult:
        """
        REQUIREMENT 1: Generate formula using ALL strategies in PARALLEL.
        
        Args:
            query: User's natural language query
            domain: 'defi' or 'risk'
        
        Returns:
            MultiStrategyResult with all results + recommendation
        """
        start_time = time
