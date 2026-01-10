"""
Quick test of fixed prompts to verify they generate code
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
import re

# Load environment
env_locations = [
    Path("hypatiax") / ".env",
    Path(".env"),
]

for env_path in env_locations:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"[INFO] Loaded .env from: {env_path}")
        break

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("[ERROR] ANTHROPIC_API_KEY not set")
    exit(1)

client = Anthropic(api_key=api_key)

# Fixed Kelly Criterion prompt
kelly_prompt = """Task: Implement the risk-adjusted Kelly criterion formula
Variables: expected_fee_apy, il_risk

CRITICAL INSTRUCTIONS:
You must output working Python code that implements this formula:
- Formula: f* = min(μ / (λ × σ²), 1.0)
- μ = expected_fee_apy (first parameter)
- σ = il_risk (second parameter)
- λ = 2.0 (risk aversion, define as constant)

OUTPUT FORMAT (you must follow this exactly):

FORMULA:
f* = min(μ / (λ × σ²), 1.0)

PYTHON:
def formula(expected_fee_apy, il_risk):
    risk_aversion = 2.0
    f_star = expected_fee_apy / (risk_aversion * il_risk**2)
    return np.minimum(f_star, 1.0)

EXPLANATION:
Kelly criterion for optimal position sizing

DO NOT add any commentary before or after. Output ONLY the three sections above."""

print("=" * 80)
print("Testing Fixed Kelly Criterion Prompt".center(80))
print("=" * 80)

print("\n[SENDING PROMPT]")
print("-" * 80)
print(kelly_prompt)
print("-" * 80)

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2000,
    messages=[{"role": "user", "content": kelly_prompt}],
)

content = response.content[0].text

print("\n[RESPONSE]")
print("-" * 80)
print(content)
print("-" * 80)

# Parse response
print("\n[PARSING]")

# Check for PYTHON section
if "PYTHON:" in content:
    print("✅ Found PYTHON: section")

    # Extract code
    match = re.search(
        r"PYTHON:\s*\n(.*?)(?=\n\n[A-Z]+:|$)", content, re.DOTALL | re.IGNORECASE
    )
    if match:
        code = match.group(1).strip()
        print("✅ Extracted code successfully")

        if "def formula" in code:
            print("✅ Found 'def formula' in code")
            print("\n[CODE]")
            print(code)

            # Try to execute it
            try:
                import numpy as np

                local_vars = {}
                exec(code, {"np": np, "numpy": np}, local_vars)

                if "formula" in local_vars:
                    print("\n✅ Code executes successfully!")

                    # Test it
                    func = local_vars["formula"]
                    result = func(0.10, 0.15)
                    print(f"✅ Test call: formula(0.10, 0.15) = {result}")

                    expected = min(0.10 / (2.0 * 0.15**2), 1.0)
                    if abs(result - expected) < 1e-6:
                        print(f"✅ Result matches expected: {expected}")
                    else:
                        print(f"❌ Result mismatch! Expected {expected}, got {result}")
                else:
                    print("❌ No 'formula' function found after exec")

            except Exception as e:
                print(f"❌ Code execution failed: {e}")
        else:
            print("❌ No 'def formula' found in code")
    else:
        print("❌ Failed to extract code with regex")
else:
    print("❌ No PYTHON: section found")
    print("\n[DIAGNOSTIC]")
    if "def formula" in content:
        print("-> 'def formula' exists but not in PYTHON: section")
    else:
        print("-> No 'def formula' found at all")

    if "enhancement" in content.lower() or "consider" in content.lower():
        print("-> Response contains commentary/enhancements")
        print("-> Claude is discussing the formula instead of implementing it")

"""
python test_fixed_prompts.py
```

This will:
1. ✅ Send the fixed Kelly Criterion prompt
2. ✅ Show the raw response
3. ✅ Parse it
4. ✅ Execute the code
5. ✅ Test it with actual values

**Expected output:**
```
✅ Found PYTHON: section
✅ Extracted code successfully
✅ Found 'def formula' in code
✅ Code executes successfully!
✅ Test call: formula(0.10, 0.15) = 1.0
✅ Result matches expected: 1.0

"""
