import math
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# ===== DATA FETCHING =====

COINGECKO_IDS = {
    "ETH": "ethereum",
    "DAI": "dai",
    "USDT": "tether",
    "USDC": "usd-coin",
    "BTC": "bitcoin",
    "UNI": "uniswap",
    "LINK": "chainlink",
    "WBTC": "wrapped-bitcoin",
    "SHIB": "shiba-inu",
    "AAVE": "aave",
    "CURVE": "curve-dao-token",
    "FRAX": "frax",
    "LUSD": "liquity-usd",
    "MIM": "magic-internet-money",
}


def get_coin_historical_prices(coin_symbol, days=90):
    """Fetch historical price data from CoinGecko"""

    coin_id = COINGECKO_IDS.get(coin_symbol.upper())

    if not coin_id:
        print(f"❌ Coin '{coin_symbol}' not found!")
        return []

    print(f"📊 Fetching {coin_symbol} prices ({days} days)...")

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        prices = []
        for timestamp, price in data["prices"]:
            prices.append(
                {"timestamp": timestamp, "date": datetime.fromtimestamp(timestamp / 1000), "price_usd": price}
            )
        return prices
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return []


# ===== UNISWAP V3 CORE MATH =====


class V3PoolMath:
    """Uniswap V3 mathematical functions"""

    @staticmethod
    def get_liquidity(amount0, amount1, price_lower, price_upper, price_current):
        """Calculate liquidity L for V3 position"""
        sqrt_Pa = math.sqrt(price_lower)
        sqrt_Pb = math.sqrt(price_upper)
        sqrt_P = math.sqrt(price_current)

        if price_current <= price_lower:
            # Only token0
            if amount0 > 0:
                L = amount0 * sqrt_Pa * sqrt_Pb / (sqrt_Pb - sqrt_Pa)
            else:
                L = 0
        elif price_current >= price_upper:
            # Only token1
            if amount1 > 0:
                L = amount1 / (sqrt_Pb - sqrt_Pa)
            else:
                L = 0
        else:
            # Both tokens
            if amount0 > 0:
                L0 = amount0 * sqrt_P * sqrt_Pb / (sqrt_Pb - sqrt_P)
            else:
                L0 = float("inf")

            if amount1 > 0:
                L1 = amount1 / (sqrt_P - sqrt_Pa)
            else:
                L1 = float("inf")

            L = min(L0, L1)

        return L

    @staticmethod
    def get_amounts(L, price_lower, price_upper, price_current):
        """Calculate token amounts from liquidity"""
        sqrt_Pa = math.sqrt(price_lower)
        sqrt_Pb = math.sqrt(price_upper)
        sqrt_P = math.sqrt(price_current)

        if price_current <= price_lower:
            amount0 = L * (sqrt_Pb - sqrt_Pa) / (sqrt_Pa * sqrt_Pb)
            amount1 = 0
        elif price_current >= price_upper:
            amount0 = 0
            amount1 = L * (sqrt_Pb - sqrt_Pa)
        else:
            amount0 = L * (sqrt_Pb - sqrt_P) / (sqrt_P * sqrt_Pb)
            amount1 = L * (sqrt_P - sqrt_Pa)

        return amount0, amount1


# ===== V3 CALCULATIONS =====


