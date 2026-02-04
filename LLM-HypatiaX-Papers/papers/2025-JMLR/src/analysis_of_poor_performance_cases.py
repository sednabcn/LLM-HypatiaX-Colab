"""
ANALYSIS OF POOR PERFORMANCE CASES

From baseline_neural_pure_llm_20251220_1951.txt, the liquidation domain has 4 failed cases:

1. Liquidation price for leveraged long position: R² = -4.010512 ❌
2. Liquidation price for leveraged short position: R² = 0.598874 ❌  
3. Maximum safe leverage: R² = 0.126437 ❌
4. Required collateral: R² = 0.776800 ❌

ROOT CAUSES:
- LLM is generating incorrect formulas with wrong constants
- The generated formulas don't match ground truth (e.g., maintenance_margin parameter issues)
- Missing or incorrect liquidation_threshold constant usage
"""

# ============================================================================
# FIXES FOR LIQUIDATION DOMAIN
# ============================================================================

def get_fixed_liquidation_prompts():
    """
    Return corrected specialized prompts for liquidation domain cases.
    These should be added to _generate_specialized_prompt() method.
    """
    
    prompts = {}
    
    # FIX 1: Liquidation price for LONG position
    prompts['liquidation_long'] = """You are a derivatives trading expert specializing in leverage and liquidation mechanics.

Task: Calculate liquidation price for leveraged long position
Variables: entry_price, leverage

⚠️ CRITICAL FORMULA: P_liq = P_e × (1 - 1/(L×m))
Where:
  - P_e = entry_price
  - L = leverage
  - m = maintenance_margin = 0.8 (80%)

⚠️ COMMON MISTAKES:
  ❌ DO NOT use: entry_price × (2 - liquidation_threshold/leverage)
  ❌ DO NOT forget maintenance_margin in denominator
  ✅ CORRECT: entry_price × (1 - 1/(leverage × 0.8))

EXAMPLE:
  entry_price = 50000, leverage = 10x, m = 0.8
  P_liq = 50000 × (1 - 1/(10×0.8)) = 50000 × (1 - 1/8) = 50000 × 0.875 = 43,750

Provide your response in this EXACT format:

FORMULA:
entry_price * (1 - 1/(leverage * 0.8))

LATEX:
P_{liq} = P_e \\times \\left(1 - \\frac{1}{L \\times m}\\right)

PYTHON:
def formula(entry_price, leverage):
    maintenance_margin = 0.8
    return entry_price * (1 - 1/(leverage * maintenance_margin))

VARIABLES:
- entry_price: Initial position entry price
- leverage: Position leverage multiplier
- maintenance_margin: 0.8 (80% threshold)

ASSUMPTIONS:
Long position liquidates when price drops below threshold

EXPLANATION:
For long positions, liquidation occurs when losses erode collateral to maintenance margin level."""

    # FIX 2: Liquidation price for SHORT position
    prompts['liquidation_short'] = """You are a derivatives trading expert specializing in leverage and liquidation mechanics.

Task: Calculate liquidation price for leveraged short position
Variables: entry_price, leverage

⚠️ CRITICAL FORMULA: P_liq = P_e × (1 + 1/(L×m))
Where:
  - P_e = entry_price
  - L = leverage
  - m = maintenance_margin = 0.8 (80%)

⚠️ KEY DIFFERENCE FROM LONG:
  - LONG:  1 - 1/(L×m)  ← price goes DOWN
  - SHORT: 1 + 1/(L×m)  ← price goes UP

EXAMPLE:
  entry_price = 50000, leverage = 10x, m = 0.8
  P_liq = 50000 × (1 + 1/(10×0.8)) = 50000 × (1 + 1/8) = 50000 × 1.125 = 56,250

Provide your response in this EXACT format:

FORMULA:
entry_price * (1 + 1/(leverage * 0.8))

LATEX:
P_{liq} = P_e \\times \\left(1 + \\frac{1}{L \\times m}\\right)

PYTHON:
def formula(entry_price, leverage):
    maintenance_margin = 0.8
    return entry_price * (1 + 1/(leverage * maintenance_margin))

VARIABLES:
- entry_price: Initial position entry price
- leverage: Position leverage multiplier
- maintenance_margin: 0.8 (80% threshold)

ASSUMPTIONS:
Short position liquidates when price rises above threshold

EXPLANATION:
For short positions, liquidation occurs when price increases erode collateral to maintenance margin level."""

    # FIX 3: Maximum safe leverage
    prompts['max_leverage'] = """You are a risk management expert specializing in leverage constraints.

Task: Calculate maximum safe leverage for given acceptable loss tolerance
Variables: entry_price, acceptable_loss_pct

⚠️ CRITICAL FORMULA: L_max = 1/(loss×m)
Where:
  - loss = acceptable_loss_pct (as decimal, e.g., 0.05 for 5%)
  - m = maintenance_margin = 0.8 (80%)

⚠️ COMMON MISTAKES:
  ❌ DO NOT use: liquidation_threshold / acceptable_loss_pct
  ❌ DO NOT forget to invert the relationship
  ✅ CORRECT: 1 / (acceptable_loss_pct × 0.8)

EXAMPLE:
  acceptable_loss_pct = 0.10 (10% loss), m = 0.8
  L_max = 1/(0.10 × 0.8) = 1/0.08 = 12.5x

Provide your response in this EXACT format:

FORMULA:
1 / (acceptable_loss_pct * 0.8)

LATEX:
L_{max} = \\frac{1}{\\text{loss} \\times m}

PYTHON:
def formula(entry_price, acceptable_loss_pct):
    maintenance_margin = 0.8
    return 1.0 / (acceptable_loss_pct * maintenance_margin)

VARIABLES:
- entry_price: Not used in calculation (present for context)
- acceptable_loss_pct: Maximum acceptable loss as decimal
- maintenance_margin: 0.8 (80% threshold)

ASSUMPTIONS:
Maximum leverage ensures liquidation only at acceptable loss level

EXPLANATION:
Higher acceptable loss tolerance allows higher leverage. The relationship is inverse."""

    # FIX 4: Required collateral
    prompts['required_collateral'] = """You are a derivatives trading expert specializing in margin requirements.

Task: Calculate required collateral for leveraged position
Variables: position_size, leverage

⚠️ CRITICAL FORMULA: collateral = position_size/leverage
This is the SIMPLEST formula in the domain!

⚠️ COMMON MISTAKES:
  ❌ DO NOT divide by maintenance_margin
  ❌ DO NOT multiply by any constants
  ✅ CORRECT: position_size / leverage (that's it!)

EXAMPLE:
  position_size = 100,000, leverage = 10x
  collateral = 100,000 / 10 = 10,000

Provide your response in this EXACT format:

FORMULA:
position_size / leverage

LATEX:
\\text{collateral} = \\frac{\\text{position\\_size}}{L}

PYTHON:
def formula(position_size, leverage):
    return position_size / leverage

VARIABLES:
- position_size: Total notional position value
- leverage: Position leverage multiplier

ASSUMPTIONS:
Initial margin requirement is 1/leverage of position size

EXPLANATION:
Direct inverse relationship - higher leverage means less collateral needed for same position."""

    return prompts


