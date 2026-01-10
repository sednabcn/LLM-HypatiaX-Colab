"""
HypatiaX Hybrid Discovery System with Real LLM Integration (ENHANCED)
Combines symbolic regression, validation, and real LLM interpretation
Version: 3.0 - Production-Ready API Integration

UPDATES:
- Direct integration with enhanced AnthropicProvider and GoogleProvider
- Removed all mock implementations
- Comprehensive fallback mechanisms
- Enhanced retry logic with backoff
- Real symbolic engine integration
- Production-ready error handling
"""

import json
import logging
import os
import time
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from dotenv import load_dotenv

from hypatiax.tools.llm_providers.anthropic_provider import AnthropicProvider
from hypatiax.tools.llm_providers.google_provider import GoogleProvider
from hypatiax.tools.symbolic.symbolic_engine import DiscoveryConfig, SymbolicEngine
from hypatiax.tools.validation.ensemble_validator import EnsembleValidator

# Configure logging
load_dotenv("/home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/.env")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Custom exception for LLM provider errors"""

    pass


class HybridDiscoverySystem:
    """
    Integrated system for discovering, validating, and interpreting mathematical formulas.

    NEW in v3.0:
    - Direct integration with production AnthropicProvider and GoogleProvider
    - No mock implementations - all real API calls
    - Enhanced fallback mechanisms with intelligent provider selection
    - Comprehensive retry logic with exponential backoff
    - Rate limiting awareness
    - Token usage tracking
    - Detailed statistics and monitoring

    Workflow:
    1. Discover symbolic expression from data (SymbolicEngine)
    2. Validate expression across multiple layers (EnsembleValidator)
    3. Interpret meaning using real LLM APIs (Claude/Gemini)
    """

    def __init__(
        self,
        domain: str = "defi",
        discovery_config: Optional[DiscoveryConfig] = None,
        max_results: Optional[int] = 100,
        validation_weights: Optional[Dict[str, float]] = None,
        use_rich_output: bool = True,
        primary_llm: str = "anthropic",  # 'anthropic' or 'google'
        enable_fallback: bool = True,
        max_retries: int = 3,
        anthropic_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
    ):
        """
        Initialize the hybrid discovery system with real LLM integration.

        Args:
            domain: Domain context ('defi', 'risk', 'finance', 'esg')
            discovery_config: Configuration for symbolic regression
            max_results: Maximum number of results to keep in memory
            validation_weights: Custom weights for validation layers
            use_rich_output: Enable rich formatted output
            primary_llm: Primary LLM provider ('anthropic' or 'google')
            enable_fallback: Enable fallback to secondary provider on failure
            max_retries: Maximum retry attempts for API calls
            anthropic_api_key: Anthropic API key (or use ANTHROPIC_API_KEY env)
            google_api_key: Google API key (or use GOOGLE_API_KEY env)
        """
        self.domain = domain
        self.primary_llm = primary_llm
        self.enable_fallback = enable_fallback
        self.max_retries = max_retries

        logger.info(f"Initializing HybridDiscoverySystem v3.0")
        logger.info(
            f"Domain: {domain} | Primary LLM: {primary_llm} | Fallback: {enable_fallback}"
        )

        # Initialize symbolic engine
        logger.info("Initializing symbolic engine...")
        self.symbolic_engine = SymbolicEngine(discovery_config or DiscoveryConfig())

        # Initialize validator
        logger.info(f"Initializing ensemble validator (domain={domain})...")
        self.validator = EnsembleValidator(
            domain=domain, max_history=max_results, weights=validation_weights
        )

        # Initialize real LLM providers
        logger.info("Initializing LLM providers...")
        self._initialize_llm_providers(anthropic_api_key, google_api_key)

        # Bounded results storage
        self.max_results = max_results
        if max_results is not None:
            self.results = deque(maxlen=max_results)
        else:
            self.results = []

        # Enhanced statistics tracking
        self.stats = {
            "anthropic_calls": 0,
            "anthropic_successes": 0,
            "anthropic_failures": 0,
            "google_calls": 0,
            "google_successes": 0,
            "google_failures": 0,
            "fallback_count": 0,
            "total_retries": 0,
            "discoveries": 0,
            "validations": 0,
            "interpretations": 0,
        }

        # Add formatter
        self.use_rich_output = use_rich_output
        if use_rich_output:
            try:
                from hypatiax.tools.formatters.hybrid_formatter import HybridFormatter

                self.formatter = HybridFormatter()
                logger.info("Rich output formatter enabled")
            except ImportError:
                logger.warning("'rich' not installed. Install with: pip install rich")
                self.formatter = None
        else:
            self.formatter = None

        logger.info("✅ HybridDiscoverySystem initialized successfully")

    def _initialize_llm_providers(
        self, anthropic_api_key: Optional[str], google_api_key: Optional[str]
    ):
        """
        Initialize production LLM providers with proper authentication.

        Uses enhanced AnthropicProvider and GoogleProvider with:
        - Built-in retry logic
        - Rate limiting handling
        - Token usage tracking
        - Comprehensive error handling
        """
        # Initialize Anthropic Claude
        try:
            api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_provider = AnthropicProvider(
                    api_key=api_key, max_tokens=4096
                )
                logger.info("✅ Anthropic Claude provider initialized")
            else:
                self.anthropic_provider = None
                logger.warning("⚠️  ANTHROPIC_API_KEY not found - Claude disabled")
        except Exception as e:
            self.anthropic_provider = None
            logger.error(f"❌ Failed to initialize Anthropic: {e}")

        # Initialize Google Gemini
        try:
            api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.google_provider = GoogleProvider(
                    api_key=api_key, max_output_tokens=8192
                )
                logger.info("✅ Google Gemini provider initialized")
            else:
                self.google_provider = None
                logger.warning("⚠️  GOOGLE_API_KEY not found - Gemini disabled")
        except Exception as e:
            self.google_provider = None
            logger.error(f"❌ Failed to initialize Google: {e}")

        # Validate at least one provider is available
        if not self.anthropic_provider and not self.google_provider:
            raise ValueError(
                "No LLM providers available. Set ANTHROPIC_API_KEY or GOOGLE_API_KEY.\n"
                "Get keys from:\n"
                "  - Anthropic: https://console.anthropic.com/\n"
                "  - Google: https://aistudio.google.com/"
            )

        # Adjust primary_llm if provider not available
        if self.primary_llm == "anthropic" and not self.anthropic_provider:
            if self.google_provider:
                logger.warning(
                    "⚠️  Anthropic unavailable, switching to Google as primary"
                )
                self.primary_llm = "google"
            else:
                raise ValueError(
                    "Primary LLM 'anthropic' not available and no fallback"
                )

        if self.primary_llm == "google" and not self.google_provider:
            if self.anthropic_provider:
                logger.warning(
                    "⚠️  Google unavailable, switching to Anthropic as primary"
                )
                self.primary_llm = "anthropic"
            else:
                raise ValueError("Primary LLM 'google' not available and no fallback")

    def _interpret_with_llm(
        self,
        expression: str,
        variables: Dict[str, str],
        r2: float,
        validation_result: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Interpret expression using LLM with intelligent fallback.

        Uses the enhanced providers with built-in retry logic.
        Implements smart fallback between providers.

        Args:
            expression: Mathematical expression
            variables: Variable descriptions
            r2: R² score
            validation_result: Validation results
            context: Additional context

        Returns:
            Interpretation dictionary with provider metadata
        """
        # Build structured prompt
        prompt = self._build_interpretation_prompt(
            expression, variables, r2, validation_result, context
        )

        # Determine provider order
        if self.primary_llm == "anthropic" and self.anthropic_provider:
            providers = [
                ("anthropic", self.anthropic_provider),
                (
                    ("google", self.google_provider)
                    if self.enable_fallback
                    else (None, None)
                ),
            ]
        else:
            providers = [
                ("google", self.google_provider),
                (
                    ("anthropic", self.anthropic_provider)
                    if self.enable_fallback
                    else (None, None)
                ),
            ]

        # Filter out None providers
        providers = [(name, prov) for name, prov in providers if prov is not None]

        last_error = None

        for i, (provider_name, provider) in enumerate(providers):
            try:
                logger.info(f"🤖 Interpreting with {provider_name.upper()}...")

                # Track call
                if provider_name == "anthropic":
                    self.stats["anthropic_calls"] += 1
                else:
                    self.stats["google_calls"] += 1

                # Call provider's generate_formula method adapted for interpretation
                start_time = time.time()

                # Use provider's infrastructure but adapt prompt
                if provider_name == "anthropic":
                    response = provider._call_with_retry(
                        prompt=prompt, max_retries=self.max_retries
                    )
                    content = response.content[0].text

                    # Update provider stats
                    provider.stats["total_tokens_input"] += response.usage.input_tokens
                    provider.stats["total_tokens_output"] += (
                        response.usage.output_tokens
                    )

                else:  # google
                    response = provider._call_with_retry(
                        prompt=prompt, max_retries=self.max_retries
                    )
                    content = response.text

                elapsed = time.time() - start_time

                # Parse interpretation
                interpretation = self._parse_interpretation(content, provider_name)

                # Add metadata
                interpretation["metadata"] = {
                    "provider": provider_name,
                    "generation_time_seconds": round(elapsed, 2),
                    "attempt": i + 1,
                    "fallback_used": i > 0,
                }

                # Track success
                if provider_name == "anthropic":
                    self.stats["anthropic_successes"] += 1
                else:
                    self.stats["google_successes"] += 1

                self.stats["interpretations"] += 1

                logger.info(
                    f"✅ Interpretation completed via {provider_name.upper()} in {elapsed:.2f}s"
                )
                return interpretation

            except Exception as e:
                last_error = e
                error_msg = str(e)

                # Track failure
                if provider_name == "anthropic":
                    self.stats["anthropic_failures"] += 1
                else:
                    self.stats["google_failures"] += 1

                logger.error(
                    f"❌ {provider_name.upper()} interpretation failed: {error_msg[:100]}"
                )

                # If fallback enabled and not last provider
                if self.enable_fallback and i < len(providers) - 1:
                    self.stats["fallback_count"] += 1
                    next_provider = providers[i + 1][0]
                    logger.info(f"↩️  Falling back to {next_provider.upper()}...")
                    continue
                else:
                    # Last provider or no fallback
                    raise LLMProviderError(f"Interpretation failed: {error_msg}")

        # If we get here, all providers failed
        raise LLMProviderError(f"All LLM providers failed. Last error: {last_error}")

    def _build_interpretation_prompt(
        self,
        expression: str,
        variables: Dict[str, str],
        r2: float,
        validation_result: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        """Build structured prompt for LLM interpretation."""

        # Build validation summary
        validation_summary = ""
        if validation_result:
            validation_summary = f"""
VALIDATION RESULTS:
- Overall Score: {validation_result.get("total_score", 0):.1f}/100
- Valid: {"Yes" if validation_result.get("valid") else "No"}
- Layer Scores:
{chr(10).join(f"  - {k.capitalize()}: {v:.1f}" for k, v in validation_result.get("layer_scores", {}).items())}
"""
            if validation_result.get("errors"):
                validation_summary += (
                    f"\n- Errors: {len(validation_result['errors'])} detected"
                )
            if validation_result.get("warnings"):
                validation_summary += (
                    f"\n- Warnings: {len(validation_result['warnings'])} detected"
                )

        prompt = f"""You are a mathematical finance expert analyzing a discovered symbolic expression in the {self.domain} domain.

DISCOVERED EXPRESSION:
{expression}

VARIABLES:
{chr(10).join(f"- {var}: {desc}" for var, desc in variables.items())}

MODEL FIT QUALITY:
- R² Score: {r2:.4f} {"(excellent fit)" if r2 > 0.95 else "(good fit)" if r2 > 0.85 else "(moderate fit)"}
{validation_summary}

YOUR TASK:
Provide a comprehensive interpretation of this mathematical expression including:

1. **What it calculates**: Brief summary of the expression's purpose
2. **Mathematical relationships**: How variables interact and what operations reveal
3. **Domain insights**: Specific relevance to {self.domain} (e.g., financial metrics, risk factors, market dynamics)
4. **Practical use cases**: Where and how this formula could be applied
5. **Limitations & assumptions**: What conditions must hold, edge cases to consider

Return ONLY valid JSON with this structure:
{{
    "interpretation": "1-2 sentence summary of what this calculates",
    "relationships": [
        "Description of key relationship 1",
        "Description of key relationship 2",
        "..."
    ],
    "domain_insights": [
        "Specific insight about {self.domain} application 1",
        "Specific insight about {self.domain} application 2",
        "..."
    ],
    "use_cases": [
        "Practical use case 1",
        "Practical use case 2",
        "..."
    ],
    "limitations": [
        "Limitation or assumption 1",
        "Edge case or constraint 2",
        "..."
    ],
    "formula_name": "Suggested name for this formula"
}}

Focus on being concrete and actionable. Reference specific {self.domain} concepts where relevant.
Return only the JSON object, no other text."""

        if context:
            prompt += f"\n\nADDITIONAL CONTEXT:\n{json.dumps(context, indent=2)}"

        return prompt

    def _parse_interpretation(self, response: str, provider: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured interpretation.

        Handles various response formats and extracts JSON.
        """
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # Extract JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)

                # Ensure required fields
                required_fields = [
                    "interpretation",
                    "relationships",
                    "use_cases",
                    "limitations",
                ]
                for field in required_fields:
                    if field not in parsed:
                        parsed[field] = []

                parsed["provider"] = provider
                parsed["raw_response"] = response
                parsed["parse_success"] = True

                return parsed
            else:
                # Fallback: return structured error
                return {
                    "interpretation": response[:500],  # First 500 chars
                    "relationships": [],
                    "domain_insights": [],
                    "use_cases": [],
                    "limitations": [
                        "Parse error: Could not extract JSON from response"
                    ],
                    "provider": provider,
                    "raw_response": response,
                    "parse_success": False,
                    "parse_error": "No JSON object found in response",
                }

        except json.JSONDecodeError as e:
            return {
                "interpretation": response[:500],
                "relationships": [],
                "domain_insights": [],
                "use_cases": [],
                "limitations": [f"Parse error: {str(e)}"],
                "provider": provider,
                "raw_response": response,
                "parse_success": False,
                "parse_error": f"JSON decode error: {str(e)}",
            }
        except Exception as e:
            return {
                "interpretation": "Failed to parse interpretation",
                "relationships": [],
                "domain_insights": [],
                "use_cases": [],
                "limitations": [f"Unexpected error: {str(e)}"],
                "provider": provider,
                "raw_response": response[:500],
                "parse_success": False,
                "parse_error": str(e),
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
        min_validation_score: float = 85.0,
    ) -> Dict[str, Any]:
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
            min_validation_score: Minimum validation score to proceed with interpretation

        Returns:
            Complete result dictionary with discovery, validation, and interpretation
        """
        print(f"\n{'=' * 70}")
        print(f"WORKFLOW: {description or 'Unnamed Discovery'}")
        print(
            f"Domain: {self.domain.upper()} | Primary LLM: {self.primary_llm.upper()}"
        )
        print(f"Fallback: {'Enabled' if self.enable_fallback else 'Disabled'}")
        print(f"{'=' * 70}")

        # STAGE 1: DISCOVER
        print(f"\n[1/3] 🔍 Discovering symbolic expression from {len(X)} samples...")

        try:
            discovery_result = self.symbolic_engine.discover(X, y, variable_names)
            self.stats["discoveries"] += 1

            print(f"✅ Found: {discovery_result['expression']}")
            print(f"   R² Score: {discovery_result['r2_score']:.4f}")
            print(f"   Complexity: {discovery_result['complexity']}")

        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            return {
                "error": "discovery_failed",
                "message": str(e),
                "stage": "discovery",
            }

        # STAGE 2: VALIDATE
        print(
            f"\n[2/3] ✓ Validating expression across {len(self.validator.weights)} layers..."
        )

        try:
            # Prepare test data from input features
            test_data = {name: X[:, i] for i, name in enumerate(variable_names)}

            validation_result = self.validator.validate_complete(
                expression_str=discovery_result["expression"],
                variable_definitions=variable_descriptions,
                variable_units=variable_units,
                test_data=test_data,
            )

            self.stats["validations"] += 1

            # Display validation results
            valid_symbol = "✓" if validation_result["valid"] else "✗"
            print(
                f"{valid_symbol} Overall Score: {validation_result['total_score']:.1f}/100"
            )
            print(f"   Layer Scores:")
            for layer, score in validation_result["layer_scores"].items():
                layer_symbol = "✓" if score >= 70 else "⚠" if score >= 50 else "✗"
                print(f"     {layer_symbol} {layer.capitalize()}: {score:.1f}")

            # Show errors/warnings summary
            if validation_result.get("errors"):
                print(f"\n   ⚠ Errors: {len(validation_result['errors'])} detected")
                for error in validation_result["errors"][:2]:
                    print(f"     - {error}")
                if len(validation_result["errors"]) > 2:
                    print(f"     ... and {len(validation_result['errors']) - 2} more")

            if validation_result.get("warnings"):
                print(f"\n   ℹ Warnings: {len(validation_result['warnings'])}")

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            validation_result = {"valid": False, "total_score": 0.0, "error": str(e)}

        # STAGE 3: INTERPRET
        interpretation = None

        should_interpret = (
            use_llm
            and (validation_result.get("valid", False) or not validate_first)
            and validation_result.get("total_score", 0) >= min_validation_score
        )

        if should_interpret:
            print(f"\n[3/3] 🤖 Interpreting with real LLM API...")
            try:
                interpretation = self._interpret_with_llm(
                    expression=discovery_result["expression"],
                    variables=variable_descriptions,
                    r2=discovery_result["r2_score"],
                    validation_result=validation_result,
                )

                provider_used = interpretation.get("metadata", {}).get(
                    "provider", "unknown"
                )
                print(f"✅ Interpretation complete via {provider_used.upper()}")

                # Show interpretation summary
                if interpretation.get("interpretation"):
                    interp_text = interpretation["interpretation"]
                    if len(interp_text) > 150:
                        print(f"   Summary: {interp_text[:150]}...")
                    else:
                        print(f"   Summary: {interp_text}")

                if interpretation.get("formula_name"):
                    print(f"   Suggested name: {interpretation['formula_name']}")

            except Exception as e:
                logger.error(f"Interpretation failed: {e}")
                interpretation = {
                    "error": str(e),
                    "interpretation": "Interpretation failed",
                    "relationships": [],
                    "use_cases": [],
                    "limitations": [str(e)],
                }
        elif not use_llm:
            print(f"\n[3/3] ⊗ LLM interpretation disabled")
        elif validation_result.get("total_score", 0) < min_validation_score:
            print(
                f"\n[3/3] ⊗ Interpretation skipped (score {validation_result.get('total_score', 0):.1f} < {min_validation_score})"
            )
            print(f"   Top recommendations:")
            for rec in validation_result.get("recommendations", [])[:3]:
                print(f"     • {rec}")
        else:
            print(f"\n[3/3] ⊗ Interpretation skipped (validation failed)")

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
                "llm_provider": (
                    interpretation.get("metadata", {}).get("provider")
                    if interpretation
                    else None
                ),
                "primary_llm": self.primary_llm,
                "fallback_enabled": self.enable_fallback,
            },
        }

        # Store result
        self.results.append(complete_result)

        print(f"\n{'=' * 70}")
        print(
            f"✅ Workflow complete. Result stored ({len(self.results)}/{self.max_results or '∞'})"
        )
        print(f"{'=' * 70}\n")

        # Display formatted output if requested
        if show_formatted and self.formatter and interpretation:
            print("\n")
            self.formatter.format_result(complete_result)

        return complete_result

    def get_llm_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about LLM API usage.

        Includes provider-specific stats and overall metrics.
        """

        def calc_rate(success, total):
            return (success / total * 100) if total > 0 else 0.0

        anthropic_total = self.stats["anthropic_calls"]
        anthropic_success = self.stats["anthropic_successes"]
        google_total = self.stats["google_calls"]
        google_success = self.stats["google_successes"]

        stats = {
            "anthropic": {
                "calls": anthropic_total,
                "successes": anthropic_success,
                "failures": self.stats["anthropic_failures"],
                "success_rate_percent": calc_rate(anthropic_success, anthropic_total),
                "available": self.anthropic_provider is not None,
            },
            "google": {
                "calls": google_total,
                "successes": google_success,
                "failures": self.stats["google_failures"],
                "success_rate_percent": calc_rate(google_success, google_total),
                "available": self.google_provider is not None,
            },
            "total_interpretations": self.stats["interpretations"],
            "fallback_count": self.stats["fallback_count"],
            "total_retries": self.stats["total_retries"],
            "primary_provider": self.primary_llm,
            "fallback_enabled": self.enable_fallback,
        }

        # Add provider-specific statistics if available
        if self.anthropic_provider:
            stats["anthropic"]["provider_stats"] = (
                self.anthropic_provider.get_statistics()
            )

        if self.google_provider:
            stats["google"]["provider_stats"] = self.google_provider.get_statistics()

        return stats

    # Results management methods

    def display_result(self, result: Dict, format: str = "rich"):
        """Display a result in various formats."""
        if format == "rich" and self.formatter:
            self.formatter.format_result(result)
        elif format == "summary" and self.formatter:
            self.formatter.format_result(result, show_full=False)
        elif format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            # Simple text format
            print(f"Expression: {result.get('discovery', {}).get('expression', 'N/A')}")
            print(f"R²: {result.get('discovery', {}).get('r2_score', 0):.4f}")
            print(
                f"Validation: {result.get('validation', {}).get('total_score', 0):.1f}/100"
            )
            if result.get("interpretation"):
                print(
                    f"Interpretation: {result['interpretation'].get('interpretation', 'N/A')}"
                )

    def compare_all_results(self, top_n: int = 10):
        """Display comparison table of all stored results."""
        if self.formatter:
            self.formatter.compare_results(list(self.results), top_n)
        else:
            print(f"\nStored Results ({len(self.results)}):")
            print(f"{'=' * 70}")
            for i, result in enumerate(list(self.results)[-top_n:], 1):
                expr = result.get("discovery", {}).get("expression", "N/A")
                r2 = result.get("discovery", {}).get("r2_score", 0)
                val_score = result.get("validation", {}).get("total_score", 0)
                valid = "✓" if result.get("validation", {}).get("valid") else "✗"
                print(
                    f"{i:2d}. {valid} {expr[:40]:40s} | R²={r2:.4f} | Val={val_score:.1f}"
                )

    def clear_results(self):
        """Clear all stored results."""
        if isinstance(self.results, deque):
            self.results.clear()
        else:
            self.results = []
        logger.info("Results cleared")
        print("✅ Results cleared")

    def get_results(self, limit: Optional[int] = None) -> List[Dict]:
        """Get stored results."""
        results_list = list(self.results)
        if limit is not None:
            return results_list[-limit:]
        return results_list

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get complete statistics about discovery runs, validation, and LLM usage.

        Returns comprehensive metrics for monitoring system performance.
        """
        if not self.results:
            base_stats = {
                "total_runs": 0,
                "valid_count": 0,
                "invalid_count": 0,
                "success_rate": 0.0,
                "average_r2": 0.0,
                "average_validation_score": 0.0,
            }
        else:
            total = len(self.results)
            valid_count = sum(
                1 for r in self.results if r.get("validation", {}).get("valid", False)
            )

            r2_scores = [
                r["discovery"]["r2_score"]
                for r in self.results
                if "discovery" in r and "r2_score" in r["discovery"]
            ]
            avg_r2 = sum(r2_scores) / len(r2_scores) if r2_scores else 0.0

            val_scores = [
                r["validation"]["total_score"]
                for r in self.results
                if "validation" in r and "total_score" in r["validation"]
            ]
            avg_val = sum(val_scores) / len(val_scores) if val_scores else 0.0

            base_stats = {
                "total_runs": total,
                "valid_count": valid_count,
                "invalid_count": total - valid_count,
                "success_rate": valid_count / total if total > 0 else 0.0,
                "average_r2": avg_r2,
                "average_validation_score": avg_val,
                "domain": self.domain,
                "max_results_capacity": self.max_results,
            }

        # Add component statistics
        base_stats["discoveries"] = self.stats["discoveries"]
        base_stats["validations"] = self.stats["validations"]
        base_stats["interpretations"] = self.stats["interpretations"]

        # Add LLM usage statistics
        base_stats["llm_usage"] = self.get_llm_statistics()

        # Add validation statistics
        base_stats["validation_stats"] = self.validator.get_statistics()

        return base_stats

    def export_results(
        self, filepath: str, format: str = "json", include_metadata: bool = True
    ):
        """
        Export results to file.

        Args:
            filepath: Output file path
            format: Export format ('json', 'csv')
            include_metadata: Include full metadata in export
        """
        results_list = list(self.results)

        if format == "json":
            export_data = {
                "metadata": {
                    "domain": self.domain,
                    "primary_llm": self.primary_llm,
                    "export_timestamp": datetime.now().isoformat(),
                    "total_results": len(results_list),
                },
                "statistics": self.get_statistics() if include_metadata else {},
                "results": results_list,
            }

            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Exported {len(results_list)} results to {filepath}")
            print(f"✅ Exported {len(results_list)} results to {filepath}")

        elif format == "csv":
            import csv

            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(
                    [
                        "Timestamp",
                        "Expression",
                        "R² Score",
                        "Complexity",
                        "Validation Score",
                        "Valid",
                        "Interpretation",
                        "Provider",
                        "Domain",
                    ]
                )

                # Rows
                for result in results_list:
                    writer.writerow(
                        [
                            result.get("timestamp", ""),
                            result.get("discovery", {}).get("expression", ""),
                            result.get("discovery", {}).get("r2_score", 0),
                            result.get("discovery", {}).get("complexity", 0),
                            result.get("validation", {}).get("total_score", 0),
                            result.get("validation", {}).get("valid", False),
                            (result.get("interpretation") or {}).get(
                                "interpretation", ""
                            )[:100],
                            result.get("metadata", {}).get("llm_provider", ""),
                            self.domain,
                        ]
                    )

            logger.info(f"Exported {len(results_list)} results to {filepath}")
            print(f"✅ Exported {len(results_list)} results to {filepath}")

        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'")

    def print_statistics_summary(self):
        """Print a formatted summary of system statistics."""
        stats = self.get_statistics()

        print(f"\n{'=' * 70}")
        print("SYSTEM STATISTICS SUMMARY")
        print(f"{'=' * 70}")

        print(f"\n📊 Discovery Performance:")
        print(f"   Total runs: {stats['total_runs']}")
        print(f"   Valid: {stats['valid_count']} | Invalid: {stats['invalid_count']}")
        print(f"   Success rate: {stats['success_rate']:.1%}")
        print(f"   Average R²: {stats['average_r2']:.4f}")
        print(f"   Average validation score: {stats['average_validation_score']:.1f}")

        print(f"\n🤖 LLM Usage:")
        llm_stats = stats["llm_usage"]
        print(f"   Primary provider: {llm_stats['primary_provider'].upper()}")
        print(f"   Total interpretations: {llm_stats['total_interpretations']}")
        print(f"   Fallback count: {llm_stats['fallback_count']}")

        if llm_stats["anthropic"]["available"]:
            anth = llm_stats["anthropic"]
            print(f"\n   Anthropic Claude:")
            print(
                f"     Calls: {anth['calls']} | Success: {anth['successes']} | Failed: {anth['failures']}"
            )
            print(f"     Success rate: {anth['success_rate_percent']:.1f}%")

        if llm_stats["google"]["available"]:
            goog = llm_stats["google"]
            print(f"\n   Google Gemini:")
            print(
                f"     Calls: {goog['calls']} | Success: {goog['successes']} | Failed: {goog['failures']}"
            )
            print(f"     Success rate: {goog['success_rate_percent']:.1f}%")

        print(f"\n✓ Validation:")
        val_stats = stats["validation_stats"]
        print(f"   Total validations: {val_stats['total_validations']}")
        print(f"   Success rate: {val_stats['success_rate']:.1%}")
        print(f"   Average score: {val_stats['average_total_score']:.1f}")
        print(f"   Weakest layer: {val_stats.get('weakest_layer', 'N/A')}")

        print(f"\n{'=' * 70}\n")


