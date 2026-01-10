"""
analysis/analyze_hybrid_performance.py

Comprehensive analysis of hybrid system performance
Generates detailed reports and visualizations
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


class HybridPerformanceAnalyzer:
    """Analyze hybrid system performance across domains"""

    def __init__(self, results_file: str):
        """Load results from JSON file"""
        with open(results_file, "r") as f:
            self.results = json.load(f)

        self.df = self._results_to_dataframe()

    def _results_to_dataframe(self):
        """Convert results to pandas DataFrame"""
        rows = []
        for result in self.results:
            row = {
                "description": result["description"],
                "domain": result["domain"],
                "decision": result["decision"],
                "decision_reason": result["decision_reason"],
                "r2": result["evaluation"]["r2"],
                "rmse": result["evaluation"]["rmse"],
                "llm_r2": result["llm_result"]["metrics"].get("r2", 0),
                "llm_success": result["llm_result"]["metrics"].get("success", False),
                "nn_r2": result["nn_result"]["metrics"].get("r2", 0),
                "extrapolation_test": result["metadata"].get(
                    "extrapolation_test", False
                ),
                "difficulty": result["metadata"].get("difficulty", "unknown"),
                "formula_type": result["metadata"].get("formula_type", "unknown"),
            }
            rows.append(row)

        return pd.DataFrame(rows)

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("=" * 80)
        print("HYBRID SYSTEM PERFORMANCE ANALYSIS".center(80))
        print("=" * 80)

        # Overall statistics
        print("\n📊 OVERALL STATISTICS")
        print("-" * 80)
        print(f"Total test cases: {len(self.df)}")
        print(f"Mean R²: {self.df['r2'].mean():.6f}")
        print(f"Median R²: {self.df['r2'].median():.6f}")
        print(f"Std Dev: {self.df['r2'].std():.6f}")
        print(f"Min R²: {self.df['r2'].min():.6f}")
        print(f"Max R²: {self.df['r2'].max():.6f}")

        # Cases with perfect or near-perfect performance
        excellent = (self.df["r2"] > 0.99).sum()
        good = ((self.df["r2"] > 0.95) & (self.df["r2"] <= 0.99)).sum()
        acceptable = ((self.df["r2"] > 0.80) & (self.df["r2"] <= 0.95)).sum()
        poor = (self.df["r2"] <= 0.80).sum()

        print(f"\nPerformance breakdown:")
        print(
            f"  Excellent (R² > 0.99): {excellent} ({excellent / len(self.df) * 100:.1f}%)"
        )
        print(f"  Good (0.95 < R² ≤ 0.99): {good} ({good / len(self.df) * 100:.1f}%)")
        print(
            f"  Acceptable (0.80 < R² ≤ 0.95): {acceptable} ({acceptable / len(self.df) * 100:.1f}%)"
        )
        print(f"  Poor (R² ≤ 0.80): {poor} ({poor / len(self.df) * 100:.1f}%)")

        # Decision breakdown
        print("\n🎯 DECISION BREAKDOWN")
        print("-" * 80)
        decision_counts = self.df["decision"].value_counts()
        for decision, count in decision_counts.items():
            pct = count / len(self.df) * 100
            avg_r2 = self.df[self.df["decision"] == decision]["r2"].mean()
            print(
                f"{decision.upper():12} : {count:3} cases ({pct:5.1f}%) | Avg R² = {avg_r2:.6f}"
            )

        # Domain breakdown
        print("\n🏢 DOMAIN BREAKDOWN")
        print("-" * 80)
        for domain in self.df["domain"].unique():
            domain_df = self.df[self.df["domain"] == domain]
            print(f"\n{domain.upper()}")
            print(f"  Cases: {len(domain_df)}")
            print(f"  Mean R²: {domain_df['r2'].mean():.6f}")
            print(f"  LLM decisions: {(domain_df['decision'] == 'llm').sum()}")
            print(f"  NN decisions: {(domain_df['decision'] == 'nn').sum()}")
            print(
                f"  Ensemble decisions: {(domain_df['decision'] == 'ensemble').sum()}"
            )

        # Extrapolation analysis
        print("\n🔍 EXTRAPOLATION TESTS")
        print("-" * 80)
        extrap_df = self.df[self.df["extrapolation_test"]]
        if len(extrap_df) > 0:
            print(f"Extrapolation cases: {len(extrap_df)}")
            print(f"Mean R²: {extrap_df['r2'].mean():.6f}")
            print(f"Cases with R² > 0.95: {(extrap_df['r2'] > 0.95).sum()}")
            print(f"\nExtrapolation cases:")
            for _, row in extrap_df.iterrows():
                print(f"  • {row['description'][:60]}...")
                print(f"    Decision: {row['decision']}, R² = {row['r2']:.6f}")
        else:
            print("No extrapolation test cases found")

        # LLM vs NN comparison
        print("\n⚖️  LLM VS NN COMPARISON")
        print("-" * 80)
        llm_better = (self.df["llm_r2"] > self.df["nn_r2"]).sum()
        nn_better = (self.df["nn_r2"] > self.df["llm_r2"]).sum()
        equal = (self.df["llm_r2"] == self.df["nn_r2"]).sum()

        print(
            f"LLM outperforms NN: {llm_better} cases ({llm_better / len(self.df) * 100:.1f}%)"
        )
        print(
            f"NN outperforms LLM: {nn_better} cases ({nn_better / len(self.df) * 100:.1f}%)"
        )
        print(f"Equal performance: {equal} cases")

        # Failed cases analysis
        print("\n⚠️  PROBLEMATIC CASES (R² < 0.80)")
        print("-" * 80)
        failed_df = self.df[self.df["r2"] < 0.80]
        if len(failed_df) > 0:
            for _, row in failed_df.iterrows():
                print(f"\n• {row['description']}")
                print(f"  Domain: {row['domain']}")
                print(f"  Decision: {row['decision']}")
                print(f"  R²: {row['r2']:.6f}")
                print(f"  LLM R²: {row['llm_r2']:.6f}, NN R²: {row['nn_r2']:.6f}")
                print(f"  Reason: {row['decision_reason']}")
        else:
            print("No problematic cases! All R² > 0.80")

        # Difficulty analysis
        print("\n🎓 DIFFICULTY ANALYSIS")
        print("-" * 80)
        for difficulty in ["easy", "medium", "hard"]:
            diff_df = self.df[self.df["difficulty"] == difficulty]
            if len(diff_df) > 0:
                print(f"\n{difficulty.upper()}:")
                print(f"  Cases: {len(diff_df)}")
                print(f"  Mean R²: {diff_df['r2'].mean():.6f}")
                print(
                    f"  Success rate (R² > 0.95): {(diff_df['r2'] > 0.95).sum() / len(diff_df) * 100:.1f}%"
                )

    def generate_comparison_table(self):
        """Generate comparison table of methods"""
        print("\n" + "=" * 80)
        print("METHOD COMPARISON TABLE".center(80))
        print("=" * 80)

        # Calculate metrics for each decision type
        comparison_data = []

        for decision in ["llm", "ensemble", "nn"]:
            decision_df = self.df[self.df["decision"] == decision]
            if len(decision_df) > 0:
                comparison_data.append(
                    {
                        "Method": decision.upper(),
                        "Cases": len(decision_df),
                        "Mean R²": decision_df["r2"].mean(),
                        "Median R²": decision_df["r2"].median(),
                        "Std Dev": decision_df["r2"].std(),
                        "Success Rate (R²>0.95)": (decision_df["r2"] > 0.95).mean()
                        * 100,
                    }
                )

        comparison_df = pd.DataFrame(comparison_data)
        print("\n", comparison_df.to_string(index=False))

        return comparison_df

    def identify_improvement_opportunities(self):
        """Identify cases where performance could be improved"""
        print("\n" + "=" * 80)
        print("IMPROVEMENT OPPORTUNITIES".center(80))
        print("=" * 80)

        # Cases where LLM failed but should have worked
        llm_failed_df = self.df[
            (~self.df["llm_success"]) & (self.df["difficulty"] != "hard")
        ]

        if len(llm_failed_df) > 0:
            print("\n⚠️  LLM FAILURES (non-hard cases):")
            for _, row in llm_failed_df.iterrows():
                print(f"  • {row['description']}")
                print(
                    f"    Difficulty: {row['difficulty']}, Current R²: {row['r2']:.6f}"
                )

        # Cases where ensemble was chosen but performed poorly
        poor_ensemble_df = self.df[
            (self.df["decision"] == "ensemble") & (self.df["r2"] < 0.90)
        ]

        if len(poor_ensemble_df) > 0:
            print("\n⚠️  POOR ENSEMBLE PERFORMANCE:")
            for _, row in poor_ensemble_df.iterrows():
                print(f"  • {row['description']}")
                print(
                    f"    R²: {row['r2']:.6f}, LLM R²: {row['llm_r2']:.6f}, NN R²: {row['nn_r2']:.6f}"
                )

        # Cases where wrong decision was made
        wrong_decision_df = self.df[
            (
                (self.df["decision"] == "llm")
                & (self.df["nn_r2"] > self.df["llm_r2"] + 0.05)
            )
            | (
                (self.df["decision"] == "nn")
                & (self.df["llm_r2"] > self.df["nn_r2"] + 0.05)
            )
        ]

        if len(wrong_decision_df) > 0:
            print("\n⚠️  POTENTIALLY WRONG DECISIONS:")
            for _, row in wrong_decision_df.iterrows():
                print(f"  • {row['description']}")
                print(
                    f"    Decision: {row['decision']}, LLM R²: {row['llm_r2']:.6f}, NN R²: {row['nn_r2']:.6f}"
                )

    def export_to_csv(self, output_dir: str = "hypatiax/data/results"):
        """Export analysis to CSV files"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Main results
        csv_file = f"{output_dir}/analysis_main_{timestamp}.csv"
        self.df.to_csv(csv_file, index=False)
        print(f"\n✅ Main results exported to: {csv_file}")

        # Summary by domain
        summary_df = (
            self.df.groupby("domain")
            .agg(
                {"r2": ["mean", "median", "std", "min", "max"], "description": "count"}
            )
            .round(6)
        )
        summary_df.columns = [
            "Mean R²",
            "Median R²",
            "Std Dev",
            "Min R²",
            "Max R²",
            "Count",
        ]

        summary_file = f"{output_dir}/analysis_by_domain_{timestamp}.csv"
        summary_df.to_csv(summary_file)
        print(f"✅ Domain summary exported to: {summary_file}")

        # Decision analysis
        decision_df = (
            self.df.groupby("decision")
            .agg({"r2": ["mean", "median", "std"], "description": "count"})
            .round(6)
        )
        decision_df.columns = ["Mean R²", "Median R²", "Std Dev", "Count"]

        decision_file = f"{output_dir}/analysis_by_decision_{timestamp}.csv"
        decision_df.to_csv(decision_file)
        print(f"✅ Decision analysis exported to: {decision_file}")


def analyze_latest_results(results_dir: str = "hypatiax/data/results"):
    """Analyze the most recent results file"""
    results_path = Path(results_dir)

    # Find most recent hybrid results file
    hybrid_files = sorted(results_path.glob("hybrid_defi_*.json"))

    if not hybrid_files:
        print("❌ No hybrid results files found!")
        return

    latest_file = hybrid_files[-1]
    print(f"📂 Analyzing: {latest_file}\n")

    analyzer = HybridPerformanceAnalyzer(str(latest_file))
    analyzer.generate_summary_report()
    analyzer.generate_comparison_table()
    analyzer.identify_improvement_opportunities()
    analyzer.export_to_csv()


if __name__ == "__main__":
    analyze_latest_results()
