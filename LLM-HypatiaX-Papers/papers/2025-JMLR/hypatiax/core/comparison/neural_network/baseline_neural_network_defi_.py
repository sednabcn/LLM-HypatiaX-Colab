import json
import os
from datetime import datetime
from typing import Dict, List, Callable, Optional

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split

# Import the experiment protocol
from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol


class SimpleNN(nn.Module):
    """Simple 3-layer MLP for regression."""

    def __init__(self, input_dim, hidden_dims=[64, 32]):
        super().__init__()
        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.extend([nn.Linear(prev_dim, hidden_dim), nn.ReLU()])
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class NeuralNetworkBaseline:
    """Neural network baseline for formula discovery in DeFi and Risk Management."""

    def __init__(self, hidden_dims=[64, 32], learning_rate=0.001, epochs=200):
        """
        Initialize Neural Network baseline.

        Args:
            hidden_dims: List of hidden layer dimensions
            learning_rate: Learning rate for Adam optimizer
            epochs: Number of training epochs
        """
        self.hidden_dims = hidden_dims
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.results = []

    def train_and_evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        description: str,
        metadata: Optional[Dict] = None,
        verbose: bool = True,
    ) -> Dict:
        """
        Train and evaluate a neural network.

        Args:
            X: Input features (N, D)
            y: Target values (N,)
            description: Description of the task
            metadata: Optional metadata about the test case
            verbose: Print training progress

        Returns:
            Dictionary containing evaluation metrics
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Initialize model
        model = SimpleNN(X.shape[1], hidden_dims=self.hidden_dims)
        optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate)
        criterion = nn.MSELoss()

        # Convert to tensors
        X_train_t = torch.FloatTensor(X_train)
        y_train_t = torch.FloatTensor(y_train).reshape(-1, 1)
        X_test_t = torch.FloatTensor(X_test)
        y_test_t = torch.FloatTensor(y_test).reshape(-1, 1)

        # Train
        model.train()
        train_losses = []

        for epoch in range(self.epochs):
            optimizer.zero_grad()
            pred = model(X_train_t)
            loss = criterion(pred, y_train_t)
            loss.backward()
            optimizer.step()

            train_losses.append(loss.item())

            if verbose and (epoch + 1) % 50 == 0:
                print(f"    Epoch {epoch + 1}/{self.epochs}, Loss: {loss.item():.6f}")

        # Evaluate on test set
        model.eval()
        with torch.no_grad():
            # Test set predictions
            y_pred = model(X_test_t).numpy().flatten()

            # Calculate test metrics
            mse_test = np.mean((y_test - y_pred) ** 2)
            mae_test = np.mean(np.abs(y_test - y_pred))
            rmse_test = np.sqrt(mse_test)

            # R² score on test set
            ss_res = np.sum((y_test - y_pred) ** 2)
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            r2_test = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            # Extrapolation test (2x beyond training range)
            # Only test extrapolation if marked as extrapolation test case
            extrap_results = None
            if metadata and metadata.get("extrapolation_test", False):
                # Test on data 2x the range
                X_max = X_train.max(axis=0)
                X_min = X_train.min(axis=0)
                X_range = X_max - X_min

                # Generate extrapolation data
                X_extrap = X_train + X_range  # Shift by one range
                X_extrap_t = torch.FloatTensor(X_extrap)
                y_extrap_pred = model(X_extrap_t).numpy().flatten()

                # Compute ground truth for extrapolation using same formula
                # We'll recompute using the ground truth formula if available
                extrap_results = {
                    "mean_prediction": float(np.mean(y_extrap_pred)),
                    "std_prediction": float(np.std(y_extrap_pred)),
                    "note": "Extrapolation predictions (no ground truth comparison in NN baseline)",
                }

        result = {
            "method": "neural_network",
            "architecture": f"{X.shape[1]}-{'-'.join(map(str, self.hidden_dims))}-1",
            "description": description,
            "metadata": metadata,
            "epochs": self.epochs,
            "final_train_loss": float(train_losses[-1]),
            "evaluation": {
                "mse": float(mse_test),
                "mae": float(mae_test),
                "rmse": float(rmse_test),
                "r2": float(r2_test),
                "success": True,
            },
            "extrapolation": extrap_results,
            "timestamp": datetime.now().isoformat(),
        }

        return result

    def save_results(self, filepath: str):
        """Save results to JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results saved to: {filepath}")


