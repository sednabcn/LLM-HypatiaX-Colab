import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from anthropic import Anthropic
from dotenv import load_dotenv


@dataclass
class InterpretationConfig:
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 2000
    temperature: float = 0.3


class LLMInterpreter:
    def __init__(self, config: InterpretationConfig = None):
        load_dotenv()
        self.config = config or InterpretationConfig()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=api_key)
        self.domain_templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        return {
            "defi": """You are interpreting a DISCOVERED analytical expression from DeFi data.
Your role is INTERPRETATION, not generation.

DISCOVERED EXPRESSION: {expression}

Context:
- Domain: Decentralized Finance (DeFi)
- Variables: {variables}
- R² score: {r2:.4f}
- Discovered via symbolic regression
{context}

Provide structured analysis:
1. PHYSICAL INTERPRETATION: What does each term represent?
2. KNOWN ANALOGIES: Similar expressions in literature?
3. NOVEL ASPECTS: What is new or unexpected?
4. PREDICTIONS: What does this expression enable?
5. LIMITATIONS: Under what conditions might it fail?

CRITICAL: Respond with ONLY valid JSON, no markdown code fences, no preamble.
Format as JSON with keys: interpretation, analogies, novelty, predictions, limitations""",
            "risk": """You are interpreting a DISCOVERED analytical expression from Risk Management data.
Your role is INTERPRETATION, not generation.

DISCOVERED EXPRESSION: {expression}

Context:
- Domain: Financial Risk Management
- Variables: {variables}
- R² score: {r2:.4f}
{context}

Provide structured analysis:
1. STATISTICAL INTERPRETATION: What risk measure is this?
2. REGULATORY CONTEXT: Relevant frameworks (Basel III, SR 11-7)?
3. KNOWN FORMULAS: Similar established risk metrics?
4. PRACTICAL USE: How would risk managers apply this?
5. VALIDATION NEEDS: What additional tests required?

CRITICAL: Respond with ONLY valid JSON, no markdown code fences, no preamble.
Format as JSON with keys: interpretation, regulatory, known_formulas, practical_use, validation""",
            "physics": """You are interpreting a DISCOVERED analytical expression from Physics data.
Your role is INTERPRETATION, not generation.

DISCOVERED EXPRESSION: {expression}

Context:
- Domain: Physics
- Variables: {variables}
- R² score: {r2:.4f}
{context}

Provide structured analysis:
1. PHYSICAL MEANING: What physical phenomenon does this describe?
2. DIMENSIONAL ANALYSIS: Are units consistent?
3. KNOWN LAWS: Similar established physics equations?
4. THEORETICAL FOUNDATION: What principles underlie this?
5. EXPERIMENTAL VALIDATION: How could this be tested?

CRITICAL: Respond with ONLY valid JSON, no markdown code fences, no preamble.
Format as JSON with keys: interpretation, dimensions, known_laws, theory, validation""",
            "generic": """You are interpreting a DISCOVERED analytical expression.
Your role is INTERPRETATION, not generation.

DISCOVERED EXPRESSION: {expression}

Context:
- Variables: {variables}
- R² score: {r2:.4f}
{context}

Provide structured analysis:
1. MATHEMATICAL INTERPRETATION: What does this expression compute?
2. COMPONENT ANALYSIS: What does each term contribute?
3. KNOWN PATTERNS: Similar mathematical forms?
4. POTENTIAL APPLICATIONS: Where could this be useful?
5. LIMITATIONS: Under what conditions might it fail?

CRITICAL: Respond with ONLY valid JSON, no markdown code fences, no preamble.
Format as JSON with keys: interpretation, components, patterns, applications, limitations""",
        }

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text that may contain markdown code fences."""
        text = re.sub(r"^```json\s*\n", "", text, flags=re.MULTILINE)
        text = re.sub(r"\n```\s*$", "", text, flags=re.MULTILINE)
        text = text.strip()
        return text

    def interpret(
        self,
        expression: str,
        domain: str,
        variables: Dict,
        r2: float,
        additional_context: Optional[str] = None,
    ) -> Dict:
        """
        Interpret a discovered symbolic expression.

        Args:
            expression: The mathematical expression to interpret
            domain: Domain category ('defi', 'risk', 'physics', 'generic')
            variables: Dictionary mapping variable names to descriptions
            r2: R-squared score of the fit
            additional_context: Optional additional context for the model

        Returns:
            Dictionary containing structured interpretation
        """
        template = self.domain_templates.get(domain, self.domain_templates["generic"])
        var_str = "\n".join([f"  - {k}: {v}" for k, v in variables.items()])

        context_str = ""
        if additional_context:
            context_str = f"\n- Additional context: {additional_context}"

        prompt = template.format(
            expression=expression, variables=var_str, r2=r2, context=context_str
        )

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        try:
            clean_text = self._extract_json(response_text)
            interpretation = json.loads(clean_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}...")
            interpretation = {
                "raw_text": response_text,
                "status": "unparsed",
                "error": str(e),
            }

        interpretation["expression"] = expression
        interpretation["domain"] = domain
        interpretation["r2_score"] = r2
        interpretation["metadata"] = {
            "model": self.config.model,
            "temperature": self.config.temperature,
        }

        return interpretation

    def batch_interpret(self, expressions: List[Dict]) -> List[Dict]:
        """
        Interpret multiple expressions.

        Args:
            expressions: List of dicts with keys: expression, domain, variables, r2

        Returns:
            List of interpretation dictionaries
        """
        results = []
        for expr_data in expressions:
            result = self.interpret(
                expression=expr_data["expression"],
                domain=expr_data.get("domain", "generic"),
                variables=expr_data["variables"],
                r2=expr_data["r2"],
                additional_context=expr_data.get("context"),
            )
            results.append(result)
        return results

    def compare_expressions(
        self,
        expressions: List[str],
        domain: str,
        variables: Dict,
        r2_scores: List[float],
    ) -> Dict:
        """
        Compare multiple candidate expressions.

        Args:
            expressions: List of mathematical expressions
            domain: Domain category
            variables: Variable descriptions (shared across expressions)
            r2_scores: R² scores for each expression

        Returns:
            Comparative analysis dictionary
        """
        expr_list = "\n".join(
            [
                f"{i + 1}. {expr} (R²={r2:.4f})"
                for i, (expr, r2) in enumerate(zip(expressions, r2_scores))
            ]
        )

        var_str = "\n".join([f"  - {k}: {v}" for k, v in variables.items()])

        prompt = f"""You are comparing multiple DISCOVERED expressions from {domain} data.

