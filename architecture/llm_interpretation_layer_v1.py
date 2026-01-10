"""
LLM Interpretation Layer for HypatiaX Unified Discovery System
================================================================

This module adds Layer 5 (Interpretation) to the unified discovery system.
It transforms discovered formulas into rich, educational explanations.

Integration: Add to unified_discovery_system_v1.py
Estimated Time: 2-3 hours
Impact: Transforms tool → teaching platform
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class FormulaInterpretation:
    """Complete interpretation of a discovered formula."""

    # Core explanation
    plain_english: str
    mathematical_meaning: str

    # Component analysis
    term_explanations: List[Dict[str, str]]

    # Context
    why_this_form: str
    physical_intuition: Optional[str]
    domain_context: str

    # Validity & limitations
    assumptions: List[str]
    domain_of_validity: str
    limitations: List[str]
    edge_cases: List[str]

    # Practical guidance
    usage_guidance: str
    interpretation_warnings: List[str]

    # Related knowledge
    related_concepts: List[str]
    related_formulas: List[str]

    # Confidence
    interpretation_confidence: float  # 0-1

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    def to_markdown(self) -> str:
        """Generate markdown report."""
        md = f"# Formula Interpretation\n\n"
        md += f"## Plain English Explanation\n{self.plain_english}\n\n"
        md += f"## Mathematical Meaning\n{self.mathematical_meaning}\n\n"

        if self.term_explanations:
            md += "## Term-by-Term Breakdown\n"
            for i, term in enumerate(self.term_explanations, 1):
                md += f"{i}. **{term['term']}**: {term['explanation']}\n"
            md += "\n"

        md += f"## Why This Functional Form?\n{self.why_this_form}\n\n"

        if self.physical_intuition:
            md += f"## Physical Intuition\n{self.physical_intuition}\n\n"

        md += f"## Domain Context\n{self.domain_context}\n\n"

        if self.assumptions:
            md += "## Key Assumptions\n"
            for assumption in self.assumptions:
                md += f"- {assumption}\n"
            md += "\n"

        md += f"## Domain of Validity\n{self.domain_of_validity}\n\n"

        if self.limitations:
            md += "## Limitations\n"
            for limitation in self.limitations:
                md += f"- {limitation}\n"
            md += "\n"

        if self.edge_cases:
            md += "## Edge Cases & Warnings\n"
            for edge_case in self.edge_cases:
                md += f"⚠️ {edge_case}\n"
            md += "\n"

        md += f"## Usage Guidance\n{self.usage_guidance}\n\n"

        if self.related_concepts:
            md += "## Related Concepts\n"
            for concept in self.related_concepts:
                md += f"- {concept}\n"
            md += "\n"

        if self.related_formulas:
            md += "## Related Formulas\n"
            for formula in self.related_formulas:
                md += f"- {formula}\n"
            md += "\n"

        md += f"**Interpretation Confidence:** {self.interpretation_confidence:.1%}\n"

        return md


class FormulaInterpreter:
    """
    LLM-powered formula interpretation system.

    This class generates rich, educational explanations of discovered formulas
    using an LLM (Claude or GPT) with carefully crafted prompts.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        use_anthropic: bool = True,
    ):
        """
        Initialize the interpreter.

        Args:
            api_key: Anthropic or OpenAI API key
            model: Model to use (default: Claude Sonnet 4)
            use_anthropic: True for Anthropic, False for OpenAI
        """
        self.api_key = api_key
        self.model = model
        self.use_anthropic = use_anthropic

        if use_anthropic:
            try:
                import anthropic

                self.client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                raise ImportError("Install anthropic: pip install anthropic")
        else:
            try:
                import openai

                self.client = openai.OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("Install openai: pip install openai")

    def interpret_formula(
        self,
        formula: str,
        variable_names: List[str],
        r_squared: float,
        validation_score: float,
        domain: Optional[str] = None,
        discovery_method: Optional[str] = None,
        axioms_used: Optional[List[str]] = None,
        data_summary: Optional[Dict] = None,
    ) -> FormulaInterpretation:
        """
        Generate complete interpretation of a discovered formula.

        Args:
            formula: The discovered equation (e.g., "0.5*m*v**2")
            variable_names: List of variable names used
            r_squared: R² score from fitting
            validation_score: Validation score (0-100)
            domain: Domain context (e.g., "physics", "economics")
            discovery_method: How it was found ("llm", "axiom", "symbolic")
            axioms_used: List of axioms if theory-based
            data_summary: Statistical summary of the data

        Returns:
            FormulaInterpretation object with all fields populated
        """

        # Build comprehensive prompt
        prompt = self._build_interpretation_prompt(
            formula=formula,
            variable_names=variable_names,
            r_squared=r_squared,
            validation_score=validation_score,
            domain=domain,
            discovery_method=discovery_method,
            axioms_used=axioms_used,
            data_summary=data_summary,
        )

        # Get LLM response
        response = self._query_llm(prompt)

        # Parse structured response
        interpretation = self._parse_llm_response(
            response, formula, r_squared, validation_score
        )

        return interpretation

    def _build_interpretation_prompt(
        self,
        formula: str,
        variable_names: List[str],
        r_squared: float,
        validation_score: float,
        domain: Optional[str],
        discovery_method: Optional[str],
        axioms_used: Optional[List[str]],
        data_summary: Optional[Dict],
    ) -> str:
        """Build comprehensive interpretation prompt for LLM."""

        prompt = f"""You are an expert in scientific formula interpretation and education. 
Your task is to provide a complete, educational explanation of a discovered formula.

DISCOVERED FORMULA:
{formula}

VARIABLES:
{", ".join(variable_names)}

QUALITY METRICS:
- R² Score: {r_squared:.4f}
- Validation Score: {validation_score:.1f}/100
- Discovery Method: {discovery_method or "unknown"}

"""

        if domain:
            prompt += f"DOMAIN CONTEXT:\n{domain}\n\n"

        if axioms_used:
            prompt += f"AXIOMS USED IN DERIVATION:\n"
            for axiom in axioms_used:
                prompt += f"- {axiom}\n"
            prompt += "\n"

        if data_summary:
            prompt += f"DATA CHARACTERISTICS:\n"
            for key, value in data_summary.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"

        prompt += """
TASK: Provide a comprehensive interpretation in JSON format with these fields:

{
  "plain_english": "One-sentence plain English explanation anyone can understand",
  "mathematical_meaning": "Detailed mathematical interpretation (2-3 sentences)",
  "term_explanations": [
    {"term": "each_term", "explanation": "what it represents and why it appears"}
  ],
  "why_this_form": "Why this specific functional form emerged (power laws, products, etc.)",
  "physical_intuition": "Physical/intuitive understanding (if applicable)",
  "domain_context": "How this fits in the broader domain",
  "assumptions": ["key assumption 1", "key assumption 2"],
  "domain_of_validity": "When/where this formula applies",
  "limitations": ["limitation 1", "limitation 2"],
  "edge_cases": ["edge case warning 1", "edge case warning 2"],
  "usage_guidance": "Practical advice on using this formula",
  "interpretation_warnings": ["warning about over-interpreting", "statistical caveat"],
  "related_concepts": ["related concept 1", "related concept 2"],
  "related_formulas": ["similar formula 1", "similar formula 2"],
  "interpretation_confidence": 0.85
}

GUIDELINES:
1. Be educational and accessible
2. Explain WHY each term appears, not just WHAT it is
3. Connect to broader scientific/domain knowledge
4. Be honest about limitations and assumptions
5. Provide practical guidance
6. Use proper mathematical notation in explanations
7. Consider the discovery method (LLM, axioms, or symbolic regression)
8. If R² is low (<0.95), acknowledge uncertainty
9. If validation score is low (<70), warn about reliability

IMPORTANT: Return ONLY valid JSON. No preamble, no markdown backticks, just the JSON object.
"""

        return prompt

    def _query_llm(self, prompt: str) -> str:
        """Query the LLM with the interpretation prompt."""

        if self.use_anthropic:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        else:
            # OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at interpreting scientific formulas.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.3,
            )
            return response.choices[0].message.content

    def _parse_llm_response(
        self, response: str, formula: str, r_squared: float, validation_score: float
    ) -> FormulaInterpretation:
        """Parse LLM JSON response into FormulaInterpretation object."""

        # Clean response (remove markdown fences if present)
        response = response.strip()
        response = re.sub(r"^```json\s*", "", response)
        response = re.sub(r"\s*```$", "", response)

        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            # Fallback: create basic interpretation
            print(f"Warning: Failed to parse LLM response: {e}")
            return self._create_fallback_interpretation(
                formula, r_squared, validation_score
            )

        # Build interpretation object
        return FormulaInterpretation(
            plain_english=data.get("plain_english", "Unknown relationship"),
            mathematical_meaning=data.get("mathematical_meaning", ""),
            term_explanations=data.get("term_explanations", []),
            why_this_form=data.get("why_this_form", ""),
            physical_intuition=data.get("physical_intuition"),
            domain_context=data.get("domain_context", ""),
            assumptions=data.get("assumptions", []),
            domain_of_validity=data.get("domain_of_validity", ""),
            limitations=data.get("limitations", []),
            edge_cases=data.get("edge_cases", []),
            usage_guidance=data.get("usage_guidance", ""),
            interpretation_warnings=data.get("interpretation_warnings", []),
            related_concepts=data.get("related_concepts", []),
            related_formulas=data.get("related_formulas", []),
            interpretation_confidence=data.get("interpretation_confidence", 0.7),
        )

    def _create_fallback_interpretation(
        self, formula: str, r_squared: float, validation_score: float
    ) -> FormulaInterpretation:
        """Create basic interpretation when LLM fails."""

        return FormulaInterpretation(
            plain_english=f"The relationship is described by: {formula}",
            mathematical_meaning=f"Formula with R²={r_squared:.3f}",
            term_explanations=[],
            why_this_form="Unable to generate detailed interpretation",
            physical_intuition=None,
            domain_context="Unknown domain",
            assumptions=["LLM interpretation failed - manual review recommended"],
            domain_of_validity="Unknown - requires expert review",
            limitations=["Automated interpretation unavailable"],
            edge_cases=["LLM interpretation failed"],
            usage_guidance="Manual validation recommended",
            interpretation_warnings=[
                "Automatic interpretation failed - use with caution"
            ],
            related_concepts=[],
            related_formulas=[],
            interpretation_confidence=0.3,
        )


