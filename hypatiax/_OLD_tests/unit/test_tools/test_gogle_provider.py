#!/usr/bin/env python3
"""
Test Google Gemini Provider for Formula Generation
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
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Test Google Gemini provider with DeFi formula generation"""

    print("=" * 70)
    print("Google Gemini Provider Test - DeFi Formula Generation")
    print("=" * 70)
    print()

    # Method 1: Try loading from hypatiax.config (if available)
    try:
        from hypatiax.config import secrets

        logger.info("✓ Loaded secrets from hypatiax.config")

        # Validate Google key
        secrets.validate(["google_api_key"])
        api_key = secrets.google_api_key

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
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            print("\n❌ ERROR: GOOGLE_API_KEY not found!")
            print("\nTo fix this, create a .env file with:")
            print("  GOOGLE_API_KEY=your-key-here")
            print("\nOr set environment variable:")
            print("  export GOOGLE_API_KEY=your-key-here")
            print("\n💡 Get your API key from: https://aistudio.google.com/")
            sys.exit(1)

        # Mask key for display
        masked_key = f"{api_key[:8]}...{api_key[-4:]}"
        print(f"✓ Google API Key loaded: {masked_key}")

    print()

    # Import provider
    try:
        from tools.llm_providers.google_provider import GoogleProvider

        logger.info("✓ GoogleProvider imported successfully")
    except ImportError as e:
        logger.error(f"❌ Could not import GoogleProvider: {e}")
        logger.error("Make sure you're running from the hypatiax directory")
        sys.exit(1)

    # Initialize provider
    try:
        provider = GoogleProvider(api_key=api_key)
        logger.info("✓ GoogleProvider initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize GoogleProvider: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    print()

    # Test 1: Basic Impermanent Loss Formula
    print("=" * 70)
    print("Test 1: Basic Impermanent Loss Formula")
    print("=" * 70)
    try:
        result = provider.generate_formula(
            requirements="Calculate impermanent loss for Uniswap V2 liquidity pools", domain="defi", n_candidates=1
        )

        formula = result[0]

        if "error" in formula:
            print(f"\n⚠️  Formula generation had issues: {formula.get('error')}")
            if "raw_content" in formula:
                print(f"\nRaw response preview:\n{formula['raw_content'][:200]}...")
        else:
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

        print("\n✓ Test 1 completed!")

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

        if "error" in formula:
            print(f"\n⚠️  Formula generation had issues: {formula.get('error')}")
        else:
            print(f"\n📐 Formula (LaTeX): {formula['formula_latex']}")
            print(f"\n💻 Python Implementation:")
            print(formula["formula_python"])
            print(f"\n📝 Explanation: {formula['explanation']}")

        print("\n✓ Test 2 completed!")

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

        if "error" in formula:
            print(f"\n⚠️  Formula generation had issues: {formula.get('error')}")
        else:
            print(f"\n📐 Formula (LaTeX): {formula['formula_latex']}")
            print(f"\n💻 Python Implementation:")
            print(formula["formula_python"])
            print(f"\n📝 Explanation: {formula['explanation']}")

            # Show variables
            if formula.get("variables"):
                print(f"\n📊 Variables:")
                for var, desc in formula["variables"].items():
                    print(f"  • {var}: {desc}")

        print("\n✓ Test 3 completed!")

    except Exception as e:
        logger.error(f"❌ Test 3 failed: {e}")

    print()

    # Test 4: Formula Refinement (if Test 1 was successful)
    print("=" * 70)
    print("Test 4: Formula Refinement")
    print("=" * 70)
    try:
        # Use the formula from Test 1
        result = provider.generate_formula(
            requirements="Calculate impermanent loss for Uniswap V2 liquidity pools", domain="defi", n_candidates=1
        )

        original_formula = result[0]

        if "error" not in original_formula:
            print("\n📝 Refining formula with feedback...")
            refined = provider.refine_formula(
                formula=original_formula, feedback="Make it more efficient and add support for fee tiers"
            )

            if "error" in refined:
                print(f"\n⚠️  Refinement had issues: {refined.get('error')}")
            else:
                print(f"\n📐 Refined Formula (LaTeX): {refined['formula_latex']}")
                print(f"\n💻 Refined Implementation:")
                print(refined["formula_python"])
                print(f"\n📝 Explanation: {refined['explanation']}")
        else:
            print("\n⚠️  Skipping refinement test due to original formula generation issue")

        print("\n✓ Test 4 completed!")

    except Exception as e:
        logger.error(f"❌ Test 4 failed: {e}")

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
    print("\n📊 Google Gemini API Statistics:")
    print(f"  • Model used: {provider.model._model_name}")
    print(f"  • Max output tokens: {provider.generation_config.max_output_tokens}")
    print(f"  • Temperature: {provider.generation_config.temperature}")
    print("=" * 70)


if __name__ == "__main__":
    main()