CANDIDATE EXPRESSIONS:
{expr_list}

Variables: {var_str}

Compare these expressions on:
1. INTERPRETABILITY: Which is most intuitive?
2. COMPLEXITY: Which balances accuracy vs simplicity?
3. ROBUSTNESS: Which is likely most stable?
4. APPLICABILITY: Which has broader use cases?
5. RECOMMENDATION: Which would you choose and why?

CRITICAL: Respond with ONLY valid JSON, no markdown code fences.
Format as JSON with keys: interpretability, complexity, robustness, applicability, recommendation"""

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        try:
            clean_text = self._extract_json(response_text)
            comparison = json.loads(clean_text)
        except json.JSONDecodeError:
            comparison = {"raw_text": response_text, "status": "unparsed"}

        comparison["expressions"] = expressions
        comparison["r2_scores"] = r2_scores
        comparison["domain"] = domain

        return comparison


if __name__ == "__main__":
    interpreter = LLMInterpreter()

    # Single interpretation
    print("=== Single Interpretation ===")
    result = interpreter.interpret(
        expression="2*sqrt(price_ratio)/(price_ratio + 1) - 1",
        domain="defi",
        variables={"price_ratio": "Current price / Initial price"},
        r2=0.98,
        additional_context="Discovered from Uniswap V2 pool data",
    )
    print(json.dumps(result, indent=2))

    # Batch interpretation
    print("\n=== Batch Interpretation ===")
    expressions = [
        {
            "expression": "log(volume) * sqrt(liquidity)",
            "domain": "defi",
            "variables": {
                "volume": "24h trading volume",
                "liquidity": "Total pool liquidity",
            },
            "r2": 0.92,
        },
        {
            "expression": "volatility^2 / (1 + price_impact)",
            "domain": "risk",
            "variables": {
                "volatility": "Historical volatility",
                "price_impact": "Slippage per unit volume",
            },
            "r2": 0.87,
        },
    ]
    batch_results = interpreter.batch_interpret(expressions)
    print(f"Interpreted {len(batch_results)} expressions")

    # Compare expressions
    print("\n=== Expression Comparison ===")
    comparison = interpreter.compare_expressions(
        expressions=[
            "2*sqrt(price_ratio)/(price_ratio + 1) - 1",
            "log(price_ratio)",
            "(price_ratio - 1)/sqrt(price_ratio)",
        ],
        domain="defi",
        variables={"price_ratio": "Current price / Initial price"},
        r2_scores=[0.98, 0.85, 0.91],
    )
    print(json.dumps(comparison, indent=2, ensure_ascii=False))

    # =========================================================
    # GUIDE USAGE
    # =========================================================
    """
    Key Enhancements Added:

Additional Domain Templates - Added physics and generic domains for broader applicability
additional_context Parameter - Allow passing dataset-specific context (e.g., "Discovered from Uniswap V2 pool data")
batch_interpret() - Process multiple expressions efficiently
compare_expressions() - Compare candidate expressions side-by-side to help choose the best one
Enhanced Metadata - Track model and temperature settings in results
Better Error Messages - More informative debugging output

Usage Examples:
python# With additional context
result = interpreter.interpret(
    expression="your_expr",
    domain="defi",
    variables={...},
    r2=0.95,
    additional_context="Trained on bear market data 2022-2023"
)

# Compare multiple candidates from symbolic regression
comparison = interpreter.compare_expressions(
    expressions=["expr1", "expr2", "expr3"],
    domain="defi",
    variables={...},
    r2_scores=[0.98, 0.95, 0.97]
)
This gives you a complete toolkit for interpreting discovered expressions in your symbolic regression pipeline!
    """