def calculate_v3_il_with_fees(
    initial_price,
    current_price,
    price_lower,
    price_upper,
    initial_x,
    initial_y,
    days_elapsed,
    daily_volume_usd,
    fee_tier=0.003,
    pool_tvl=100_000_000,
):
    """
    Calculate V3 Impermanent Loss and Fees

    Key differences from V2:
    - Liquidity is concentrated in [price_lower, price_upper]
    - Fees only earned when price is in range
    - Higher capital efficiency = more fees when in range
    """

    # Calculate initial liquidity
    L = V3PoolMath.get_liquidity(initial_x, initial_y, price_lower, price_upper, initial_price)

    # Get current amounts
    amount0_now, amount1_now = V3PoolMath.get_amounts(L, price_lower, price_upper, current_price)

    # Calculate values
    initial_value = initial_x * initial_price + initial_y
    pool_value = amount0_now * current_price + amount1_now
    hodl_value = initial_x * current_price + initial_y

    # Impermanent Loss
    il_dollar = pool_value - hodl_value
    il_percent = (il_dollar / hodl_value * 100) if hodl_value > 0 else 0

    # Check if in range
    in_range = price_lower <= current_price <= price_upper

    # Calculate time in range (simplified heuristic)
    if in_range:
        # Currently in range - assume was in range most of the time
        time_in_range_pct = 100
    else:
        # Out of range - estimate based on how far out
        if current_price < price_lower:
            distance_out = (price_lower - current_price) / price_lower * 100
        else:
            distance_out = (current_price - price_upper) / price_upper * 100

        # Rough estimate: farther out = less time in range
        time_in_range_pct = max(0, 100 - distance_out)

    time_in_range_days = days_elapsed * (time_in_range_pct / 100)

    # Calculate capital efficiency
    # V3 concentrates liquidity, so effective capital is higher
    full_range_ratio = 100  # Assume 100x would be "full range"
    actual_range_ratio = price_upper / price_lower
    capital_efficiency = min(full_range_ratio / actual_range_ratio, 50)  # Cap at 50x

    # Calculate fees
    # Assume position is small % of pool
    liquidity_share = 0.0001  # 0.01% of pool
    effective_share = liquidity_share * capital_efficiency

    # Fees only earned during time in range
    daily_fees = daily_volume_usd * fee_tier * effective_share
    total_fees = daily_fees * time_in_range_days

    # Net result
    net_result = total_fees + il_dollar

    # Range metrics
    range_width = (price_upper - price_lower) / price_lower * 100

    return {
        "il_percent": il_percent,
        "il_dollar": il_dollar,
        "daily_fees": daily_fees,
        "total_fees": total_fees,
        "net_result": net_result,
        "in_range": in_range,
        "time_in_range_pct": time_in_range_pct,
        "time_in_range_days": time_in_range_days,
        "price_lower": price_lower,
        "price_upper": price_upper,
        "range_width_pct": range_width,
        "capital_efficiency": capital_efficiency,
        "liquidity": L,
        "amount0_current": amount0_now,
        "amount1_current": amount1_now,
    }


# ===== BACKTESTING ENGINE =====


