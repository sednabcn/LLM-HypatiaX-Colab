#!/usr/bin/env python3
"""
HypatiaX Visualizer
==================

Canonical visualization entry point for HypatiaX results.

- Loads inputs from hypatiax/data/results
- Saves figures to hypatiax/data/figures
- Environment-agnostic (local / CI / Colab)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from hypatiax.config.paths import paths

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

RESULTS_DIR: Path = paths.results
FIGURES_DIR: Path = paths.figures

if not RESULTS_DIR.exists():
    raise FileNotFoundError(f"Results directory not found: {RESULTS_DIR}")

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sns.set_style("whitegrid")
plt.rcParams.update(
    {
        "figure.figsize": (12, 6),
        "font.size": 10,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
    }
)

# -----------------------------------------------------------------------------
# Visualizer
# -----------------------------------------------------------------------------


class HypatiaXVisualizer:
    """
    Production-grade visualization suite for HypatiaX.
    """

    def __init__(self) -> None:
        self.colors = {
            "profit": "#10b981",
            "loss": "#ef4444",
            "neutral": "#6366f1",
            "highlight": "#f59e0b",
        }

        logger.info(f"Using results from: {RESULTS_DIR}")
        logger.info(f"Saving figures to: {FIGURES_DIR}")

    # -------------------------------------------------------------------------
    # Data loading
    # -------------------------------------------------------------------------

    def load_json(self, filename: str) -> List[Dict[str, Any]]:
        path = RESULTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing result file: {path}")

        with open(path, "r") as f:
            return json.load(f)

    # -------------------------------------------------------------------------
    # Plots
    # -------------------------------------------------------------------------

    def plot_il_over_time(
        self,
        historical_data: List[Dict[str, Any]],
        filename: str = "il_over_time.png",
    ) -> None:
        save_path = FIGURES_DIR / filename

        dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in historical_data]
        prices = np.array([d["price_usd"] for d in historical_data])

        initial_price = prices[0]
        ratio = prices / initial_price
        il_values = (2 * np.sqrt(ratio) / (ratio + 1) - 1) * 100
        fee_values = np.arange(1, len(prices) + 1) * 0.05
        net_values = il_values + fee_values

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        ax1.plot(dates, il_values, color=self.colors["loss"], linewidth=2)
        ax1.fill_between(dates, il_values, 0, color=self.colors["loss"], alpha=0.3)
        ax1.axhline(0, color="black", linestyle="--", linewidth=1)
        ax1.set_title("Impermanent Loss Over Time")
        ax1.set_ylabel("IL (%)")
        ax1.grid(True, alpha=0.3)

        ax2.plot(dates, net_values, color=self.colors["neutral"], linewidth=2.5)
        ax2.fill_between(
            dates,
            net_values,
            0,
            where=net_values > 0,
            color=self.colors["profit"],
            alpha=0.3,
            label="Profit",
        )
        ax2.fill_between(
            dates,
            net_values,
            0,
            where=net_values < 0,
            color=self.colors["loss"],
            alpha=0.3,
            label="Loss",
        )
        ax2.axhline(0, color="black", linestyle="--", linewidth=1)
        ax2.set_title("Net Position (IL + Fees)")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Value")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved {save_path.name}")

    # -------------------------------------------------------------------------

    def plot_price_impact_heatmap(
        self,
        filename: str = "price_impact_heatmap.png",
    ) -> None:
        save_path = FIGURES_DIR / filename

        trade_sizes = np.linspace(1_000, 100_000, 20)
        liquidities = np.linspace(100_000, 10_000_000, 20)

        impact = np.minimum((trade_sizes[None, :] / liquidities[:, None]) * 100, 10)

        fig, ax = plt.subplots(figsize=(12, 8))
        im = ax.imshow(
            impact,
            aspect="auto",
            cmap="RdYlGn_r",
            origin="lower",
            extent=[
                trade_sizes[0],
                trade_sizes[-1],
                liquidities[0],
                liquidities[-1],
            ],
        )

        ax.set_title("Price Impact Heatmap")
        ax.set_xlabel("Trade Size (USD)")
        ax.set_ylabel("Pool Liquidity (USD)")

        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Price Impact (%)")

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved {save_path.name}")

    # -------------------------------------------------------------------------

    def generate_all(self) -> None:
        """
        Canonical visualization pipeline.
        """
        logger.info("Generating all HypatiaX visualizations")

        historical = self.load_json("historical_prices.json")

        self.plot_il_over_time(historical)
        self.plot_price_impact_heatmap()

        logger.info("All visualizations generated successfully")


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------


def main() -> None:
    visualizer = HypatiaXVisualizer()
    visualizer.generate_all()


if __name__ == "__main__":
    main()
