def calculate_quality_score(
    daily_volume_usd,
    fee_rate,
    tvl_usd,
    position_value_usd,
    current_price,
    initial_price,
    amount_token_a,
    amount_token_b,
    days_elapsed=1
):
    """
    Calculate quality score for a liquidity position
    
    quality_score > 1.0  = GOOD ✅ (fees > IL daily)
    quality_score 0.5-1  = MODERATE ⚠️ (fees ≈ IL)
    quality_score < 0.5  = POOR ❌ (IL > fees)
    """
    
    from decimal import Decimal
    import math
    
    # Step 1: Calculate total pool fees (distributed proportionally)
    total_pool_fees = daily_volume_usd * fee_rate
    your_pool_share = position_value_usd / tvl_usd
    daily_fees = total_pool_fees * your_pool_share
    
    # Step 2: Calculate IL percentage
    price_ratio = current_price / initial_price
    il_percent = (2 * math.sqrt(price_ratio) / (price_ratio + 1) - 1) * 100
    
    # Step 3: Calculate IL in dollars
    il_dollar_loss = abs(il_percent / 100 * position_value_usd)
    
    # Step 4: Calculate daily IL rate
    daily_il_rate = il_dollar_loss / days_elapsed
    
    # Step 5: Calculate quality score
    quality_score = daily_fees / daily_il_rate if daily_il_rate > 0 else float('inf')
    
    # Classify tier
    if quality_score > 1.0:
        tier = "✅ GOOD"
    elif quality_score >= 0.5:
        tier = "⚠️ MODERATE"
    else:
        tier = "❌ POOR"
    
    return {
        'daily_fees': round(daily_fees, 2),
        'il_percent': round(il_percent, 2),
        'il_dollar': round(il_dollar_loss, 2),
        'daily_il_rate': round(daily_il_rate, 2),
        'quality_score': round(quality_score, 2),
        'tier': tier
    }


# ============================================================
# EXAMPLES
# ============================================================

print("=" * 80)
print("QUALITY SCORE EXAMPLES")
print("=" * 80)

# Example 1: Your ETH/USDC backtest (POOR)
print("\n1️⃣  ETH/USDC (Bear Market - HIGH VOLATILITY)")
print("-" * 80)
result1 = calculate_quality_score(
    daily_volume_usd=50_000_000,      # $50M daily volume
    fee_rate=0.003,                    # 0.3% fee
    tvl_usd=1_000_000_000,            # $1B TVL
    position_value_usd=70_000,        # Your position value
    current_price=2_744,              # Current ETH price
    initial_price=4_773,              # Initial ETH price
    amount_token_a=10,                # 10 ETH
    amount_token_b=20_000,            # 20,000 USDC
    days_elapsed=91
)
print(f"  Daily Fees:        ${result1['daily_fees']}")
print(f"  IL % Loss:         {result1['il_percent']}%")
print(f"  IL $ Loss:         ${result1['il_dollar']}")
print(f"  Daily IL Rate:     ${result1['daily_il_rate']}/day")
print(f"  Quality Score:     {result1['quality_score']}")
print(f"  Tier:              {result1['tier']}")
print(f"  💡 Interpretation: Fees can't compensate for IL loss")

# Example 2: USDC/USDT (EXCELLENT - Stablecoin)
print("\n2️⃣  USDC/USDT (Stablecoin - NO VOLATILITY)")
print("-" * 80)
result2 = calculate_quality_score(
    daily_volume_usd=100_000_000,     # $100M daily volume
    fee_rate=0.0001,                  # 0.01% fee (stables have lower fees)
    tvl_usd=5_000_000_000,            # $5B TVL
    position_value_usd=20_000,        # Your position value
    current_price=1.0,                # Current USDT price
    initial_price=1.0,                # Initial USDT price (stable!)
    amount_token_a=10_000,            # 10,000 USDC
    amount_token_b=10_000,            # 10,000 USDT
    days_elapsed=30
)
print(f"  Daily Fees:        ${result2['daily_fees']}")
print(f"  IL % Loss:         {result2['il_percent']}%")
print(f"  IL $ Loss:         ${result2['il_dollar']}")
print(f"  Daily IL Rate:     ${result2['daily_il_rate']}/day")
print(f"  Quality Score:     {result2['quality_score']}")
print(f"  Tier:              {result2['tier']}")
print(f"  💡 Interpretation: Excellent! No IL, consistent fees")