def backtest_v3_strategy(
    historical_prices,
    price_lower,
    price_upper,
    initial_coin=10,
    initial_usdc=20000,
    daily_volume=5000000,
    fee_tier=0.003,
):
    """
    Run V3 backtest with concentrated liquidity

    Compares:
    - V3 LP (concentrated)
    - V2 LP (full range)
    - HODL (no LP)
    """

    if not historical_prices:
        return pd.DataFrame()

    results = []
    initial_price = historical_prices[0]["price_usd"]

    # Track rebalancing
    rebalance_count = 0
    last_rebalance_price = initial_price

    for idx, day in enumerate(historical_prices):
        current_price = day["price_usd"]
        days_elapsed = idx + 1

        # V3 calculation
        v3_calc = calculate_v3_il_with_fees(
            initial_price=initial_price,
            current_price=current_price,
            price_lower=price_lower,
            price_upper=price_upper,
            initial_x=initial_coin,
            initial_y=initial_usdc,
            days_elapsed=days_elapsed,
            daily_volume_usd=daily_volume,
            fee_tier=fee_tier,
        )

        # V2 calculation (full range for comparison)
        v2_calc = calculate_v3_il_with_fees(
            initial_price=initial_price,
            current_price=current_price,
            price_lower=initial_price * 0.1,  # Very wide range
            price_upper=initial_price * 10,
            initial_x=initial_coin,
            initial_y=initial_usdc,
            days_elapsed=days_elapsed,
            daily_volume_usd=daily_volume,
            fee_tier=fee_tier,
        )

        # HODL value
        hodl_value = initial_coin * current_price + initial_usdc

        # V3 LP value
        v3_value = v3_calc["amount0_current"] * current_price + v3_calc["amount1_current"] + v3_calc["total_fees"]

        # V2 LP value
        v2_value = v2_calc["amount0_current"] * current_price + v2_calc["amount1_current"] + v2_calc["total_fees"]

        # Check if need to rebalance (V3 only)
        needs_rebalance = not v3_calc["in_range"]
        if needs_rebalance and abs(current_price - last_rebalance_price) / last_rebalance_price > 0.05:
            rebalance_count += 1
            last_rebalance_price = current_price

        results.append(
            {
                "date": day["date"],
                "day": days_elapsed,
                "price": current_price,
                "price_change_pct": ((current_price - initial_price) / initial_price) * 100,
                # V3 metrics
                "v3_in_range": v3_calc["in_range"],
                "v3_il_percent": v3_calc["il_percent"],
                "v3_il_dollar": v3_calc["il_dollar"],
                "v3_fees": v3_calc["total_fees"],
                "v3_value": v3_value,
                "v3_net": v3_value - hodl_value,
                # V2 metrics
                "v2_il_percent": v2_calc["il_percent"],
                "v2_fees": v2_calc["total_fees"],
                "v2_value": v2_value,
                "v2_net": v2_value - hodl_value,
                # HODL
                "hodl_value": hodl_value,
                # Comparisons
                "v3_vs_hodl": v3_value - hodl_value,
                "v3_vs_v2": v3_value - v2_value,
                "v3_advantage_pct": ((v3_value - hodl_value) / hodl_value) * 100,
                # Range info
                "price_lower": price_lower,
                "price_upper": price_upper,
                "time_in_range_pct": v3_calc["time_in_range_pct"],
                "rebalance_count": rebalance_count,
            }
        )

    return pd.DataFrame(results)


# ===== ANALYSIS =====


def analyze_v3_results(df):
    """Analyze V3 backtest results"""

    if df.empty:
        return "No data"

    analysis = {"summary": {}, "v3_performance": {}, "v2_comparison": {}, "range_analysis": {}}

    # Summary
    analysis["summary"] = {
        "total_days": len(df),
        "initial_price": df["price"].iloc[0],
        "final_price": df["price"].iloc[-1],
        "price_change_pct": df["price_change_pct"].iloc[-1],
        "final_v3_value": df["v3_value"].iloc[-1],
        "final_v2_value": df["v2_value"].iloc[-1],
        "final_hodl_value": df["hodl_value"].iloc[-1],
    }

    # V3 Performance
    analysis["v3_performance"] = {
        "days_in_range": df["v3_in_range"].sum(),
        "days_out_of_range": len(df) - df["v3_in_range"].sum(),
        "time_in_range_pct": (df["v3_in_range"].sum() / len(df)) * 100,
        "total_fees_earned": df["v3_fees"].iloc[-1],
        "final_il_dollar": df["v3_il_dollar"].iloc[-1],
        "final_il_percent": df["v3_il_percent"].iloc[-1],
        "net_vs_hodl": df["v3_vs_hodl"].iloc[-1],
        "days_beating_hodl": len(df[df["v3_vs_hodl"] > 0]),
        "rebalance_count": df["rebalance_count"].iloc[-1],
    }

    # V2 Comparison
    analysis["v2_comparison"] = {
        "v3_fees_vs_v2_fees": df["v3_fees"].iloc[-1] - df["v2_fees"].iloc[-1],
        "v3_il_vs_v2_il": df["v3_il_dollar"].iloc[-1] - df["v2_il_dollar"].iloc[-1],
        "v3_total_advantage": df["v3_vs_v2"].iloc[-1],
        "days_v3_beats_v2": len(df[df["v3_vs_v2"] > 0]),
    }

    # Range Analysis
    analysis["range_analysis"] = {
        "price_lower": df["price_lower"].iloc[0],
        "price_upper": df["price_upper"].iloc[0],
        "range_width_pct": ((df["price_upper"].iloc[0] - df["price_lower"].iloc[0]) / df["price_lower"].iloc[0]) * 100,
        "avg_time_in_range": df["time_in_range_pct"].mean(),
        "price_stayed_in_range": df["v3_in_range"].all(),
    }

    return analysis


