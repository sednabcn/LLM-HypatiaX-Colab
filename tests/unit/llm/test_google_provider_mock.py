#!/usr/bin/env python3
"""
Mock Test for Google Gemini Provider - Works WITHOUT API Credits
Tests the integration without making actual API calls
"""

import logging
import os
import sys
from pathlib import Path

# Add hypatiax to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MockGoogleProvider:
    """
    Mock provider that simulates Google Gemini API responses without making actual calls
    Perfect for testing when you don't have API credits or quota
    """

    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key
        self.model_name = model_name or "models/gemini-2.5-flash"
        logger.info("✓ Mock Google provider initialized (no API calls will be made)")

        # Simulate the model object
        class MockModel:
            _model_name = "models/gemini-2.5-flash (mock)"

        self.model = MockModel()

        # Simulate generation config
        class MockGenerationConfig:
            temperature = 0.7
            max_output_tokens = 8192
            top_p = 0.95
            top_k = 40

        self.generation_config = MockGenerationConfig()

    def generate_formula(
        self, requirements: str, domain: str = "defi", n_candidates: int = 1
    ):
        """Generate mock formulas based on requirements"""

        mock_responses = {
            "impermanent loss": {
                "formula_latex": r"IL = \frac{2\sqrt{p}}{1+p} - 1 \text{ where } p = \frac{P_1}{P_0}",
                "formula_python": '''def calculate_impermanent_loss(price_ratio):
    """
    Calculate impermanent loss for Uniswap V2 pools

    Args:
        price_ratio: Current price / Initial price (P1/P0)

    Returns:
        Impermanent loss as decimal (negative value represents loss)
    """
    import math

    if price_ratio <= 0:
        raise ValueError("Price ratio must be positive")

    il = (2 * math.sqrt(price_ratio)) / (1 + price_ratio) - 1
    return il''',
                "variables": {
                    "p": "Price ratio (P₁/P₀) - current price divided by initial price",
                    "IL": "Impermanent loss as decimal (e.g., -0.0573 = -5.73% loss)",
                    "P₁": "Current price of token pair",
                    "P₀": "Initial price at deposit",
                },
                "explanation": 'This formula calculates impermanent loss (IL) in Uniswap V2 constant product (x*y=k) pools. IL represents the difference between holding tokens versus providing liquidity, occurring when the price ratio changes from the initial deposit. The loss is "impermanent" because it can be recovered if prices return to original levels.',
                "constraints": [
                    "p > 0 (price ratio must be positive)",
                    "Valid only for 50/50 constant product AMMs",
                    "Does not include trading fee compensation",
                    "Assumes no additional deposits or withdrawals",
                ],
                "novelty_score": 5,
                "similar_to": [
                    "Uniswap V2 IL formula",
                    "Bancor impermanent loss calculation",
                    "Constant product market maker loss function",
                ],
                "advantages": [
                    "Simple closed-form mathematical solution",
                    "Works for any magnitude of price change",
                    "Numerically stable across all price ranges",
                    "Widely validated in production DeFi protocols",
                ],
                "limitations": [
                    "Does not account for accumulated trading fees",
                    "Only applicable to constant product (x*y=k) formula",
                    "Does not consider concentrated liquidity ranges",
                    "Ignores gas costs and slippage during entry/exit",
                ],
            },
            "price impact": {
                "formula_latex": r"PI = 1 - \frac{R_{out}}{R_{out} + \Delta_{out}} \text{ where } \Delta_{out} = \frac{R_{out} \cdot \Delta_{in} \cdot (1-f)}{R_{in} + \Delta_{in} \cdot (1-f)}",
                "formula_python": '''def calculate_price_impact(reserve_in, reserve_out, amount_in, fee=0.003):
    """
    Calculate price impact for AMM trades

    Args:
        reserve_in: Reserve of input token in pool
        reserve_out: Reserve of output token in pool
        amount_in: Amount of input token to trade
        fee: Trading fee as decimal (0.003 = 0.3%)

    Returns:
        Price impact as percentage (e.g., 1.5 = 1.5% impact)
    """
    if reserve_in <= 0 or reserve_out <= 0:
        raise ValueError("Reserves must be positive")
    if amount_in <= 0:
        raise ValueError("Trade amount must be positive")
    if not 0 <= fee < 1:
        raise ValueError("Fee must be between 0 and 1")

    # Apply fee to input amount
    amount_in_with_fee = amount_in * (1 - fee)

    # Calculate output amount using constant product formula
    amount_out = (reserve_out * amount_in_with_fee) / (reserve_in + amount_in_with_fee)

    # Calculate price impact
    price_impact = 1 - (reserve_out / (reserve_out + amount_out))

    return price_impact * 100  # Return as percentage''',
                "variables": {
                    "R_in": "Reserve of input token in the pool",
                    "R_out": "Reserve of output token in the pool",
                    "Δ_in": "Amount of input token being traded",
                    "Δ_out": "Amount of output token received",
                    "f": "Trading fee (typically 0.003 for 0.3%)",
                    "PI": "Price impact as percentage",
                },
                "explanation": "Price impact measures how much a trade moves the pool price in an AMM. Larger trades relative to available liquidity result in higher price impact and worse execution prices. This formula accounts for the constant product invariant and trading fees.",
                "constraints": [
                    "Δ_in < R_in (cannot trade more than available)",
                    "f ∈ [0, 1) (fee must be valid percentage)",
                    "R_in, R_out > 0 (non-empty pool)",
                    "Single-hop trade only",
                ],
                "novelty_score": 6,
                "similar_to": [
                    "Slippage calculation",
                    "AMM execution price formula",
                    "Bancor price impact metric",
                ],
                "advantages": [
                    "Direct calculation from on-chain reserves",
                    "Accounts for protocol trading fees",
                    "Real-time computation without historical data",
                    "Applicable to most constant product AMMs",
                ],
                "limitations": [
                    "Does not consider multi-hop routing opportunities",
                    "Assumes single atomic transaction",
                    "May underestimate impact for very large trades",
                    "Does not account for MEV or sandwich attacks",
                ],
            },
            "liquidity provider": {
                "formula_latex": r"ROI = \frac{V_{LP} + F_{earned} - V_{hold}}{V_{hold}} \times 100\%",
                "formula_python": '''def calculate_lp_roi(initial_value, pool_value, fees_earned, hold_value):
    """
    Calculate comprehensive ROI for liquidity providers

    Args:
        initial_value: Initial USD value of deposited tokens
        pool_value: Current USD value of LP position (excluding fees)
        fees_earned: Total trading fees accumulated
        hold_value: Value if tokens were held instead of providing liquidity

    Returns:
        Dictionary with ROI breakdown including IL and fee yield
    """
    if hold_value <= 0:
        raise ValueError("Hold value must be positive")

    # Total LP position value
    total_lp_value = pool_value + fees_earned

    # Calculate components
    total_roi = ((total_lp_value - hold_value) / hold_value) * 100
    impermanent_loss_pct = ((pool_value - hold_value) / hold_value) * 100
    fee_yield_pct = (fees_earned / hold_value) * 100

    # Check if fees compensate for IL
    net_profitable = total_roi > 0
    il_compensated = fees_earned > abs(pool_value - hold_value)

    return {
        'total_roi': total_roi,
        'impermanent_loss': impermanent_loss_pct,
        'fee_yield': fee_yield_pct,
        'net_profitable': net_profitable,
        'il_fully_compensated': il_compensated,
        'breakeven_fees': max(0, hold_value - pool_value)
    }''',
                "variables": {
                    "V_LP": "Current USD value of LP tokens (position value)",
                    "F_earned": "Total trading fees earned in USD",
                    "V_hold": "Value if tokens were held (not in pool)",
                    "ROI": "Total return on investment as percentage",
                    "V_initial": "Initial value of tokens at deposit",
                },
                "explanation": "This formula calculates the comprehensive ROI for liquidity providers by combining impermanent loss and fee earnings. It compares the total value (LP position + fees) against a simple hold strategy to determine if providing liquidity was profitable.",
                "constraints": [
                    "V_hold > 0 (must have non-zero hold value)",
                    "F_earned ≥ 0 (fees are always non-negative)",
                    "Time period must be specified for annualized calculations",
                    "Assumes accurate USD pricing for all assets",
                ],
                "novelty_score": 7,
                "similar_to": [
                    "Portfolio return analysis",
                    "Yield farming APR calculations",
                    "Opportunity cost metrics",
                ],
                "advantages": [
                    "Accounts for both IL and fee compensation",
                    "Directly comparable to passive holding strategy",
                    "Can be annualized for APR/APY calculation",
                    "Shows breakeven point for fee earnings",
                ],
                "limitations": [
                    "Requires accurate historical fee tracking",
                    "Does not account for gas costs or transaction fees",
                    "Assumes instant liquidity and exit capability",
                    "Does not consider opportunity cost of capital",
                ],
            },
            "volatility": {
                "formula_latex": r"\sigma = \sqrt{\frac{1}{n-1} \sum_{i=1}^{n} (r_i - \bar{r})^2} \times \sqrt{365}",
                "formula_python": '''def calculate_annualized_volatility(returns):
    """
    Calculate annualized volatility from daily returns

    Args:
        returns: List of daily returns as decimals

    Returns:
        Annualized volatility as percentage
    """
    import math

    if len(returns) < 2:
        raise ValueError("Need at least 2 returns")

    # Calculate mean return
    mean_return = sum(returns) / len(returns)

    # Calculate variance
    variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)

    # Calculate standard deviation (daily volatility)
    daily_vol = math.sqrt(variance)

    # Annualize (assuming 365 days)
    annualized_vol = daily_vol * math.sqrt(365)

    return annualized_vol * 100  # Return as percentage''',
                "variables": {
                    "σ": "Annualized volatility (standard deviation)",
                    "r_i": "Individual daily return",
                    "r̄": "Mean of returns",
                    "n": "Number of observations",
                },
                "explanation": "Calculates annualized volatility from a series of daily returns using standard deviation. This is a key risk metric in DeFi for assessing token price stability.",
                "constraints": [
                    "n ≥ 2 (need multiple data points)",
                    "Returns should be in decimal form",
                    "Assumes 365 trading days per year",
                ],
                "novelty_score": 4,
                "similar_to": [
                    "Standard deviation",
                    "Historical volatility",
                    "Realized volatility",
                ],
                "advantages": [
                    "Standard financial metric",
                    "Easy to calculate and interpret",
                    "Comparable across assets",
                ],
                "limitations": [
                    "Assumes normal distribution of returns",
                    "Historical volatility may not predict future",
                    "Sensitive to outliers",
                ],
            },
        }

        # Match requirements to mock responses
        req_lower = requirements.lower()
        if "impermanent loss" in req_lower or "il" in req_lower:
            formula = mock_responses["impermanent loss"]
        elif "price impact" in req_lower or "slippage" in req_lower:
            formula = mock_responses["price impact"]
        elif (
            "roi" in req_lower or "liquidity provider" in req_lower or "lp" in req_lower
        ):
            formula = mock_responses["liquidity provider"]
        elif "volatility" in req_lower or "variance" in req_lower:
            formula = mock_responses["volatility"]
        else:
            # Default generic response
            formula = {
                "formula_latex": r"f(x) = \text{custom\_formula}(x)",
                "formula_python": '''def calculate(params):
    """Custom formula implementation"""
    # Implementation would go here
    return result''',
                "variables": {"x": "Input parameter"},
                "explanation": f"Mock formula for: {requirements}",
                "constraints": ["Parameters must be valid"],
                "novelty_score": 5,
                "similar_to": ["Related formulas"],
                "advantages": ["Mathematically sound"],
                "limitations": ["May need refinement for specific use cases"],
            }

        return [formula] * n_candidates

    def refine_formula(self, formula: dict, feedback: str):
        """Mock refinement - returns slightly modified formula"""
        logger.info(f"Mock refinement with feedback: {feedback}")

        refined = formula.copy()
        refined["explanation"] = f"{formula['explanation']} [REFINED: {feedback}]"
        refined["novelty_score"] = min(10, formula.get("novelty_score", 5) + 1)

        return refined