# Example usage and testing
if __name__ == "__main__":
    # Check for API keys
    import sys

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    if not anthropic_key and not google_key:
        print("❌ No LLM API keys found!")
        print("\nSet at least one of:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        print("  export GOOGLE_API_KEY='your-key-here'")
        print("\nGet keys from:")
        print("  - Anthropic: https://console.anthropic.com/")
        print("  - Google: https://aistudio.google.com/")
        sys.exit(1)

    # Initialize system
    print("Initializing HybridDiscoverySystem v3.0...")
    system = HybridDiscoverySystem(
        domain="defi",
        max_results=50,
        use_rich_output=True,
        primary_llm="anthropic" if anthropic_key else "google",
        enable_fallback=True,
    )

    # Generate sample data (AMM constant product formula)
    print("\nGenerating sample data for AMM constant product formula...")
    np.random.seed(42)
    n_samples = 100
    X = np.random.uniform(10, 1000, (n_samples, 2))
    # y = sqrt(reserve0 * reserve1) with noise
    y = np.sqrt(X[:, 0] * X[:, 1]) + np.random.normal(0, 5, n_samples)

    print(f"✅ Generated {n_samples} samples")
    print(f"   Feature 1 (reserve0): range [{X[:, 0].min():.1f}, {X[:, 0].max():.1f}]")
    print(f"   Feature 2 (reserve1): range [{X[:, 1].min():.1f}, {X[:, 1].max():.1f}]")
    print(f"   Target (K): range [{y.min():.1f}, {y.max():.1f}]")

    # Run complete discovery workflow
    result = system.discover_validate_interpret(
        X=X,
        y=y,
        variable_names=["reserve0", "reserve1"],
        variable_descriptions={
            "reserve0": "Token 0 reserves in liquidity pool",
            "reserve1": "Token 1 reserves in liquidity pool",
        },
        variable_units={"reserve0": "dimensionless", "reserve1": "dimensionless"},
        description="AMM Constant Product Formula Discovery",
        show_formatted=True,
        use_llm=True,
        min_validation_score=85.0,
    )

    # Display complete statistics
    system.print_statistics_summary()

    # Export results
    system.export_results("discovery_results.json", format="json")

    print("\n✅ Example workflow complete!")

    """
    Key Updates in v3.0:
1. Real LLM Provider Integration
✅ Direct integration with enhanced AnthropicProvider and GoogleProvider
✅ No mock implementations - all real API calls
✅ Leverages built-in retry logic and error handling from providers
2. Intelligent Fallback Mechanism
✅ Automatic provider selection based on availability
✅ Graceful fallback on primary provider failure
✅ Tracks fallback usage in statistics
3. Enhanced Error Handling
✅ Comprehensive exception handling at each stage
✅ Detailed error logging and reporting
✅ Graceful degradation when components fail
4. Production Features
✅ Statistics tracking for all components:

Discovery success rates
Validation scores
LLM call statistics (per provider)
Fallback counts

✅ Results management:

Export to JSON/CSV
Comparison tables
Formatted display

✅ Monitoring & Debugging:

Comprehensive logging
Provider-specific stats
Token usage tracking
Success rate calculations

5. Three-Stage Workflow

Discovery → Symbolic engine finds expressions
Validation → Ensemble validator checks quality (85.0 threshold)
Interpretation → Real LLM provides domain insights

6. API Key Management
✅ Supports environment variables
✅ Validates provider availability
✅ Auto-selects primary provider based on availability
✅ Clear error messages for missing keys
The system is now fully production-ready with real API integrations, comprehensive error handling, intelligent fallbacks, and detailed monitoring capabilities!

"""