def print_v3_analysis(coin_symbol, analysis):
    """Print V3 analysis report"""

    if isinstance(analysis, str):
        print(analysis)
        return

    print("\n" + "=" * 80)
    print("🚀 UNISWAP V3 CONCENTRATED LIQUIDITY BACKTEST")
    print("=" * 80)

    # Summary
    print("\n📊 SUMMARY")
    print("-" * 80)
    s = analysis["summary"]
    print(f"Duration: {s['total_days']} days")
    print(
        f"{coin_symbol.upper()} Price: ${s['initial_price']:.2f} → ${s['final_price']:.2f} ({s['price_change_pct']:+.2f}%)"
    )
    print(f"Final V3 Value: ${s['final_v3_value']:,.2f}")
    print(f"Final V2 Value: ${s['final_v2_value']:,.2f}")
    print(f"Final HODL Value: ${s['final_hodl_value']:,.2f}")

    # V3 Performance
    print("\n🎯 V3 CONCENTRATED POSITION PERFORMANCE")
    print("-" * 80)
    v3 = analysis["v3_performance"]
    print(f"Days In Range: {v3['days_in_range']}/{s['total_days']} ({v3['time_in_range_pct']:.1f}%)")
    print(f"Days Out of Range: {v3['days_out_of_range']} (earning $0 fees)")
    print(f"Total Fees Earned: ${v3['total_fees_earned']:,.2f}")
    print(f"Final IL: {v3['final_il_percent']:.2f}% (${v3['final_il_dollar']:,.2f})")
    print(f"Net vs HODL: ${v3['net_vs_hodl']:+,.2f}")
    print(f"Days Beating HODL: {v3['days_beating_hodl']}/{s['total_days']}")
    print(f"Rebalances Needed: {v3['rebalance_count']}")

    # V2 vs V3 Comparison
    print("\n⚔️  V3 vs V2 COMPARISON")
    print("-" * 80)
    v2 = analysis["v2_comparison"]
    print(f"V3 Fees vs V2 Fees: ${v2['v3_fees_vs_v2_fees']:+,.2f}")
    print(f"V3 IL vs V2 IL: ${v2['v3_il_vs_v2_il']:+,.2f}")
    print(f"V3 Total Advantage over V2: ${v2['v3_total_advantage']:+,.2f}")
    print(f"Days V3 Beats V2: {v2['days_v3_beats_v2']}/{s['total_days']}")

    # Range Analysis
    print("\n📏 RANGE ANALYSIS")
    print("-" * 80)
    r = analysis["range_analysis"]
    print(f"Price Range: ${r['price_lower']:.2f} - ${r['price_upper']:.2f}")
    print(f"Range Width: {r['range_width_pct']:.1f}%")
    print(f"Avg Time In Range: {r['avg_time_in_range']:.1f}%")
    print(f"Price Always In Range: {'Yes ✓' if r['price_stayed_in_range'] else 'No ✗'}")

    print("\n" + "=" * 80)


# ===== VISUALIZATION =====


