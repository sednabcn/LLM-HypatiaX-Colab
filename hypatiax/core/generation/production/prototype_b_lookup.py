# prototype_b_llm.py
"""
Prototype B: LLM-Based Formula Generation
Uses Claude Sonnet to generate formulas from descriptions
"""

import json
import os
import sys
from typing import Dict

import anthropic

sys.path.append('../tools')
from validation.ensemble_validator import EnsembleValidator


class LLMGeneratorAPI:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.validator = EnsembleValidator(domain='defi')

    def generate_formula(self, user_query: str, domain: str = 'defi') -> Dict:
        """Generate formula using LLM."""

        prompt = f"""You are a mathematical formula generator for {domain.upper()} applications.

User request: "{user_query}"

Generate a mathematical formula that answers this request.

Respond ONLY with valid JSON in this exact format:
{{
  "formula": "mathematical expression using standard notation",
  "latex": "LaTeX version",
  "variables": [
    {{"name": "var_name", "description": "what it represents", "unit": "unit type"}}
  ],
  "output_unit": "unit of result",
  "category": "formula category",
  "constraints": ["list of constraints like 'x > 0'"],
  "description": "brief explanation of what the formula calculates"
}}

CRITICAL RULES:
1. Use standard notation: sqrt(), exp(), log(), ^, *, /, +, -
2. Variable names must be alphanumeric (no spaces)
3. All variables in formula must be listed in variables array
4. Be mathematically precise
5. For DeFi: use common variables like reserve_x, reserve_y, price_ratio, fee
6. For Risk: use mu, sigma, confidence, t (time)

Examples:
- Impermanent Loss: "2*sqrt(price_ratio)/(price_ratio + 1) - 1"
- VaR 95%: "mu - 1.645*sigma*sqrt(t)"
- Uniswap swap: "(amount_in*(1-fee)*reserve_out)/(reserve_in + amount_in*(1-fee))"

Respond with JSON only, no other text."""

        # Call Claude
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]

            formula_data = json.loads(response_text)

            # Validate the generated formula
            validation_result = self._validate_formula(
                formula_data['formula'],
                formula_data['variables'],
                domain
            )

            return {
                'status': 'success',
                'method': 'llm_generation',
                'formula': {
                    'expression': formula_data['formula'],
                    'latex': formula_data['latex'],
                    'description': formula_data['description'],
                    'category': formula_data['category']
                },
                'validation': validation_result,
                'metadata': {
                    'variables': formula_data['variables'],
                    'output_unit': formula_data['output_unit'],
                    'constraints': formula_data['constraints'],
                    'domain': domain
                },
                'warnings': self._check_hallucination_risk(formula_data),
                'response_time_ms': 2500  # Typical
            }

        except json.JSONDecodeError as e:
            return {
                'status': 'error',
                'error': 'LLM returned invalid JSON',
                'details': str(e),
                'raw_response': response_text[:500]
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _validate_formula(self, formula: str, variables: List[Dict], domain: str) -> Dict:
        """Validate using your ensemble validator."""
        try:
            self.validator.domain = domain

            variable_defs = {v['name']: v['description'] for v in variables}
            variable_units = {v['name']: v['unit'] for v in variables}

            result = self.validator.validate_complete(
                expression_str=formula,
                variable_definitions=variable_defs,
                variable_units=variable_units
            )

            return {
                'passed': result['valid'],
                'score': result['total_score'],
                'method': 'ensemble_validation',
                'layers': result['layer_scores'],
                'errors': result['errors'],
                'warnings': result.get('warnings', [])
            }
        except Exception as e:
            return {
                'passed': False,
                'score': 0,
                'method': 'ensemble_validation',
                'errors': [str(e)]
            }

    def _check_hallucination_risk(self, formula_data: Dict) -> List[str]:
        """Check for common LLM hallucination patterns."""
        warnings = []

        formula = formula_data['formula']

        # Check for suspicious patterns
        if 'undefined' in formula.lower():
            warnings.append("Formula contains 'undefined' - possible hallucination")

        if len(formula) > 200:
            warnings.append("Formula is unusually long - verify correctness")

        # Check if all variables in formula are defined
        import re
        formula_vars = set(re.findall(r'\b[a-z_][a-z0-9_]*\b', formula.lower()))
        defined_vars = set(v['name'] for v in formula_data['variables'])

        undefined = formula_vars - defined_vars - {'sqrt', 'exp', 'log', 'sin', 'cos'}
        if undefined:
            warnings.append(f"Undefined variables in formula: {undefined}")

        return warnings

# ===== TEST =====
if __name__ == "__main__":
    api = LLMGeneratorAPI()

    test_queries = [
        ("Calculate impermanent loss for 50/50 pool", "defi"),
        ("Value at Risk at 99% confidence", "risk"),
        ("Optimal fee for volatile market", "defi"),
        ("Sortino ratio with 5% target", "risk")
    ]

    for query, domain in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Domain: {domain}")
        print('='*60)

        result = api.generate_formula(query, domain)
        print(json.dumps(result, indent=2))
```

**Test Metrics:**
- Validation rate: % that pass your ensemble validator
- Hallucination rate: % with warnings
- User satisfaction: Does it match intent?

---

# PROTOTYPE C: "Hybrid Discovery" (Your Full System)

## Architecture
```
User description
  → Generate synthetic data from description
  → PySR symbolic regression discovers formula
  → Ensemble validation (4 layers)
  → LLM interprets result
  → Return discovered formula + full metadata
