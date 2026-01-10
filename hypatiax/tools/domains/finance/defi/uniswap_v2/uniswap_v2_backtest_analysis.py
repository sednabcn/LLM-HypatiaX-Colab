from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# ===== DATA FETCHING =====

# CoinGecko coin IDs mapping
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
    """Fetch historical price data for any coin from CoinGecko"""

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
        print(f"Error fetching prices: {e}")
        return []


def get_uniswap_pool_data(pool_address):
    """Get Uniswap pool data from The Graph"""
    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    query = f"""
    {{
      pair(id: "{pool_address.lower()}") {{
        token0 {{ symbol decimals }}
        token1 {{ symbol decimals }}
        reserve0
        reserve1
        reserveUSD
        volumeUSD
        txCount
      }}
    }}
    """

    try:
        response = requests.post(url, json={"query": query})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching pool data: {e}")
        return None


# ===== CORE CALCULATIONS =====


def calculate_il_with_fees(
    initial_price,
    current_price,
    initial_x,
    initial_y,
    days_elapsed,
    daily_volume_usd,
    fee_tier=0.003,
):
    """
    Calculate Impermanent Loss and Fees Earned

    Args:
        initial_price: Starting COIN price in USD
        current_price: Current COIN price in USD
        initial_x: Initial COIN amount
        initial_y: Initial USDC amount
        days_elapsed: Days since deposit
        daily_volume_usd: Average daily trading volume
        fee_tier: Pool fee (0.3% = 0.003)
    """

    # Price ratio
    price_ratio = current_price / initial_price

    # Impermanent Loss formula: 2*sqrt(price_ratio) / (1 + price_ratio) - 1
    il_multiplier = (2 * np.sqrt(price_ratio)) / (1 + price_ratio)
    il_percent = (il_multiplier - 1) * 100

    # Calculate initial pool value
    initial_pool_value = initial_x * initial_price + initial_y

    # Calculate IL in USD
    il_usd = initial_pool_value * (1 - il_multiplier)

    # Calculate fees earned
    # Fees = (Your Liquidity / Total Pool Liquidity) * Daily Volume * Fee Tier * Days
    # Assuming your position is ~0.01% of pool (adjust based on pool size)
    liquidity_share = 0.0001  # 0.01% of pool
    daily_fees = daily_volume_usd * fee_tier * liquidity_share
    total_fees = daily_fees * days_elapsed

    return {
        "il_percent": il_percent,
        "il_usd": il_usd,
        "daily_fees": daily_fees,
        "total_fees": total_fees,
        "net_gain_loss": total_fees - il_usd,
        "price_ratio": price_ratio,
    }


# ===== BACKTESTING ENGINE =====


def backtest_lp_strategy(
    historical_prices, initial_coin=10, initial_usdc=20000, daily_volume=5000000
):
    """
    Run complete backtest comparing LP vs HODL

    Returns DataFrame with daily results
    """

    if not historical_prices:
        print("No historical data available")
        return pd.DataFrame()

    results = []
    initial_price = historical_prices[0]["price_usd"]

    for idx, day in enumerate(historical_prices):
        current_price = day["price_usd"]
        days_elapsed = idx + 1

        # Calculate IL and fees
        calc = calculate_il_with_fees(
            initial_price=initial_price,
            current_price=current_price,
            initial_x=initial_coin,
            initial_y=initial_usdc,
            days_elapsed=days_elapsed,
            daily_volume_usd=daily_volume,
        )

        # HODL value (just holding COIN + USDC separately)
        hodl_value = initial_coin * current_price + initial_usdc

        # LP value (constant product formula)
        lp_value_no_fees = 2 * np.sqrt(initial_coin * initial_usdc * current_price)
        lp_value_with_fees = lp_value_no_fees + calc["total_fees"]

        # LP advantage over HODL
        advantage = lp_value_with_fees - hodl_value
        advantage_percent = (advantage / hodl_value) * 100

        results.append(
            {
                "date": day["date"],
                "day": days_elapsed,
                "price": current_price,
                "price_change_pct": ((current_price - initial_price) / initial_price)
                * 100,
                "il_percent": calc["il_percent"],
                "il_usd": calc["il_usd"],
                "daily_fees": calc["daily_fees"],
                "total_fees": calc["total_fees"],
                "hodl_value": hodl_value,
                "lp_value": lp_value_with_fees,
                "advantage_usd": advantage,
                "advantage_pct": advantage_percent,
                "breakeven": calc["total_fees"] >= calc["il_usd"],
            }
        )

    return pd.DataFrame(results)


# ===== ANALYSIS FUNCTIONS =====


