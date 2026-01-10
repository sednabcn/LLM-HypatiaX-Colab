mappings / llm_mapping.py
#!/usr/bin/env python3
"""
LLM-Based Mapping for Query to Formula
Integrates with existing HypatiaX architecture
Part of mappings/ directory
"""
import sys
from pathlib import Path

# Add tools to path
sys.path.append(str(Path(__file__).parent.parent / "tools"))

from tools.llm_providers.anthropic_provider import AnthropicProvider
from tools.validation.symbolic_validator import SymbolicValidator


class LLMMapper:
    """
    LLM-based formula generation and mapping

    Integrates with existing HypatiaX:
        - Uses NER results as input context
        - Validates with symbolic validator
        - Returns compatible format

    Usage:
        mapper = LLMMapper(api_key="your-key")
        result = mapper.map("Calculate impermanent loss for ETH/USDC")
    """

    def __init__(self, api_key: str):
        self.llm = AnthropicProvider(api_key=api_key)
        self.validator = SymbolicValidator()

    def map(self, query: str, domain: str = "defi", ner_entities: dict = None) -> dict:
        """
        Map natural language query to formula

        Args:
            query: Natural language query
            domain: Target domain
            ner_entities: Optional NER results from custom_ner/

        Returns:
            {
                'formula': LaTeX formula,
                'code': Python implementation,
                'validation': Validation results,
                'score': Quality score,
                'explanation': Human-readable explanation
            }
        """
        # Enhance query with NER context if available
        enhanced_query = self._enhance_with_ner(query, ner_entities)

        # Generate formula candidates
        candidates = self.llm.generate_formula(
            requirements=enhanced_query, domain=domain, n_candidates=3
        )

        # Validate each candidate
        validated = []
        for candidate in candidates:
            validation = self.validator.validate(
                candidate["formula_latex"], domain=domain
            )
            candidate["validation"] = validation
            candidate["score"] = self._calculate_overall_score(candidate, validation)
            validated.append(candidate)

        # Sort by score
        validated.sort(key=lambda x: x["score"], reverse=True)

        # Return best
        best = validated[0]
        return {
            "formula": best["formula_latex"],
            "code": best["formula_python"],
            "validation": best["validation"],
            "score": best["score"],
            "explanation": best["explanation"],
            "variables": best["variables"],
            "all_candidates": validated,
        }

    def _enhance_with_ner(self, query: str, ner_entities: dict) -> str:
        """Enhance query with NER context"""
        if not ner_entities:
            return query

        # Add recognized entities to context
        context = f"{query}\n\nRecognized entities: {ner_entities}"
        return context

    def _calculate_overall_score(self, formula: dict, validation: dict) -> float:
        """Calculate combined score"""
        # Weight validation score (60%) and novelty (40%)
        validation_score = validation["score"]
        novelty_score = formula.get("novelty_score", 5) * 10

        return validation_score * 0.6 + novelty_score * 0.4
