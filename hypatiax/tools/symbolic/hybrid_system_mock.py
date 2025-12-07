"""
HypatiaX Hybrid Discovery System with Real LLM Integration
Combines symbolic regression, validation, and real LLM interpretation
Version: 2.0 - Real API Integration (Week 2-3 Update)
"""

import asyncio
import json
import logging
import os
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Union

import numpy as np

from hypatiax.tools.llm_providers.llm_interpreter import InterpretationConfig, LLMInterpreter
from hypatiax.tools.symbolic.symbolic_engine import DiscoveryConfig, SymbolicEngine
from hypatiax.tools.validation.ensemble_validator import EnsembleValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Custom exception for LLM provider errors"""

    pass


class HybridDiscoverySystem:
    """
    Integrated system for discovering, validating, and interpreting mathematical formulas.

    NEW in v2.0:
    - Real Anthropic Claude API integration
    - Real Google Gemini API integration
    - Fallback mechanisms between providers
    - Retry logic with exponential backoff
    - Rate limiting support
    - Enhanced error handling

    Workflow:
    1. Discover symbolic expression from data (SymbolicEngine)
    2. Validate expression across multiple layers (EnsembleValidator)
    3. Interpret meaning using real LLM APIs (Claude/Gemini)
    """

    def __init__(
        self,
        domain: str = "defi",
        discovery_config: Optional[DiscoveryConfig] = None,
        interpretation_config: Optional[InterpretationConfig] = None,
        max_results: Optional[int] = 100,
        validation_weights: Optional[Dict[str, float]] = None,
        use_rich_output: bool = True,
        primary_llm: str = "anthropic",  # 'anthropic' or 'google'
        enable_fallback: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the hybrid discovery system with real LLM integration.

        Args:
            domain: Domain context ('defi', 'risk', 'finance', 'esg')
            discovery_config: Configuration for symbolic regression
            interpretation_config: Configuration for LLM interpretation
            max_results: Maximum number of results to keep in memory
            validation_weights: Custom weights for validation layers
            use_rich_output: Enable rich formatted output
            primary_llm: Primary LLM provider ('anthropic' or 'google')
            enable_fallback: Enable fallback to secondary provider on failure
            max_retries: Maximum retry attempts for API calls
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.domain = domain
        self.primary_llm = primary_llm
        self.enable_fallback = enable_fallback
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Initialize components
        self.symbolic_engine = SymbolicEngine(discovery_config or DiscoveryConfig())
        self.llm_interpreter = LLMInterpreter(interpretation_config or InterpretationConfig())
        self.validator = EnsembleValidator(domain=domain, max_history=max_results, weights=validation_weights)

        # Initialize real LLM providers
        self._initialize_llm_providers()

        # Bounded results storage
        self.max_results = max_results
        if max_results is not None:
            self.results = deque(maxlen=max_results)
        else:
            self.results = []

        # Statistics tracking
        self.stats = {
            "anthropic_calls": 0,
            "anthropic_failures": 0,
            "google_calls": 0,
            "google_failures": 0,
            "fallback_count": 0,
            "total_retries": 0,
        }

        # Add formatter
        self.use_rich_output = use_rich_output
        if use_rich_output:
            try:
                from hypatiax.tools.formatters.hybrid_formatter import HybridFormatter

                self.formatter = HybridFormatter()
            except ImportError:
                logger.warning("'rich' not installed. Install with: pip install rich")
                self.formatter = None
        else:
            self.formatter = None

    def _initialize_llm_providers(self):
        """Initialize real LLM API providers with proper authentication."""
        try:
            # Initialize Anthropic Claude
            from anthropic import Anthropic, AsyncAnthropic

            anthropic_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
            if anthropic_key:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                self.anthropic_async_client = AsyncAnthropic(api_key=anthropic_key)
                logger.info("✓ Anthropic Claude API initialized")
            else:
                self.anthropic_client = None
                self.anthropic_async_client = None
                logger.warning("⚠ ANTHROPIC_API_KEY not found. Claude integration disabled.")
        except ImportError:
            self.anthropic_client = None
            self.anthropic_async_client = None
            logger.warning("⚠ Anthropic SDK not installed. Install with: pip install anthropic")

        try:
            # Initialize Google Gemini
            from google import genai

            google_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if google_key:
                self.gemini_client = genai.Client(api_key=google_key)
                logger.info("✓ Google Gemini API initialized")
            else:
                self.gemini_client = None
                logger.warning("⚠ GEMINI_API_KEY not found. Gemini integration disabled.")
        except ImportError:
            self.gemini_client = None
            logger.warning("⚠ Google GenAI SDK not installed. Install with: pip install google-genai")

    def _call_anthropic(
        self, prompt: str, model: str = "claude-sonnet-4-5-20250929", max_tokens: int = 2000, temperature: float = 0.7
    ) -> str:
        """
        Call Anthropic Claude API with retry logic.

        Args:
            prompt: Input prompt
            model: Claude model identifier
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Model response text

        Raises:
            LLMProviderError: If API call fails after retries
        """
        if not self.anthropic_client:
            raise LLMProviderError("Anthropic client not initialized")

        for attempt in range(self.max_retries):
            try:
                self.stats["anthropic_calls"] += 1

                response = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}],
                )

                # Extract text from response
                if response.content and len(response.content) > 0:
                    return response.content[0].text
                else:
                    raise LLMProviderError("Empty response from Claude")

            except Exception as e:
                self.stats["anthropic_failures"] += 1
                logger.warning(f"Claude API attempt {attempt + 1}/{self.max_retries} failed: {str(e)}")

                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay:.1f}s...")
                    asyncio.sleep(delay)
                else:
                    raise LLMProviderError(f"Claude API failed after {self.max_retries} attempts: {str(e)}")

    def _call_gemini(
        self, prompt: str, model: str = "gemini-2.5-flash", max_tokens: int = 2000, temperature: float = 0.7
    ) -> str:
        """
        Call Google Gemini API with retry logic.

        Args:
            prompt: Input prompt
            model: Gemini model identifier
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Model response text

        Raises:
            LLMProviderError: If API call fails after retries
        """
        if not self.gemini_client:
            raise LLMProviderError("Gemini client not initialized")

        for attempt in range(self.max_retries):
            try:
                self.stats["google_calls"] += 1

                response = self.gemini_client.models.generate_content(
                    model=model, contents=prompt, config={"temperature": temperature, "max_output_tokens": max_tokens}
                )

                if response.text:
                    return response.text
                else:
                    raise LLMProviderError("Empty response from Gemini")

            except Exception as e:
                self.stats["google_failures"] += 1
                logger.warning(f"Gemini API attempt {attempt + 1}/{self.max_retries} failed: {str(e)}")

                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay:.1f}s...")
                    asyncio.sleep(delay)
                else:
                    raise LLMProviderError(f"Gemini API failed after {self.max_retries} attempts: {str(e)}")

    def _interpret_with_llm(
        self, expression: str, variables: Dict[str, str], r2: float, context: Optional[Dict] = None
    ) -> Dict:
        """
        Interpret expression using LLM with fallback mechanism.

        Args:
            expression: Mathematical expression
            variables: Variable descriptions
            r2: R² score
            context: Additional context

        Returns:
            Interpretation dictionary
        """
        # Build prompt
        prompt = self._build_interpretation_prompt(expression, variables, r2, context)

        # Determine provider order
        providers = ["anthropic", "google"] if self.primary_llm == "anthropic" else ["google", "anthropic"]

        for i, provider in enumerate(providers):
            try:
                if provider == "anthropic" and self.anthropic_client:
                    logger.info(f"🤖 Calling Claude API...")
                    response = self._call_anthropic(prompt)
                    return self._parse_interpretation(response, provider="claude")

                elif provider == "google" and self.gemini_client:
                    logger.info(f"🤖 Calling Gemini API...")
                    response = self._call_gemini(prompt)
                    return self._parse_interpretation(response, provider="gemini")

            except LLMProviderError as e:
                logger.error(f"❌ {provider.capitalize()} failed: {str(e)}")

                # Try fallback if enabled and this is the primary provider
                if self.enable_fallback and i == 0 and len(providers) > 1:
                    self.stats["fallback_count"] += 1
                    logger.info(f"↩ Falling back to {providers[1]}...")
                    continue
                else:
                    raise

        # If we get here, all providers failed
        raise LLMProviderError("All LLM providers failed")

    def _build_interpretation_prompt(
        self, expression: str, variables: Dict[str, str], r2: float, context: Optional[Dict] = None
    ) -> str:
        """Build structured prompt for LLM interpretation."""
        prompt = f"""You are a mathematical and domain expert analyzing symbolic expressions in the {self.domain} domain.

