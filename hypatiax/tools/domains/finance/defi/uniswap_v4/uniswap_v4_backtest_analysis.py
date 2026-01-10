"""
Uniswap V4 Backtest Analysis
=============================
Backtest V4 positions with hooks vs V3 vs HODL.

IMPORTANT: V4 concentrated liquidity math is SAME AS V3!
V4 advantages come from:
- Dynamic fees via hooks
- Gas savings (flash accounting, native ETH)
- Singleton architecture
"""

import math
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# ===== DATA FETCHING (SAME AS BEFORE) =====

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
}


def get_coin_historical_prices(coin_symbol, days=90):
    """Fetch historical price data"""
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
                {
                    "timestamp": timestamp,
                    "date": datetime.fromtimestamp(timestamp / 1000),
                    "price_usd": price,
                }
            )
        return prices
    except Exception as e:
        print(f"Error: {e}")
        return []


# ===== V4 MATH (SAME AS V3) =====


class V4PoolMath:
    """V4 uses V3's concentrated liquidity math"""

    @staticmethod
    def get_liquidity(amount0, amount1, price_lower, price_upper, price_current):
        """Calculate liquidity (SAME AS V3)"""
        sqrt_Pa = math.sqrt(price_lower)
        sqrt_Pb = math.sqrt(price_upper)
        sqrt_P = math.sqrt(price_current)

        if price_current <= price_lower:
            L = amount0 * sqrt_Pa * sqrt_Pb / (sqrt_Pb - sqrt_Pa) if amount0 > 0 else 0
        elif price_current >= price_upper:
            L = amount1 / (sqrt_Pb - sqrt_Pa) if amount1 > 0 else 0
        else:
            L0 = (
                amount0 * sqrt_P * sqrt_Pb / (sqrt_Pb - sqrt_P)
                if amount0 > 0
                else float("inf")
            )
            L1 = amount1 / (sqrt_P - sqrt_Pa) if amount1 > 0 else float("inf")
            L = min(L0, L1)

        return L

    @staticmethod
    def get_amounts(L, price_lower, price_upper, price_current):
        """Calculate amounts (SAME AS V3)"""
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


# ===== V4 HOOK SIMULATOR =====


def simulate_dynamic_fee_hook(
    price_current, price_initial, base_fee, volatility_estimate
):
    """
    Simulate dynamic fee adjustment via V4 hook

    Args:
        price_current: Current price
        price_initial: Initial price
        base_fee: Base fee tier
        volatility_estimate: Estimated volatility

    Returns:
        Adjusted fee tier
    """
    # Calculate price movement
    price_change = abs(price_current - price_initial) / price_initial

    # Higher volatility = higher fees (protect LPs)
    volatility_multiplier = 1.0 + (volatility_estimate * 1.5)

    # Large price movements = higher fees
    movement_multiplier = 1.0 + (price_change * 0.5)

    # Combined multiplier (capped at 2x)
    total_multiplier = min(2.0, volatility_multiplier * movement_multiplier)

    return base_fee * total_multiplier


# ===== V4 BACKTEST ENGINE =====


