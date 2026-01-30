# =====================================================================
# FILE 1: core/models.py
# =====================================================================
"""
Data models for Formula Generator Multiverse.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Dict, List, Optional


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
    status: str

    formula_expression: Optional[str] = None
    formula_latex: Optional[str] = None
    formula_description: Optional[str] = None
    category: Optional[str] = None

    variables: List[Dict] = field(default_factory=list)
    output_unit: Optional[str] = None

    validation_passed: bool = False
    validation_score: float = 0.0
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    validation_layers: Optional[Dict] = None

    confidence: float = 0.0
    match_similarity: Optional[float] = None
    r2_score: Optional[float] = None
    complexity: Optional[int] = None

    interpretation: Optional[Dict] = None

    time_ms: float = 0.0
    cost_estimate: float = 0.0

    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result["strategy"] = self.strategy.value
        return result


@dataclass
class MultiStrategyResult:
    """Results from all strategies for one query."""

    query: str
    domain: str
    timestamp: str

    results: Dict[Strategy, FormulaResult] = field(default_factory=dict)

    total_time_ms: float = 0.0
    strategies_succeeded: int = 0
    strategies_validated: int = 0

    recommended_strategy: Optional[Strategy] = None
    recommendation_reason: str = ""
    recommendation_score: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "query": self.query,
            "domain": self.domain,
            "timestamp": self.timestamp,
            "results": {k.value: v.to_dict() for k, v in self.results.items()},
            "total_time_ms": self.total_time_ms,
            "strategies_succeeded": self.strategies_succeeded,
            "strategies_validated": self.strategies_validated,
            "recommended_strategy": (
                self.recommended_strategy.value if self.recommended_strategy else None
            ),
            "recommendation_reason": self.recommendation_reason,
            "recommendation_score": self.recommendation_score,
        }