EXPRESSION: {expression}

VARIABLES:
{chr(10).join(f"- {var}: {desc}" for var, desc in variables.items())}

MODEL QUALITY:
- R² Score: {r2:.4f}

TASK:
Provide a clear, concise interpretation of this expression including:
1. What the formula calculates
2. Relationship between variables
3. Domain-specific insights
4. Potential use cases
5. Any limitations or assumptions

Format your response as JSON with the following structure:
{{
    "interpretation": "Brief summary",
    "relationships": ["Relationship 1", "Relationship 2", ...],
    "insights": ["Insight 1", "Insight 2", ...],
    "use_cases": ["Use case 1", "Use case 2", ...],
    "limitations": ["Limitation 1", "Limitation 2", ...]
}}
"""

        if context:
            prompt += f"\n\nADDITIONAL CONTEXT:\n{json.dumps(context, indent=2)}"

        return prompt

    def _parse_interpretation(self, response: str, provider: str) -> Dict:
        """Parse LLM response into structured interpretation."""
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)
                parsed["provider"] = provider
                parsed["raw_response"] = response
                return parsed
            else:
                # Fallback: return raw response
                return {
                    "interpretation": response,
                    "provider": provider,
                    "raw_response": response,
                    "parse_error": "Could not extract JSON",
                }
        except json.JSONDecodeError:
            return {
                "interpretation": response,
                "provider": provider,
                "raw_response": response,
                "parse_error": "JSON decode error",
            }

    def discover_validate_interpret(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str],
        variable_descriptions: Dict[str, str],
        variable_units: Dict[str, str],
        description: Optional[str] = None,
        validate_first: bool = True,
        show_formatted: bool = True,
        use_llm: bool = True,
    ) -> Dict:
        """
        Complete discovery workflow with validation and real LLM interpretation.

        Args:
            X: Input features (n_samples, n_features)
            y: Target values (n_samples,)
            variable_names: Names of variables
            variable_descriptions: Descriptions of what each variable represents
            variable_units: Unit strings for each variable
            description: Optional description of this discovery run
            validate_first: If True, skip interpretation if validation fails
            show_formatted: If True, display formatted output (requires rich)
            use_llm: If True, use real LLM for interpretation

        Returns:
            Complete result dictionary with discovery, validation, and interpretation
        """
        print(f"\n{'='*70}")
        print(f"WORKFLOW: {description or 'Unnamed Discovery'}")
        print(f"Domain: {self.domain.upper()} | LLM: {self.primary_llm.upper()}")
        print(f"{'='*70}")

        # STAGE 1: DISCOVER
        print(f"\n[1/3] 🔍 Discovering symbolic expression from {len(X)} samples...")
        discovery_result = self.symbolic_engine.discover(X, y, variable_names)

        print(f"✓ Found: {discovery_result['expression']}")
        print(f"  R² Score: {discovery_result['r2_score']:.4f}")
        print(f"  Complexity: {discovery_result['complexity']}")

        # STAGE 2: VALIDATE
        print(f"\n[2/3] ✓ Validating expression across {len(self.validator.weights)} layers...")

        # Prepare test data from input features
        test_data = {name: X[:, i] for i, name in enumerate(variable_names)}

        validation_result = self.validator.validate_complete(
            expression_str=discovery_result["expression"],
            variable_definitions=variable_descriptions,
            variable_units=variable_units,
            test_data=test_data,
        )

        # Display validation results
        valid_symbol = "✓" if validation_result["valid"] else "✗"
        print(f"{valid_symbol} Overall Score: {validation_result['total_score']:.1f}/100")
        print(f"  Layer Scores:")
        for layer, score in validation_result["layer_scores"].items():
            layer_symbol = "✓" if score >= 70 else "⚠" if score >= 50 else "✗"
            print(f"    {layer_symbol} {layer.capitalize()}: {score:.1f}")

        # Show errors if any
        if validation_result.get("errors"):
            print(f"\n  ⚠ Errors ({len(validation_result['errors'])}):")
            for error in validation_result["errors"][:3]:
                print(f"    - {error}")
            if len(validation_result["errors"]) > 3:
                print(f"    ... and {len(validation_result['errors']) - 3} more")

        # Show warnings if any
        if validation_result.get("warnings"):
            print(f"\n  ℹ Warnings ({len(validation_result['warnings'])}):")
            for warning in validation_result["warnings"][:3]:
                print(f"    - {warning}")
            if len(validation_result["warnings"]) > 3:
                print(f"    ... and {len(validation_result['warnings']) - 3} more")

        # STAGE 3: INTERPRET
        interpretation = None

        if (validation_result["valid"] or not validate_first) and use_llm:
            print(f"\n[3/3] 🤖 Interpreting with real LLM API...")
            try:
                interpretation = self._interpret_with_llm(
                    expression=discovery_result["expression"],
                    variables=variable_descriptions,
                    r2=discovery_result["r2_score"],
                    context={"validation": validation_result},
                )
                print(f"✓ Interpretation complete via {interpretation.get('provider', 'unknown').upper()}")

                # Show interpretation summary
                if "interpretation" in interpretation:
                    interp_text = interpretation["interpretation"]
                    if len(interp_text) > 150:
                        print(f"  Summary: {interp_text[:150]}...")
                    else:
                        print(f"  Summary: {interp_text}")

            except Exception as e:
                print(f"✗ Interpretation failed: {str(e)}")
                interpretation = {"error": str(e)}
        elif not use_llm:
            print(f"\n[3/3] ⊗ LLM interpretation disabled")
        else:
            print(f"\n[3/3] ⊗ Interpretation skipped (validation failed)")
            print(f"  Recommendations:")
            for rec in validation_result.get("recommendations", [])[:3]:
                print(f"    • {rec}")

        # Compile complete result
        complete_result = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "domain": self.domain,
            "discovery": discovery_result,
            "validation": validation_result,
            "interpretation": interpretation,
            "metadata": {
                "n_samples": len(X),
                "n_features": X.shape[1],
                "variable_names": variable_names,
                "llm_provider": interpretation.get("provider") if interpretation else None,
            },
        }

        # Store result
        self.results.append(complete_result)

        print(f"\n{'='*70}")
        print(f"Workflow complete. Result stored ({len(self.results)}/{self.max_results or '∞'})")
        print(f"{'='*70}\n")

        # Display formatted output if requested
        if show_formatted and self.formatter:
            print("\n")
            self.formatter.format_result(complete_result)

        return complete_result

    def get_llm_statistics(self) -> Dict:
        """Get statistics about LLM API usage."""
        return {
            "anthropic": {
                "calls": self.stats["anthropic_calls"],
                "failures": self.stats["anthropic_failures"],
                "success_rate": (
                    ((self.stats["anthropic_calls"] - self.stats["anthropic_failures"]) / self.stats["anthropic_calls"])
                    if self.stats["anthropic_calls"] > 0
                    else 0.0
                ),
            },
            "google": {
                "calls": self.stats["google_calls"],
                "failures": self.stats["google_failures"],
                "success_rate": (
                    ((self.stats["google_calls"] - self.stats["google_failures"]) / self.stats["google_calls"])
                    if self.stats["google_calls"] > 0
                    else 0.0
                ),
            },
            "fallback_count": self.stats["fallback_count"],
            "total_retries": self.stats["total_retries"],
        }

    # Keep existing methods from original implementation
    def display_result(self, result: Dict, format: str = "rich"):
        """Display a result in various formats."""
        if format == "rich" and self.formatter:
            self.formatter.format_result(result)
        elif format == "summary" and self.formatter:
            self.formatter.format_result(result, show_full=False)
        elif format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Expression: {result.get('discovery', {}).get('expression')}")
            print(f"R²: {result.get('discovery', {}).get('r2_score'):.4f}")
            print(f"Validation: {result.get('validation', {}).get('total_score'):.1f}/100")

    def compare_all_results(self, top_n: int = 10):
        """Display comparison table of all stored results."""
        if self.formatter:
            self.formatter.compare_results(list(self.results), top_n)
        else:
            print(f"Stored {len(self.results)} results")
            for i, result in enumerate(list(self.results)[-top_n:], 1):
                expr = result.get("discovery", {}).get("expression", "N/A")
                r2 = result.get("discovery", {}).get("r2_score", 0)
                print(f"{i}. {expr[:50]}... | R²={r2:.4f}")

    def clear_results(self):
        """Clear all stored results."""
        if isinstance(self.results, deque):
            self.results.clear()
        else:
            self.results = []
        print("✓ Results cleared")

    def get_results(self, limit: Optional[int] = None) -> List[Dict]:
        """Get stored results."""
        results_list = list(self.results)
        if limit is not None:
            return results_list[-limit:]
        return results_list

    def get_statistics(self) -> Dict:
        """Get complete statistics about discovery runs and LLM usage."""
        if not self.results:
            base_stats = {"total_runs": 0, "valid_count": 0, "average_r2": 0.0, "average_validation_score": 0.0}
        else:
            total = len(self.results)
            valid_count = sum(1 for r in self.results if "validation" in r and r["validation"].get("valid", False))

            r2_scores = [r["discovery"]["r2_score"] for r in self.results if "discovery" in r]
            avg_r2 = sum(r2_scores) / len(r2_scores) if r2_scores else 0.0

            val_scores = [r["validation"]["total_score"] for r in self.results if "validation" in r]
            avg_val = sum(val_scores) / len(val_scores) if val_scores else 0.0

            base_stats = {
                "total_runs": total,
                "valid_count": valid_count,
                "invalid_count": total - valid_count,
                "success_rate": valid_count / total if total > 0 else 0.0,
                "average_r2": avg_r2,
                "average_validation_score": avg_val,
                "domain": self.domain,
            }

        # Add LLM statistics
        base_stats["llm_usage"] = self.get_llm_statistics()

        return base_stats


if __name__ == "__main__":
    # Initialize with real LLM integration
    system = HybridDiscoverySystem(
        domain="defi",
        max_results=50,
        use_rich_output=True,
        primary_llm="anthropic",  # or 'google'
        enable_fallback=True,
    )

    # Generate sample data
    np.random.seed(42)
    X = np.random.uniform(10, 1000, (100, 2))
    y = np.sqrt(X[:, 0] * X[:, 1]) + np.random.normal(0, 5, 100)

    # Run discovery with real LLM
    result = system.discover_validate_interpret(
        X=X,
        y=y,
        variable_names=["reserve0", "reserve1"],
        variable_descriptions={"reserve0": "Token 0 reserves in pool", "reserve1": "Token 1 reserves in pool"},
        variable_units={"reserve0": "dimensionless", "reserve1": "dimensionless"},
        description="AMM Constant Product Formula Discovery",
        show_formatted=True,
        use_llm=True,
    )

    # Get complete statistics
    stats = system.get_statistics()
    print(f"\nSystem Statistics:")
    print(f"  Total runs: {stats['total_runs']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Average R²: {stats['average_r2']:.4f}")
    print(f"  Average validation score: {stats['average_validation_score']:.1f}")
    print(f"\nLLM Statistics:")
    print(f"  Anthropic calls: {stats['llm_usage']['anthropic']['calls']}")
    print(f"  Google calls: {stats['llm_usage']['google']['calls']}")
    print(f"  Fallback count: {stats['llm_usage']['fallback_count']}")