# ============================================================================
# INTEGRATION WITH UNIFIED DISCOVERY SYSTEM
# ============================================================================


def add_interpretation_to_discovery_result(
    discovery_result: Dict, api_key: str, domain: Optional[str] = None
) -> Dict:
    """
    Add interpretation layer to a discovery result.

    This is the main integration function. Call it after discovery completes.

    Args:
        discovery_result: Output from unified discovery system containing:
            - equation: str
            - variables: List[str]
            - r_squared: float
            - validation_score: float
            - method: str ('llm', 'axiom', 'symbolic')
            - axioms_used: Optional[List[str]]
            - data_summary: Optional[Dict]
        api_key: Anthropic/OpenAI API key
        domain: Domain context override

    Returns:
        Enhanced discovery result with 'interpretation' field
    """

    # Initialize interpreter
    interpreter = FormulaInterpreter(api_key=api_key)

    # Extract discovery details
    formula = discovery_result.get("equation", "")
    variables = discovery_result.get("variables", [])
    r_squared = discovery_result.get("r_squared", 0.0)
    validation_score = discovery_result.get("validation_score", 0.0)
    method = discovery_result.get("method", "unknown")
    axioms_used = discovery_result.get("axioms_used")
    data_summary = discovery_result.get("data_summary")

    # Generate interpretation
    interpretation = interpreter.interpret_formula(
        formula=formula,
        variable_names=variables,
        r_squared=r_squared,
        validation_score=validation_score,
        domain=domain or discovery_result.get("domain"),
        discovery_method=method,
        axioms_used=axioms_used,
        data_summary=data_summary,
    )

    # Add to result
    discovery_result["interpretation"] = interpretation.to_dict()
    discovery_result["interpretation_markdown"] = interpretation.to_markdown()

    return discovery_result


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================