def backtest_v4_strategy(
    historical_prices,
    price_lower,
    price_upper,
    initial_coin=10,
    initial_usdc=20000,
    daily_volume=5000000,
    base_fee=0.003,
    enable_hooks=True,
):
    """
    Run V4 backtest

    Compares:
    - V4 with hooks
    - V3 (concentrated, no hooks)
    - HODL
    """

    if not historical_prices:
        return pd.DataFrame()

    results = []
    initial_price = historical_prices[0]["price_usd"]

    # Track volatility (rolling 7-day)
    price_history = []

    for idx, day in enumerate(historical_prices):
        current_price = day["price_usd"]
        days_elapsed = idx + 1

        # Update price history for volatility calculation
        price_history.append(current_price)
        if len(price_history) > 7:
            price_history.pop(0)

        # Calculate volatility (std dev of returns)
        if len(price_history) > 1:
            returns = [
                price_history[i] / price_history[i - 1] - 1
                for i in range(1, len(price_history))
            ]
            volatility = np.std(returns) if returns else 0.3
        else:
            volatility = 0.3

        # V4 calculation (with hook)
        if enable_hooks:
            effective_fee_v4 = simulate_dynamic_fee_hook(
                current_price, initial_price, base_fee, volatility
            )
        else:
            effective_fee_v4 = base_fee

        v4_calc = calculate_position_metrics(
            initial_price,
            current_price,
            price_lower,
            price_upper,
            initial_coin,
            initial_usdc,
            days_elapsed,
            daily_volume,
            effective_fee_v4,
        )

        # V3 calculation (no hooks, static fee)
        v3_calc = calculate_position_metrics(
            initial_price,
            current_price,
            price_lower,
            price_upper,
            initial_coin,
            initial_usdc,
            days_elapsed,
            daily_volume,
            base_fee,
        )

        # HODL
        hodl_value = initial_coin * current_price + initial_usdc

        # V4 gas savings (flash accounting + native ETH)
        v4_gas_savings = days_elapsed * 5 * 0.5  # ~$2.50/day saved

        # V4 total value
        v4_value = (
            v4_calc["amount0"] * current_price
            + v4_calc["amount1"]
            + v4_calc["fees"]
            + v4_gas_savings
        )

        # V3 total value
        v3_value = (
            v3_calc["amount0"] * current_price + v3_calc["amount1"] + v3_calc["fees"]
        )

        results.append(
            {
                "date": day["date"],
                "day": days_elapsed,
                "price": current_price,
                "volatility": volatility,
                "price_change_pct": ((current_price - initial_price) / initial_price)
                * 100,
                # V4 metrics
                "v4_in_range": v4_calc["in_range"],
                "v4_effective_fee": effective_fee_v4 * 100,
                "v4_fees": v4_calc["fees"],
                "v4_gas_savings": v4_gas_savings,
                "v4_value": v4_value,
                "v4_il": v4_calc["il"],
                # V3 metrics
                "v3_in_range": v3_calc["in_range"],
                "v3_fees": v3_calc["fees"],
                "v3_value": v3_value,
                "v3_il": v3_calc["il"],
                # HODL
                "hodl_value": hodl_value,
                # Comparisons
                "v4_vs_hodl": v4_value - hodl_value,
                "v4_vs_v3": v4_value - v3_value,
                "v4_advantage_pct": ((v4_value - hodl_value) / hodl_value) * 100,
                # Range info
                "price_lower": price_lower,
                "price_upper": price_upper,
            }
        )

    return pd.DataFrame(results)


def calculate_position_metrics(
    initial_price,
    current_price,
    price_lower,
    price_upper,
    initial_x,
    initial_y,
    days_elapsed,
    daily_volume,
    fee_tier,
):
    """Calculate position metrics (same logic as V3)"""

    # Calculate liquidity
    L = V4PoolMath.get_liquidity(
        initial_x, initial_y, price_lower, price_upper, initial_price
    )

    # Current amounts
    amount0, amount1 = V4PoolMath.get_amounts(
        L, price_lower, price_upper, current_price
    )

    # Values
    initial_value = initial_x * initial_price + initial_y
    current_value = amount0 * current_price + amount1
    hodl_value = initial_x * current_price + initial_y

    # IL
    il = current_value - hodl_value

    # In range check
    in_range = price_lower <= current_price <= price_upper

    # Fee calculation
    if in_range:
        time_in_range = 1.0
    else:
        if current_price < price_lower:
            distance = (price_lower - current_price) / price_lower
        else:
            distance = (current_price - price_upper) / price_upper
        time_in_range = max(0, 1 - distance)

    # Capital efficiency
    range_factor = 100 / (price_upper / price_lower) if price_lower > 0 else 1
    effective_share = 0.0001 * min(range_factor, 50)

    total_volume = daily_volume * days_elapsed * time_in_range
    fees = total_volume * fee_tier * effective_share

    return {
        "amount0": amount0,
        "amount1": amount1,
        "il": il,
        "fees": fees,
        "in_range": in_range,
    }


