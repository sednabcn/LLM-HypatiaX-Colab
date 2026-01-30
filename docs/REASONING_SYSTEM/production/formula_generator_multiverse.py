# formula_generator_multiverse.py
"""
Formula Generator Multiverse
Tests ALL generation strategies simultaneously and compares results

Architecture:
- Single input → Multiple strategies in parallel
- Log everything → Compare → Analytics → Recommend best approach

Strategies:
1. Smart Lookup (Semantic Search)
2. LLM Generation (Claude)
3. Symbolic Discovery (PySR)
4. Hybrid (Lookup + LLM)
5. Hybrid (Lookup + Discovery)
"""

import sys

sys.path.append("../tools")

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Your existing tools
from symbolic.hybrid_system import HybridDiscoverySystem
from validation.ensemble_validator import EnsembleValidator

# External libraries
try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print(
        "⚠️  sentence-transformers not available. Install: pip install sentence-transformers"
    )

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  anthropic not available. Install: pip install anthropic")

import os

# =====================================================================
# DATA MODELS
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
    """Result from a single strategy."""

    strategy: Strategy
    status: str  # 'success', 'error', 'no_match'

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
    confidence: float = 0.0  # 0-1, how confident is this result
    match_similarity: Optional[float] = None  # For lookup strategies
    r2_score: Optional[float] = None  # For discovery
    complexity: Optional[int] = None

    # Interpretation
    interpretation: Optional[Dict] = None

    # Performance
    time_ms: float = 0.0
    cost_estimate: float = 0.0  # USD

    # Error handling
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


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

    # Recommendation
    recommended_strategy: Optional[Strategy] = None
    recommendation_reason: str = ""


# =====================================================================
# STRATEGY IMPLEMENTATIONS
# =====================================================================


class SmartLookupStrategy:
    """Strategy 1: Semantic search over existing formulas."""

    def __init__(self, defi_csv: str, risk_csv: str):
        self.name = Strategy.SMART_LOOKUP

        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers required")

        # Load embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Load formulas
        self.defi_df = pd.read_csv(defi_csv)
        self.risk_df = pd.read_csv(risk_csv)
        self.formulas_df = pd.concat([self.defi_df, self.risk_df], ignore_index=True)

        # Pre-compute embeddings
        logging.info("Computing embeddings for formula database...")
        self.embeddings = self.model.encode(
            self.formulas_df["description"].tolist(), show_progress_bar=False
        )
        logging.info(f"✓ Loaded {len(self.formulas_df)} formulas")

    def generate(self, query: str, domain: str) -> FormulaResult:
        """Generate formula via semantic search."""
        start = time.time()

        try:
            # Embed query
            query_embedding = self.model.encode([query])[0]

            # Cosine similarity
            similarities = np.dot(self.embeddings, query_embedding) / (
                np.linalg.norm(self.embeddings, axis=1)
                * np.linalg.norm(query_embedding)
            )

            # Best match
            best_idx = np.argmax(similarities)
            similarity = similarities[best_idx]
            match = self.formulas_df.iloc[best_idx]

            # Confidence thresholds
            if similarity < 0.3:
                status = "no_match"
                confidence = 0.0
            elif similarity < 0.6:
                status = "success"
                confidence = 0.5
            else:
                status = "success"
                confidence = similarity

            # Extract variables
            variables = self._extract_variables(match["analytical_formula"])

            # Quick validation
            validation = self._quick_validate(match["analytical_formula"])

            elapsed_ms = (time.time() - start) * 1000

            return FormulaResult(
                strategy=self.name,
                status=status,
                formula_expression=match["analytical_formula"],
                formula_latex=self._to_latex(match["analytical_formula"]),
                formula_description=match["description"],
                category=match["category"],
                variables=variables,
                validation_passed=validation["passed"],
                validation_score=validation["score"],
                confidence=confidence,
                match_similarity=similarity,
                time_ms=elapsed_ms,
                cost_estimate=0.0001,  # Essentially free
                warnings=(
                    [] if similarity > 0.6 else [f"Low similarity: {similarity:.2f}"]
                ),
            )

        except Exception as e:
            return FormulaResult(
                strategy=self.name,
                status="error",
                error_message=str(e),
                time_ms=(time.time() - start) * 1000,
            )

    def _extract_variables(self, formula: str) -> List[Dict]:
        """Extract variables from formula string."""
        import re

        vars_raw = re.findall(r"\b[a-z_][a-z0-9_]*\b", formula.lower())
        functions = ["sqrt", "exp", "log", "sin", "cos", "tan", "abs"]
        vars_unique = [v for v in set(vars_raw) if v not in functions]

        return [
            {
                "name": v,
                "description": f"Variable {v}",
                "unit": "dimensionless",
                "type": "float",
            }
            for v in vars_unique
        ]

    def _quick_validate(self, formula: str) -> Dict:
        """Quick syntax validation."""
        try:
            from sympy import sympify

            sympify(formula)
            return {"passed": True, "score": 80}
        except:
            return {"passed": False, "score": 0}

    def _to_latex(self, formula: str) -> str:
        """Convert to LaTeX."""
        try:
            from sympy import latex, sympify

            return latex(sympify(formula))
        except:
            return formula


