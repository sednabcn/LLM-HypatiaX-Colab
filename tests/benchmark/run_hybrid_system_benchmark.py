#!/usr/bin/env python3
"""
run_full_benchmark.py

Master script to run comprehensive benchmark suite:
1. Hybrid system evaluation (in-distribution)
2. Extrapolation tests
3. Performance analysis
4. Generate final report
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json


def run_command(cmd, description):
    """Run a command and handle output"""
    print("\n" + "=" * 80)
    print(f"▶️  {description}".center(80))
    print("=" * 80 + "\n")

    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"\n❌ Failed: {description}")
        return False
    else:
        print(f"\n✅ Completed: {description}")
        return True


def main():
    """Run complete benchmark suite"""

    start_time = datetime.now()

    print("=" * 80)
    print("🚀 FULL BENCHMARK SUITE - HYPATIAX DEFI 🚀".center(80))
    print("=" * 80)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nBenchmark plan:")
    print("  1. Hybrid System - In-distribution tests")
    print("  2. Extrapolation Tests")
    print("  3. Performance Analysis")
    print("  4. Final Report")
    print("=" * 80)

    verbose = "--verbose" if "--verbose" in sys.argv else ""

    # Step 1: Run hybrid system tests
    success = run_command(
        f"python hypatiax/core/generation/hybrid_system_defi_domain.py {verbose}",
        "Step 1/4: Hybrid System Evaluation",
    )

    if not success:
        print("\n⚠️  Continuing despite errors...")

    # Step 2: Run extrapolation tests
    success = run_command(
        f"python tests/integration/extrapolation/test_defi_extrapolation.py",
        "Step 2/4: Extrapolation Tests",
    )

    if not success:
        print("\n⚠️  Continuing despite errors...")

    # Step 3: Run performance analysis
    success = run_command(
        f"python analysis/analyze_hybrid_performance.py",
        "Step 3/4: Performance Analysis",
    )

    if not success:
        print("\n⚠️  Continuing despite errors...")

    # Step 4: Generate final report
    print("\n" + "=" * 80)
    print("▶️  Step 4/4: Generating Final Report".center(80))
    print("=" * 80 + "\n")

    generate_final_report()

    # Completion
    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 80)
    print("🎉 BENCHMARK COMPLETE 🎉".center(80))
    print("=" * 80)
    print(f"Duration: {duration}")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📊 Results saved in: hypatiax/data/results/")
    print("=" * 80)


def generate_final_report():
    """Generate final comprehensive report"""

    results_dir = Path("hypatiax/data/results")

    # Find latest files
    hybrid_files = sorted(results_dir.glob("hybrid_defi_*.json"))
    report_files = sorted(results_dir.glob("report_hybrid_*.json"))
    extrap_files = sorted(results_dir.glob("extrapolation_*.csv"))

    if not hybrid_files:
        print("❌ No results files found")
        return

    print("📄 FINAL REPORT")
    print("-" * 80)

    # Load latest hybrid results
    with open(hybrid_files[-1]) as f:
        hybrid_data = json.load(f)

    # Load latest report
    if report_files:
        with open(report_files[-1]) as f:
            report_data = json.load(f)

        overall = report_data.get("overall", {})

        print(f"\n📊 Overall Performance:")
        print(f"   Total cases: {overall.get('total_cases', 0)}")
        print(f"   Success rate: {overall.get('success_rate', 0) * 100:.1f}%")
        print(f"   Mean R²: {overall.get('mean_r2', 0):.6f}")
        print(f"   Median R²: {overall.get('median_r2', 0):.6f}")

        print(f"\n🏢 By Domain:")
        for domain, stats in report_data.get("by_domain", {}).items():
            print(
                f"   {domain:20} : {stats.get('mean_r2', 0):.6f} R² ({stats.get('total', 0)} cases)"
            )

        print(f"\n🔍 Extrapolation Tests:")
        extrap_tests = report_data.get("extrapolation_tests", [])
        if extrap_tests:
            extrap_r2 = [
                t["r2"]
                for t in extrap_tests
                if t.get("success") and t.get("r2") is not None
            ]
            if extrap_r2:
                print(f"   Cases: {len(extrap_tests)}")
                print(f"   Mean R²: {sum(extrap_r2) / len(extrap_r2):.6f}")
                print(f"   Min R²: {min(extrap_r2):.6f}")
                print(f"   Max R²: {max(extrap_r2):.6f}")

    # Decision breakdown
    decisions = {"llm": 0, "ensemble": 0, "nn": 0}
    for result in hybrid_data:
        decision = result.get("decision", "unknown")
        if decision in decisions:
            decisions[decision] += 1

    total = sum(decisions.values())
    print(f"\n🎯 Decision Breakdown:")
    print(f"   LLM: {decisions['llm']}/{total} ({decisions['llm'] / total * 100:.1f}%)")
    print(
        f"   Ensemble: {decisions['ensemble']}/{total} ({decisions['ensemble'] / total * 100:.1f}%)"
    )
    print(f"   NN: {decisions['nn']}/{total} ({decisions['nn'] / total * 100:.1f}%)")

    # Key findings
    print(f"\n🔑 Key Findings:")

    excellent_count = sum(
        1 for r in hybrid_data if r.get("evaluation", {}).get("r2", 0) > 0.99
    )
    print(f"   • {excellent_count}/{total} cases achieved R² > 0.99")

    llm_decisions = [r for r in hybrid_data if r.get("decision") == "llm"]
    if llm_decisions:
        llm_avg_r2 = sum(r["evaluation"]["r2"] for r in llm_decisions) / len(
            llm_decisions
        )
        print(f"   • LLM decisions averaged R² = {llm_avg_r2:.6f}")

    nn_decisions = [r for r in hybrid_data if r.get("decision") == "nn"]
    if nn_decisions:
        nn_avg_r2 = sum(r["evaluation"]["r2"] for r in nn_decisions) / len(nn_decisions)
        print(f"   • NN decisions averaged R² = {nn_avg_r2:.6f}")

    ensemble_decisions = [r for r in hybrid_data if r.get("decision") == "ensemble"]
    if ensemble_decisions:
        ens_avg_r2 = sum(r["evaluation"]["r2"] for r in ensemble_decisions) / len(
            ensemble_decisions
        )
        print(f"   • Ensemble decisions averaged R² = {ens_avg_r2:.6f}")

    # Recommendations
    print(f"\n💡 Recommendations:")

    poor_cases = [r for r in hybrid_data if r.get("evaluation", {}).get("r2", 1) < 0.80]
    if poor_cases:
        print(f"   ⚠️  {len(poor_cases)} cases with R² < 0.80 need attention:")
        for case in poor_cases[:3]:  # Show first 3
            print(f"      • {case.get('description', 'Unknown')[:60]}...")
    else:
        print(f"   ✅ All cases performing well (R² > 0.80)")

    failed_llm = [
        r
        for r in hybrid_data
        if not r.get("llm_result", {}).get("metrics", {}).get("success", True)
    ]
    if failed_llm:
        print(
            f"   ⚠️  {len(failed_llm)} cases where LLM failed - consider specialized prompts"
        )

    print(f"\n📁 Output files:")
    print(f"   • Latest results: {hybrid_files[-1].name}")
    if report_files:
        print(f"   • Latest report: {report_files[-1].name}")
    if extrap_files:
        print(f"   • Extrapolation: {extrap_files[-1].name}")


if __name__ == "__main__":
    main()