# ===== ANALYSIS =====


def analyze_v4_results(df):
    """Analyze V4 backtest results"""

    if df.empty:
        return "No data"

    analysis = {
        "summary": {
            "total_days": len(df),
            "initial_price": df["price"].iloc[0],
            "final_price": df["price"].iloc[-1],
            "price_change_pct": df["price_change_pct"].iloc[-1],
            "avg_volatility": df["volatility"].mean(),
            "final_v4_value": df["v4_value"].iloc[-1],
            "final_v3_value": df["v3_value"].iloc[-1],
            "final_hodl_value": df["hodl_value"].iloc[-1],
        },
        "v4_performance": {
            "days_in_range": df["v4_in_range"].sum(),
            "total_fees": df["v4_fees"].iloc[-1],
            "total_gas_savings": df["v4_gas_savings"].iloc[-1],
            "final_il": df["v4_il"].iloc[-1],
            "net_vs_hodl": df["v4_vs_hodl"].iloc[-1],
            "days_beating_hodl": len(df[df["v4_vs_hodl"] > 0]),
            "avg_effective_fee": df["v4_effective_fee"].mean(),
        },
        "v4_vs_v3": {
            "fee_advantage": df["v4_fees"].iloc[-1] - df["v3_fees"].iloc[-1],
            "gas_savings_advantage": df["v4_gas_savings"].iloc[-1],
            "total_advantage": df["v4_vs_v3"].iloc[-1],
            "days_v4_wins": len(df[df["v4_vs_v3"] > 0]),
        },
    }

    return analysis


def print_v4_analysis(coin_symbol, analysis):
    """Print V4 analysis report"""

    if isinstance(analysis, str):
        print(analysis)
        return

    print("\n" + "=" * 80)
    print("🚀 UNISWAP V4 BACKTEST ANALYSIS")
    print("=" * 80)

    # Summary
    print("\n📊 SUMMARY")
    print("-" * 80)
    s = analysis["summary"]
    print(f"Duration: {s['total_days']} days")
    print(
        f"{coin_symbol.upper()} Price: ${s['initial_price']:.2f} → ${s['final_price']:.2f} ({s['price_change_pct']:+.2f}%)"
    )
    print(f"Avg Volatility: {s['avg_volatility']:.2%}")
    print(f"Final V4 Value: ${s['final_v4_value']:,.2f}")
    print(f"Final V3 Value: ${s['final_v3_value']:,.2f}")
    print(f"Final HODL Value: ${s['final_hodl_value']:,.2f}")

    # V4 Performance
    print("\n🎯 V4 PERFORMANCE (With Hooks)")
    print("-" * 80)
    v4 = analysis["v4_performance"]
    print(f"Days In Range: {v4['days_in_range']}/{s['total_days']}")
    print(f"Total Fees (Dynamic): ${v4['total_fees']:,.2f}")
    print(f"Gas Savings (V4): ${v4['total_gas_savings']:,.2f}")
    print(f"Avg Effective Fee: {v4['avg_effective_fee']:.3f}%")
    print(f"Final IL: ${v4['final_il']:,.2f}")
    print(f"Net vs HODL: ${v4['net_vs_hodl']:+,.2f}")
    print(f"Days Beating HODL: {v4['days_beating_hodl']}/{s['total_days']}")

    # V4 vs V3
    print("\n⚔️  V4 vs V3 COMPARISON")
    print("-" * 80)
    comp = analysis["v4_vs_v3"]
    print(f"Fee Advantage (Hooks): ${comp['fee_advantage']:+,.2f}")
    print(f"Gas Savings (V4 Architecture): ${comp['gas_savings_advantage']:,.2f}")
    print(f"Total V4 Advantage: ${comp['total_advantage']:+,.2f}")
    print(f"Days V4 Beats V3: {comp['days_v4_wins']}/{s['total_days']}")

    print("\n" + "=" * 80)


