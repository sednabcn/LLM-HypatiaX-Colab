"""LLM-based expression mapping"""
from typing import Any, Dict, Optional

from tools.llm_providers.base_provider import BaseLLMProvider


class LLMMapper:
    """Map queries using LLM providers"""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider

    def map(self, query: str, use_few_shot: bool = True) -> Dict[str, Any]:
        """Map query to expression using LLM"""
        if not self.llm_provider:
            return {
                'query': query,
                'expression': None,
                'method': 'llm',
                'error': 'No LLM provider configured'
            }

        # Create prompt
        prompt = self._create_prompt(query, use_few_shot)

        # Generate expression
        response = self.llm_provider.generate(prompt)

        return {
            'query': query,
            'expression': response,
            'method': 'llm',
            'provider': self.llm_provider.__class__.__name__
        }

    def _create_prompt(self, query: str, use_few_shot: bool) -> str:
        """Create prompt for LLM"""
        base_prompt = f"Convert the following natural language query to a mathematical expression:

Query: {query}
Expression:"

        if use_few_shot:
            # Add few-shot examples
            examples = """Here are some examples:

Query: Find the integral of x squared
Expression: ∫x² dx

Query: What is the derivative of sine x?
Expression: d/dx[sin(x)]

Query: Solve x squared equals 4
Expression: x² = 4

"""
            return examples + base_prompt

        return base_prompt