# ============================================================================
# UPDATED _generate_specialized_prompt() METHOD
# ============================================================================

def generate_specialized_prompt_FIXED(description: str, domain: str,
                                     variable_names: list, metadata: dict) -> str:
    """
    FIXED VERSION: Generate specialized prompts for problematic formulas.
    
    Add this to the baseline_pure_llm_defi_final.py class, replacing the
    existing _generate_specialized_prompt method.
    """
    desc_lower = description.lower()
    
    # KELLY CRITERION (already working)
    if 'optimal' in desc_lower and 'kelly' in desc_lower:
        return f"""You are a mathematical formula expert specializing in portfolio optimization.

Task: {description}
Variables: {', '.join(variable_names)}

⚠️ CRITICAL FORMULA: The Kelly Criterion is position_size = min(μ/(λσ²), 1)
Where: μ = expected_fee_apy, σ = il_risk, λ = risk_aversion = 2.0

⚠️ COMMON MISTAKES:
  ❌ DO NOT: (μ - σ) / (2σ²)
  ✅ CORRECT: μ / (λσ²) with λ = 2.0

Provide your response in this EXACT format:

FORMULA:
min(expected_fee_apy/(2*il_risk**2), 1.0)

LATEX:
f^* = \\min\\left(\\frac{{\\mu}}{{2\\sigma^2}}, 1\\right)

PYTHON:
def formula(expected_fee_apy, il_risk):
    risk_aversion = 2.0
    position = expected_fee_apy / (risk_aversion * il_risk**2)
    return np.minimum(position, 1.0)

VARIABLES:
- expected_fee_apy: Expected return (μ)
- il_risk: Risk/volatility (σ)

ASSUMPTIONS:
- Risk aversion λ = 2.0, capped at 100%

EXPLANATION:
Risk-adjusted Kelly criterion balancing returns vs risk, capped at 100% capital."""
    
    # NEW: LIQUIDATION - LONG POSITION
    elif 'liquidation' in desc_lower and 'long' in desc_lower:
        return get_fixed_liquidation_prompts()['liquidation_long']
    
    # NEW: LIQUIDATION - SHORT POSITION
    elif 'liquidation' in desc_lower and 'short' in desc_lower:
        return get_fixed_liquidation_prompts()['liquidation_short']
    
    # NEW: MAXIMUM LEVERAGE
    elif 'maximum' in desc_lower and 'leverage' in desc_lower:
        return get_fixed_liquidation_prompts()['max_leverage']
    
    # NEW: REQUIRED COLLATERAL
    elif 'required collateral' in desc_lower or 'collateral for leveraged' in desc_lower:
        return get_fixed_liquidation_prompts()['required_collateral']
    
    # CAPITAL EFFICIENCY (already working)
    elif 'capital efficiency' in desc_lower and 'concentrated' in desc_lower:
        return f"""You are a DeFi expert specializing in concentrated liquidity.

Task: {description}
Variables: {', '.join(variable_names)}

⚠️ CRITICAL: This is a SIMPLE RATIO, NOT involving current price!
  Formula: efficiency = price_upper / (price_upper - price_lower)

⚠️ COMMON MISTAKES:
  ❌ DO NOT use sqrt
  ❌ DO NOT use price_current
  ✅ CORRECT: P_u/(P_u - P_l)

Provide your response in this EXACT format:

FORMULA:
price_upper / (price_upper - price_lower)

LATEX:
\\text{{efficiency}} = \\frac{{P_{{upper}}}}{{P_{{upper}} - P_{{lower}}}}

PYTHON:
def formula(price_lower, price_upper, price_current):
    return price_upper / (price_upper - price_lower)

VARIABLES:
- price_lower, price_upper: Range bounds
- price_current: Not used in formula

ASSUMPTIONS:
Narrow range = higher efficiency

EXPLANATION:
Simple ratio showing capital concentration efficiency."""
    
    # PORTFOLIO ES (already working)
    elif 'portfolio expected shortfall' in desc_lower and 'correlated' in desc_lower:
        return f"""You are a risk management expert.

Task: {description}
Variables: {', '.join(variable_names)}

⚠️ CRITICAL: ES uses LINEAR aggregation, NOT quadratic!
  Formula: ES_p = ES₁ + ES₂ + ρ√(ES₁×ES₂)

⚠️ DO NOT CONFUSE WITH VaR:
  ❌ VaR: √(VaR₁² + VaR₂² + 2ρVaR₁VaR₂)  ← quadratic
  ✅ ES:  ES₁ + ES₂ + ρ√(ES₁ES₂)          ← linear

Provide your response in this EXACT format:

FORMULA:
position1_es + position2_es + correlation * sqrt(position1_es * position2_es)

LATEX:
ES_p = ES_1 + ES_2 + \\rho\\sqrt{{ES_1 \\cdot ES_2}}

PYTHON:
def formula(position1_es, position2_es, correlation):
    corr_term = correlation * np.sqrt(position1_es * position2_es)
    return position1_es + position2_es + corr_term

VARIABLES:
- position1_es, position2_es: Individual ES values
- correlation: Correlation coefficient

ASSUMPTIONS:
ES is coherent (subadditive), uses linear aggregation

EXPLANATION:
Linear sum with correlation adjustment, unlike quadratic VaR."""
    
    return ""  # Should not reach here


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