def run_comprehensive_nn_baseline(domains: List[str] = None, num_samples: int = 100):
    """
    Run comprehensive neural network baseline using experiment protocol.

    Args:
        domains: List of domains to test (None = all domains)
        num_samples: Number of samples per test case
    """
    protocol = DeFiExperimentProtocol()
    baseline = NeuralNetworkBaseline(
        hidden_dims=[64, 32], learning_rate=0.001, epochs=200
    )

    if domains is None:
        domains = protocol.get_all_domains()

    print("=" * 80)
    print("NEURAL NETWORK BASELINE EVALUATION - DEFI & RISK MANAGEMENT".center(80))
    print("=" * 80)
    print(f"Architecture: 3-layer MLP ({baseline.hidden_dims})")
    print(f"Epochs: {baseline.epochs}")
    print(f"Learning Rate: {baseline.learning_rate}")
    print(f"Domains: {', '.join(domains)}")
    print(f"Samples per test: {num_samples}")
    print("=" * 80)

    all_results = []

    for domain in domains:
        print(f"\n{'=' * 80}")
        print(f"DOMAIN: {domain.upper()}".center(80))
        print(f"{protocol.get_domain_description(domain)}".center(80))
        print("=" * 80)

        # Load test cases from protocol
        test_cases = protocol.load_test_data(domain, num_samples=num_samples)

        for i, (description, X, y_true, var_names, metadata) in enumerate(
            test_cases, 1
        ):
            print(f"\n[{i}/{len(test_cases)}] {description}")
            print(f"  Variables: {', '.join(var_names)}")
            print(f"  Ground truth: {metadata.get('ground_truth', 'N/A')}")
            print(f"  Difficulty: {metadata.get('difficulty', 'N/A')}")
            print(f"  Shape: X={X.shape}, y={y_true.shape}")

            if metadata.get("extrapolation_test"):
                print(f"  ⚠️  EXTRAPOLATION TEST CASE")

            # Train and evaluate
            print(f"  Training neural network...")
            result = baseline.train_and_evaluate(
                X=X, y=y_true, description=description, metadata=metadata, verbose=False
            )

            eval_metrics = result["evaluation"]

            if eval_metrics.get("success"):
                print(f"  ✅ R² Score: {eval_metrics['r2']:.6f}")
                print(f"  RMSE: {eval_metrics['rmse']:.6f}")
                print(f"  MAE: {eval_metrics['mae']:.6f}")
                print(f"  Final Train Loss: {result['final_train_loss']:.6f}")

                # Quality assessment
                if eval_metrics["r2"] > 0.99:
                    print(f"  🎯 EXCELLENT FIT")
                elif eval_metrics["r2"] > 0.95:
                    print(f"  ✓ Good fit")
                elif eval_metrics["r2"] > 0.80:
                    print(f"  ⚠️  Moderate fit")
                else:
                    print(f"  ❌ Poor fit")

                # Extrapolation note
                if result.get("extrapolation"):
                    print(
                        f"  📊 Extrapolation: mean={result['extrapolation']['mean_prediction']:.4f}"
                    )
            else:
                print(f"  ❌ Evaluation failed")

            all_results.append(result)
            baseline.results.append(result)

    # Generate comprehensive report using protocol
    print("\n" + "=" * 80)
    print("GENERATING COMPREHENSIVE REPORT".center(80))
    print("=" * 80)

    # Adapt results format for protocol's report generator
    adapted_results = []
    for result in all_results:
        adapted_results.append(
            {
                "domain": result.get("metadata", {}).get("domain", "unknown"),
                "description": result["description"],
                "evaluation": result["evaluation"],
                "method": result["method"],
            }
        )

    report = protocol.generate_experiment_report(adapted_results)

    # Save results
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"results/baseline_nn_defi_{timestamp}.json"
    report_file = f"results/report_nn_defi_{timestamp}.json"

    baseline.save_results(results_file)

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"✅ Report saved to: {report_file}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY".center(80))
    print("=" * 80)

    overall = report["overall"]
    print(f"\n📊 Overall Performance:")
    print(f"  Total test cases: {overall['total_cases']}")
    print(
        f"  Successful: {overall['successful']}/{overall['total_cases']} "
        f"({100 * overall['success_rate']:.1f}%)"
    )

    if "mean_r2" in overall:
        print(f"  Mean R²: {overall['mean_r2']:.6f}")
        print(f"  Median R²: {overall['median_r2']:.6f}")
        print(f"  Std R²: {overall['std_r2']:.6f}")
        print(f"  Min R²: {overall['min_r2']:.6f}")
        print(f"  Max R²: {overall['max_r2']:.6f}")

    print(f"\n📈 By Domain:")
    for domain, stats in report["by_domain"].items():
        r2_str = f"R²: {stats['mean_r2']:.4f}" if stats["mean_r2"] else "N/A"
        print(
            f"  {domain}: {stats['successful']}/{stats['total']} "
            f"({100 * stats['success_rate']:.1f}%) - {r2_str}"
        )

    # Highlight extrapolation test results
    if report["extrapolation_tests"]:
        print(f"\n🎯 Extrapolation Test Cases:")
        for test in report["extrapolation_tests"]:
            status = "✅" if test["success"] else "❌"
            r2_str = f"R²: {test['r2']:.4f}" if test.get("r2") is not None else "Failed"
            print(f"  {status} {test['description'][:60]}")
            print(f"     {r2_str}")

    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE".center(80))
    print("=" * 80)

    # Neural network characteristics
    print(f"\n⚠️  Neural Network Limitations:")
    print(f"  • Black box model - no interpretable formula")
    print(f"  • May struggle with extrapolation beyond training range")
    print(f"  • Requires retraining for each new dataset")
    print(f"  • Cannot provide mathematical insights")


def run_single_test():
    """Run a single test on impermanent loss for quick validation."""
    print("=" * 80)
    print("Neural Network Single Test - Impermanent Loss".center(80))
    print("=" * 80 + "\n")

    # Generate impermanent loss data
    np.random.seed(42)
    price_ratios = np.random.uniform(0.5, 2.0, 100).reshape(-1, 1)
    il = 2 * np.sqrt(price_ratios[:, 0]) / (1 + price_ratios[:, 0]) - 1

    baseline = NeuralNetworkBaseline(epochs=200)
    result = baseline.train_and_evaluate(
        X=price_ratios,
        y=il,
        description="Impermanent Loss (Quick Test)",
        metadata={"extrapolation_test": True},
        verbose=True,
    )

    print(f"\n{'=' * 80}")
    print("RESULTS".center(80))
    print("=" * 80)
    print(f"R² Score: {result['evaluation']['r2']:.6f}")
    print(f"RMSE: {result['evaluation']['rmse']:.6f}")
    print(f"Architecture: {result['architecture']}")


if __name__ == "__main__":
    # Run comprehensive evaluation on all domains
    run_comprehensive_nn_baseline(domains=None, num_samples=100)

    # Or run single test for quick validation:
    # run_single_test()

    # Or test specific domains:
    # run_comprehensive_nn_baseline(domains=["amm", "liquidation"], num_samples=100)