# Example 3: DAI/USDC (GOOD - Low volatility stablecoin)
print("\n3️⃣  DAI/USDC (Stablecoin - VERY LOW VOLATILITY)")
print("-" * 80)
result3 = calculate_quality_score(
    daily_volume_usd=80_000_000,      # $80M daily volume
    fee_rate=0.0001,                  # 0.01% fee
    tvl_usd=3_000_000_000,            # $3B TVL
    position_value_usd=20_000,        # Your position value
    current_price=1.001,              # Tiny price difference
    initial_price=1.0,
    amount_token_a=10_000,
    amount_token_b=10_000,
    days_elapsed=30
)
print(f"  Daily Fees:        ${result3['daily_fees']}")
print(f"  IL % Loss:         {result3['il_percent']}%")
print(f"  IL $ Loss:         ${result3['il_dollar']}")
print(f"  Daily IL Rate:     ${result3['daily_il_rate']}/day")
print(f"  Quality Score:     {result3['quality_score']}")
print(f"  Tier:              {result3['tier']}")
print(f"  💡 Interpretation: Very good! Minimal IL, solid fees")

# Example 4: UNI/ETH (MODERATE - Medium volatility)
print("\n4️⃣  UNI/ETH (Medium Volatility)")
print("-" * 80)
result4 = calculate_quality_score(
    daily_volume_usd=30_000_000,      # $30M daily volume
    fee_rate=0.003,                   # 0.3% fee
    tvl_usd=500_000_000,              # $500M TVL
    position_value_usd=20_000,        # Your position value
    current_price=12,                 # UNI price
    initial_price=10,                 # Initial UNI price (20% increase)
    amount_token_a=1_000,             # 1000 UNI
    amount_token_b=10_000,            # 10 ETH worth
    days_elapsed=30
)
print(f"  Daily Fees:        ${result4['daily_fees']}")
print(f"  IL % Loss:         {result4['il_percent']}%")
print(f"  IL $ Loss:         ${result4['il_dollar']}")
print(f"  Daily IL Rate:     ${result4['daily_il_rate']}/day")
print(f"  Quality Score:     {result4['quality_score']}")
print(f"  Tier:              {result4['tier']}")
print(f"  💡 Interpretation: Moderate. Fees roughly cover IL")

# Example 5: SHIB/USDC (POOR - High volatility)
print("\n5️⃣  SHIB/USDC (Extreme Volatility)")
print("-" * 80)
result5 = calculate_quality_score(
    daily_volume_usd=20_000_000,      # $20M daily volume
    fee_rate=0.003,                   # 0.3% fee
    tvl_usd=100_000_000,              # $100M TVL
    position_value_usd=20_000,        # Your position value
    current_price=0.000015,           # SHIB price (highly volatile)
    initial_price=0.00002,            # Initial SHIB price (25% down)
    amount_token_a=1_000_000_000,     # 1B SHIB
    amount_token_b=10_000,            # 10,000 USDC
    days_elapsed=30
)
print(f"  Daily Fees:        ${result5['daily_fees']}")
print(f"  IL % Loss:         {result5['il_percent']}%")
print(f"  IL $ Loss:         ${result5['il_dollar']}")
print(f"  Daily IL Rate:     ${result5['daily_il_rate']}/day")
print(f"  Quality Score:     {result5['quality_score']}")
print(f"  Tier:              {result5['tier']}")
print(f"  💡 Interpretation: Poor. IL far exceeds fees")

# Summary
print("\n" + "=" * 80)
print("SUMMARY TABLE")
print("=" * 80)
print(f"{'Pool':<20} {'Quality Score':<15} {'Tier':<20} {'Action':<20}")
print("-" * 80)
print(f"{'ETH/USDC':<20} {result1['quality_score']:<15} {result1['tier']:<20} {'❌ AVOID':<20}")
print(f"{'USDC/USDT':<20} {result2['quality_score']:<15} {result2['tier']:<20} {'✅ GREAT':<20}")
print(f"{'DAI/USDC':<20} {result3['quality_score']:<15} {result3['tier']:<20} {'✅ GREAT':<20}")
print(f"{'UNI/ETH':<20} {result4['quality_score']:<15} {result4['tier']:<20} {'⚠️ MODERATE':<20}")
print(f"{'SHIB/USDC':<20} {result5['quality_score']:<15} {result5['tier']:<20} {'❌ AVOID':<20}")
print("=" * 80)