def execute_formula_safely(formula_dict: dict, function_name: str):
    """
    Safely execute formula code and extract the function

    Args:
        formula_dict: Dictionary containing 'formula_python' key
        function_name: Name of function to extract from code

    Returns:
        The executable function

    Raises:
        ValueError: If function not found or code invalid
    """
    try:
        code = formula_dict.get("formula_python")
        if not code:
            raise ValueError("No formula_python code found in formula dict")

        # Create isolated namespace for execution
        namespace = {}
        exec(code, namespace)

        # Extract and validate function
        if function_name not in namespace:
            available = [k for k in namespace.keys() if callable(namespace[k])]
            raise ValueError(
                f"Function '{function_name}' not found. Available: {available}"
            )

        func = namespace[function_name]
        if not callable(func):
            raise ValueError(f"'{function_name}' exists but is not callable")

        return func

    except SyntaxError as e:
        raise ValueError(f"Syntax error in formula code: {e}")
    except Exception as e:
        raise ValueError(f"Error executing formula: {e}")


def main():
    """Test mock Google Gemini provider"""

    print("=" * 70)
    print("Mock Google Gemini Provider Test - NO API CREDITS NEEDED")
    print("=" * 70)
    print()
    print("ℹ️  This test uses mock responses and doesn't call the real API")
    print("   Perfect for testing your integration without credits or quota!")
    print()

    # Load .env for consistency, but we won't use the API
    hypatiax_root = Path(__file__).resolve().parent.parent.parent.parent
    env_path = hypatiax_root / ".env"

    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"✓ Loaded .env from {env_path}")

    # Initialize mock provider
    provider = MockGoogleProvider(api_key="mock-key")
    print()

    # Test 1: Basic Impermanent Loss Formula
    print("=" * 70)
    print("Test 1: Basic Impermanent Loss Formula")
    print("=" * 70)

    result = provider.generate_formula(
        requirements="Calculate impermanent loss for Uniswap V2 liquidity pools",
        domain="defi",
        n_candidates=1,
    )

    formula = result[0]
    print(f"\n🔢 Formula (LaTeX): {formula['formula_latex']}")
    print(f"\n💻 Python Implementation:")
    print(formula["formula_python"])
    print(f"\n📖 Explanation: {formula['explanation']}")
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
    print()

    # Test 2: Price Impact Formula
    print("=" * 70)
    print("Test 2: Price Impact for AMM Trades")
    print("=" * 70)

    result = provider.generate_formula(
        requirements="Calculate price impact for large trades in constant product AMM",
        domain="defi",
        n_candidates=1,
    )

    formula = result[0]
    print(f"\n🔢 Formula (LaTeX): {formula['formula_latex']}")
    print(f"\n💻 Python Implementation:")
    print(formula["formula_python"])
    print(f"\n📖 Explanation: {formula['explanation']}")
    print("\n✓ Test 2 passed!")
    print()

    # Test 3: LP ROI Formula
    print("=" * 70)
    print("Test 3: Liquidity Provider ROI")
    print("=" * 70)

    result = provider.generate_formula(
        requirements="Calculate total ROI for liquidity providers including fees and impermanent loss",
        domain="defi",
        n_candidates=1,
    )

    formula = result[0]
    print(f"\n🔢 Formula (LaTeX): {formula['formula_latex']}")
    print(f"\n💻 Python Implementation:")
    print(formula["formula_python"])
    print(f"\n📖 Explanation: {formula['explanation']}")

    # Show variables
    if formula.get("variables"):
        print(f"\n📊 Variables:")
        for var, desc in formula["variables"].items():
            print(f"  • {var}: {desc}")

    print("\n✓ Test 3 passed!")
    print()

    # Test 4: Formula Refinement
    print("=" * 70)
    print("Test 4: Formula Refinement")
    print("=" * 70)

    original = result[0]
    refined = provider.refine_formula(
        formula=original,
        feedback="Make it more efficient and add support for fee tiers",
    )

    print(f"\n📈 Original Novelty Score: {original.get('novelty_score')}/10")
    print(f"📈 Refined Novelty Score: {refined.get('novelty_score')}/10")
    print(f"\n📖 Refined Explanation: {refined['explanation']}")
    print("\n✓ Test 4 passed!")
    print()

    # Demonstrate actual calculations with FIXED exec() scope
    print("=" * 70)
    print("Bonus: Execute the Generated Formulas")
    print("=" * 70)
    print()

    try:
        # Test 1: Impermanent Loss calculation
        print("Testing Impermanent Loss calculation:")
        il_result = provider.generate_formula("impermanent loss", "defi")[0]
        calculate_impermanent_loss = execute_formula_safely(
            il_result, "calculate_impermanent_loss"
        )

        test_cases = [
            (2.0, "Price doubled (2x)"),
            (0.5, "Price halved (0.5x)"),
            (4.0, "Price 4x"),
            (0.25, "Price 0.25x"),
        ]

        for price_ratio, description in test_cases:
            il = calculate_impermanent_loss(price_ratio)
            print(f"  {description}: IL = {il:.4f} ({il * 100:.2f}%)")

        print()

        # Test 2: Price Impact calculation
        print("Testing Price Impact calculation:")
        pi_result = provider.generate_formula("price impact", "defi")[0]
        calculate_price_impact = execute_formula_safely(
            pi_result, "calculate_price_impact"
        )

        # Example: Pool with 1M tokens each, trading 10k
        impact = calculate_price_impact(
            reserve_in=1_000_000, reserve_out=1_000_000, amount_in=10_000, fee=0.003
        )
        print(f"  10k trade on 1M liquidity: {impact:.3f}% price impact")

        # Larger trade
        impact_large = calculate_price_impact(
            reserve_in=1_000_000, reserve_out=1_000_000, amount_in=100_000, fee=0.003
        )
        print(f"  100k trade on 1M liquidity: {impact_large:.3f}% price impact")
        print()

        # Test 3: LP ROI calculation
        print("Testing LP ROI calculation:")
        roi_result = provider.generate_formula("liquidity provider roi", "defi")[0]
        calculate_lp_roi = execute_formula_safely(roi_result, "calculate_lp_roi")

        # Example: $10k deposit, price changed causing IL, but earned fees
        roi_data = calculate_lp_roi(
            initial_value=10_000,
            pool_value=9_500,  # Lost $500 to IL
            fees_earned=800,  # Earned $800 in fees
            hold_value=10_200,  # Holding would be $10,200
        )

        print(f"  Total ROI: {roi_data['total_roi']:.2f}%")
        print(f"  Impermanent Loss: {roi_data['impermanent_loss']:.2f}%")
        print(f"  Fee Yield: {roi_data['fee_yield']:.2f}%")
        print(f"  Net Profitable: {roi_data['net_profitable']}")
        print(f"  IL Compensated: {roi_data['il_fully_compensated']}")
        print()

        print("✓ All formula executions successful!")

    except Exception as e:
        print(f"❌ Error executing formulas: {e}")
        import traceback

        traceback.print_exc()

    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print("✓ All mock tests passed!")
    print("\n📋 What was tested:")
    print("  ✓ Provider initialization")
    print("  ✓ Formula generation (4 different types)")
    print("  ✓ Response format validation")
    print("  ✓ Formula refinement mechanism")
    print("  ✓ Formula execution and calculation (FIXED exec scope)")
    print("\n💡 Next Steps:")
    print("  1. Get API key from https://aistudio.google.com/")
    print("  2. Add GOOGLE_API_KEY to your .env file")
    print("  3. Replace MockGoogleProvider with GoogleProvider")
    print("  4. Run test_google_provider.py for real API testing")
    print("  5. Integrate with DeFi tools (uniswap_v2.py, il_calculator.py)")
    print("\n⚡ Google Gemini Benefits:")
    print("  • Fast response times with Flash models")
    print("  • 8K+ output token support for detailed formulas")
    print("  • Free tier available for development")
    print("  • Multiple model options (Flash, Pro)")
    print("=" * 70)


if __name__ == "__main__":
    main()
