import os

import numpy as np
from src.hybrid_system import HybridDiscoverySystem


def generate_advanced_defi(n_samples=150, noise_level=0.01):
    """
    Generate advanced DeFi formulas with realistic market dynamics.

    Args:
        n_samples: Number of samples per formula
        noise_level: Relative noise level for realistic data
    """
    system = HybridDiscoverySystem(domain="defi")

    print("=" * 60)
    print("Generating Advanced DeFi Formula Dataset")
    print("=" * 60)

    # Formula 1: Constant Product AMM Price Impact
    print("\n[1/10] Price Impact (Constant Product AMM)...")
    amount_in = np.random.uniform(1, 1000, n_samples)
    reserve_in = np.random.uniform(10000, 1000000, n_samples)
    reserve_out = np.random.uniform(10000, 1000000, n_samples)
    fee = 0.003  # 0.3% fee

    X = np.column_stack([amount_in, reserve_in, reserve_out])

    # x * y = k formula: amount_out = reserve_out * amount_in / (reserve_in + amount_in)
    # With fee: amount_in_with_fee = amount_in * (1 - fee)
    amount_in_with_fee = amount_in * (1 - fee)
    amount_out = reserve_out * amount_in_with_fee / (reserve_in + amount_in_with_fee)
    # Price impact as percentage of expected output
    expected_price = reserve_out / reserve_in
    actual_price = amount_out / amount_in
    price_impact = (expected_price - actual_price) / expected_price
    price_impact += np.random.normal(0, noise_level * np.mean(price_impact), n_samples)

    system.discover_validate_interpret(
        X=X,
        y=price_impact,
        variable_names=["amount_in", "reserve_in", "reserve_out"],
        variable_descriptions={
            "amount_in": "Swap input amount",
            "reserve_in": "Input token reserves",
            "reserve_out": "Output token reserves",
        },
        variable_units={"amount_in": "tokens", "reserve_in": "tokens", "reserve_out": "tokens"},
        description="Price impact percentage in constant product AMM (Uniswap V2 style)",
    )

    # Formula 2: Optimal LP Position Size with Fee APY
    print("[2/10] Optimal LP Position Sizing...")
    capital = np.random.uniform(1000, 500000, n_samples)
    fee_apy = np.random.uniform(0.05, 0.50, n_samples)  # 5-50% APY
    volatility = np.random.uniform(0.3, 2.0, n_samples)  # Annualized volatility
    risk_tolerance = np.random.uniform(0.1, 0.5, n_samples)

    X = np.column_stack([capital, fee_apy, volatility, risk_tolerance])

    # Position sizing: balance fee income vs IL risk
    # Kelly-inspired: size = capital * (expected_return / volatility^2) * risk_tolerance
    expected_return = fee_apy
    kelly_fraction = expected_return / (volatility**2)
    position_size = capital * kelly_fraction * risk_tolerance
    position_size = np.clip(position_size, 0, capital)  # Can't exceed capital
    position_size += np.random.normal(0, noise_level * np.mean(position_size), n_samples)

    system.discover_validate_interpret(
        X=X,
        y=position_size,
        variable_names=["capital", "fee_apy", "volatility", "risk_tolerance"],
        variable_descriptions={
            "capital": "Available capital",
            "fee_apy": "Expected fee APY",
            "volatility": "Pool price volatility (annualized)",
            "risk_tolerance": "Risk tolerance (0-1 scale)",
        },
        variable_units={
            "capital": "USD",
            "fee_apy": "percent",
            "volatility": "percent",
            "risk_tolerance": "dimensionless",
        },
        description="Optimal LP position size balancing fee income and IL risk",
    )

    # Formula 3: Time-Weighted Impermanent Loss
    print("[3/10] Time-Weighted Impermanent Loss...")
    days_held = np.random.uniform(1, 365, n_samples)
    price_ratio = np.random.uniform(0.5, 2.0, n_samples)  # Price multiplier
    initial_volatility = np.random.uniform(0.5, 2.5, n_samples)

    X = np.column_stack([days_held, price_ratio, initial_volatility])

    # Standard IL formula: 2*sqrt(price_ratio)/(1+price_ratio) - 1
    il_pct = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1
    # Time decay factor: IL realizes over time
    time_factor = 1 - np.exp(-days_held / 30)  # 30-day half-life
    # Volatility scaling
    vol_scaling = 1 + (initial_volatility - 1) * 0.2  # Higher vol = slightly more IL
    time_weighted_il = il_pct * time_factor * vol_scaling
    time_weighted_il += np.random.normal(0, noise_level * 0.5, n_samples)

    system.discover_validate_interpret(
        X=X,
        y=time_weighted_il,
        variable_names=["days_held", "price_ratio", "volatility"],
        variable_descriptions={
            "days_held": "Days position held",
            "price_ratio": "Final/initial price ratio",
            "volatility": "Pool volatility parameter",
        },
        variable_units={"days_held": "days", "price_ratio": "dimensionless", "volatility": "dimensionless"},
        description="Time-weighted impermanent loss with volatility adjustment",
    )

    # Formula 4: Liquidation Price (Long Position)
    print("[4/10] Liquidation Price - Long Position...")
    leverage = np.random.uniform(2, 20, n_samples)
    entry_price = np.random.uniform(1000, 50000, n_samples)
    maintenance_margin = np.random.uniform(0.03, 0.10, n_samples)  # 3-10%

    X = np.column_stack([leverage, entry_price, maintenance_margin])

    # Long liquidation: price * (1 - 1/leverage + maintenance_margin)
    liq_price_long = entry_price * (1 - 1 / leverage + maintenance_margin)
    liq_price_long += np.random.normal(0, noise_level * entry_price * 0.01, n_samples)

    system.discover_validate_interpret(
        X=X,
        y=liq_price_long,
        variable_names=["leverage", "entry_price", "maintenance_margin"],
        variable_descriptions={
            "leverage": "Position leverage multiplier",
            "entry_price": "Entry price",
            "maintenance_margin": "Maintenance margin ratio",
        },
        variable_units={"leverage": "x", "entry_price": "USD", "maintenance_margin": "percent"},
        description="Liquidation price for leveraged long position",
    )

    # Formula 5: Liquidation Price (Short Position)
    print("[5/10] Liquidation Price - Short Position...")
    leverage_short = np.random.uniform(2, 20, n_samples)
    entry_price_short = np.random.uniform(1000, 50000, n_samples)
    maintenance_margin_short = np.random.uniform(0.03, 0.10, n_samples)

    X = np.column_stack([leverage_short, entry_price_short, maintenance_margin_short])

    # Short liquidation: price * (1 + 1/leverage - maintenance_margin)
    liq_price_short = entry_price_short * (1 + 1 / leverage_short - maintenance_margin_short)
    liq_price_short += np.random.normal(0, noise_level * entry_price_short * 0.01, n_samples)

    system.discover_validate_interpret(
        X=X,
        y=liq_price_short,
        variable_names=["leverage", "entry_price", "maintenance_margin"],
        variable_descriptions={
            "leverage": "Position leverage multiplier",
            "entry_price": "Entry price",
            "maintenance_margin": "Maintenance margin ratio",
        },
        variable_units={"leverage": "x", "entry_price": "USD", "maintenance_margin": "percent"},
        description="Liquidation price for leveraged short position",
    )

    # Formula 6: Flash Loan Arbitrage Profit
    print("[6/10] Flash Loan Arbitrage Profit...")
    loan_amount = np.random.uniform(10000, 1000000, n_samples)
    price_diff = np.random.uniform(0.001, 0.05, n_samples)  # 0.1% to 5% difference
    gas_cost = np.random.uniform(10, 200, n_samples)
    flash_loan_fee = 0.0009  # 0.09% typical fee

    X = np.column_stack([loan_amount, price_diff, gas_cost])

    # Profit = loan_amount * price_diff - loan_amount * flash_loan_fee - gas_cost
    profit = loan_amount * price_diff - loan_amount * flash_loan_fee - gas_cost
    profit += np.random.normal(0, noise_level * np.abs(profit.mean()), n_samples)

    system.discover_validate_interpret(
        X=X,
        y=profit,
        variable_names=["loan_amount", "price_diff", "gas_cost"],
        variable_descriptions={
            "loan_amount": "Flash loan amount",
            "price_diff": "Price difference between venues",
            "gas_cost": "Transaction gas cost",
        },
        variable_units={"loan_amount": "USD", "price_diff": "percent", "gas_cost": "USD"},
        description="Expected profit from flash loan arbitrage",
    )

    # Formula 7: Concentrated Liquidity Range (Uniswap V3)
    print("[7/10] Concentrated Liquidity Range...")
    current_price = np.random.uniform(1000, 5000, n_samples)
    volatility_daily = np.random.uniform(0.01, 0.10, n_samples)  # 1-10% daily
    days_horizon = np.random.uniform(1, 30, n_samples)
    confidence = 0.95  # 95% confidence interval

    X = np.column_stack([current_price, volatility_daily, days_horizon])

    # Range width using volatility: width = price * vol * sqrt(days) * z_score
    z_score = 1.96  # 95% confidence
    range_width = current_price * volatility_daily * np.sqrt(days_horizon) * z_score
    range_width += np.random.normal(0, noise_level * range_width.mean(), n_samples)

    system.discover_validate_interpret(
        X=X,
        y=range_width,
        variable_names=["current_price", "volatility", "days"],
        variable_descriptions={
            "current_price": "Current asset price",
            "volatility": "Daily volatility",
            "days": "Time horizon in days",
        },
        variable_units={"current_price": "USD", "volatility": "percent", "days": "days"},
        description="Optimal concentrated liquidity range width (95% confidence)",
    )

    # Formula 8: Lending Protocol Utilization Rate
    print("[8/10] Lending Protocol Utilization Rate...")
    total_borrows = np.random.uniform(1000000, 50000000, n_samples)
    total_supply = np.random.uniform(2000000, 100000000, n_samples)
    # Ensure borrows <= supply
    total_borrows = np.minimum(total_borrows, total_supply * 0.95)

    X = np.column_stack([total_borrows, total_supply])

    utilization = total_borrows / total_supply
    utilization += np.random.normal(0, noise_level * 0.1, n_samples)
    utilization = np.clip(utilization, 0, 1)

    system.discover_validate_interpret(
        X=X,
        y=utilization,
        variable_names=["borrows", "supply"],
        variable_descriptions={"borrows": "Total borrowed amount", "supply": "Total supplied amount"},
        variable_units={"borrows": "USD", "supply": "USD"},
        description="Lending protocol utilization rate",
    )

    # Formula 9: Dynamic Borrow APY (Interest Rate Model)
    print("[9/10] Dynamic Borrow Interest Rate...")
    utilization_rate = np.random.uniform(0.1, 0.95, n_samples)
    base_rate = np.random.uniform(0.01, 0.05, n_samples)  # 1-5%
    optimal_util = 0.80  # Target 80% utilization
    slope1 = 0.05  # Below optimal
    slope2 = 0.50  # Above optimal (steep)

    X = np.column_stack([utilization_rate, base_rate])

    # Kinked interest rate model (like Aave)
    borrow_apy = np.where(
        utilization_rate <= optimal_util,
        base_rate + slope1 * (utilization_rate / optimal_util),
        base_rate + slope1 + slope2 * ((utilization_rate - optimal_util) / (1 - optimal_util)),
    )
    borrow_apy += np.random.normal(0, noise_level * 0.1, n_samples)

    system.discover_validate_interpret(
        X=X,
        y=borrow_apy,
        variable_names=["utilization", "base_rate"],
        variable_descriptions={"utilization": "Protocol utilization rate", "base_rate": "Base interest rate"},
        variable_units={"utilization": "percent", "base_rate": "percent"},
        description="Dynamic borrow APY with kinked rate model",
    )

    # Formula 10: Health Factor (Lending Protocol)
    print("[10/10] Lending Protocol Health Factor...")
    collateral_value = np.random.uniform(10000, 500000, n_samples)
    borrowed_value = np.random.uniform(1000, 300000, n_samples)
    liquidation_threshold = np.random.uniform(0.75, 0.85, n_samples)  # 75-85%
    # Ensure borrowed <= collateral * threshold
    borrowed_value = np.minimum(borrowed_value, collateral_value * liquidation_threshold * 0.95)

    X = np.column_stack([collateral_value, borrowed_value, liquidation_threshold])

    # Health factor = (collateral * liquidation_threshold) / borrowed
    health_factor = (collateral_value * liquidation_threshold) / borrowed_value
    health_factor += np.random.normal(0, noise_level * 0.1, n_samples)

    system.discover_validate_interpret(
        X=X,
        y=health_factor,
        variable_names=["collateral", "borrowed", "liq_threshold"],
        variable_descriptions={
            "collateral": "Collateral value in USD",
            "borrowed": "Borrowed value in USD",
            "liq_threshold": "Liquidation threshold ratio",
        },
        variable_units={"collateral": "USD", "borrowed": "USD", "liq_threshold": "percent"},
        description="Health factor for lending positions (>1 = safe, <1 = liquidatable)",
    )

    # Save results
    os.makedirs("data", exist_ok=True)
    system.save_results("data/defi_advanced.json")

    # Summary
    valid = sum(1 for r in system.results if r["validation"]["valid"])
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  Total formulas: {len(system.results)}")
    print(f"  Validated: {valid}/{len(system.results)} ({100*valid/len(system.results):.1f}%)")
    print(f"  Samples per formula: {n_samples}")
    print(f"  Noise level: {noise_level}")
    print(f"  Output: data/defi_advanced.json")
    print("=" * 60)

    return system


