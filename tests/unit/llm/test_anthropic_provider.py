#!/usr/bin/env python3
"""
Test Anthropic Provider for Formula Generation
Tests integration with HypatiaX DeFi tools
"""

import logging
import os
import sys
from pathlib import Path

# Add hypatiax to path - we're in tests/unit/test_tools/, need to go up 3 levels
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Test Anthropic provider with DeFi formula generation"""

    print("=" * 70)
    print("Anthropic Provider Test - DeFi Formula Generation")
    print("=" * 70)
    print()

    # Method 1: Try loading from hypatiax.config (if available)
    try:
        from hypatiax.config import secrets

        logger.info("✓ Loaded secrets from hypatiax.config")

        # Validate Anthropic key
        secrets.validate(["anthropic_api_key"])
        api_key = secrets.anthropic_api_key

        # Print status
        secrets.print_status()

    except (ImportError, ValueError) as e:
        logger.warning(f"Could not load from hypatiax.config: {e}")

        # Method 2: Fallback to direct .env loading
        logger.info("Falling back to direct .env loading...")

        # Try to find .env file (in hypatiax/ root, we're in tests/unit/test_tools/)
        hypatiax_root = Path(__file__).resolve().parent.parent.parent.parent

        env_paths = [
            hypatiax_root / ".env",  # hypatiax/.env (main location)
            Path.cwd() / ".env",  # Current working directory
            Path(__file__).parent / ".env",  # Same dir as test
            hypatiax_root / "config" / ".env",  # hypatiax/config/.env
        ]

        logger.info(f"Searching for .env file from: {Path(__file__).resolve()}")
        logger.info(f"Project root detected as: {hypatiax_root}")

        env_loaded = False
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                logger.info(f"✓ Loaded .env from {env_path}")
                env_loaded = True
                break

        if not env_loaded:
            logger.warning("No .env file found in expected locations")

        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            print("\n❌ ERROR: ANTHROPIC_API_KEY not found!")
            print("\nTo fix this, create a .env file with:")
            print("  ANTHROPIC_API_KEY=your-key-here")
            print("\nOr set environment variable:")
            print("  export ANTHROPIC_API_KEY=your-key-here")
            sys.exit(1)

        # Mask key for display
        masked_key = f"{api_key[:8]}...{api_key[-4:]}"
        print(f"✓ Anthropic API Key loaded: {masked_key}")

    print()

    # Import provider
    try:
        from tools.llm_providers.anthropic_provider import AnthropicProvider

        logger.info("✓ AnthropicProvider imported successfully")
    except ImportError as e:
        logger.error(f"❌ Could not import AnthropicProvider: {e}")
        logger.error("Make sure you're running from the hypatiax directory")
        sys.exit(1)

    # Initialize provider
    provider = AnthropicProvider(api_key=api_key)
    logger.info("✓ AnthropicProvider initialized")

    print()

    # Test 1: Basic Impermanent Loss Formula
    print("=" * 70)
    print("Test 1: Basic Impermanent Loss Formula")
    print("=" * 70)
    try:
        result = provider.generate_formula(
            requirements="Calculate impermanent loss for Uniswap V2 liquidity pools",
            domain="defi",
            n_candidates=1,
        )

        formula = result[0]
        print(f"\n📐 Formula (LaTeX): {formula['formula_latex']}")
        print(f"\n💻 Python Implementation:")
        print(formula["formula_python"])
        print(f"\n📝 Explanation: {formula['explanation']}")
        print(f"\n⭐ Novelty Score: {formula.get('novelty_score', 'N/A')}/10")

        if formula.get("advantages"):
            print(f"\n✅ Advantages:")
            for adv in formula["advantages"]:
                print(f"  • {adv}")

        if formula.get("limitations"):
            print(f"\n⚠️  Limitations:")
            for lim in formula["limitations"]:
                print(f"  • {lim}")

        print("\n✓ Test 1 passed!")

    except Exception as e:
        logger.error(f"❌ Test 1 failed: {e}")
        import traceback

        traceback.print_exc()

    print()

    # Test 2: Price Impact Formula
    print("=" * 70)
    print("Test 2: Price Impact for AMM Trades")
    print("=" * 70)
    try:
        result = provider.generate_formula(
            requirements="Calculate price impact for large trades in constant product AMM",
            domain="defi",
            n_candidates=1,
        )

        formula = result[0]
        print(f"\n📐 Formula (LaTeX): {formula['formula_latex']}")
        print(f"\n💻 Python Implementation:")
        print(formula["formula_python"])
        print(f"\n📝 Explanation: {formula['explanation']}")
        print("\n✓ Test 2 passed!")

    except Exception as e:
        logger.error(f"❌ Test 2 failed: {e}")

    print()

    # Test 3: LP ROI Formula
    print("=" * 70)
    print("Test 3: Liquidity Provider ROI")
    print("=" * 70)
    try:
        result = provider.generate_formula(
            requirements="Calculate total ROI for liquidity providers including fees and impermanent loss",
            domain="defi",
            n_candidates=1,
        )

        formula = result[0]
        print(f"\n📐 Formula (LaTeX): {formula['formula_latex']}")
        print(f"\n💻 Python Implementation:")
        print(formula["formula_python"])
        print(f"\n📝 Explanation: {formula['explanation']}")

        # Show variables
        if formula.get("variables"):
            print(f"\n📊 Variables:")
            for var, desc in formula["variables"].items():
                print(f"  • {var}: {desc}")

        print("\n✓ Test 3 passed!")

    except Exception as e:
        logger.error(f"❌ Test 3 failed: {e}")

    print()

    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print("✓ All tests completed!")
    print("\nAPI Response Format documented:")
    print("  • formula_latex: LaTeX mathematical notation")
    print("  • formula_python: Executable Python function")
    print("  • variables: Dictionary of variable descriptions")
    print("  • explanation: What the formula measures")
    print("  • constraints: Mathematical constraints")
    print("  • novelty_score: 0-10 rating")
    print("  • advantages: List of benefits")
    print("  • limitations: List of edge cases")
    print("=" * 70)


if __name__ == "__main__":
    main()
