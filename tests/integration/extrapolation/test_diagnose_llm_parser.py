"""
Diagnostic Script to Debug LLM Response Parsing

This script captures the raw LLM responses to see why parsing is failing.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

import re
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path

# Load environment - try multiple locations
env_locations = [
    Path("hypatiax") / ".env",  # Standard location
    Path(".env"),  # Root fallback
    Path(__file__).parent.parent.parent
    / "hypatiax"
    / ".env",  # From tests/integration/extrapolation/
    Path(__file__).parent.parent.parent
    / ".env",  # From tests/integration/extrapolation/
    Path.cwd() / "hypatiax" / ".env",  # From any working directory
    Path.cwd() / ".env",
]

loaded = False
for env_path in env_locations:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        loaded = True
        print(f"[INFO] Loaded .env from: {env_path}")
        break

if not loaded:
    # Try without path (will search parent dirs)
    load_dotenv()
    print(f"[INFO] Using system environment or searching parent directories")


def test_specialized_prompts():
    """Test all specialized prompts and show raw responses"""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not set")
        return

    client = Anthropic(api_key=api_key)
    model = "claude-sonnet-4-20250514"

    # Define test prompts
    test_cases = [
        {
            "name": "Kelly Criterion",
            "prompt": """Task: Optimal LP position size using risk-adjusted Kelly criterion
Domain: liquidity
Variables: expected_fee_apy, il_risk

[CRITICAL] Risk-Adjusted Kelly Criterion:

f* = min(mu / (lambda * sigma^2), 1.0)

Where:
- mu = expected return (expected_fee_apy)
- sigma = risk/volatility (il_risk)  
- lambda = 2.0 (risk aversion coefficient)
- Result capped at 1.0 (100% of capital)

PYTHON:
def formula(expected_fee_apy, il_risk):
    risk_aversion = 2.0
    f_star = expected_fee_apy / (risk_aversion * il_risk**2)
    return np.minimum(f_star, 1.0)

This formula determines optimal position size balancing expected returns against risk.""",
        },
        {
            "name": "Liquidation Long",
            "prompt": """Task: Liquidation price for leveraged long position
Domain: liquidation
Variables: entry_price, leverage

[CRITICAL] Liquidation Price for Long:

P_liq = P_entry * (1 - 1/(L * m))

Where:
- P_entry = entry price
- L = leverage multiplier
- m = 0.8 (80% maintenance margin threshold)

PYTHON:
def formula(entry_price, leverage):
    maintenance_margin = 0.8
    return entry_price * (1.0 - 1.0/(leverage * maintenance_margin))

Price at which long position gets liquidated due to margin call.""",
        },
        {
            "name": "Liquidation Short",
            "prompt": """Task: Liquidation price for leveraged short position
Domain: liquidation
Variables: entry_price, leverage

[CRITICAL] Liquidation Price for Short:

P_liq = P_entry * (1 + 1/(L * m))

Where:
- P_entry = entry price
- L = leverage multiplier
- m = 0.8 (80% maintenance margin threshold)

PYTHON:
def formula(entry_price, leverage):
    maintenance_margin = 0.8
    return entry_price * (1.0 + 1.0/(leverage * maintenance_margin))

Price at which short position gets liquidated.""",
        },
        {
            "name": "Impermanent Loss %",
            "prompt": """Task: Impermanent loss percentage in AMM
Domain: amm
Variables: price_ratio

[CRITICAL] Impermanent Loss %:

IL% = (2*sqrt(r)/(1+r) - 1) * 100

Where r = price_ratio (final price / initial price)

PYTHON:
def formula(price_ratio):
    il_fraction = 2.0 * np.sqrt(price_ratio) / (1.0 + price_ratio) - 1.0
    return il_fraction * 100.0

