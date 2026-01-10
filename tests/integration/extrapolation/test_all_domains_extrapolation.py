"""
scripts/test_all_domains_extrapolation.py

Extrapolation testing for all scientific/engineering domains
Similar to DeFi version but for materials, fluids, etc.
"""

import json
import numpy as np
from datetime import datetime
from scipy import stats
import pandas as pd

from experiment_protocol import ExperimentProtocol
from baseline_pure_llm import PureLLMBaseline
from baseline_neural_network import train_and_evaluate
from hybrid_system_all_domains import HybridSystemAllDomains


class ExtrapolationTesterAllDomains:
    """
    Extrapolation tester for all scientific domains.
    """

    def __init__(self):
        self.protocol = ExperimentProtocol()
        self.results = {}

    def create_extrapolation_split(self, X, y, var_names, test_case_name):
        """
        Create extrapolation split based on test case.

        Examples:
        - Hall-Petch: Train on grain_size 10-50μm, test on 50-100μm
        - Darcy's Law: Train on viscosity 0.001-0.01, test on 0.01-0.1
        - Ideal Gas: Train on pressure 1-5 atm, test on 5-10 atm
        """

        # Identify primary variable for extrapolation
        if (
            "grain size" in test_case_name.lower()
            or "hall-petch" in test_case_name.lower()
        ):
            # Grain size extrapolation
            primary_idx = 0
            split_value = np.median(X[:, primary_idx])
            train_mask = X[:, primary_idx] <= split_value
            test_mask = X[:, primary_idx] > split_value

        elif "viscosity" in test_case_name.lower() or "darcy" in test_case_name.lower():
            # Viscosity/flow extrapolation
            if "viscosity" in var_names[0].lower() if var_names else False:
                primary_idx = 0
            elif len(var_names) > 1 and "viscosity" in var_names[1].lower():
                primary_idx = 1
            else:
                primary_idx = 0

            split_value = np.percentile(X[:, primary_idx], 60)
            train_mask = X[:, primary_idx] <= split_value
            test_mask = X[:, primary_idx] > split_value

        elif (
            "pressure" in test_case_name.lower()
            or "temperature" in test_case_name.lower()
        ):
            # Thermodynamic extrapolation
            # Use first variable (often P or T)
            primary_idx = 0
            split_value = np.percentile(X[:, primary_idx], 60)
            train_mask = X[:, primary_idx] <= split_value
            test_mask = X[:, primary_idx] > split_value

        elif "stress" in test_case_name.lower() or "strain" in test_case_name.lower():
            # Mechanical property extrapolation
            primary_idx = 0
            split_value = np.percentile(X[:, primary_idx], 60)
            train_mask = X[:, primary_idx] <= split_value
            test_mask = X[:, primary_idx] > split_value

        else:
            # Default: 60/40 split by first variable
            primary_idx = 0
            split_value = np.percentile(X[:, primary_idx], 60)
            train_mask = X[:, primary_idx] <= split_value
            test_mask = X[:, primary_idx] > split_value

        X_train = X[train_mask]
        y_train = y[train_mask]
        X_test = X[test_mask]
        y_test = y[test_mask]

        return X_train, y_train, X_test, y_test

    def test_pure_llm_extrapolation(self, test_case, verbose=False):
        """Test Pure LLM on extrapolation"""
        desc, X_full, y_full, var_names, meta = test_case

        X_train, y_train, X_test, y_test = self.create_extrapolation_split(
            X_full, y_full, var_names, desc
        )

        if verbose:
            print(f"  [LLM] Train: {len(X_train)}, Test: {len(X_test)}")

        # Generate formula
        llm = PureLLMBaseline()
        domain = meta.get("domain", "general")
        result = llm.generate_formula(desc, domain, var_names, meta)

        # Evaluate on train
        train_metrics = llm.test_formula_accuracy(
            result, X_train, y_train, verbose=False
        )

        # Evaluate on test
        test_metrics = llm.test_formula_accuracy(result, X_test, y_test, verbose=False)

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
        }

    def test_nn_extrapolation(self, test_case, verbose=False):
        """Test NN on extrapolation"""
        desc, X_full, y_full, var_names, meta = test_case

        X_train, y_train, X_test, y_test = self.create_extrapolation_split(
            X_full, y_full, var_names, desc
        )

        if verbose:
            print(f"  [NN] Train: {len(X_train)}, Test: {len(X_test)}")

        # Train NN
        result = train_and_evaluate(
            X_train, y_train, desc, meta.get("domain", "general"), meta, epochs=200
        )

        train_r2 = result["evaluation"]["r2"]
        train_rmse = result["evaluation"]["rmse"]

        # Evaluate on test - simplified version
        from sklearn.preprocessing import StandardScaler
        import torch
        from baseline_neural_network import SimpleNN

        scaler_X = StandardScaler()
        scaler_y = StandardScaler()

        X_train_s = scaler_X.fit_transform(X_train)
        y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

        model = SimpleNN(X_train.shape[1])
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = torch.nn.MSELoss()

        X_train_t = torch.FloatTensor(X_train_s)
        y_train_t = torch.FloatTensor(y_train_s).reshape(-1, 1)

        for _ in range(200):
            optimizer.zero_grad()
            pred = model(X_train_t)
            loss = criterion(pred, y_train_t)
            loss.backward()
            optimizer.step()

        # Test evaluation
        model.eval()
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
        }

    def test_hybrid_extrapolation(self, test_case, verbose=False):
        """Test Hybrid on extrapolation"""
        desc, X_full, y_full, var_names, meta = test_case

        X_train, y_train, X_test, y_test = self.create_extrapolation_split(
            X_full, y_full, var_names, desc
        )

        if verbose:
            print(f"  [HYBRID] Train: {len(X_train)}, Test: {len(X_test)}")

        hybrid = HybridSystemAllDomains()

        # Train
        result = hybrid.hybrid_predict(
            desc,
            meta.get("domain", "general"),
            X_train,
            y_train,
            var_names,
            meta,
            verbose=False,
        )

        train_r2 = result["evaluation"]["r2"]
        train_rmse = result["evaluation"]["rmse"]

        # Test
        llm_result = hybrid.generate_llm_formula(
            desc, meta.get("domain", "general"), var_names, meta
        )

        if "error" not in llm_result:
            test_metrics = hybrid.evaluate_llm_formula(
                llm_result, X_test, y_test, var_names
            )
            test_r2 = test_metrics.get("r2", 0) if test_metrics.get("success") else 0
            test_rmse = (
                test_metrics.get("rmse", 1e10) if test_metrics.get("success") else 1e10
            )
        else:
            test_r2 = 0
            test_rmse = 1e10

        return {
            "method": "hybrid",
            "train_r2": float(train_r2),
            "test_r2": float(test_r2),
            "train_rmse": float(train_rmse),
            "test_rmse": float(test_rmse),
            "success": True,
        }

    def run_extrapolation_tests(self, domains=None, verbose=False):
        """Run extrapolation tests across all domains"""

        print("=" * 80)
        print("EXTRAPOLATION TEST - ALL SCIENTIFIC DOMAINS".center(80))
        print("=" * 80)
        print("Testing: Materials, Fluids, Thermodynamics, Mechanics, Chemistry")
        print("=" * 80)

        if domains is None:
            domains = self.protocol.get_all_domains()

        all_test_cases = []

        for domain in domains:
            test_cases = self.protocol.load_test_data(domain, num_samples=200)

            for test_case in test_cases:
                desc, X, y, var_names, meta = test_case
                # Add all test cases (not just extrapolation_test marked ones)
                all_test_cases.append((desc, X, y, var_names, meta))

        print(
            f"\nTesting {len(all_test_cases)} total cases across {len(domains)} domains\n"
        )

        all_results = []

        for i, test_case in enumerate(all_test_cases, 1):
            desc = test_case[0]
            print(f"\n[{i}/{len(all_test_cases)}] {desc[:60]}")

            print("  Testing Pure LLM...")
            llm_result = self.test_pure_llm_extrapolation(test_case, verbose=verbose)

            print("  Testing Neural Network...")
            nn_result = self.test_nn_extrapolation(test_case, verbose=verbose)

            print("  Testing Hybrid...")
            hybrid_result = self.test_hybrid_extrapolation(test_case, verbose=verbose)

            print(f"\n  Results (Test R²):")
            print(f"    LLM:    {llm_result['test_r2']:.4f}")
            print(f"    NN:     {nn_result['test_r2']:.4f}")
            print(f"    Hybrid: {hybrid_result['test_r2']:.4f}")

            all_results.append(
                {
                    "description": desc,
                    "llm": llm_result,
                    "nn": nn_result,
                    "hybrid": hybrid_result,
                }
            )

        self.generate_extrapolation_report(all_results)

        return all_results

    def generate_extrapolation_report(self, results):
        """Generate comprehensive statistical report"""

        print("\n" + "=" * 80)
        print("EXTRAPOLATION ANALYSIS - ALL DOMAINS".center(80))
        print("=" * 80)

        llm_test_r2 = [r["llm"]["test_r2"] for r in results if r["llm"]["success"]]
        nn_test_r2 = [r["nn"]["test_r2"] for r in results if r["nn"]["success"]]
        hybrid_test_r2 = [
            r["hybrid"]["test_r2"] for r in results if r["hybrid"]["success"]
        ]

        llm_mean = np.mean(llm_test_r2) if llm_test_r2 else 0
        llm_std = np.std(llm_test_r2) if llm_test_r2 else 0

        nn_mean = np.mean(nn_test_r2) if nn_test_r2 else 0
        nn_std = np.std(nn_test_r2) if nn_test_r2 else 0

        hybrid_mean = np.mean(hybrid_test_r2) if hybrid_test_r2 else 0
        hybrid_std = np.std(hybrid_test_r2) if hybrid_test_r2 else 0

        print(f"\n📊 Test Set R² Performance:")
        print(f"{'Method':<20} {'Mean':<12} {'Std Dev':<12} {'Min':<10} {'Max':<10}")
        print("-" * 70)

        print(
            f"{'Pure LLM':<20} {llm_mean:<12.4f} {llm_std:<12.4f} {min(llm_test_r2) if llm_test_r2 else 0:<10.4f} {max(llm_test_r2) if llm_test_r2 else 0:<10.4f}"
        )
        print(
            f"{'Neural Network':<20} {nn_mean:<12.4f} {nn_std:<12.4f} {min(nn_test_r2) if nn_test_r2 else 0:<10.4f} {max(nn_test_r2) if nn_test_r2 else 0:<10.4f}"
        )
        print(
            f"{'Hybrid System':<20} {hybrid_mean:<12.4f} {hybrid_std:<12.4f} {min(hybrid_test_r2) if hybrid_test_r2 else 0:<10.4f} {max(hybrid_test_r2) if hybrid_test_r2 else 0:<10.4f}"
        )

        # Statistical significance
        if len(llm_test_r2) > 1 and len(nn_test_r2) > 1:
            t_stat, p_val = stats.ttest_ind(llm_test_r2, nn_test_r2)
            print(f"\n📈 T-test LLM vs NN: t={t_stat:.4f}, p={p_val:.4f}")
            if p_val < 0.05:
                winner = "LLM" if llm_mean > nn_mean else "NN"
                print(f"   ✅ {winner} significantly better")

        if len(hybrid_test_r2) > 1 and len(nn_test_r2) > 1:
            t_stat, p_val = stats.ttest_ind(hybrid_test_r2, nn_test_r2)
            print(f"📈 T-test Hybrid vs NN: t={t_stat:.4f}, p={p_val:.4f}")
            if p_val < 0.05:
                winner = "Hybrid" if hybrid_mean > nn_mean else "NN"
                print(f"   ✅ {winner} significantly better")

        # Table 1
        print("\n" + "=" * 80)
        print("TABLE 1: EXTRAPOLATION RESULTS - ALL DOMAINS".center(80))
        print("=" * 80)

        print(
            f"\n{'Method':<20} {'Test R² (%)':<15} {'Std Dev (%)':<15} {'vs Baseline':<15}"
        )
        print("-" * 70)

        baseline = nn_mean
        llm_diff = ((llm_mean - baseline) / baseline * 100) if baseline > 0 else 0
        hybrid_diff = ((hybrid_mean - baseline) / baseline * 100) if baseline > 0 else 0

        print(
            f"{'Neural Network':<20} {nn_mean * 100:<15.1f} {nn_std * 100:<15.1f} {'(baseline)':<15}"
        )
        print(
            f"{'Pure LLM':<20} {llm_mean * 100:<15.1f} {llm_std * 100:<15.1f} {llm_diff:+.1f}%"
        )
        print(
            f"{'Hybrid System':<20} {hybrid_mean * 100:<15.1f} {hybrid_std * 100:<15.1f} {hybrid_diff:+.1f}%"
        )

        # Export
        df = pd.DataFrame(
            {
                "Method": ["Neural Network", "Pure LLM", "Hybrid System"],
                "Mean_R2": [nn_mean, llm_mean, hybrid_mean],
                "Std_Dev": [nn_std, llm_std, hybrid_std],
                "Improvement_vs_NN": [0, llm_diff, hybrid_diff],
            }
        )

        df.to_csv("results/extrapolation_all_domains_table1.csv", index=False)
        print("\n✅ Results exported to: results/extrapolation_all_domains_table1.csv")

        print("=" * 80)


if __name__ == "__main__":
    import sys

    domains = None
    if "--quick" in sys.argv:
        domains = ["materials", "fluids"]
        print("Quick test mode: Materials + Fluids only")

    verbose = "--verbose" in sys.argv

    tester = ExtrapolationTesterAllDomains()
    results = tester.run_extrapolation_tests(domains=domains, verbose=verbose)