def example_usage():
    """Example of how to use the interpretation layer."""

    # Simulated discovery result from unified system
    discovery_result = {
        "equation": "0.5*m*v**2",
        "variables": ["m", "v"],
        "r_squared": 0.9999,
        "validation_score": 98.5,
        "method": "llm",
        "domain": "physics",
        "data_summary": {
            "num_points": 100,
            "mass_range": "0.1-10 kg",
            "velocity_range": "0-100 m/s",
        },
    }

    # Add interpretation (requires API key)
    # api_key = "your-api-key-here"
    # enhanced_result = add_interpretation_to_discovery_result(
    #     discovery_result,
    #     api_key=api_key,
    #     domain="classical mechanics"
    # )

    # Print interpretation
    # print(enhanced_result['interpretation_markdown'])

    print("Example setup complete. Uncomment API key section to test.")


if __name__ == "__main__":
    example_usage()

    print("\n" + "=" * 70)
    print("LLM INTERPRETATION LAYER - READY FOR INTEGRATION")
    print("=" * 70)
    print("\nIntegration Steps:")
    print("1. Add this module to your unified_discovery_system_v1.py")
    print("2. After discovery completes, call add_interpretation_to_discovery_result()")
    print("3. Display interpretation_markdown to users")
    print("\nEstimated overhead: +2-5 seconds per discovery")
    print("Impact: Transforms HypatiaX into educational platform")
    print("=" * 70)