def analyze_results(df):
    """Generate comprehensive analysis of backtest results"""

    if df.empty:
        return "No data to analyze"

    analysis = {"summary": {}, "breakeven": {}, "performance": {}, "risk": {}}

    # Summary stats
    analysis["summary"] = {
        "total_days": len(df),
        "initial_price": df["price"].iloc[0],
        "final_price": df["price"].iloc[-1],
        "price_change_pct": df["price_change_pct"].iloc[-1],
        "total_fees_earned": df["total_fees"].iloc[-1],
        "final_il_usd": df["il_usd"].iloc[-1],
        "final_advantage": df["advantage_usd"].iloc[-1],
    }

    # Breakeven analysis
    breakeven_days = df[df["breakeven"] == True]
    if not breakeven_days.empty:
        first_breakeven = breakeven_days.iloc[0]
        analysis["breakeven"] = {
            "days_to_breakeven": first_breakeven["day"],
            "breakeven_date": first_breakeven["date"],
            "fees_at_breakeven": first_breakeven["total_fees"],
            "il_at_breakeven": first_breakeven["il_usd"],
        }
    else:
        analysis["breakeven"] = {
            "days_to_breakeven": None,
            "message": "Never reached breakeven in this period",
        }

    # Performance metrics
    analysis["performance"] = {
        "days_lp_wins": len(df[df["advantage_usd"] > 0]),
        "days_hodl_wins": len(df[df["advantage_usd"] < 0]),
        "win_rate_pct": (len(df[df["advantage_usd"] > 0]) / len(df)) * 100,
        "avg_daily_advantage": df["advantage_usd"].mean(),
        "max_advantage": df["advantage_usd"].max(),
        "min_advantage": df["advantage_usd"].min(),
    }

    # Risk metrics
    analysis["risk"] = {
        "max_il_pct": df["il_percent"].min(),  # Most negative
        "max_il_usd": df["il_usd"].max(),
        "volatility": df["price"].std(),
        "max_drawdown_from_hodl": df["advantage_usd"].min(),
    }

    return analysis


def print_analysis_report(coin_symbol, analysis):
    """Print formatted analysis report"""

    if isinstance(analysis, str):
        print(analysis)
        return

    print("\n" + "=" * 60)
    print("📊 LP vs HODL BACKTEST ANALYSIS REPORT")
    print("=" * 60)

    # Summary
    print("\n📈 SUMMARY")
    print("-" * 60)
    s = analysis["summary"]
    print(f"Duration: {s['total_days']} days")
    print(
        f"{coin_symbol.upper()} Price: ${s['initial_price']:.2f} → ${s['final_price']:.2f} ({s['price_change_pct']:+.2f}%)"
    )
    print(f"Total Fees Earned: ${s['total_fees_earned']:.2f}")
    print(f"Final IL: ${s['final_il_usd']:.2f}")
    print(f"Final LP Advantage: ${s['final_advantage']:+.2f}")

    # Breakeven
    print("\n⚖️  BREAKEVEN ANALYSIS")
    print("-" * 60)
    b = analysis["breakeven"]
    if b.get("days_to_breakeven"):
        print(f"✅ Reached breakeven after {b['days_to_breakeven']} days")
        print(f"Date: {b['breakeven_date'].strftime('%Y-%m-%d')}")
        print(f"Fees needed: ${b['fees_at_breakeven']:.2f}")
    else:
        print(f"❌ {b['message']}")

    # Performance
    print("\n🏆 PERFORMANCE METRICS")
    print("-" * 60)
    p = analysis["performance"]
    print(f"Days LP Won: {p['days_lp_wins']} ({p['win_rate_pct']:.1f}%)")
    print(f"Days HODL Won: {p['days_hodl_wins']} ({100-p['win_rate_pct']:.1f}%)")
    print(f"Avg Daily Advantage: ${p['avg_daily_advantage']:+.2f}")
    print(f"Best Day: ${p['max_advantage']:+.2f}")
    print(f"Worst Day: ${p['min_advantage']:+.2f}")

    # Risk
    print("\n⚠️  RISK METRICS")
    print("-" * 60)
    r = analysis["risk"]
    print(f"Maximum IL: {r['max_il_pct']:.2f}% (${r['max_il_usd']:.2f})")
    print(f"Price Volatility (StdDev): ${r['volatility']:.2f}")
    print(f"Max Drawdown vs HODL: ${r['max_drawdown_from_hodl']:+.2f}")

    print("\n" + "=" * 60)


# ===== VISUALIZATION =====