def generate_fee_optimization(n_samples=120, noise_level=0.0001):
    """
    Generate fee optimization formulas for different market scenarios.

    Args:
        n_samples: Number of samples per formula
        noise_level: Noise level for fee calculations
    """
    system = HybridDiscoverySystem(domain="defi")

    print("\n" + "=" * 60)
    print("Generating Fee Optimization Formulas")
    print("=" * 60)

    # Formula 11: Low Volatility - Volume-Driven Fee
    print("\n[11/15] Optimal Fee - Low Volatility Market...")
    volume_24h = np.random.uniform(100000, 10000000, n_samples)
    liquidity_low = np.random.uniform(1000000, 50000000, n_samples)
    volatility_low = np.random.uniform(0.05, 0.3, n_samples)  # 5-30% annual

    X = np.column_stack([volume_24h, liquidity_low, volatility_low])

    # Low vol: compete on fees, use volume/liquidity ratio
    # Base fee 0.05% (5 bps), increase with low liquidity
    volume_to_liquidity = volume_24h / liquidity_low
    optimal_fee_low = 0.0005 + 0.002 * (1 / (1 + volume_to_liquidity * 10))
    optimal_fee_low = np.clip(optimal_fee_low, 0.0001, 0.01)
    optimal_fee_low += np.random.normal(0, noise_level, n_samples)

    system.discover_validate_interpret(
        X=X,
        y=optimal_fee_low,
        variable_names=["volume_24h", "liquidity", "volatility"],
        variable_descriptions={
            "volume_24h": "24-hour trading volume",
            "liquidity": "Total pool liquidity",
            "volatility": "Annualized volatility",
        },
        variable_units={"volume_24h": "USD", "liquidity": "USD", "volatility": "percent"},
        description="Optimal fee for low volatility, competitive market",
    )

    # Formula 12: High Volatility - IL Compensation Fee
    print("[12/15] Optimal Fee - High Volatility Market...")
    volume_high = np.random.uniform(100000, 10000000, n_samples)
    liquidity_high = np.random.uniform(1000000, 50000000, n_samples)
    volatility_high = np.random.uniform(0.5, 3.0, n_samples)  # 50-300% annual

    X = np.column_stack([volume_high, liquidity_high, volatility_high])

    # High vol: fee must compensate for IL risk
    # Base 0.3% + volatility premium
    expected_il_annual = 0.5 * volatility_high**2  # Simplified IL expectation
    turnover_rate = volume_high / liquidity_high  # Annual turnovers
    # Fee needs to cover IL over typical holding period
    optimal_fee_high = 0.003 + expected_il_annual / (turnover_rate * 365)
    optimal_fee_high = np.clip(optimal_fee_high, 0.001, 0.03)
    optimal_fee_high += np.random.normal(0, noise_level * 10, n_samples)

    system.discover_validate_interpret(
        X=X,
        y=optimal_fee_high,
        variable_names=["volume_24h", "liquidity", "volatility"],
        variable_descriptions={
            "volume_24h": "24-hour trading volume",
            "liquidity": "Total pool liquidity",
            "volatility": "Annualized volatility",
        },
        variable_units={"volume_24h": "USD", "liquidity": "USD", "volatility": "percent"},
        description="Optimal fee for high volatility market (IL compensation)",
    )

    # Formula 13: Trending Market - Dynamic Fee
    print("[13/15] Optimal Fee - Trending Market...")
    volume_trend = np.random.uniform(100000, 10000000, n_samples)
    price_momentum = np.random.uniform(-0.5, 0.5, n_samples)  # Price change rate
    liquidity_depth = np.random.uniform(1000000, 50000000, n_samples)
    volatility_trend = np.random.uniform(0.3, 1.5, n_samples)

    X = np.column_stack([volume_trend, price_momentum, liquidity_depth, volatility_trend])

    # Trending: higher fees during directional moves (more IL risk)
    # Lower fees when price stable
    momentum_factor = 1 + np.abs(price_momentum)  # Stronger trend = higher fees
    base_fee = 0.003
    optimal_fee_trend = base_fee * momentum_factor * (1 + volatility_trend * 0.2)
    optimal_fee_trend = np.clip(optimal_fee_trend, 0.001, 0.02)
    optimal_fee_trend += np.random.normal(0, noise_level * 10, n_samples)

    system.discover_validate_interpret(
        X=X,
        y=optimal_fee_trend,
        variable_names=["volume", "momentum", "liquidity", "volatility"],
        variable_descriptions={
            "volume": "24-hour trading volume",
            "momentum": "Price momentum (daily change)",
            "liquidity": "Pool liquidity depth",
            "volatility": "Annualized volatility",
        },
        variable_units={"volume": "USD", "momentum": "percent", "liquidity": "USD", "volatility": "percent"},
        description="Dynamic fee for trending market (momentum-adjusted)",
    )

    # Formula 14: Ranging Market - Optimized for Volume
    print("[14/15] Optimal Fee - Ranging Market...")
    volume_range = np.random.uniform(100000, 10000000, n_samples)
    price_range_width = np.random.uniform(0.02, 0.15, n_samples)  # 2-15% range
    liquidity_range = np.random.uniform(1000000, 50000000, n_samples)
    competitor_fee = np.random.uniform(0.001, 0.01, n_samples)

    X = np.column_stack([volume_range, price_range_width, liquidity_range, competitor_fee])

    # Ranging: maximize volume, compete with other pools
    # Lower fees to capture market share, but cover costs
    volume_share = volume_range / (liquidity_range * 0.01)  # Expected daily volume
    # Undercut competitor slightly, but maintain minimum
    optimal_fee_range = competitor_fee * 0.8  # 20% discount
    # But ensure minimum profitability based on range width (proxy for IL risk)
    min_fee = 0.0005 + price_range_width * 0.01
    optimal_fee_range = np.maximum(optimal_fee_range, min_fee)
    optimal_fee_range = np.clip(optimal_fee_range, 0.0001, 0.01)
    optimal_fee_range += np.random.normal(0, noise_level * 5, n_samples)

    system.discover_validate_interpret(
        X=X,
        y=optimal_fee_range,
        variable_names=["volume", "price_range", "liquidity", "competitor_fee"],
        variable_descriptions={
            "volume": "24-hour trading volume",
            "price_range": "Price range width",
            "liquidity": "Pool liquidity",
            "competitor_fee": "Competitor pool fee",
        },
        variable_units={"volume": "USD", "price_range": "percent", "liquidity": "USD", "competitor_fee": "percent"},
        description="Optimal fee for ranging market (volume-maximizing)",
    )

    # Formula 15: Volatile/Choppy Market - Risk-Adjusted Fee
    print("[15/15] Optimal Fee - Volatile/Choppy Market...")
    volume_vol = np.random.uniform(100000, 10000000, n_samples)
    realized_vol = np.random.uniform(1.0, 5.0, n_samples)  # Very high vol
    liquidity_vol = np.random.uniform(1000000, 50000000, n_samples)
    daily_trades = np.random.uniform(100, 10000, n_samples)

    X = np.column_stack([volume_vol, realized_vol, liquidity_vol, daily_trades])

    # Volatile: maximize fee income to offset high IL
    # Fee should scale with realized volatility
    avg_trade_size = volume_vol / daily_trades
    # Larger trades can bear higher fees
    size_factor = 1 + np.log1p(avg_trade_size / 10000) * 0.1
    # Base fee increases with volatility squared (IL risk)
    optimal_fee_vol = 0.005 + 0.002 * realized_vol * size_factor
    optimal_fee_vol = np.clip(optimal_fee_vol, 0.003, 0.05)
    optimal_fee_vol += np.random.normal(0, noise_level * 20, n_samples)

    system.discover_validate_interpret(
        X=X,
        y=optimal_fee_vol,
        variable_names=["volume", "volatility", "liquidity", "trades"],
        variable_descriptions={
            "volume": "24-hour trading volume",
            "volatility": "Realized volatility (very high)",
            "liquidity": "Pool liquidity",
            "trades": "Number of daily trades",
        },
        variable_units={"volume": "USD", "volatility": "percent", "liquidity": "USD", "trades": "count"},
        description="Optimal fee for volatile/choppy market (high IL protection)",
    )

    # Save results
    system.save_results("data/defi_fees.json")

    # Summary
    valid = sum(1 for r in system.results if r["validation"]["valid"])
    print("\n" + "=" * 60)
    print(f"FEE OPTIMIZATION SUMMARY:")
    print(f"  Total formulas: {len(system.results)}")
    print(f"  Validated: {valid}/{len(system.results)} ({100*valid/len(system.results):.1f}%)")
    print(f"  Samples per formula: {n_samples}")
    print(f"  Output: data/defi_fees.json")
    print("=" * 60)

    return system


if __name__ == "__main__":
    # Generate main advanced DeFi formulas
    print("\nPHASE 1: Advanced DeFi Formulas")
    system1 = generate_advanced_defi(n_samples=150, noise_level=0.01)

    # Generate fee optimization formulas
    print("\nPHASE 2: Fee Optimization Formulas")
    system2 = generate_fee_optimization(n_samples=120, noise_level=0.0001)

    # Combined summary
    print("\n" + "=" * 60)
    print("COMPLETE GENERATION SUMMARY")
    print("=" * 60)
    print(f"Phase 1 (Advanced): 10 formulas → data/defi_advanced.json")
    print(f"Phase 2 (Fees): 5 formulas → data/defi_fees.json")
    print(f"Total: 15 advanced DeFi formulas generated")
    print("=" * 60)
