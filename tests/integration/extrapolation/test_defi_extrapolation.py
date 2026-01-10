"""
tests/integration/extrapolation/test_defi_extrapolation.py - UPDATED

Goal: Demonstrate 84.7% vs 23% extrapolation performance
Tests models on data OUTSIDE their training range
Fixes: Better splits, true ensemble evaluation, enhanced reporting
"""

import json
import numpy as np
from datetime import datetime
from scipy import stats
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol
from hypatiax.core.generation.baseline_pure_llm_defi_discovery import PureLLMBaseline
from hypatiax.core.training.baseline_neural_network_defi_improved import (
    train_neural_network,
)
from hypatiax.core.generation.hybrid_system_defi_domain import HybridSystemDeFi


class ExtrapolationTester:
    """
    UPDATED: Test extrapolation capability with better evaluation.

    Framework:
    - Train on LIMITED range (e.g., price_ratio 0.5-1.5)
    - Test on EXTENDED range (e.g., price_ratio 1.5-2.5)
    - Measure performance degradation
    - Use consistent test cases across all methods
    """

    def __init__(self):
        self.protocol = DeFiExperimentProtocol()
        self.results = {}

    def create_extrapolation_split(self, X, y, var_names, test_case_name):
        """
        ENHANCED: Create more aggressive extrapolation splits.
        """

        if "impermanent loss" in test_case_name.lower():
            # Price ratio extrapolation: train on 0.5-1.3, test on 1.5-2.0
            primary_var_idx = 0
            train_mask = X[:, primary_var_idx] <= 1.3
            test_mask = X[:, primary_var_idx] >= 1.5

        elif "value at risk at 95%" in test_case_name.lower():
            # Volatility extrapolation: train on 0.01-0.03, test on 0.035-0.05
            if X.shape[1] >= 2:
                vol_idx = 1
                train_mask = X[:, vol_idx] <= 0.03
                test_mask = X[:, vol_idx] >= 0.035
            else:
                train_mask = np.arange(len(X)) < int(0.6 * len(X))
                test_mask = ~train_mask

        elif (
            "liquidation price" in test_case_name.lower()
            and "long" in test_case_name.lower()
        ):
            # Leverage extrapolation: train on 2-5, test on 7-10
            if X.shape[1] >= 2:
                lev_idx = 1
                train_mask = X[:, lev_idx] <= 5.0
                test_mask = X[:, lev_idx] >= 7.0
            else:
                train_mask = np.arange(len(X)) < int(0.6 * len(X))
                test_mask = ~train_mask

        elif "expected shortfall at 95%" in test_case_name.lower():
            # Volatility extrapolation
            if X.shape[1] >= 2:
                vol_idx = 1
                train_mask = X[:, vol_idx] <= 0.03
                test_mask = X[:, vol_idx] >= 0.035
            else:
                train_mask = np.arange(len(X)) < int(0.6 * len(X))
                test_mask = ~train_mask

        elif (
            "optimal lp" in test_case_name.lower() or "kelly" in test_case_name.lower()
        ):
            # APY extrapolation: train on 0.05-0.18, test on 0.22-0.30
            if X.shape[1] >= 1:
                apy_idx = 0
                train_mask = X[:, apy_idx] <= 0.18
                test_mask = X[:, apy_idx] >= 0.22
            else:
                train_mask = np.arange(len(X)) < int(0.6 * len(X))
                test_mask = ~train_mask
        else:
            # Default: 60/40 split
            train_mask = np.arange(len(X)) < int(0.6 * len(X))
            test_mask = ~train_mask

        # Ensure both sets have data
        if train_mask.sum() < 10 or test_mask.sum() < 10:
            # Fallback to simple split
            train_mask = np.arange(len(X)) < int(0.6 * len(X))
            test_mask = ~train_mask

        X_train = X[train_mask]
        y_train = y[train_mask]
        X_test = X[test_mask]
        y_test = y[test_mask]

        return X_train, y_train, X_test, y_test

    def test_pure_llm_extrapolation(self, test_case, verbose=False):
        """Test Pure LLM on extrapolation"""
        desc, X_full, y_full, var_names, meta = test_case

        # Split data
        X_train, y_train, X_test, y_test = self.create_extrapolation_split(
            X_full, y_full, var_names, desc
        )

        if verbose:
            print(f"\n  [LLM] Train: {len(X_train)}, Test: {len(X_test)}")

        # LLM generates formula (not dependent on training data)
        llm = PureLLMBaseline()
        result = llm.generate_formula(desc, meta.get("domain", "defi"), var_names, meta)

        # Evaluate on TRAINING data
        train_metrics = llm.test_formula_accuracy(
            result, X_train, y_train, var_names, verbose=False
        )

        # Evaluate on TEST data (extrapolation)
        test_metrics = llm.test_formula_accuracy(
            result, X_test, y_test, var_names, verbose=False
        )

        return {
            "method": "pure_llm",
            "train_r2": train_metrics.get("r2", 0)
            if train_metrics.get("success")
            else 0,
            "test_r2": test_metrics.get("r2", 0) if test_metrics.get("success") else 0,
            "train_rmse": train_metrics.get("rmse", 1e10)
            if train_metrics.get("success")
            else 1e10,
            "test_rmse": test_metrics.get("rmse", 1e10)
            if test_metrics.get("success")
            else 1e10,
            "success": train_metrics.get("success", False)
            and test_metrics.get("success", False),
            "train_size": len(X_train),
            "test_size": len(X_test),
        }

    def test_nn_extrapolation(self, test_case, verbose=False):
        """Test Neural Network on extrapolation"""
        desc, X_full, y_full, var_names, meta = test_case

        X_train, y_train, X_test, y_test = self.create_extrapolation_split(
            X_full, y_full, var_names, desc
        )

        if verbose:
            print(f"\n  [NN] Train: {len(X_train)}, Test: {len(X_test)}")

        # Train NN on training data only
        from sklearn.preprocessing import StandardScaler
        import torch
        from hypatiax.core.training.baseline_neural_network_defi_improved import (
            ImprovedNN,
        )

        scaler_X = StandardScaler()
        scaler_y = StandardScaler()

        X_train_s = scaler_X.fit_transform(X_train)
        y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

        model = ImprovedNN(X_train.shape[1], [128, 64, 32])
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = torch.nn.MSELoss()

        X_train_t = torch.FloatTensor(X_train_s)
        y_train_t = torch.FloatTensor(y_train_s).reshape(-1, 1)

        # Training
        for _ in range(300):
            optimizer.zero_grad()
            pred = model(X_train_t)
            loss = criterion(pred, y_train_t)
            loss.backward()
            optimizer.step()

        # Evaluate on training data
        model.eval()
        with torch.no_grad():
            y_pred_train_s = model(X_train_t).numpy().flatten()
            y_pred_train = scaler_y.inverse_transform(
                y_pred_train_s.reshape(-1, 1)
            ).flatten()

            mse_train = np.mean((y_train - y_pred_train) ** 2)
            ss_res = np.sum((y_train - y_pred_train) ** 2)
            ss_tot = np.sum((y_train - np.mean(y_train)) ** 2)
            train_r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0
            train_rmse = np.sqrt(mse_train)

        # Evaluate on test data (extrapolation)
        with torch.no_grad():
            X_test_s = scaler_X.transform(X_test)
            X_test_t = torch.FloatTensor(X_test_s)
            y_pred_s = model(X_test_t).numpy().flatten()
            y_pred = scaler_y.inverse_transform(y_pred_s.reshape(-1, 1)).flatten()

            mse = np.mean((y_test - y_pred) ** 2)
            ss_res = np.sum((y_test - y_pred) ** 2)
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            test_r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0
            test_rmse = np.sqrt(mse)

        return {
            "method": "neural_network",
            "train_r2": float(train_r2),
            "test_r2": float(test_r2),
            "train_rmse": float(train_rmse),
            "test_rmse": float(test_rmse),
            "success": True,
            "train_size": len(X_train),
            "test_size": len(X_test),
        }

    def test_hybrid_extrapolation(self, test_case, verbose=False):
        """Test UPDATED Hybrid system on extrapolation"""
        desc, X_full, y_full, var_names, meta = test_case

        X_train, y_train, X_test, y_test = self.create_extrapolation_split(
            X_full, y_full, var_names, desc
        )

        if verbose:
            print(f"\n  [HYBRID] Train: {len(X_train)}, Test: {len(X_test)}")

        # Use UPDATED hybrid system
        hybrid = HybridSystemDeFi()

        # Train on training data (hybrid learns from this)
        train_result = hybrid.hybrid_predict(
            desc,
            meta.get("domain", "defi"),
            X_train,
            y_train,
            var_names,
            meta,
            verbose=False,
        )

        train_r2 = train_result["evaluation"]["r2"]
        train_rmse = train_result["evaluation"]["rmse"]

        # Evaluate on test data (extrapolation)
        # The LLM formula should work on test data without retraining
        llm_result = train_result["llm_result"]

        if llm_result.get("python_code") and llm_result["python_code"] != "N/A":
            test_metrics = hybrid.evaluate_llm_formula(
                {"python_code": llm_result["python_code"]}, X_test, y_test, var_names
            )
            test_r2 = test_metrics.get("r2", 0) if test_metrics.get("success") else 0
            test_rmse = (
                test_metrics.get("rmse", 1e10) if test_metrics.get("success") else 1e10
            )
        else:
            # Fallback: assume NN-like extrapolation
            test_r2 = 0
            test_rmse = 1e10

        return {
            "method": "hybrid",
            "train_r2": float(train_r2),
            "test_r2": float(test_r2),
            "train_rmse": float(train_rmse),
            "test_rmse": float(test_rmse),
            "success": True,
            "decision": train_result["decision"],
            "train_size": len(X_train),
            "test_size": len(X_test),
        }

    def run_extrapolation_tests(self, verbose=False):
        """Run comprehensive extrapolation tests"""

        print("=" * 80)
        print("EXTRAPOLATION TEST FRAMEWORK (UPDATED)".center(80))
        print("=" * 80)
        print("Goal: Achieve 84.7% vs 23% extrapolation accuracy")
        print("Method: Train on LIMITED range, test on EXTENDED range")
        print("Updates: Better splits, true ensemble, enhanced reporting")
        print("=" * 80)

        # Get extrapolation test cases
        critical_tests = []

        for domain in self.protocol.get_all_domains():
            test_cases = self.protocol.load_test_data(domain, num_samples=200)

            for test_case in test_cases:
                desc, X, y, var_names, meta = test_case
                if meta.get("extrapolation_test", False):
                    critical_tests.append((desc, X, y, var_names, meta))

        print(f"\nFound {len(critical_tests)} extrapolation test cases\n")

        all_results = []

        for i, test_case in enumerate(critical_tests, 1):
            desc = test_case[0]
            print(f"\n[{i}/{len(critical_tests)}] {desc}")

            # Test all three methods
            print("  Testing Pure LLM...")
            llm_result = self.test_pure_llm_extrapolation(test_case, verbose=verbose)

            print("  Testing Neural Network...")
            nn_result = self.test_nn_extrapolation(test_case, verbose=verbose)

            print("  Testing Hybrid (Updated)...")
            hybrid_result = self.test_hybrid_extrapolation(test_case, verbose=verbose)

            # Display results
            print(f"\n  Results:")
            print(
                f"    Pure LLM:  Train R²={llm_result['train_r2']:.4f}, Test R²={llm_result['test_r2']:.4f}"
            )
            print(
                f"    NN:        Train R²={nn_result['train_r2']:.4f}, Test R²={nn_result['test_r2']:.4f}"
            )
            print(
                f"    Hybrid:    Train R²={hybrid_result['train_r2']:.4f}, Test R²={hybrid_result['test_r2']:.4f} ({hybrid_result['decision']})"
            )

            # Performance drop analysis
            llm_drop = llm_result["train_r2"] - llm_result["test_r2"]
            nn_drop = nn_result["train_r2"] - nn_result["test_r2"]
            hybrid_drop = hybrid_result["train_r2"] - hybrid_result["test_r2"]

            print(f"\n  Extrapolation Drop:")
            print(
                f"    LLM: {llm_drop:+.4f} | NN: {nn_drop:+.4f} | Hybrid: {hybrid_drop:+.4f}"
            )

            all_results.append(
                {
                    "description": desc,
                    "llm": llm_result,
                    "nn": nn_result,
                    "hybrid": hybrid_result,
                }
            )

        # Statistical analysis
        self.generate_extrapolation_report(all_results)

        return all_results

    def generate_extrapolation_report(self, results):
        """Generate ENHANCED statistical analysis and Table 1"""

        print("\n" + "=" * 80)
        print("EXTRAPOLATION PERFORMANCE ANALYSIS (UPDATED)".center(80))
        print("=" * 80)

        # Extract metrics
        llm_test_r2 = [r["llm"]["test_r2"] for r in results if r["llm"]["success"]]
        nn_test_r2 = [r["nn"]["test_r2"] for r in results if r["nn"]["success"]]
        hybrid_test_r2 = [
            r["hybrid"]["test_r2"] for r in results if r["hybrid"]["success"]
        ]

        # Calculate statistics
        llm_mean = np.mean(llm_test_r2) if llm_test_r2 else 0
        llm_std = np.std(llm_test_r2) if llm_test_r2 else 0

        nn_mean = np.mean(nn_test_r2) if nn_test_r2 else 0
        nn_std = np.std(nn_test_r2) if nn_test_r2 else 0

        hybrid_mean = np.mean(hybrid_test_r2) if hybrid_test_r2 else 0
        hybrid_std = np.std(hybrid_test_r2) if hybrid_test_r2 else 0

        print(f"\n📊 Extrapolation Test R² Scores:")
        print(f"{'Method':<20} {'Mean R²':<12} {'Std Dev':<12} {'95% CI':<20}")
        print("-" * 70)

        # Confidence intervals
        ci_llm = 1.96 * llm_std / np.sqrt(len(llm_test_r2)) if llm_test_r2 else 0
        ci_nn = 1.96 * nn_std / np.sqrt(len(nn_test_r2)) if nn_test_r2 else 0
        ci_hybrid = (
            1.96 * hybrid_std / np.sqrt(len(hybrid_test_r2)) if hybrid_test_r2 else 0
        )

        print(
            f"{'Pure LLM':<20} {llm_mean:<12.4f} {llm_std:<12.4f} [{llm_mean - ci_llm:.4f}, {llm_mean + ci_llm:.4f}]"
        )
        print(
            f"{'Neural Network':<20} {nn_mean:<12.4f} {nn_std:<12.4f} [{nn_mean - ci_nn:.4f}, {nn_mean + ci_nn:.4f}]"
        )
        print(
            f"{'Hybrid System':<20} {hybrid_mean:<12.4f} {hybrid_std:<12.4f} [{hybrid_mean - ci_hybrid:.4f}, {hybrid_mean + ci_hybrid:.4f}]"
        )

        # T-test for significance
        if len(llm_test_r2) > 1 and len(nn_test_r2) > 1:
            try:
                t_stat_llm_nn, p_val_llm_nn = stats.ttest_ind(llm_test_r2, nn_test_r2)
                print(
                    f"\n📈 T-test LLM vs NN: t={t_stat_llm_nn:.4f}, p={p_val_llm_nn:.4f}"
                )
                if p_val_llm_nn < 0.05:
                    winner = "LLM" if llm_mean > nn_mean else "NN"
                    print(f"   ✅ {winner} significantly better (p < 0.05)")
            except:
                print(f"\n📈 T-test LLM vs NN: Unable to compute")

        if len(hybrid_test_r2) > 1 and len(nn_test_r2) > 1:
            try:
                t_stat_hyb_nn, p_val_hyb_nn = stats.ttest_ind(
                    hybrid_test_r2, nn_test_r2
                )
                print(
                    f"📈 T-test Hybrid vs NN: t={t_stat_hyb_nn:.4f}, p={p_val_hyb_nn:.4f}"
                )
                if p_val_hyb_nn < 0.05:
                    winner = "Hybrid" if hybrid_mean > nn_mean else "NN"
                    print(f"   ✅ {winner} significantly better (p < 0.05)")
            except:
                print(f"📈 T-test Hybrid vs NN: Unable to compute")

        # Table 1 format
        print("\n" + "=" * 80)
        print("TABLE 1: EXTRAPOLATION ACCURACY COMPARISON".center(80))
        print("=" * 80)

        print(f"\n{'Method':<20} {'Test R² (Mean)':<20} {'Std Dev':<15} {'vs NN':<15}")
        print("-" * 70)

        baseline_score = nn_mean

        llm_improvement = (
            ((llm_mean - baseline_score) / baseline_score * 100)
            if baseline_score > 0
            else 0
        )
        hybrid_improvement = (
            ((hybrid_mean - baseline_score) / baseline_score * 100)
            if baseline_score > 0
            else 0
        )

        print(
            f"{'Neural Network':<20} {nn_mean * 100:<20.1f} {nn_std * 100:<15.1f} {'(baseline)':<15}"
        )
        print(
            f"{'Pure LLM':<20} {llm_mean * 100:<20.1f} {llm_std * 100:<15.1f} {llm_improvement:+.1f}%"
        )
        print(
            f"{'Hybrid System':<20} {hybrid_mean * 100:<20.1f} {hybrid_std * 100:<15.1f} {hybrid_improvement:+.1f}%"
        )

        # Target analysis
        target_gap = 84.7 - 23.0
        actual_gap = hybrid_mean * 100 - nn_mean * 100

        print(f"\n🎯 Target Gap: {target_gap:.1f}% (84.7% - 23%)")
        print(
            f"📊 Actual Gap: {actual_gap:.1f}% ({hybrid_mean * 100:.1f}% - {nn_mean * 100:.1f}%)"
        )

        if actual_gap >= target_gap * 0.8:
            print(f"✅ TARGET ACHIEVED (within 80%)")
        elif actual_gap >= 0:
            print(
                f"🟡 PARTIAL SUCCESS ({actual_gap / target_gap * 100:.1f}% of target)"
            )
        else:
            print(f"⚠️  Continue optimization needed")

        # Export to CSV
        df = pd.DataFrame(
            {
                "Method": ["Neural Network", "Pure LLM", "Hybrid System"],
                "Mean_R2": [nn_mean, llm_mean, hybrid_mean],
                "Std_Dev": [nn_std, llm_std, hybrid_std],
                "CI_Lower": [
                    nn_mean - ci_nn,
                    llm_mean - ci_llm,
                    hybrid_mean - ci_hybrid,
                ],
                "CI_Upper": [
                    nn_mean + ci_nn,
                    llm_mean + ci_llm,
                    hybrid_mean + ci_hybrid,
                ],
                "Improvement_vs_NN": [0, llm_improvement, hybrid_improvement],
            }
        )

        df.to_csv("hypatiax/data/results/extrapolation_table1_updated.csv", index=False)
        print(
            "\n✅ Results exported to: hypatiax/data/results/extrapolation_table1_updated.csv"
        )

        print("=" * 80)


if __name__ == "__main__":
    tester = ExtrapolationTester()
    results = tester.run_extrapolation_tests(verbose=False)
