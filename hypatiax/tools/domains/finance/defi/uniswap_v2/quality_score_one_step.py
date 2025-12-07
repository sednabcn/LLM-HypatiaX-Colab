def calculate_quality_score(
    daily_volume_usd, fee_rate, tvl_usd, current_price, initial_price, amount_token_a, amount_token_b
):
    """
    Calculate pool quality score

    quality_score > 1.0  = GOOD (collect more fees than IL loss)
    quality_score 0.5-1  = MODERATE (fees ≈ IL loss)
    quality_score < 0.5  = WORSE (IL loss > fees)

    position_value = token_a * price + token_b
    pool_share = position_value / pool_tvl
    daily_fees = daily_volume * fee_rate * pool_share
    """

    # Step 1: Calculate daily fees (use current TVL and volume)
    position_value = amount_token_a * current_price + amount_token_b
    daily_fees = daily_volume_usd * fee_rate * (position_value / tvl_usd)

    # Step 2: Calculate IL percentage (ratio of CURRENT to INITIAL price)
    price_ratio = current_price / initial_price
    il_percent = (2 * (price_ratio**0.5) / (price_ratio + 1) - 1) * 100

    # Step 3: Calculate IL in dollars (use CURRENT price for valuation)

    il_dollar_loss = abs(il_percent / 100 * position_value)

    # Step 4: Calculate quality score
    quality_score = daily_fees / il_dollar_loss if il_dollar_loss > 0 else float("inf")

    return {
        "daily_fees": daily_fees,
        "il_percent": il_percent,
        "il_dollar": il_dollar_loss,
        "quality_score": quality_score,
        "tier": classify_tier(quality_score),
    }


def classify_tier(score):
    if score > 1.0:
        return "GOOD ✅"
    elif score >= 0.5:
        return "MODERATE ⚠️"
    else:
        return "WORSE ❌"


"""
1. Improved Quality Score Method

python

calculate_quality_score(daily_fees, il_dollar, days_elapsed)

Calculates: quality_score = daily_fees / daily_il_rate

Interpretation:

> 1.0 = GOOD ✅ (fees cover IL daily)
0.5-1 = MODERATE ⚠️ (fees ≈ IL)
< 0.5 = POOR ❌ (IL exceeds fees)



2. More Accurate Fee Calculation

Fixed the fee formula to properly calculate pool share:

python

position_value = token_a * price + token_b

pool_share = position_value / pool_tvl

daily_fees = daily_volume * fee_rate * pool_share

3. Enhanced Results Output

Now displays:

Quality Score (numeric)
Quality Tier (GOOD/MODERATE/POOR)
Daily IL rate
Pool share percentage

4. Better Summary Statistics
Added:

Count of Good/Excellent quality positions

Average quality score across all positions

Quality score interpretation guide

The quality score gives you a quick way to evaluate if a pool's trading fees are sufficient to compensate for impermanent loss over time. For example, the DAI/USDC position will show an excellent quality score because minimal IL + decent fees = great pool!


Want me to create a visualization or add any other features?RetryRHow to calculate daily_rateGreat question! Let me explain how to calculate the daily_rate (daily IL rate) step by step.


Daily IL Rate Calculation

The daily IL rate represents how much impermanent loss you're experiencing per day on average.


Formula:

python


daily_il_rate = abs(total_il_dollar) / days_elapsed



Step-by-Step Example:

Let's use the ETH/USDC position from your code:

Given:

Initial price: $2,000
Current price: $3,000 (50% increase)
Position: 1 ETH + 2,000 USDC
Days elapsed: 30 days

Step 1: Calculate IL Percentage
python


ratio = 3000 / 2000 = 1.5

il_percent = (2 * sqrt(1.5) / (1.5 + 1) - 1) * 100
il_percent = (2 * 1.2247 / 2.5 - 1) * 100
il_percent = (0.9798 - 1) * 100
il_percent = -2.02%



Step 2: Calculate Current Position Value


python


current_value = (1 ETH * $3,000) + 2,000 USDC


current_value = $3,000 + $2,000 = $5,000


Step 3: Calculate Total IL in Dollars


python

il_dollar = current_value * (il_percent / 100)
il_dollar = $5,000 * (-2.02 / 100)
il_dollar = -$101
(Negative means you lost $101 compared to just holding)
Step 4: Calculate Daily IL Rate
python

daily_il_rate = abs(-101) / 30 days
daily_il_rate = $3.37 per day

What This Means:

You're losing an average of $3.37 per day to impermanent loss. Now you can compare this to your daily fee earnings:

If daily fees = $10 → Quality Score = 10 / 3.37 = 2.97 ✅ GOOD
If daily fees = $2 → Quality Score = 2 / 3.37 = 0.59 ⚠️ MODERATE
If daily fees = $1 → Quality Score = 1 / 3.37 = 0.30 ❌ POOR

Key Insights:

Daily IL Rate is NOT constant - it's an average over the elapsed period
Higher volatility = higher daily IL rate
Stablecoin pairs (DAI/USDC) have very low daily IL rates (~$0.01/day)
The earlier you exit, the lower your total IL might be

Would you like me to create a function that shows how the daily IL rate changes over time, or add a visualization showing the relationship between daily fees and daily IL rate?

"""