# ===== VISUALIZATION =====


def create_v4_visualizations(df, coin_symbol, save_path):
    """Create V4 visualizations"""

    if df.empty:
        return

    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle(
        f"Uniswap V4 vs V3 Backtest - {coin_symbol.upper()}",
        fontsize=16,
        fontweight="bold",
    )

    # 1. Price with dynamic fees
    ax1 = axes[0, 0]
    ax1_twin = ax1.twinx()
    ax1.plot(df["date"], df["price"], "b-", linewidth=2, label="Price")
    ax1_twin.plot(
        df["date"], df["v4_effective_fee"], "r-", linewidth=2, label="V4 Dynamic Fee"
    )
    ax1.axhline(y=df["price_lower"].iloc[0], color="gray", linestyle="--", alpha=0.5)
    ax1.axhline(y=df["price_upper"].iloc[0], color="gray", linestyle="--", alpha=0.5)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price (USD)", color="b")
    ax1_twin.set_ylabel("Effective Fee (%)", color="r")
    ax1.set_title("Price & Dynamic Fee (V4 Hook)")
    ax1.legend(loc="upper left")
    ax1_twin.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)

    # 2. V4 vs V3 vs HODL
    ax2 = axes[0, 1]
    ax2.plot(
        df["date"],
        df["v4_value"],
        "purple",
        linewidth=2,
        label="V4 (Hooks + Gas Savings)",
    )
    ax2.plot(df["date"], df["v3_value"], "blue", linewidth=2, label="V3 (Concentrated)")
    ax2.plot(df["date"], df["hodl_value"], "orange", linewidth=2, label="HODL")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Portfolio Value (USD)")
    ax2.set_title("V4 vs V3 vs HODL")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. Fees comparison
    ax3 = axes[0, 2]
    ax3.plot(df["date"], df["v4_fees"], "green", linewidth=2, label="V4 Fees (Dynamic)")
    ax3.plot(
        df["date"], df["v3_fees"], "lightgreen", linewidth=2, label="V3 Fees (Static)"
    )
    ax3.fill_between(
        df["date"],
        df["v4_fees"],
        df["v3_fees"],
        where=(df["v4_fees"] >= df["v3_fees"]),
        alpha=0.3,
        color="green",
    )
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Cumulative Fees (USD)")
    ax3.set_title("Fee Earnings: V4 vs V3")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 4. V4 Gas Savings
    ax4 = axes[1, 0]
    ax4.plot(df["date"], df["v4_gas_savings"], "gold", linewidth=2)
    ax4.fill_between(df["date"], 0, df["v4_gas_savings"], alpha=0.3, color="gold")
    ax4.set_xlabel("Date")
    ax4.set_ylabel("Cumulative Gas Savings (USD)")
    ax4.set_title("V4 Gas Savings (Flash Accounting + Native ETH)")
    ax4.grid(True, alpha=0.3)

    # 5. V4 Advantage
    ax5 = axes[1, 1]
    colors = ["green" if x > 0 else "red" for x in df["v4_vs_v3"]]
    ax5.bar(df["date"], df["v4_vs_v3"], color=colors, alpha=0.6)
    ax5.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax5.set_xlabel("Date")
    ax5.set_ylabel("V4 Advantage (USD)")
    ax5.set_title("V4 vs V3 Daily Advantage")
    ax5.grid(True, alpha=0.3, axis="y")

    # 6. Volatility tracking
    ax6 = axes[1, 2]
    ax6.plot(df["date"], df["volatility"] * 100, "purple", linewidth=2)
    ax6.fill_between(df["date"], 0, df["volatility"] * 100, alpha=0.3, color="purple")
    ax6.set_xlabel("Date")
    ax6.set_ylabel("Volatility (%)")
    ax6.set_title("Market Volatility (Drives Dynamic Fees)")
    ax6.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"\n📊 Visualization saved: {save_path}")