def create_v3_visualizations(df, coin_symbol, save_path):
    """Create V3-specific visualizations"""

    if df.empty:
        return

    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle(f"Uniswap V3 Concentrated Liquidity Analysis - {coin_symbol.upper()}", fontsize=16, fontweight="bold")

    # 1. Price with Range Boundaries
    ax1 = axes[0, 0]
    ax1.plot(df["date"], df["price"], "b-", linewidth=2, label=f"{coin_symbol.upper()} Price")
    ax1.axhline(y=df["price_lower"].iloc[0], color="red", linestyle="--", linewidth=2, label="Lower Bound", alpha=0.7)
    ax1.axhline(y=df["price_upper"].iloc[0], color="red", linestyle="--", linewidth=2, label="Upper Bound", alpha=0.7)
    ax1.fill_between(
        df["date"],
        df["price_lower"].iloc[0],
        df["price_upper"].iloc[0],
        alpha=0.2,
        color="green",
        label="In Range Zone",
    )
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price (USD)")
    ax1.set_title("Price Movement vs V3 Range")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. In Range Status
    ax2 = axes[0, 1]
    in_range_colors = ["green" if x else "red" for x in df["v3_in_range"]]
    ax2.scatter(df["date"], df["v3_in_range"], c=in_range_colors, alpha=0.6, s=20)
    ax2.set_xlabel("Date")
    ax2.set_ylabel("In Range Status")
    ax2.set_title("V3 Position: In Range vs Out of Range")
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["Out of Range\n(No Fees)", "In Range\n(Earning Fees)"])
    ax2.grid(True, alpha=0.3)

    # 3. V3 vs V2 vs HODL
    ax3 = axes[0, 2]
    ax3.plot(df["date"], df["v3_value"], "purple", linewidth=2, label="V3 Concentrated")
    ax3.plot(df["date"], df["v2_value"], "blue", linewidth=2, label="V2 Full Range")
    ax3.plot(df["date"], df["hodl_value"], "orange", linewidth=2, label="HODL")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Portfolio Value (USD)")
    ax3.set_title("Strategy Comparison")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 4. IL Comparison
    ax4 = axes[1, 0]
    ax4.plot(df["date"], df["v3_il_percent"], "purple", linewidth=2, label="V3 IL%")
    ax4.plot(df["date"], df["v2_il_percent"], "blue", linewidth=2, label="V2 IL%")
    ax4.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax4.set_xlabel("Date")
    ax4.set_ylabel("Impermanent Loss (%)")
    ax4.set_title("IL Comparison: V3 vs V2")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 5. Fees Earned
    ax5 = axes[1, 1]
    ax5.plot(df["date"], df["v3_fees"], "green", linewidth=2, label="V3 Fees")
    ax5.plot(df["date"], df["v2_fees"], "lightgreen", linewidth=2, label="V2 Fees")
    ax5.fill_between(
        df["date"],
        df["v3_fees"],
        df["v2_fees"],
        where=(df["v3_fees"] >= df["v2_fees"]),
        alpha=0.3,
        color="green",
        label="V3 Advantage",
    )
    ax5.set_xlabel("Date")
    ax5.set_ylabel("Cumulative Fees (USD)")
    ax5.set_title("Fees Earned: V3 vs V2")
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # 6. V3 Net Advantage
    ax6 = axes[1, 2]
    colors = ["green" if x > 0 else "red" for x in df["v3_vs_hodl"]]
    ax6.bar(df["date"], df["v3_vs_hodl"], color=colors, alpha=0.6)
    ax6.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax6.set_xlabel("Date")
    ax6.set_ylabel("V3 Advantage (USD)")
    ax6.set_title("V3 vs HODL: Daily Net Position")
    ax6.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"\n📊 Visualization saved to: {save_path}")


# ===== MAIN EXECUTION =====


