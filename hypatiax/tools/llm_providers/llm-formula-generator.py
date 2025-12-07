import json

import anthropic


class FormulaGenerator:
    """
    Core AI formula generation engine
    THIS IS WHAT YOU WANTED
    """

    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_novel_formula(self, requirements, domain="finance"):
        """
        Generate NEW analytical expression

        Args:
            requirements: Natural language description
            domain: "finance", "defi", "esg", etc.

        Returns:
            Dict with formula, explanation, code
        """

        prompt = f"""You are a mathematical finance expert generating NOVEL analytical expressions.

Domain: {domain}
User Requirements: {requirements}

Generate a NOVEL formula (not just existing ones like Sharpe ratio).

Return JSON:
{{
    "formula_latex": "LaTeX notation",
    "formula_python": "def calculate(...): return ...",
    "variables": {{"var": "description"}},
    "explanation": "What this measures",
    "constraints": ["mathematical constraints"],
    "novelty_score": 0-10,
    "similar_to": ["existing formulas it builds on"],
    "advantages": ["why this is better"],
    "limitations": ["when this fails"]
}}

Be creative but mathematically rigorous!
"""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=2000, messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        content = message.content[0].text

        # Extract JSON
        json_match = content[content.find("{") : content.rfind("}") + 1]
        result = json.loads(json_match)

        return result
