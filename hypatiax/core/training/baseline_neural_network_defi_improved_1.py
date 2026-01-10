"""
baseline_neural_network_defi_improved.py - ENHANCED
Better architecture, regularization, and extrapolation handling
"""

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple, Dict
import json
import os
from datetime import datetime
from pathlib import Path

# Import protocol
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol


class ImprovedNN(nn.Module):
    """Improved neural network architecture with regularization"""

    def __init__(self, input_dim: int, hidden_dims: List[int] = [128, 64, 32]):
        super().__init__()

        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.extend(
                [
                    nn.Linear(prev_dim, hidden_dim),
                    nn.BatchNorm1d(hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                ]
            )
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, 1))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class NeuralNetworkBaseline:
    """Enhanced Neural Network baseline for DeFi formulas"""

    def __init__(
        self,
        hidden_dims: List[int] = [128, 64, 32],
        learning_rate: float = 0.001,
        epochs: int = 500,
        batch_size: int = 32,
    ):
        self.hidden_dims = hidden_dims
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.results = []

    def train_and_evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        description: str,
        domain: str,
        var_names: List[str],
        metadata: Dict,
        verbose: bool = False,
    ) -> Dict:
        """Train NN and evaluate performance"""

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale data
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()

        X_train_s = scaler_X.fit_transform(X_train)
        X_test_s = scaler_X.transform(X_test)
        y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
        y_test_s = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

        # Create model
        model = ImprovedNN(X.shape[1], self.hidden_dims)
        optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate)
        criterion = nn.MSELoss()

        # Training
        X_train_t = torch.FloatTensor(X_train_s)
        y_train_t = torch.FloatTensor(y_train_s).reshape(-1, 1)

        model.train()
        for epoch in range(self.epochs):
            # Mini-batch training
            indices = torch.randperm(len(X_train_t))
            for i in range(0, len(X_train_t), self.batch_size):
                batch_indices = indices[i : i + self.batch_size]
                X_batch = X_train_t[batch_indices]
                y_batch = y_train_t[batch_indices]

                optimizer.zero_grad()
                pred = model(X_batch)
                loss = criterion(pred, y_batch)
                loss.backward()
                optimizer.step()

            if verbose and (epoch + 1) % 100 == 0:
                print(f"  Epoch {epoch + 1}/{self.epochs}, Loss: {loss.item():.6f}")

        # Evaluate on test set
        model.eval()
        with torch.no_grad():
            # Test metrics (scaled)
            X_test_t = torch.FloatTensor(X_test_s)
            y_pred_s = model(X_test_t).numpy().flatten()

            # Inverse transform to original scale
            y_pred = scaler_y.inverse_transform(y_pred_s.reshape(-1, 1)).flatten()

            # Calculate metrics
            mse = np.mean((y_test - y_pred) ** 2)
            mae = np.mean(np.abs(y_test - y_pred))
            rmse = np.sqrt(mse)

            ss_res = np.sum((y_test - y_pred) ** 2)
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0.0

        # Full dataset prediction for analysis
        with torch.no_grad():
            X_full_s = scaler_X.transform(X)
            X_full_t = torch.FloatTensor(X_full_s)
            y_full_pred_s = model(X_full_t).numpy().flatten()
            y_full_pred = scaler_y.inverse_transform(
                y_full_pred_s.reshape(-1, 1)
            ).flatten()

            full_mse = np.mean((y - y_full_pred) ** 2)
            full_ss_res = np.sum((y - y_full_pred) ** 2)
            full_ss_tot = np.sum((y - np.mean(y)) ** 2)
            full_r2 = 1 - (full_ss_res / full_ss_tot) if full_ss_tot > 1e-10 else 0.0

        result = {
            "method": "neural_network",
            "description": description,
            "domain": domain,
            "variables": var_names,
            "architecture": {
                "input_dim": X.shape[1],
                "hidden_dims": self.hidden_dims,
                "total_params": sum(p.numel() for p in model.parameters()),
            },
            "training": {
                "epochs": self.epochs,
                "learning_rate": self.learning_rate,
                "batch_size": self.batch_size,
                "train_samples": len(X_train),
                "test_samples": len(X_test),
            },
            "evaluation": {
                "test_r2": float(r2),
                "test_rmse": float(rmse),
                "test_mae": float(mae),
                "full_dataset_r2": float(full_r2),
                "success": True,
            },
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
        }

        return result

    def save_results(self, filepath: str):
        """Save results to JSON"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results saved: {filepath}")


def train_neural_network(
    X: np.ndarray,
    y: np.ndarray,
    hidden_dims: List[int] = [128, 64, 32],
    epochs: int = 500,
) -> Tuple[nn.Module, Dict, StandardScaler, StandardScaler]:
    """
    Standalone function to train a neural network (for hybrid system use).
    Returns: (model, metrics, scaler_X, scaler_y)
    """

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    X_train_s = scaler_X.fit_transform(X_train)
    X_test_s = scaler_X.transform(X_test)
    y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

    model = ImprovedNN(X.shape[1], hidden_dims)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    X_train_t = torch.FloatTensor(X_train_s)
    y_train_t = torch.FloatTensor(y_train_s).reshape(-1, 1)

    # Training loop
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        pred = model(X_train_t)
        loss = criterion(pred, y_train_t)
        loss.backward()
        optimizer.step()

    # Evaluate
    model.eval()
    with torch.no_grad():
        X_test_t = torch.FloatTensor(X_test_s)
        y_pred_s = model(X_test_t).numpy().flatten()
        y_pred = scaler_y.inverse_transform(y_pred_s.reshape(-1, 1)).flatten()

        mse = np.mean((y_test - y_pred) ** 2)
        ss_res = np.sum((y_test - y_pred) ** 2)
        ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0.0

        metrics = {
            "r2": float(r2),
            "rmse": float(np.sqrt(mse)),
            "mae": float(np.mean(np.abs(y_test - y_pred))),
        }

    return model, metrics, scaler_X, scaler_y


def run_nn_baseline_test(
    domains: List[str] = None, num_samples: int = 100, verbose: bool = False
):
    """Run NN baseline on all test cases"""

    protocol = DeFiExperimentProtocol()
    nn_baseline = NeuralNetworkBaseline(
        hidden_dims=[128, 64, 32], learning_rate=0.001, epochs=500, batch_size=32
    )

    if domains is None:
        domains = protocol.get_all_domains()

    print("=" * 80)
    print("🧠 NEURAL NETWORK BASELINE - DeFi Formulas 🧠".center(80))
    print("=" * 80)
    print(f"Architecture: {nn_baseline.hidden_dims}")
    print(f"Epochs: {nn_baseline.epochs}")
    print(f"Domains: {', '.join(domains)}")
    print("=" * 80)

    all_results = []

    for domain in domains:
        print(f"\n{'=' * 80}")
        print(f"DOMAIN: {domain.upper()}".center(80))
        print("=" * 80)

        test_cases = protocol.load_test_data(domain, num_samples=num_samples)

        for i, (desc, X, y, var_names, meta) in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {desc}")
            print(f"  Variables: {', '.join(var_names)}")
            print(f"  Data shape: X={X.shape}, y={y.shape}")

            if meta.get("extrapolation_test"):
                print(f"  ⚠️  EXTRAPOLATION TEST")

            result = nn_baseline.train_and_evaluate(
                X, y, desc, domain, var_names, meta, verbose=verbose
            )

            metrics = result["evaluation"]
            print(
                f"  ✅ Test R²: {metrics['test_r2']:.6f}, RMSE: {metrics['test_rmse']:.6f}"
            )
            print(f"  📊 Full R²: {metrics['full_dataset_r2']:.6f}")

            if metrics["test_r2"] > 0.99:
                print(f"  🎯 EXCELLENT")
            elif metrics["test_r2"] > 0.95:
                print(f"  ✓ Good")
            elif metrics["test_r2"] > 0.80:
                print(f"  ~ Acceptable")
            else:
                print(f"  ⚠️  Needs improvement")

            all_results.append(result)
            nn_baseline.results.append(result)

    # Save results
    os.makedirs("hypatiax/data/results", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    nn_baseline.save_results(f"hypatiax/data/results/baseline_nn_improved_{ts}.json")

    # Generate report
    report = protocol.generate_experiment_report(all_results)
    with open(f"hypatiax/data/results/report_nn_improved_{ts}.json", "w") as f:
        json.dump(report, f, indent=2)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY".center(80))
    print("=" * 80)

    overall = report["overall"]
    print(f"\n📊 Total: {overall['total_cases']}")
    print(
        f"Success: {overall['successful']}/{overall['total_cases']} ({100 * overall['success_rate']:.1f}%)"
    )
    print(f"Mean R²: {overall['mean_r2']:.6f}")

    print(f"\n📈 By Domain:")
    for domain, stats in report["by_domain"].items():
        mean_r2 = stats.get("mean_r2")
        r2_str = f"{mean_r2:.4f}" if mean_r2 is not None else "N/A"
        print(f"  {domain}: {stats['successful']}/{stats['total']} - R²: {r2_str}")

    if report.get("extrapolation_tests"):
        print(f"\n🔍 Extrapolation Tests:")
        for test in report["extrapolation_tests"]:
            status = "✅" if test["success"] else "❌"
            r2 = test.get("r2")
            r2_str = f"R²: {r2:.4f}" if r2 is not None else "Failed"
            print(f"  {status} {test['description'][:50]}: {r2_str}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    import sys

    verbose = "--verbose" in sys.argv
    run_nn_baseline_test(domains=None, num_samples=100, verbose=verbose)
