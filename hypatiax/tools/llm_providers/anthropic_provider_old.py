#!/usr/bin/env python3
"""
Anthropic Claude API Provider for Formula Generation
Part of HypatiaX tools/llm_providers/anthropic_provider.py
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import anthropic


class AnthropicProvider:
    """
    Anthropic Claude integration for formula generation

    Usage:
        provider = AnthropicProvider(api_key="your-key")
        result = provider.generate_formula(requirements="...", domain="defi")
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic client"""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    def generate_formula(self, requirements: str, domain: str = "defi", n_candidates: int = 1) -> List[Dict[str, Any]]:
        """
        Generate analytical formulas using Claude

        Args:
            requirements: Natural language description
            domain: "defi", "finance", "esg", "risk"
            n_candidates: Number of formula variants

        Returns:
            List of formula dictionaries with structure:
            {
                'formula_latex': LaTeX notation,
                'formula_python': Python implementation,
                'variables': {var: description},
                'explanation': What this measures,
                'constraints': [mathematical constraints],
                'novelty_score': 0-10,
                'advantages': [list],
                'limitations': [list]
            }
        """
        formulas = []

        for i in range(n_candidates):
            prompt = self._build_prompt(requirements, domain, i)

            message = self.client.messages.create(
                model=self.model, max_tokens=2000, messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            content = message.content[0].text
            formula = self._parse_response(content)
            formulas.append(formula)

        return formulas

    def _build_prompt(self, requirements: str, domain: str, variant: int) -> str:
        """Build generation prompt"""
        domain_contexts = {
            "defi": "DeFi protocols, AMMs, liquidity pools, impermanent loss",
            "finance": "Portfolio optimization, risk metrics, returns, volatility",
            "esg": "Environmental, Social, Governance scores and impact",
            "risk": "Risk assessment, VaR, stress testing, exposure",
        }

        context = domain_contexts.get(domain, "financial mathematics")

        return f"""You are a mathematical finance expert generating NOVEL analytical expressions.

Domain: {domain} ({context})
User Requirements: {requirements}

Generate a NOVEL formula (variant {variant + 1}) - not just existing ones like Sharpe ratio.
Focus on computational rigor suitable for blockchain/smart contracts.

Return ONLY valid JSON (no markdown, no explanation outside JSON):
{{
    "formula_latex": "LaTeX notation of the formula",
    "formula_python": "def calculate(param1, param2, ...): return ...",
    "variables": {{"var_name": "description of variable"}},
    "explanation": "What this formula measures and why it's useful",
    "constraints": ["mathematical constraint 1", "constraint 2"],
    "novelty_score": 7,
    "similar_to": ["existing formula it builds on"],
    "advantages": ["advantage 1", "advantage 2"],
    "limitations": ["when this fails", "edge cases"]
}}

Requirements for formula:
1. Mathematically rigorous
2. Numerically stable (avoid division by near-zero)
3. Computationally efficient
4. Novel but builds on established principles
5. Suitable for real-time calculation

Be creative but ensure mathematical validity!"""

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Extract JSON from response"""
        try:
            # Find JSON in response
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]

            result = json.loads(json_str)

            # Ensure all required fields
            required = ["formula_latex", "formula_python", "variables", "explanation", "novelty_score"]
            for field in required:
                if field not in result:
                    result[field] = "N/A"

            # Set defaults
            result.setdefault("constraints", [])
            result.setdefault("advantages", [])
            result.setdefault("limitations", [])
            result.setdefault("similar_to", [])

            return result
        except Exception as e:
            return {
                "formula_latex": "Parse error",
                "formula_python": "# Error parsing response",
                "error": str(e),
                "raw_content": content,
            }

    def refine_formula(self, formula: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Iteratively improve formula based on feedback

        Args:
            formula: Original formula dict
            feedback: User feedback on what to improve

        Returns:
            Refined formula dict
        """
        prompt = f"""
Original formula: {formula['formula_latex']}
Original implementation: {formula['formula_python']}

User feedback: {feedback}

Generate an improved version addressing this feedback.
Maintain mathematical validity and improve based on the specific feedback.

Return ONLY valid JSON with the same structure as before.
"""

        message = self.client.messages.create(
            model=self.model, max_tokens=2000, messages=[{"role": "user", "content": prompt}]
        )

        content = message.content[0].text
        return self._parse_response(content)


# Example usage and testing
if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        exit(1)

    provider = AnthropicProvider(api_key=api_key)

    print("Testing Anthropic Provider...")
    print("=" * 60)

    # Test formula generation
    results = provider.generate_formula(
        requirements="Calculate impermanent loss for Uniswap V2 pools", domain="defi", n_candidates=1
    )

    formula = results[0]
    print(f"\n📐 Formula: {formula['formula_latex']}")
    print(f"\n💻 Implementation:\n{formula['formula_python']}")
    print(f"\n📝 Explanation: {formula['explanation']}")
    print("\n✓ Test completed!")