class LLMGenerationStrategy:
    """Strategy 2: Generate formula using Claude."""

    def __init__(self, api_key: str):
        self.name = Strategy.LLM_GENERATION

        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic SDK required")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.validator = EnsembleValidator(domain="defi")

    def generate(self, query: str, domain: str) -> FormulaResult:
        """Generate formula using LLM."""
        start = time.time()

        prompt = self._create_prompt(query, domain)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text.strip()

            # Parse JSON
            formula_data = self._parse_response(response_text)

            if not formula_data:
                return FormulaResult(
                    strategy=self.name,
                    status="error",
                    error_message="Failed to parse LLM response",
                    time_ms=(time.time() - start) * 1000,
                    cost_estimate=0.01,
                )

            # Validate
            self.validator.domain = domain
            validation = self._validate_formula(formula_data, domain)

            elapsed_ms = (time.time() - start) * 1000

            return FormulaResult(
                strategy=self.name,
                status="success",
                formula_expression=formula_data["formula"],
                formula_latex=formula_data["latex"],
                formula_description=formula_data["description"],
                category=formula_data.get("category", "Unknown"),
                variables=formula_data["variables"],
                output_unit=formula_data.get("output_unit", "dimensionless"),
                validation_passed=validation["passed"],
                validation_score=validation["score"],
                validation_errors=validation["errors"],
                validation_warnings=validation.get("warnings", []),
                validation_layers=validation.get("layers"),
                confidence=0.7,  # LLM confidence
                time_ms=elapsed_ms,
                cost_estimate=0.01,
                warnings=self._check_hallucination_patterns(formula_data),
            )

        except Exception as e:
            return FormulaResult(
                strategy=self.name,
                status="error",
                error_message=str(e),
                time_ms=(time.time() - start) * 1000,
                cost_estimate=0.01,
            )

    def _create_prompt(self, query: str, domain: str) -> str:
        """Create LLM prompt."""
        return f"""You are a mathematical formula generator for {domain.upper()}.

User request: "{query}"

Generate a precise mathematical formula. Respond ONLY with valid JSON:
{{
  "formula": "expression using: sqrt(), exp(), log(), ^, *, /, +, -",
  "latex": "LaTeX version",
  "variables": [
    {{"name": "var_name", "description": "what it is", "unit": "unit", "type": "float"}}
  ],
  "output_unit": "result unit",
  "category": "formula type",
  "description": "brief explanation"
}}

Rules:
- Use standard math notation
- All variables in formula must be in variables array
- DeFi variables: reserve_x, reserve_y, price_ratio, fee, liquidity
- Risk variables: mu, sigma, confidence, t

Examples:
- Impermanent Loss: "2*sqrt(price_ratio)/(price_ratio + 1) - 1"
- VaR 95%: "mu - 1.645*sigma*sqrt(t)"

JSON only, no other text."""

    def _parse_response(self, text: str) -> Optional[Dict]:
        """Parse LLM JSON response."""
        try:
            # Remove markdown code blocks
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.rsplit("```", 1)[0]

            return json.loads(text.strip())
        except:
            return None

    def _validate_formula(self, formula_data: Dict, domain: str) -> Dict:
        """Validate using ensemble validator."""
        try:
            variable_defs = {
                v["name"]: v["description"] for v in formula_data["variables"]
            }
            variable_units = {v["name"]: v["unit"] for v in formula_data["variables"]}

            result = self.validator.validate_complete(
                expression_str=formula_data["formula"],
                variable_definitions=variable_defs,
                variable_units=variable_units,
            )

            return {
                "passed": result["valid"],
                "score": result["total_score"],
                "layers": result["layer_scores"],
                "errors": result["errors"],
                "warnings": result.get("warnings", []),
            }
        except Exception as e:
            return {"passed": False, "score": 0, "errors": [str(e)]}

    def _check_hallucination_patterns(self, formula_data: Dict) -> List[str]:
        """Detect potential LLM hallucinations."""
        warnings = []
        formula = formula_data["formula"]

        if len(formula) > 200:
            warnings.append("Formula unusually long - verify")

        if "undefined" in formula.lower():
            warnings.append("Contains 'undefined' - likely hallucination")

        # Check variable consistency
        import re

        formula_vars = set(re.findall(r"\b[a-z_][a-z0-9_]*\b", formula.lower()))
        defined_vars = set(v["name"] for v in formula_data["variables"])
        functions = {"sqrt", "exp", "log", "sin", "cos", "tan", "abs"}

        undefined = formula_vars - defined_vars - functions
        if undefined:
            warnings.append(f"Undefined variables: {undefined}")

        return warnings


