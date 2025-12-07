#!/usr/bin/env python3
"""
HypatiaX Visualization Scripts
Beautiful, professional charts for DeFi analysis
"""

import json
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set professional style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 12


class HypatiaXVisualizer:
    """
    Professional visualization suite for DeFi analytics
    """

    def __init__(self):
        self.colors = {
            "profit": "#10b981",
            "loss": "#ef4444",
            "neutral": "#6366f1",
            "highlight": "#f59e0b",
            "background": "#f8fafc",
        }

    def plot_il_over_time(self, historical_data, save_path="il_over_time.png"):
        """
        Plot IL% progression over time with fee income
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in historical_data]
        prices = [d["price_usd"] for d in historical_data]

        # Calculate IL for each point
        initial_price = prices[0]
        il_values = []
        fee_values = []

        for i, price in enumerate(prices):
            ratio = price / initial_price
            il = (2 * np.sqrt(ratio) / (ratio + 1) - 1) * 100
            il_values.append(il)

            # Estimate fees (simplified)
            days = i + 1
            fees = days * 0.05  # $50 per day average
            fee_values.append(fees)

        # Plot 1: IL Percentage
        ax1.fill_between(
            dates, il_values, 0, where=np.array(il_values) < 0, color=self.colors["loss"], alpha=0.3, label="Loss"
        )
        ax1.plot(dates, il_values, color=self.colors["loss"], linewidth=2)
        ax1.axhline(y=0, color="black", linestyle="--", linewidth=1, alpha=0.5)
        ax1.set_ylabel("Impermanent Loss (%)", fontsize=12, fontweight="bold")
        ax1.set_title("Impermanent Loss Over Time", fontsize=14, fontweight="bold", pad=20)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc="lower left")

        # Plot 2: Net Position (IL + Fees)
        net_values = [il + fee for il, fee in zip(il_values, fee_values)]
        ax2.fill_between(
            dates,
            net_values,
            0,
            where=np.array(net_values) > 0,
            color=self.colors["profit"],
            alpha=0.3,
            label="Net Profit",
        )
        ax2.fill_between(
            dates, net_values, 0, where=np.array(net_values) < 0, color=self.colors["loss"], alpha=0.3, label="Net Loss"
        )
        ax2.plot(dates, net_values, color=self.colors["neutral"], linewidth=2.5, label="Net Position")
        ax2.axhline(y=0, color="black", linestyle="--", linewidth=1, alpha=0.5)
        ax2.set_xlabel("Date", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Net Value ($)", fontsize=12, fontweight="bold")
        ax2.set_title("Net Position: IL + Fee Income", fontsize=14, fontweight="bold", pad=20)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc="upper left")

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white")
        print(f"✅ Saved: {save_path}")
        plt.close()

    def plot_price_impact_heatmap(self, save_path="price_impact_heatmap.png"):
        """
        Heatmap showing price impact vs trade size and liquidity
        """
        trade_sizes = np.linspace(1000, 100000, 20)
        liquidities = np.linspace(100000, 10000000, 20)

        impact_matrix = np.zeros((len(liquidities), len(trade_sizes)))

        for i, liq in enumerate(liquidities):
            for j, trade in enumerate(trade_sizes):
                # Simplified price impact formula
                impact = (trade / liq) * 100
                impact_matrix[i, j] = min(impact, 10)  # Cap at 10%

        fig, ax = plt.subplots(figsize=(12, 8))

        im = ax.imshow(
            impact_matrix,
            aspect="auto",
            cmap="RdYlGn_r",
            extent=[trade_sizes[0], trade_sizes[-1], liquidities[0], liquidities[-1]],
            origin="lower",
        )

        ax.set_xlabel("Trade Size (USD)", fontsize=12, fontweight="bold")
        ax.set_ylabel("Pool Liquidity (USD)", fontsize=12, fontweight="bold")
        ax.set_title("Price Impact Heatmap", fontsize=14, fontweight="bold", pad=20)

        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Price Impact (%)", fontsize=11, fontweight="bold")

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white")
        print(f"✅ Saved: {save_path}")
        plt.close()

    def plot_risk_score_breakdown(self, il_pct, volatility, range_width, days, save_path="risk_breakdown.png"):
        """
        Bar chart showing risk score components
        """
        components = {
            "IL Risk": min(100, abs(il_pct) * 5),
            "Volatility": min(100, volatility * 100),
            "Range Risk": 100 - min(100, range_width * 10),
            "Time Risk": min(100, days / 365 * 100),
        }
        weights = {"IL Risk": 0.4, "Volatility": 0.3, "Range Risk": 0.2, "Time Risk": 0.1}

        weighted_scores = {k: v * weights[k] for k, v in components.items()}
        total_score = sum(weighted_scores.values())

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Plot 1: Component Scores
        colors_list = [self.colors["loss"], self.colors["highlight"], self.colors["neutral"], self.colors["profit"]]
        bars = ax1.bar(
            range(len(components)), components.values(), color=colors_list, alpha=0.7, edgecolor="black", linewidth=1.5
        )
        ax1.set_xticks(range(len(components)))
        ax1.set_xticklabels(components.keys(), rotation=45, ha="right")
        ax1.set_ylabel("Score (0-100)", fontsize=12, fontweight="bold")
        ax1.set_title("Risk Component Scores", fontsize=14, fontweight="bold", pad=20)
        ax1.axhline(y=50, color="red", linestyle="--", alpha=0.5, label="High Risk Threshold")
        ax1.grid(axis="y", alpha=0.3)
        ax1.legend()

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.1f}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # Plot 2: Weighted Contribution
        wedges, texts, autotexts = ax2.pie(
            weighted_scores.values(),
            labels=weighted_scores.keys(),
            autopct="%1.1f%%",
            colors=colors_list,
            startangle=90,
            textprops={"fontweight": "bold"},
        )
        ax2.set_title(f"Weighted Risk Score: {total_score:.1f}/100", fontsize=14, fontweight="bold", pad=20)

        # Determine risk category
        if total_score < 30:
            category = "LOW RISK"
            cat_color = self.colors["profit"]
        elif total_score < 60:
            category = "MEDIUM RISK"
            cat_color = self.colors["highlight"]
        elif total_score < 80:
            category = "HIGH RISK"
            cat_color = self.colors["loss"]
        else:
            category = "EXTREME RISK"
            cat_color = "#dc2626"

        ax2.text(0, -1.3, category, ha="center", fontsize=16, fontweight="bold", color=cat_color)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white")
        print(f"✅ Saved: {save_path}")
        plt.close()

    def plot_scenario_comparison(self, scenarios_data, save_path="scenario_comparison.png"):
        """
        Compare multiple Uniswap scenarios side by side
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        scenarios = ["Stable", "Bull", "Bear", "Volatile", "Whale"]
        il_values = [-0.31, -5.72, -5.72, 0.0, -0.02]
        fee_values = [450, 1200, 800, 2500, 150]
        net_values = [il + fee for il, fee in zip(il_values, fee_values)]

        # Plot 1: IL Comparison
        bars1 = ax1.barh(scenarios, il_values, color=self.colors["loss"], alpha=0.7)
        ax1.set_xlabel("IL (%)", fontsize=11, fontweight="bold")
        ax1.set_title("Impermanent Loss by Scenario", fontsize=13, fontweight="bold")
        ax1.grid(axis="x", alpha=0.3)
        for i, (bar, val) in enumerate(zip(bars1, il_values)):
            ax1.text(val - 0.3, i, f"{val:.2f}%", va="center", ha="right", fontweight="bold", color="white")

        # Plot 2: Fee Income
        bars2 = ax2.barh(scenarios, fee_values, color=self.colors["profit"], alpha=0.7)
        ax2.set_xlabel("Fees Earned ($)", fontsize=11, fontweight="bold")
        ax2.set_title("Fee Income by Scenario", fontsize=13, fontweight="bold")
        ax2.grid(axis="x", alpha=0.3)
        for i, (bar, val) in enumerate(zip(bars2, fee_values)):
            ax2.text(val + 30, i, f"${val:.0f}", va="center", ha="left", fontweight="bold")

        # Plot 3: Net Result
        colors_net = [self.colors["profit"] if v > 0 else self.colors["loss"] for v in net_values]
        bars3 = ax3.barh(scenarios, net_values, color=colors_net, alpha=0.7)
        ax3.set_xlabel("Net Result ($)", fontsize=11, fontweight="bold")
        ax3.set_title("Net Position (IL + Fees)", fontsize=13, fontweight="bold")
        ax3.axvline(x=0, color="black", linestyle="--", linewidth=1)
        ax3.grid(axis="x", alpha=0.3)
        for i, (bar, val) in enumerate(zip(bars3, net_values)):
            ax3.text(
                val + (20 if val > 0 else -20),
                i,
                f"${val:.0f}",
                va="center",
                ha="left" if val > 0 else "right",
                fontweight="bold",
            )

        # Plot 4: Performance Summary
        perf_metrics = ["Best Fee\nIncome", "Lowest IL", "Best Net\nResult"]
        best_scenarios = ["Volatile", "Volatile", "Volatile"]
        values = [2500, 0.0, 2500]
        bars4 = ax4.bar(
            perf_metrics,
            values,
            color=[self.colors["highlight"], self.colors["profit"], self.colors["neutral"]],
            alpha=0.7,
        )
        ax4.set_ylabel("Value", fontsize=11, fontweight="bold")
        ax4.set_title("Best Performers", fontsize=13, fontweight="bold")
        ax4.grid(axis="y", alpha=0.3)
        for i, (bar, scenario) in enumerate(zip(bars4, best_scenarios)):
            height = bar.get_height()
            ax4.text(i, height + 50, scenario, ha="center", va="bottom", fontweight="bold", fontsize=10)

        plt.suptitle("Uniswap Scenario Comparison", fontsize=16, fontweight="bold", y=0.995)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white")
        print(f"✅ Saved: {save_path}")
        plt.close()

    def plot_backtest_summary(self, historical_data, save_path="backtest_summary.png"):
        """
        Comprehensive backtest visualization
        """
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.25)

        dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in historical_data]
        prices = [d["price_usd"] for d in historical_data]

        # Calculate metrics
        initial_price = prices[0]
        il_values = [(2 * np.sqrt(p / initial_price) / (p / initial_price + 1) - 1) * 100 for p in prices]
        fees = [i * 0.05 for i in range(len(prices))]
        hodl = [100 * p + 180000 for p in prices]
        lp_value = [200 * np.sqrt(initial_price * p) + f for p, f in zip(prices, fees)]

        # Plot 1: Price Movement (Large, top)
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(dates, prices, color=self.colors["neutral"], linewidth=2.5, label="ETH Price")
        ax1.fill_between(
            dates,
            prices,
            initial_price,
            where=np.array(prices) > initial_price,
            color=self.colors["profit"],
            alpha=0.2,
            label="Price Increase",
        )
        ax1.fill_between(
            dates,
            prices,
            initial_price,
            where=np.array(prices) < initial_price,
            color=self.colors["loss"],
            alpha=0.2,
            label="Price Decrease",
        )
        ax1.axhline(y=initial_price, color="black", linestyle="--", linewidth=1, alpha=0.5)
        ax1.set_ylabel("ETH Price (USD)", fontsize=12, fontweight="bold")
        ax1.set_title("90-Day Price Movement", fontsize=14, fontweight="bold", pad=15)
        ax1.legend(loc="best")
        ax1.grid(True, alpha=0.3)

        # Plot 2: IL Timeline
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.plot(dates, il_values, color=self.colors["loss"], linewidth=2)
        ax2.fill_between(dates, il_values, 0, alpha=0.3, color=self.colors["loss"])
        ax2.set_ylabel("IL (%)", fontsize=11, fontweight="bold")
        ax2.set_title("Impermanent Loss", fontsize=12, fontweight="bold")
        ax2.grid(True, alpha=0.3)

        # Plot 3: Cumulative Fees
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.plot(dates, fees, color=self.colors["profit"], linewidth=2)
        ax3.fill_between(dates, fees, 0, alpha=0.3, color=self.colors["profit"])
        ax3.set_ylabel("Fees ($)", fontsize=11, fontweight="bold")
        ax3.set_title("Fee Income", fontsize=12, fontweight="bold")
        ax3.grid(True, alpha=0.3)

        # Plot 4: Strategy Comparison
        ax4 = fig.add_subplot(gs[2, :])
        ax4.plot(dates, hodl, color=self.colors["highlight"], linewidth=2.5, label="HODL Strategy", linestyle="--")
        ax4.plot(dates, lp_value, color=self.colors["profit"], linewidth=2.5, label="LP Strategy")
        ax4.fill_between(
            dates,
            hodl,
            lp_value,
            where=np.array(lp_value) > np.array(hodl),
            color=self.colors["profit"],
            alpha=0.2,
            label="LP Outperforms",
        )
        ax4.fill_between(
            dates,
            hodl,
            lp_value,
            where=np.array(lp_value) < np.array(hodl),
            color=self.colors["loss"],
            alpha=0.2,
            label="HODL Outperforms",
        )
        ax4.set_xlabel("Date", fontsize=12, fontweight="bold")
        ax4.set_ylabel("Portfolio Value ($)", fontsize=12, fontweight="bold")
        ax4.set_title("Strategy Performance Comparison", fontsize=14, fontweight="bold", pad=15)
        ax4.legend(loc="best")
        ax4.grid(True, alpha=0.3)

        plt.suptitle("90-Day Backtest Summary", fontsize=16, fontweight="bold", y=0.998)
        plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white")
        print(f"✅ Saved: {save_path}")
        plt.close()

    def generate_all_charts(self, historical_data):
        """
        Generate complete visualization suite
        """
        print("\n🎨 Generating HypatiaX Visualization Suite...")
        print("=" * 60)

        self.plot_il_over_time(historical_data)
        self.plot_price_impact_heatmap()
        self.plot_risk_score_breakdown(-8.0, 0.45, 0.3, 45)
        self.plot_scenario_comparison([])
        self.plot_backtest_summary(historical_data)

        print("=" * 60)
        print("✅ All visualizations generated successfully!")
        print("\nFiles created:")
        print("  • il_over_time.png")
        print("  • price_impact_heatmap.png")
        print("  • risk_breakdown.png")
        print("  • scenario_comparison.png")
        print("  • backtest_summary.png")


# Example usage
if __name__ == "__main__":
    from hypatiax_dataset import HypatiaXDatasetGenerator

    # Generate data
    generator = HypatiaXDatasetGenerator()
    historical = generator.generate_historical_prices(90)

    # Create visualizations
    viz = HypatiaXVisualizer()
    viz.generate_all_charts(historical)

    print("\n🎉 Ready to impress clients with professional visualizations!")