Returns IL as percentage (e.g., -2.5 means 2.5% loss).""",
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print("\n" + "=" * 80)
        print(f"TEST {i}/4: {test_case['name']}".center(80))
        print("=" * 80)

        print("\n[PROMPT SENT]")
        print("-" * 80)
        print(test_case["prompt"])
        print("-" * 80)

        try:
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[{"role": "user", "content": test_case["prompt"]}],
            )

            content = response.content[0].text

            print("\n[RAW RESPONSE]")
            print("-" * 80)
            print(content)
            print("-" * 80)

            # Test current parser
            print("\n[PARSER TEST]")
            parsed = parse_response(content)

            print(f"  Formula: {parsed.get('formula', 'N/A')}")
            print(
                f"  Python Code: {'[FOUND]' if parsed.get('python') != 'N/A' else '[NOT FOUND]'}"
            )
            print(
                f"  Explanation: {'[FOUND]' if parsed.get('explanation') != 'N/A' else '[NOT FOUND]'}"
            )

            if parsed.get("python") != "N/A":
                print("\n  Parsed Python Code:")
                for line in parsed["python"].split("\n"):
                    print(f"    {line}")
            else:
                print("\n  [ERROR] Failed to parse Python code!")
                print("\n  Attempting manual extraction...")

                # Try to find code manually
                if "def formula" in content:
                    print("  -> 'def formula' found in response")
                    code_start = content.find("def formula")
                    print(f"  -> Position: {code_start}")
                    snippet = content[code_start : code_start + 200]
                    print(f"  -> Snippet:\n{snippet}")
                else:
                    print("  -> 'def formula' NOT found in response!")

            input("\n[Press Enter to continue to next test...]")

        except Exception as e:
            print(f"\n[ERROR] API call failed: {e}")
            import traceback

            traceback.print_exc()


def parse_response(content: str):
    """Current parser logic from hybrid_system_defi_domain.py"""
    parsed = {}

    match = re.search(r"FORMULA:\s*\n([^\n]+)", content, re.IGNORECASE)
    parsed["formula"] = match.group(1).strip() if match else "N/A"

    match = re.search(
        r"PYTHON:\s*\n(.*?)(?=\n\n[A-Z]+:|$)", content, re.DOTALL | re.IGNORECASE
    )
    code = match.group(1).strip() if match else "N/A"
    parsed["python"] = re.sub(r"^```python\s*\n", "", re.sub(r"\n```\s*$", "", code))

    match = re.search(
        r"EXPLANATION:\s*\n(.*?)(?=\n\n[A-Z]+:|$)", content, re.DOTALL | re.IGNORECASE
    )
    parsed["explanation"] = match.group(1).strip() if match else "N/A"

    return parsed


def test_improved_parser():
    """Test an improved parser that's more robust"""

    # Sample problematic response (simulate what LLM might return)
    sample_responses = [
        # Case 1: Response without section headers
        """Here's the formula:

def formula(expected_fee_apy, il_risk):
    risk_aversion = 2.0
    f_star = expected_fee_apy / (risk_aversion * il_risk**2)
    return np.minimum(f_star, 1.0)

This implements the Kelly criterion.""",
        # Case 2: Response with different formatting
        """FORMULA: f* = min(mu / (lambda * sigma^2), 1.0)

PYTHON:
```python
def formula(expected_fee_apy, il_risk):
    risk_aversion = 2.0
    f_star = expected_fee_apy / (risk_aversion * il_risk**2)
    return np.minimum(f_star, 1.0)
```

EXPLANATION: Kelly criterion for position sizing.""",
        # Case 3: Response with markdown code blocks
        """```python
def formula(entry_price, leverage):
    maintenance_margin = 0.8
    return entry_price * (1.0 - 1.0/(leverage * maintenance_margin))
```""",
    ]

    print("\n" + "=" * 80)
    print("TESTING IMPROVED PARSER".center(80))
    print("=" * 80)

    for i, response in enumerate(sample_responses, 1):
        print(f"\n[TEST {i}]")
        print("Response:")
        print(response[:200] + "...")

        print("\n  Current Parser:")
        parsed = parse_response(response)
        print(
            f"    Python: {'[FOUND]' if parsed.get('python') != 'N/A' else '[NOT FOUND]'}"
        )

        print("\n  Improved Parser:")
        parsed_improved = parse_response_improved(response)
        print(
            f"    Python: {'[FOUND]' if parsed_improved.get('python') != 'N/A' else '[NOT FOUND]'}"
        )

        if parsed_improved.get("python") != "N/A":
            print(f"\n    Code:")
            for line in parsed_improved["python"].split("\n")[:5]:
                print(f"      {line}")


def parse_response_improved(content: str):
    """Improved parser that handles multiple formats"""
    parsed = {}

    # Try to extract formula
    match = re.search(r"FORMULA:\s*\n([^\n]+)", content, re.IGNORECASE)
    if match:
        parsed["formula"] = match.group(1).strip()
    else:
        # Try to find mathematical notation
        match = re.search(r"([A-Za-z_]+\s*=\s*[^=]+(?:\n|$))", content)
        parsed["formula"] = match.group(1).strip() if match else "N/A"

    # Try multiple strategies to extract Python code
    python_code = None

    # Strategy 1: Look for PYTHON: section
    match = re.search(
        r"PYTHON:\s*\n(.*?)(?=\n\n[A-Z]+:|$)", content, re.DOTALL | re.IGNORECASE
    )
    if match:
        python_code = match.group(1).strip()

    # Strategy 2: Look for ```python code blocks
    if not python_code or python_code == "N/A":
        match = re.search(r"```python\s*\n(.*?)\n```", content, re.DOTALL)
        if match:
            python_code = match.group(1).strip()

    # Strategy 3: Look for any ``` code blocks with def formula
    if not python_code or python_code == "N/A":
        match = re.search(r"```\s*\n(def formula.*?)\n```", content, re.DOTALL)
        if match:
            python_code = match.group(1).strip()

    # Strategy 4: Look for def formula directly (no code blocks)
    if not python_code or python_code == "N/A":
        match = re.search(
            r"(def formula\([^)]+\):.*?)(?=\n\n|\nEXPLANATION|\nThis |$)",
            content,
            re.DOTALL,
        )
        if match:
            python_code = match.group(1).strip()

    # Clean up code blocks markers if present
    if python_code:
        python_code = re.sub(r"^```python\s*\n", "", python_code)
        python_code = re.sub(r"\n```\s*$", "", python_code)
        parsed["python"] = python_code
    else:
        parsed["python"] = "N/A"

    # Extract explanation
    match = re.search(
        r"EXPLANATION:\s*\n(.*?)(?=\n\n[A-Z]+:|$)", content, re.DOTALL | re.IGNORECASE
    )
    if match:
        parsed["explanation"] = match.group(1).strip()
    else:
        # Try to find any explanation text after the code
        match = re.search(r"(?:This |The formula|Returns)([^.]+\.)", content)
        parsed["explanation"] = match.group(0).strip() if match else "N/A"

    return parsed


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Diagnose LLM Response Parsing")
    parser.add_argument(
        "--mode",
        choices=["live", "test_parser"],
        default="live",
        help="Test mode: live (call API) or test_parser (test parsing)",
    )

    args = parser.parse_args()

    if args.mode == "live":
        print("=" * 80)
        print("DIAGNOSING LLM RESPONSE PARSING - LIVE API CALLS".center(80))
        print("=" * 80)
        print("\nThis will make 4 API calls to test specialized prompts.")
        print("Press Ctrl+C to cancel, or Enter to continue...")
        input()

        test_specialized_prompts()

    elif args.mode == "test_parser":
        test_improved_parser()