class SymbolicDiscoveryStrategy:
    """Strategy 3: Discover formula using symbolic regression."""

    def __init__(self, api_key: str):
        self.name = Strategy.SYMBOLIC_DISCOVERY

        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic SDK required for data planning")

        self.llm_client = anthropic.Anthropic(api_key=api_key)
        self.defi_system = HybridDiscoverySystem(domain="defi")
        self.risk_system = HybridDiscoverySystem(domain="risk")

    def generate(self, query: str, domain: str) -> FormulaResult:
        """Discover formula via symbolic regression."""
        start = time.time()

        try:
            # Step 1: Plan data generation
            data_strategy = self._plan_data_generation(query, domain)

            if not data_strategy:
                return FormulaResult(
                    strategy=self.name,
                    status="error",
                    error_message="Failed to plan data generation",
                    time_ms=(time.time() - start) * 1000,
                    cost_estimate=0.05,
                )

            # Step 2: Generate synthetic data
            X, y = self._generate_data(data_strategy)

            # Step 3: Discover
            system = self.defi_system if domain == "defi" else self.risk_system

            result = system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=data_strategy["variable_names"],
                variable_descriptions=data_strategy["variable_descriptions"],
                variable_units=data_strategy["variable_units"],
                description=query,
            )

            elapsed_ms = (time.time() - start) * 1000

            return FormulaResult(
                strategy=self.name,
                status="success",
                formula_expression=result["discovery"]["expression"],
                formula_latex=self._to_latex(result["discovery"]["sympy_expr"]),
                formula_description=query,
                variables=[
                    {
                        "name": name,
                        "description": data_strategy["variable_descriptions"][name],
                        "unit": data_strategy["variable_units"][name],
                        "type": "float",
                    }
                    for name in data_strategy["variable_names"]
                ],
                validation_passed=result["validation"]["valid"],
                validation_score=result["validation"]["total_score"],
                validation_errors=result["validation"]["errors"],
                validation_layers=result["validation"]["layer_scores"],
                r2_score=result["discovery"]["r2_score"],
                complexity=result["discovery"]["complexity"],
                interpretation=result.get("interpretation"),
                confidence=min(result["discovery"]["r2_score"], 1.0),
                time_ms=elapsed_ms,
                cost_estimate=0.05,
            )

        except Exception as e:
            return FormulaResult(
                strategy=self.name,
                status="error",
                error_message=str(e),
                time_ms=(time.time() - start) * 1000,
                cost_estimate=0.05,
            )

    def _plan_data_generation(self, query: str, domain: str) -> Optional[Dict]:
        """Use LLM to plan data generation."""
        prompt = f"""Plan data generation for formula discovery in {domain.upper()}.

Query: "{query}"

Respond with JSON:
{{
  "variable_names": ["var1", "var2"],
  "variable_descriptions": {{"var1": "description"}},
  "variable_units": {{"var1": "unit"}},
  "data_ranges": {{"var1": [min, max]}},
  "n_samples": 100
}}

Examples:
- "Impermanent loss" → {{"variable_names": ["price_ratio"], "data_ranges": {{"price_ratio": [0.1, 10]}}}}
- "VaR 95%" → {{"variable_names": ["mu", "sigma", "t"], "data_ranges": {{"mu": [-0.1, 0.1], "sigma": [0.1, 0.5], "t": [1, 252]}}}}"""

        try:
            response = self.llm_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.content[0].text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.rsplit("```", 1)[0]

            return json.loads(text.strip())
        except:
            return None

    def _generate_data(self, strategy: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic data."""
        n_samples = strategy["n_samples"]
        n_vars = len(strategy["variable_names"])

        X = np.zeros((n_samples, n_vars))
        for i, var_name in enumerate(strategy["variable_names"]):
            min_val, max_val = strategy["data_ranges"][var_name]
            X[:, i] = np.random.uniform(min_val, max_val, n_samples)

        # Generate y with a pattern (simplified)
        y = self._synthesize_target(X, strategy["variable_names"])

        # Add noise
        y += np.random.normal(0, 0.05 * np.std(y), n_samples)

        return X, y

    def _synthesize_target(self, X: np.ndarray, var_names: List[str]) -> np.ndarray:
        """Create target values with pattern."""
        # Heuristics based on common patterns
        if "price_ratio" in var_names:
            p = X[:, var_names.index("price_ratio")]
            return 2 * np.sqrt(p) / (p + 1) - 1  # IL pattern

        elif "sigma" in var_names and "mu" in var_names:
            mu_idx = var_names.index("mu")
            sigma_idx = var_names.index("sigma")
            if "t" in var_names:
                t_idx = var_names.index("t")
                return X[:, mu_idx] - 1.645 * X[:, sigma_idx] * np.sqrt(X[:, t_idx])
            else:
                return X[:, mu_idx] - 1.645 * X[:, sigma_idx]

        else:
            # Generic combination
            return np.sum(X, axis=1) / X.shape[1]

    def _to_latex(self, sympy_expr) -> str:
        """Convert to LaTeX."""
        try:
            from sympy import latex

            return latex(sympy_expr)
        except:
            return str(sympy_expr)


# =====================================================================
# MULTIVERSE CLASS - THE MAIN ENGINE
# =====================================================================


class FormulaGeneratorMultiverse:
    """
    The complete multiverse class that runs ALL strategies
    and provides analytics to determine the best approach.
    """

    def __init__(
        self,
        defi_csv: str,
        risk_csv: str,
        anthropic_api_key: str,
        enable_strategies: Optional[List[Strategy]] = None,
    ):
        """
        Initialize all strategies.

        Args:
            defi_csv: Path to DeFi formulas CSV
            risk_csv: Path to Risk formulas CSV
            anthropic_api_key: Anthropic API key
            enable_strategies: List of strategies to enable (default: all)
        """
        self.defi_csv = defi_csv
        self.risk_csv = risk_csv
        self.api_key = anthropic_api_key

        # Results storage
        self.results_history: List[MultiStrategyResult] = []

        # Initialize strategies
        self.strategies = {}

        enabled = enable_strategies or list(Strategy)

        logging.info("Initializing Formula Generator Multiverse...")

        if Strategy.SMART_LOOKUP in enabled:
            try:
                self.strategies[Strategy.SMART_LOOKUP] = SmartLookupStrategy(
                    defi_csv, risk_csv
                )
                logging.info("✓ Smart Lookup ready")
            except Exception as e:
                logging.warning(f"✗ Smart Lookup failed: {e}")

        if Strategy.LLM_GENERATION in enabled:
            try:
                self.strategies[Strategy.LLM_GENERATION] = LLMGenerationStrategy(
                    anthropic_api_key
                )
                logging.info("✓ LLM Generation ready")
            except Exception as e:
                logging.warning(f"✗ LLM Generation failed: {e}")

        if Strategy.SYMBOLIC_DISCOVERY in enabled:
            try:
                self.strategies[Strategy.SYMBOLIC_DISCOVERY] = (
                    SymbolicDiscoveryStrategy(anthropic_api_key)
                )
                logging.info("✓ Symbolic Discovery ready")
            except Exception as e:
                logging.warning(f"✗ Symbolic Discovery failed: {e}")

        logging.info(f"Multiverse initialized with {len(self.strategies)} strategies")

    def generate_all_strategies(
        self, query: str, domain: str = "defi", parallel: bool = True
    ) -> MultiStrategyResult:
        """
        Generate formula using ALL available strategies.

        Args:
            query: User's natural language query
            domain: 'defi' or 'risk'
            parallel: Run strategies in parallel (faster) or sequential (easier debugging)

        Returns:
            MultiStrategyResult with all strategy results
        """
        start_time = time.time()

        logging.info(f"\n{'='*80}")
        logging.info(f"MULTIVERSE GENERATION")
        logging.info(f"Query: {query}")
        logging.info(f"Domain: {domain}")
        logging.info(f"Strategies: {len(self.strategies)}")
        logging.info(f"{'='*80}\n")

        result = MultiStrategyResult(
            query=query, domain=domain, timestamp=datetime.now().isoformat()
        )

        if parallel:
            # Run strategies in parallel for speed
            with ThreadPoolExecutor(max_workers=len(self.strategies)) as executor:
                future_to_strategy = {
                    executor.submit(strategy.generate, query, domain): name
                    for name, strategy in self.strategies.items()
                }

                for future in as_completed(future_to_strategy):
                    strategy_name = future_to_strategy[future]
                    try:
                        strategy_result = future.result()
                        result.results[strategy_name] = strategy_result

                        logging.info(
                            f"✓ {strategy_name.value}: {strategy_result.status} "
                            f"({strategy_result.time_ms:.0f}ms)"
                        )

                        if strategy_result.status == "success":
                            result.strategies_succeeded += 1
                            if strategy_result.validation_passed:
                                result.strategies_validated += 1

                    except Exception as e:
                        logging.error(f"✗ {strategy_name.value} failed: {e}")
        else:
            # Sequential for debugging
            for strategy_name, strategy in self.strategies.items():
                try:
                    strategy_result = strategy.generate(query, domain)
                    result.results[strategy_name] = strategy_result

                    logging.info(
                        f"✓ {strategy_name.value}: {strategy_result.status} "
                        f"({strategy_result.time_ms:.0f}ms)"
                    )

                    if strategy_result.status == "success":
                        result.strategies_succeeded += 1
                        if strategy_result.validation_passed:
                            result.strategies_validated += 1

                except Exception as e:
                    logging.error(f"✗ {strategy_name.value} failed: {e}")

        result.total_time_ms = (time.time() - start_time) * 1000

        # Determine recommendation
        result.recommended_strategy, result.recommendation_reason = (
            self._recommend_strategy(result)
        )

        # Store in history
        self.results_history.append(result)

        logging.info(f"\n{'='*80}")
        logging.info(
            f"RECOMMENDATION: {result.recommended_strategy.value if result.recommended_strategy else 'None'}"
        )
        logging.info(f"REASON: {result.recommendation_reason}")
        logging.info(f"{'='*80}\n")

        return result

    def _recommend_strategy(
        self, result: MultiStrategyResult
    ) -> Tuple[Optional[Strategy], str]:
        """
        Determine which strategy performed best for this query.

        Scoring criteria:
        1. Validation passed (required)
        2. High validation score (>80 preferred)
        3. Fast response time (<5s bonus)
        4. Low cost (<$0.02 bonus)
        5. High confidence (>0.7 preferred)
        """
        scores = {}

        for strategy, strategy_result in result.results.items():
            if strategy_result.status != "success":
                continue

            score = 0
            reasons = []

            # Validation (most important)
            if strategy_result.validation_passed:
                score += 50
                reasons.append("validated")
            else:
                continue  # Skip if validation failed

            # Validation score
            score += strategy_result.validation_score * 0.3
            if strategy_result.validation_score >= 80:
                reasons.append(f"high score ({strategy_result.validation_score:.0f})")

            # Speed bonus
            if strategy_result.time_ms < 500:
                score += 20
                reasons.append("very fast")
            elif strategy_result.time_ms < 5000:
                score += 10
                reasons.append("fast")

            # Cost bonus
            if strategy_result.cost_estimate < 0.01:
                score += 10
                reasons.append("low cost")

            # Confidence
            if strategy_result.confidence:
                score += strategy_result.confidence * 20
                if strategy_result.confidence > 0.8:
                    reasons.append("high confidence")

            # R² bonus for discovery
            if strategy_result.r2_score and strategy_result.r2_score > 0.95:
                score += 10
                reasons.append(f"excellent fit (R²={strategy_result.r2_score:.2f})")

            scores[strategy] = (score, ", ".join(reasons))

        if not scores:
            return None, "No strategies succeeded with valid results"

        best_strategy = max(scores, key=lambda k: scores[k][0])
        return best_strategy, scores[best_strategy][1]

    def generate_analytics(self) -> pd.DataFrame:
        """
        Generate comprehensive analytics from all test runs.

        Returns:
            DataFrame with strategy performance metrics
        """
        if not self.results_history:
            return pd.DataFrame()

        analytics = []

        for strategy in self.strategies.keys():
            strategy_results = []

            for multi_result in self.results_history:
                if strategy in multi_result.results:
                    strategy_results.append(multi_result.results[strategy])

            if not strategy_results:
                continue

            # Calculate metrics
            total = len(strategy_results)
            successes = sum(1 for r in strategy_results if r.status == "success")
            validated = sum(1 for r in strategy_results if r.validation_passed)

            avg_time = np.mean([r.time_ms for r in strategy_results])
            avg_score = np.mean(
                [r.validation_score for r in strategy_results if r.status == "success"]
            )
            avg_cost = np.mean([r.cost_estimate for r in strategy_results])

            times_recommended = sum(
                1 for mr in self.results_history if mr.recommended_strategy == strategy
            )

            analytics.append(
                {
                    "Strategy": strategy.value,
                    "Total Runs": total,
                    "Successes": successes,
                    "Success Rate": f"{(successes/total)*100:.1f}%",
                    "Validated": validated,
                    "Validation Rate": f"{(validated/total)*100:.1f}%",
                    "Avg Time (ms)": f"{avg_time:.0f}",
                    "Avg Score": f"{avg_score:.1f}",
                    "Avg Cost": f"${avg_cost:.4f}",
                    "Times Recommended": times_recommended,
                    "Recommend %": f"{(times_recommended/len(self.results_history))*100:.1f}%",
                }
            )

        return pd.DataFrame(analytics)

    def export_results(self, filepath: str):
        """Export all results to JSON file."""
        data = {
            "metadata": {
                "total_queries": len(self.results_history),
                "strategies_enabled": [s.value for s in self.strategies.keys()],
                "export_time": datetime.now().isoformat(),
            },
            "results": [],
        }

        for multi_result in self.results_history:
            result_dict = {
                "query": multi_result.query,
                "domain": multi_result.domain,
                "timestamp": multi_result.timestamp,
                "recommended_strategy": (
                    multi_result.recommended_strategy.value
                    if multi_result.recommended_strategy
                    else None
                ),
                "recommendation_reason": multi_result.recommendation_reason,
                "strategies": {},
            }

        for strategy, strategy_result in multi_result.results.items():
            result_dict["strategies"][strategy.value] = {
                "status": strategy_result.status,
                "formula": strategy_result.formula_expression,
                "validation_passed": strategy_result.validation_passed,
                "validation_score": strategy_result.validation_score,
                "time_ms": strategy_result.time_ms,
                "cost": strategy_result.cost_estimate,
                "confidence": strategy_result.confidence,
            }

        data["results"].append(result_dict)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logging.info(f"✓ Results exported to {filepath}")

    def print_summary(self):
        """Print human-readable summary of all tests."""
        print("\n" + "=" * 80)
        print("FORMULA GENERATOR MULTIVERSE - SUMMARY")
        print("=" * 80)
        print(f"Total Queries Tested: {len(self.results_history)}")
        print(f"Strategies Enabled: {len(self.strategies)}")
        print("\n" + "-" * 80)
        print("STRATEGY PERFORMANCE")
        print("-" * 80)

        analytics_df = self.generate_analytics()
        if not analytics_df.empty:
            print(analytics_df.to_string(index=False))

        print("\n" + "-" * 80)
        print("RECOMMENDATIONS")
        print("-" * 80)

        for i, result in enumerate(self.results_history, 1):
            print(f"\n{i}. Query: {result.query[:60]}...")
            print(f"   Domain: {result.domain}")
            print(
                f"   Winner: {result.recommended_strategy.value if result.recommended_strategy else 'None'}"
            )
            print(f"   Reason: {result.recommendation_reason}")

        print("\n" + "=" * 80)