def run_v3_backtest(
    days=90,
    initial_coin=10,
    initial_usdc=20000,
    price_range_pct=10,
    daily_volume=50_000_000,
    coin_symbol="ETH",
    fee_tier=0.003,
    export_excel=True,
):
    """
    Run complete V3 backtest with concentrated liquidity

    Args:
        days: Backtest period
        initial_coin: Initial token0 amount
        initial_usdc: Initial token1 (USD) amount
        price_range_pct: Range width as % (e.g., 10 = ±10%)
        daily_volume: Average daily trading volume
        coin_symbol: Token symbol
        fee_tier: Fee tier (0.0001, 0.0005, 0.003, 0.01)
        export_excel: Export results to Excel
    """

    print("🚀 Starting Uniswap V3 Backtest...")
    print(f"Parameters: {days} days, {initial_coin} {coin_symbol.upper()}, ${initial_usdc} USDC")
    print(f"Range: ±{price_range_pct}%, Fee Tier: {fee_tier*100}%")
    print("-" * 80)

    # Fetch data
    print("\n1️⃣ Fetching historical prices...")
    historical_prices = get_coin_historical_prices(coin_symbol, days)

    if not historical_prices:
        print("❌ Failed to fetch price data")
        return None

    initial_price = historical_prices[0]["price_usd"]
    print(f"✅ Fetched {len(historical_prices)} days | Initial price: ${initial_price:.2f}")

    # Calculate range bounds
    price_lower = initial_price * (1 - price_range_pct / 100)
    price_upper = initial_price * (1 + price_range_pct / 100)

    print(f"\n📏 V3 Range: ${price_lower:.2f} - ${price_upper:.2f}")

    # Run backtest
    print("\n2️⃣ Running V3 backtest simulation...")
    results_df = backtest_v3_strategy(
        historical_prices=historical_prices,
        price_lower=price_lower,
        price_upper=price_upper,
        initial_coin=initial_coin,
        initial_usdc=initial_usdc,
        daily_volume=daily_volume,
        fee_tier=fee_tier,
    )

    if results_df.empty:
        print("❌ Backtest failed")
        return None

    print(f"✅ Backtest complete: {len(results_df)} days simulated")

    # Analyze
    print("\n3️⃣ Analyzing results...")
    analysis = analyze_v3_results(results_df)
    print_v3_analysis(coin_symbol, analysis)

    # Visualize
    print("\n4️⃣ Creating visualizations...")
    png_path = (
        f'v3_backtest_{coin_symbol.upper()}_range{price_range_pct}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    )
    create_v3_visualizations(results_df, coin_symbol, png_path)

    # Export
    if export_excel:
        print("\n5️⃣ Exporting to Excel...")
        excel_path = (
            f'v3_backtest_{coin_symbol.upper()}_range{price_range_pct}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )

        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            results_df.to_excel(writer, sheet_name="Daily Results", index=False)

            summary_df = pd.DataFrame([analysis["summary"]])
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

            v3_perf_df = pd.DataFrame([analysis["v3_performance"]])
            v3_perf_df.to_excel(writer, sheet_name="V3 Performance", index=False)

            comparison_df = pd.DataFrame([analysis["v2_comparison"]])
            comparison_df.to_excel(writer, sheet_name="V2 Comparison", index=False)

        print(f"✅ Excel file saved: {excel_path}")

    print("\n🎉 V3 Analysis complete!")

    return results_df, analysis


# ===== RUN ANALYSIS =====
if __name__ == "__main__":

    # Test different range strategies
    strategies = [
        {"range": 5, "name": "Tight"},  # ±5% - aggressive
        {"range": 15, "name": "Medium"},  # ±15% - balanced
        {"range": 30, "name": "Wide"},  # ±30% - conservative
    ]

    coin_symbol = "ETH"

    print("\n" + "=" * 80)
    print("COMPARING V3 RANGE STRATEGIES")
    print("=" * 80)

    for strategy in strategies:
        print(f"\n{'='*80}")
        print(f"🎯 Testing {strategy['name']} Strategy (±{strategy['range']}%)")
        print(f"{'='*80}")

        results, analysis = run_v3_backtest(
            days=90,
            initial_coin=10,
            initial_usdc=20000,
            price_range_pct=strategy["range"],
            daily_volume=50_000_000,
            coin_symbol=coin_symbol,
            fee_tier=0.003,
            export_excel=True,
        )

        print("\n" + "-" * 80)

    print("\n" + "=" * 80)
    print("KEY V3 INSIGHTS:")
    print("=" * 80)
    print("✅ Tight ranges (±5%) = Maximum fees BUT high rebalancing cost")
    print("✅ Wide ranges (±30%) = Lower fees BUT more stable, less management")
    print("✅ Optimal range depends on: volatility, gas costs, your time horizon")
    print("✅ Out of range = ZERO fees earned (critical difference from V2)")
    print("=" * 80)
