#!/usr/bin/env python3
"""
Anthropic Claude API Provider for Formula Generation (ENHANCED)
Part of HypatiaX tools/llm_providers/anthropic_provider.py

UPDATES:
- Real API integration with comprehensive error handling
- Exponential backoff retry logic for rate limits
- Structured prompt engineering for better results
- Token usage tracking and optimization
- Response validation and fallback handling
"""
import json
import os
import time
from typing import Any, Dict, List, Optional

import anthropic


class AnthropicProvider:
    """
    Anthropic Claude integration for formula generation with production-ready features.

    Features:
    - Automatic retry with exponential backoff
    - Rate limit handling (429 errors)
    - Token usage tracking
    - Response validation
    - Multiple prompt strategies (primary + fallback)

    Usage:
        provider = AnthropicProvider(api_key="your-key")
        result = provider.generate_formula(requirements="...", domain="defi")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
    ):
        """
        Initialize Anthropic client with configuration.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Model to use (defaults to claude-sonnet-4-20250514)
            max_tokens: Maximum tokens per response
        """
        # Get API key from parameter or environment
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key required. Set ANTHROPIC_API_KEY environment variable "
                    "or pass api_key parameter"
                )

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model or "claude-sonnet-4-20250514"
        self.max_tokens = max_tokens

        # Track usage statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "retry_count": 0,
        }

        print(f"✅ Anthropic Provider initialized")
        print(f"   Model: {self.model}")
        print(f"   Max tokens: {self.max_tokens}")

    def generate_formula(
        self,
        requirements: str,
        domain: str = "defi",
        n_candidates: int = 1,
        max_retries: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Generate analytical formulas using Claude with retry logic.

        Args:
            requirements: Natural language description of what to calculate
            domain: Domain context ("defi", "finance", "esg", "risk")
            n_candidates: Number of formula variants to generate
            max_retries: Maximum retry attempts per request

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
                'limitations': [list],
                'metadata': {usage stats, timing}
            }
        """
        formulas = []

        for i in range(n_candidates):
            print(f"\n🔄 Generating formula variant {i + 1}/{n_candidates}...")

            # Try primary prompt first, then fallback if needed
            for attempt in range(2):
                try:
                    if attempt == 0:
                        prompt = self._build_prompt(requirements, domain, i)
                        prompt_type = "primary"
                    else:
                        prompt = self._build_fallback_prompt(requirements, domain, i)
                        prompt_type = "fallback"

                    print(f"   Using {prompt_type} prompt strategy")

                    # Call API with retry logic
                    start_time = time.time()
                    response = self._call_with_retry(
                        prompt=prompt, max_retries=max_retries
                    )
                    elapsed = time.time() - start_time

                    # Extract content
                    content = response.content[0].text

                    # Parse and validate response
                    formula = self._parse_response(content)

                    # Add metadata
                    formula["metadata"] = {
                        "model": self.model,
                        "prompt_type": prompt_type,
                        "generation_time_seconds": round(elapsed, 2),
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                        "variant": i + 1,
                    }

                    # Update stats
                    self.stats["total_tokens_input"] += response.usage.input_tokens
                    self.stats["total_tokens_output"] += response.usage.output_tokens
                    self.stats["successful_requests"] += 1

                    # Validate that we got a proper formula
                    if self._validate_formula(formula):
                        print(f"   ✅ Generated successfully in {elapsed:.2f}s")
                        formulas.append(formula)
                        break  # Success, exit attempt loop
                    else:
                        if attempt == 0:
                            print(
                                f"   ⚠️  Invalid formula structure, trying fallback..."
                            )
                            continue
                        else:
                            print(f"   ❌ Failed to generate valid formula")
                            formulas.append(
                                self._create_error_formula(
                                    "Invalid formula structure after retry"
                                )
                            )
                            break

                except anthropic.RateLimitError as e:
                    error_msg = f"Rate limit exceeded: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    self.stats["failed_requests"] += 1

                    if attempt == 1:  # Last attempt
                        formulas.append(self._create_error_formula(error_msg))
                        break
                    else:
                        print(f"   🔄 Waiting before retry...")
                        time.sleep(5)

                except anthropic.APIError as e:
                    error_msg = f"API error: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    self.stats["failed_requests"] += 1

                    if attempt == 1:
                        formulas.append(self._create_error_formula(error_msg))
                        break
                    else:
                        print(f"   🔄 Trying fallback prompt...")

                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    self.stats["failed_requests"] += 1

                    if attempt == 1:
                        formulas.append(self._create_error_formula(error_msg))
                        break
                    else:
                        print(f"   🔄 Trying fallback prompt...")

        return formulas

    def _call_with_retry(
        self, prompt: str, max_retries: int = 3
    ) -> anthropic.types.Message:
        """
        Call Claude API with exponential backoff retry logic.

        Handles:
        - Rate limit errors (429)
        - Temporary server errors (5xx)
        - Network timeouts

        Args:
            prompt: The prompt to send
            max_retries: Maximum number of retry attempts

        Returns:
            API response message

        Raises:
            Exception if all retries fail
        """
        self.stats["total_requests"] += 1

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,  # Balanced creativity/consistency
                )
                return response

            except anthropic.RateLimitError as e:
                self.stats["retry_count"] += 1
                if attempt < max_retries - 1:
                    # Exponential backoff: 2, 4, 8 seconds
                    wait_time = 2 ** (attempt + 1)
                    print(
                        f"   ⏳ Rate limit hit. Waiting {wait_time}s (retry {attempt + 2}/{max_retries})..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"   ❌ Rate limit exceeded after {max_retries} attempts")
                    raise

            except anthropic.APIStatusError as e:
                self.stats["retry_count"] += 1
                # Retry on 5xx server errors
                if e.status_code >= 500 and attempt < max_retries - 1:
                    wait_time = 2**attempt  # 1, 2, 4 seconds
                    print(
                        f"   ⏳ Server error ({e.status_code}). Waiting {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    raise

            except anthropic.APIConnectionError as e:
                self.stats["retry_count"] += 1
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    print(f"   ⏳ Connection error. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise

        raise Exception(f"Max retries ({max_retries}) exceeded")

    def _build_prompt(self, requirements: str, domain: str, variant: int) -> str:
        """
        Build primary generation prompt with comprehensive instructions.

        Uses structured prompt engineering for optimal results.
        """
        domain_contexts = {
            "defi": {
                "description": "DeFi protocols, AMMs, liquidity pools, yield farming",
                "examples": "impermanent loss, price impact, liquidity depth",
                "constraints": "Must handle edge cases like zero liquidity, price manipulation",
            },
            "finance": {
                "description": "Portfolio optimization, risk metrics, returns analysis",
                "examples": "Sharpe ratio, VaR, correlation matrices",
                "constraints": "Must handle market volatility, missing data, extreme events",
            },
            "esg": {
                "description": "Environmental, Social, Governance scoring and impact",
                "examples": "carbon footprint, social responsibility scores",
                "constraints": "Must normalize across different reporting standards",
            },
            "risk": {
                "description": "Risk assessment, exposure analysis, stress testing",
                "examples": "Value at Risk, Expected Shortfall, sensitivity analysis",
                "constraints": "Must handle tail events, concentration risk",
            },
        }

        context = domain_contexts.get(
            domain,
            {
                "description": "financial mathematics",
                "examples": "general financial calculations",
                "constraints": "Must be mathematically rigorous",
            },
        )

        return f"""You are a mathematical finance expert specializing in {domain} analytics. Generate a NOVEL, production-ready formula.

<task>
User Requirements: {requirements}
Domain: {domain} - {context['description']}
Variant: {variant + 1} (generate a unique approach)
</task>

<requirements>
1. Mathematical Rigor: Formula must be mathematically sound and well-defined
2. Numerical Stability: Avoid division by near-zero, overflow, underflow
3. Computational Efficiency: Suitable for real-time calculation
4. Novelty: Build on established principles but introduce new insights
5. Domain Constraints: {context['constraints']}
6. Edge Cases: Explicitly handle boundary conditions
</requirements>

<output_format>
Return ONLY valid JSON (no markdown, no explanation outside JSON):
{{
    "formula_latex": "Complete LaTeX notation using standard mathematical symbols",
    "formula_python": "def calculate(param1, param2, ...):
    '''Docstring explaining parameters and return value'''
    # Implementation with proper error handling
    return result",
    "variables": {{
        "var_name": "Clear description with expected range/units"
    }},
    "explanation": "What this formula measures, why it's useful, and key insights",
    "constraints": [
        "Mathematical constraint 1 (e.g., param1 > 0)",
        "Domain constraint 2",
        "Edge case handling"
    ],
    "novelty_score": 7,
    "similar_to": ["Existing formula 1", "Concept 2 it builds upon"],
    "advantages": [
        "Specific advantage over alternatives",
        "Computational benefit",
        "Insight it provides"
    ],
    "limitations": [
        "When this formula may fail",
        "Assumptions that must hold",
        "Edge cases to watch"
    ]
}}
</output_format>

<domain_examples>
Similar {domain} concepts: {context['examples']}
</domain_examples>

Generate a formula that is:
✓ Novel but grounded in established theory
✓ Computationally stable and efficient
✓ Suitable for blockchain/smart contract deployment
✓ Explicitly handles edge cases
✓ Provides actionable insights

Return ONLY the JSON object."""

    def _build_fallback_prompt(
        self, requirements: str, domain: str, variant: int
    ) -> str:
        """
        Build simplified fallback prompt for when primary prompt fails.

        More concise, focused on core requirements.
        """
        return f"""Generate a mathematical formula for {domain} analytics.

Task: {requirements}
Variant: {variant + 1}

Return JSON only:
{{
    "formula_latex": "LaTeX formula",
    "formula_python": "def calculate(...): return ...",
    "variables": {{"name": "description"}},
    "explanation": "What it calculates and why",
    "constraints": ["constraint 1", "constraint 2"],
    "novelty_score": 5,
    "similar_to": ["related concept"],
    "advantages": ["benefit 1", "benefit 2"],
    "limitations": ["limitation 1", "limitation 2"]
}}

Requirements:
- Mathematically rigorous
- Numerically stable
- Production-ready
- Handles edge cases

JSON only, no other text."""

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Extract and validate JSON from API response.

        Handles:
        - Markdown code blocks
        - Extra whitespace
        - Partial JSON
        """
        try:
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Find JSON object in response
            start = content.find("{")
            end = content.rfind("}") + 1

            if start == -1 or end == 0:
                raise ValueError("No JSON object found in response")

            json_str = content[start:end]
            result = json.loads(json_str)

            # Ensure all required fields exist
            required_fields = [
                "formula_latex",
                "formula_python",
                "variables",
                "explanation",
                "novelty_score",
            ]

            for field in required_fields:
                if field not in result or result[field] in [None, "", "N/A"]:
                    result[field] = f"Missing: {field}"

            # Set defaults for optional fields
            result.setdefault("constraints", [])
            result.setdefault("advantages", [])
            result.setdefault("limitations", [])
            result.setdefault("similar_to", [])

            # Normalize novelty score
            if isinstance(result.get("novelty_score"), (int, float)):
                result["novelty_score"] = max(0, min(10, int(result["novelty_score"])))
            else:
                result["novelty_score"] = 5  # Default

            return result

        except json.JSONDecodeError as e:
            return {
                "formula_latex": "JSON parse error",
                "formula_python": "# Failed to parse JSON response",
                "error": f"JSON decode error: {str(e)}",
                "raw_content": content[:1000],  # Limit length
                "variables": {},
                "explanation": "Failed to parse API response as JSON",
                "novelty_score": 0,
            }
        except Exception as e:
            return {
                "formula_latex": "Parse error",
                "formula_python": "# Error parsing response",
                "error": f"Parse error: {str(e)}",
                "raw_content": content[:1000],
                "variables": {},
                "explanation": f"Failed to parse response: {str(e)}",
                "novelty_score": 0,
            }

    def _validate_formula(self, formula: Dict[str, Any]) -> bool:
        """
        Validate that formula dictionary has required structure.

        Returns True if formula is valid, False otherwise.
        """
        if "error" in formula:
            return False

        # Check required fields are not error messages
        required_checks = [
            formula.get("formula_latex", "").lower()
            not in ["parse error", "json parse error", ""],
            formula.get("formula_python", "").lower()
            not in ["# error", "# failed", ""],
            formula.get("explanation", "").lower() not in ["failed", "missing", ""],
            isinstance(formula.get("variables"), dict),
            isinstance(formula.get("novelty_score"), (int, float)),
        ]

        return all(required_checks)

    def _create_error_formula(self, error_message: str) -> Dict[str, Any]:
        """Create an error formula dictionary."""
        return {
            "formula_latex": "Generation failed",
            "formula_python": "# Formula generation failed",
            "error": error_message,
            "variables": {},
            "explanation": f"Failed to generate formula: {error_message}",
            "constraints": [],
            "novelty_score": 0,
            "advantages": [],
            "limitations": ["Generation failed"],
            "similar_to": [],
        }

    def refine_formula(
        self, formula: Dict[str, Any], feedback: str, max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Iteratively improve formula based on user feedback.

        Args:
            formula: Original formula dictionary
            feedback: User feedback on what to improve
            max_retries: Maximum retry attempts

        Returns:
            Refined formula dictionary
        """
        print(f"\n🔄 Refining formula based on feedback...")

        prompt = f"""Improve this mathematical formula based on user feedback.

<original_formula>
LaTeX: {formula.get('formula_latex', 'N/A')}
Python: {formula.get('formula_python', 'N/A')}
Explanation: {formula.get('explanation', 'N/A')}
</original_formula>

<user_feedback>
{feedback}
</user_feedback>

Generate an improved version that addresses the feedback while maintaining mathematical validity.

Return the same JSON structure as before:
{{
    "formula_latex": "improved formula",
    "formula_python": "improved implementation",
    "variables": {{}},
    "explanation": "updated explanation",
    "constraints": [],
    "novelty_score": 5,
    "similar_to": [],
    "advantages": [],
    "limitations": []
}}

Key improvements to make:
1. Address the specific feedback
2. Maintain or improve mathematical rigor
3. Ensure numerical stability
4. Clarify any ambiguities

Return JSON only."""

        try:
            start_time = time.time()
            response = self._call_with_retry(prompt, max_retries=max_retries)
            elapsed = time.time() - start_time

            content = response.content[0].text
            refined_formula = self._parse_response(content)

            # Add refinement metadata
            refined_formula["metadata"] = {
                "refined": True,
                "original_novelty_score": formula.get("novelty_score", 0),
                "refinement_time_seconds": round(elapsed, 2),
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

            # Update stats
            self.stats["total_tokens_input"] += response.usage.input_tokens
            self.stats["total_tokens_output"] += response.usage.output_tokens
            self.stats["successful_requests"] += 1

            print(f"   ✅ Refined successfully in {elapsed:.2f}s")
            return refined_formula

        except Exception as e:
            error_msg = f"Refinement failed: {str(e)}"
            print(f"   ❌ {error_msg}")
            self.stats["failed_requests"] += 1
            return self._create_error_formula(error_msg)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get usage statistics for this provider instance.

        Returns:
            Dictionary with usage stats
        """
        total_tokens = (
            self.stats["total_tokens_input"] + self.stats["total_tokens_output"]
        )
        success_rate = (
            self.stats["successful_requests"] / self.stats["total_requests"] * 100
            if self.stats["total_requests"] > 0
            else 0
        )

        return {
            **self.stats,
            "total_tokens": total_tokens,
            "success_rate_percent": round(success_rate, 1),
            "avg_tokens_per_request": (
                total_tokens / self.stats["total_requests"]
                if self.stats["total_requests"] > 0
                else 0
            ),
        }

    def reset_statistics(self):
        """Reset usage statistics."""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "retry_count": 0,
        }


# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("💡 Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        print("💡 Get your API key from: https://console.anthropic.com/")
        exit(1)

    provider = AnthropicProvider(api_key=api_key)

    print("\n" + "=" * 70)
    print("Testing Anthropic Claude Provider")
    print("=" * 70)

    # Test formula generation
    results = provider.generate_formula(
        requirements="Calculate impermanent loss for Uniswap V2 liquidity pools",
        domain="defi",
        n_candidates=1,
    )

    formula = results[0]

    print("\n" + "=" * 70)
    print("GENERATED FORMULA")
    print("=" * 70)

    if "error" in formula:
        print(f"\n❌ Error: {formula['error']}")
        if "raw_content" in formula:
            print(f"\n📄 Raw response (truncated):\n{formula['raw_content'][:500]}...")
    else:
        print(f"\n📐 Formula: {formula['formula_latex']}")
        print(f"\n💻 Implementation:\n{formula['formula_python']}")
        print(f"\n📝 Explanation: {formula['explanation']}")
        print(f"\n🎯 Novelty Score: {formula['novelty_score']}/10")

        if formula.get("advantages"):
            print(f"\n✅ Advantages:")
            for adv in formula["advantages"]:
                print(f"   • {adv}")

        if formula.get("limitations"):
            print(f"\n⚠️  Limitations:")
            for lim in formula["limitations"]:
                print(f"   • {lim}")

        if formula.get("metadata"):
            meta = formula["metadata"]
            print(f"\n📊 Metadata:")
            print(f"   Model: {meta.get('model')}")
            print(f"   Generation time: {meta.get('generation_time_seconds')}s")
            print(
                f"   Tokens: {meta.get('input_tokens')} in, {meta.get('output_tokens')} out"
            )

    # Show statistics
    print("\n" + "=" * 70)
    print("USAGE STATISTICS")
    print("=" * 70)
    stats = provider.get_statistics()
    print(f"Total requests: {stats['total_requests']}")
    print(f"Successful: {stats['successful_requests']}")
    print(f"Failed: {stats['failed_requests']}")
    print(f"Success rate: {stats['success_rate_percent']}%")
    print(
        f"Total tokens: {stats['total_tokens']} ({stats['total_tokens_input']} in + {stats['total_tokens_output']} out)"
    )
    print(f"Retries: {stats['retry_count']}")

    print("\n✅ Test completed!")

    """
    Anthropic Provider (anthropic_provider.py)
✅ Real API Integration

Full Claude Sonnet 4 integration
Proper error handling for all API exceptions
Token usage tracking

✅ Retry Logic

Exponential backoff (2s, 4s, 8s)
Rate limit detection (429 errors)
Server error handling (5xx)
Connection error recovery

✅ Prompt Strategies

Primary: Comprehensive structured prompt
Fallback: Simplified prompt for edge cases
Validation of formula structure

✅ Usage Tracking

Request counts (total, successful, failed)
Token usage (input/output)
Retry statistics
Success rate calculation

"""