# ===== MAIN =====


def run_v4_backtest(
    days=90,
    initial_coin=10,
    initial_usdc=20000,
    price_range_pct=10,
    daily_volume=50_000_000,
    coin_symbol="ETH",
    base_fee=0.003,
    enable_hooks=True,
    export_excel=True,
):
    """Run complete V4 backtest"""

    print("🚀 Starting Uniswap V4 Backtest...")
    print(
        f"Parameters: {days} days, {initial_coin} {coin_symbol.upper()}, ${initial_usdc} USDC"
    )
    print(f"Range: ±{price_range_pct}%, Base Fee: {base_fee * 100}%")
    print(f"Hooks Enabled: {enable_hooks}")
    print("-" * 80)

    # Fetch data
    print("\n1️⃣ Fetching historical prices...")
    historical_prices = get_coin_historical_prices(coin_symbol, days)

    if not historical_prices:
        print("❌ Failed")
        return None

    initial_price = historical_prices[0]["price_usd"]
    print(f"✅ Fetched {len(historical_prices)} days | Initial: ${initial_price:.2f}")

    # Calculate range
    price_lower = initial_price * (1 - price_range_pct / 100)
    price_upper = initial_price * (1 + price_range_pct / 100)
    print(f"\n📏 Range: ${price_lower:.2f} - ${price_upper:.2f}")

    # Run backtest
    print("\n2️⃣ Running V4 backtest...")
    results_df = backtest_v4_strategy(
        historical_prices,
        price_lower,
        price_upper,
        initial_coin,
        initial_usdc,
        daily_volume,
        base_fee,
        enable_hooks,
    )

    if results_df.empty:
        print("❌ Failed")
        return None

    print(f"✅ Complete: {len(results_df)} days")

    # Analyze
    print("\n3️⃣ Analyzing...")
    analysis = analyze_v4_results(results_df)
    print_v4_analysis(coin_symbol, analysis)

    # Visualize
    print("\n4️⃣ Creating visualizations...")
    png_path = f"v4_backtest_{coin_symbol.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    create_v4_visualizations(results_df, coin_symbol, png_path)

    # Export
    if export_excel:
        print("\n5️⃣ Exporting to Excel...")
        excel_path = f"v4_backtest_{coin_symbol.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            results_df.to_excel(writer, sheet_name="Daily Results", index=False)
            pd.DataFrame([analysis["summary"]]).to_excel(
                writer, sheet_name="Summary", index=False
            )
            pd.DataFrame([analysis["v4_performance"]]).to_excel(
                writer, sheet_name="V4 Performance", index=False
            )
            pd.DataFrame([analysis["v4_vs_v3"]]).to_excel(
                writer, sheet_name="V4 vs V3", index=False
            )

        print(f"✅ Saved: {excel_path}")

    print("\n🎉 V4 Analysis complete!")
    return results_df, analysis


if __name__ == "__main__":
    # Run V4 backtest
    results, analysis = run_v4_backtest(
        days=90,
        initial_coin=10,
        initial_usdc=20000,
        price_range_pct=10,
        daily_volume=50_000_000,
        coin_symbol="ETH",
        base_fee=0.003,
        enable_hooks=True,
        export_excel=True,
    )

    print("\n" + "=" * 80)
    print("KEY V4 INSIGHTS:")
    print("=" * 80)
    print("✅ V4 uses SAME concentrated liquidity math as V3")
    print("✅ Hooks enable dynamic fees (higher during volatility)")
    print("✅ Flash accounting saves gas on multi-hop swaps")
    print("✅ Native ETH saves ~15% gas (no WETH wrapping)")
    print("✅ Singleton = 99% cheaper pool creation")
    print("✅ Total advantage = Better fees + Lower costs")
    print("=" * 80)