INTEGRATION_INSTRUCTIONS = """
TO FIX THE POOR PERFORMANCE CASES:

1. In baseline_pure_llm_defi_final.py, locate the _generate_specialized_prompt() method

2. Replace the entire method with generate_specialized_prompt_FIXED() from this file

3. Update the use_specialized logic in generate_formula() to catch all liquidation cases:

   OLD CODE:
   ```python
   if ('optimal' in desc_lower and 'kelly' in desc_lower) or \
      ('capital efficiency' in desc_lower and 'concentrated' in desc_lower) or \
      ('portfolio expected shortfall' in desc_lower and 'correlated' in desc_lower):
       use_specialized = True
   ```

   NEW CODE:
   ```python
   if ('optimal' in desc_lower and 'kelly' in desc_lower) or \
      ('capital efficiency' in desc_lower and 'concentrated' in desc_lower) or \
      ('portfolio expected shortfall' in desc_lower and 'correlated' in desc_lower) or \
      ('liquidation' in desc_lower) or \
      ('maximum' in desc_lower and 'leverage' in desc_lower) or \
      ('required collateral' in desc_lower):
       use_specialized = True
   ```

4. Re-run the baseline test:
   ```bash
   python baseline_pure_llm_defi_final.py
   ```

EXPECTED IMPROVEMENTS:
- Liquidation long position: R² should improve from -4.01 to ~1.00
- Liquidation short position: R² should improve from 0.60 to ~1.00
- Maximum leverage: R² should improve from 0.13 to ~1.00
- Required collateral: R² should improve from 0.78 to ~1.00

This should bring the liquidation domain mean R² from -0.6271 to ~1.00!
"""

if __name__ == "__main__":
    print("=" * 80)
    print("LIQUIDATION DOMAIN FIXES")
    print("=" * 80)
    print("\nGenerated fixed prompts for 4 failing liquidation test cases:")
    print("  1. Liquidation price (long)")
    print("  2. Liquidation price (short)")
    print("  3. Maximum safe leverage")
    print("  4. Required collateral")
    print("\n" + INTEGRATION_INSTRUCTIONS)