def create_visualizations(df, coin_symbol, save_path):
    """Create comprehensive visualization dashboard"""

    if df.empty:
        print("No data to visualize")
        return

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle(
        "LP vs HODL Strategy Backtest Analysis", fontsize=16, fontweight="bold"
    )

    # 1. Price and IL over time
    ax1 = axes[0, 0]
    ax1_twin = ax1.twinx()
    ax1.plot(
        df["date"], df["price"], "b-", linewidth=2, label=f"{coin_symbol.upper()} Price"
    )
    ax1_twin.plot(df["date"], df["il_percent"], "r-", linewidth=2, label="IL %")
    ax1.set_xlabel("Date")
    ax1.set_ylabel(f"{coin_symbol.upper()}  Price (USD)", color="b")
    ax1_twin.set_ylabel("Impermanent Loss (%)", color="r")
    ax1.set_title("Price Movement & Impermanent Loss")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left")
    ax1_twin.legend(loc="upper right")

    # 2. Cumulative fees vs IL
    ax2 = axes[0, 1]
    ax2.plot(df["date"], df["total_fees"], "g-", linewidth=2, label="Cumulative Fees")
    ax2.plot(df["date"], df["il_usd"], "r-", linewidth=2, label="IL (USD)")
    ax2.fill_between(
        df["date"],
        df["total_fees"],
        df["il_usd"],
        where=(df["total_fees"] >= df["il_usd"]),
        alpha=0.3,
        color="green",
        label="Profit Zone",
    )
    ax2.set_xlabel("Date")
    ax2.set_ylabel("USD")
    ax2.set_title("Fees vs Impermanent Loss")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. LP vs HODL value comparison
    ax3 = axes[1, 0]
    ax3.plot(df["date"], df["hodl_value"], "orange", linewidth=2, label="HODL Value")
    ax3.plot(df["date"], df["lp_value"], "purple", linewidth=2, label="LP Value")
    ax3.fill_between(
        df["date"],
        df["hodl_value"],
        df["lp_value"],
        where=(df["lp_value"] >= df["hodl_value"]),
        alpha=0.3,
        color="green",
        label="LP Wins",
    )
    ax3.fill_between(
        df["date"],
        df["hodl_value"],
        df["lp_value"],
        where=(df["lp_value"] < df["hodl_value"]),
        alpha=0.3,
        color="red",
        label="HODL Wins",
    )
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Portfolio Value (USD)")
    ax3.set_title("LP vs HODL Portfolio Value")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 4. Daily advantage
    ax4 = axes[1, 1]
    colors = ["green" if x > 0 else "red" for x in df["advantage_usd"]]
    ax4.bar(df["date"], df["advantage_usd"], color=colors, alpha=0.6)
    ax4.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax4.set_xlabel("Date")
    ax4.set_ylabel("LP Advantage (USD)")
    ax4.set_title("Daily LP Advantage Over HODL")
    ax4.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"\n📊 Visualization saved to: {save_path}")

    return fig


# ===== MAIN EXECUTION =====


def run_complete_backtest(
    days=90,
    initial_coin=10,
    initial_usdc=20000,
    daily_volume=5000000,
    coin_symbol="ETH",
    export_excel=True,
):
    """
    Run complete backtest with all analysis and visualizations
    """

    print("🚀 Starting DeFi LP Backtest Analysis...")
    print(
        f"Parameters: {days} days, {initial_coin} {coin_symbol.upper()}, ${initial_usdc} USDC"
    )
    print("-" * 60)

    # Fetch data
    print("\n1️⃣ Fetching historical ETH prices...")
    historical_prices = get_coin_historical_prices(coin_symbol, days)

    if not historical_prices:
        print("❌ Failed to fetch price data")
        return None

    print(f"✅ Fetched {len(historical_prices)} days of price data")

    # Run backtest
    print("\n2️⃣ Running backtest simulation...")
    results_df = backtest_lp_strategy(
        historical_prices=historical_prices,
        initial_coin=initial_coin,
        initial_usdc=initial_usdc,
        daily_volume=daily_volume,
    )

    if results_df.empty:
        print("❌ Backtest failed")
        return None

    print(f"✅ Backtest complete: {len(results_df)} days simulated")

    # Analyze
    print("\n3️⃣ Analyzing results...")
    analysis = analyze_results(results_df)
    print_analysis_report(coin_symbol, analysis)

    # Visualize
    print("\n4️⃣ Creating visualizations...")
    png_path = f'backtest_analysis_{coin_symbol.upper()}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    create_visualizations(results_df, coin_symbol, png_path)

    # Export to Excel
    if export_excel:
        print("\n5️⃣ Exporting to Excel...")
        excel_path = f'lp_backtest_{coin_symbol.upper()}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            results_df.to_excel(writer, sheet_name="Daily Results", index=False)

            # Create summary sheet
            summary_df = pd.DataFrame([analysis["summary"]])
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

            # Performance metrics
            perf_df = pd.DataFrame([analysis["performance"]])
            perf_df.to_excel(writer, sheet_name="Performance", index=False)

        print(f"✅ Excel file saved: {excel_path}")

    print("\n🎉 Analysis complete!")

    return results_df, analysis


# ===== RUN THE ANALYSIS =====
if __name__ == "__main__":

    data_source = [
        (10, 20_000, 50_000_000, "ETH"),
        (10_000, 10_000, 100_000_000, "USDT"),
        (10_000, 10_000, 80_000_000, "DAI"),
        (1_000_000, 10_000, 20_000_000, "SHIB"),
    ]
    for idx, (initial_coin, initial_usdc, daily_volume, coin_symbol) in enumerate(
        data_source
    ):
        results, analysis = run_complete_backtest(
            days=90,
            initial_coin=initial_coin,
            initial_usdc=initial_usdc,
            daily_volume=daily_volume,
            coin_symbol=coin_symbol,
        )


### 📊 The Three Key Metrics to Analyze
# 1. Breakeven Point

# How many days until LP fees > impermanent loss?
# At what volatility level do fees compensate for IL?

# 2. Max Drawdown

# What's the worst IL you experienced?
# Could you stomach that loss psychologically?

# 3. Win Rate

# What % of days was LP > HODL?
# Is it consistently better or volatile?
