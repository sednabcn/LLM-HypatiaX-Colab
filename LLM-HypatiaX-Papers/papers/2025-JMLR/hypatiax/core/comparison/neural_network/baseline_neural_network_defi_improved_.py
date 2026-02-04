"""
COMPLETE REWRITE: baseline_neural_network_defi.py
Fixed version with improved architecture, training, and data handling.

KEY IMPROVEMENTS:
1. Better data normalization (StandardScaler for both X and y)
2. Improved network architecture with dropout and batch norm
3. Early stopping to prevent overfitting
4. Learning rate scheduling
5. Proper train/val/test split
6. Better handling of extrapolation tests
7. Consistent evaluation metrics with Pure LLM baseline

Expected improvements:
- Better generalization on extrapolation tests
- More stable training with fewer poor fits
- Comparable or better performance to Pure LLM on some domains
"""

import json
import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from pathlib import Path

# Import experiment protocol
from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol


class ImprovedNN(nn.Module):
    """
    Improved neural network architecture with:
    - Batch normalization for stable training
    - Dropout for regularization
    - Larger hidden layers for better capacity
    """

    def __init__(self, input_dim, hidden_dims=[128, 64, 32]):
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

        # Output layer (no activation, no dropout)
        layers.append(nn.Linear(prev_dim, 1))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class EarlyStopping:
    """Early stopping to prevent overfitting."""

    def __init__(self, patience=20, min_delta=1e-6):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False

    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0


def train_neural_network(
    X, y, description, domain, metadata=None, epochs=500, lr=0.001, verbose=False
):
    """
    Train and evaluate an improved neural network with proper data handling.

    Args:
        X: Input features (numpy array)
        y: Target values (numpy array)
        description: Test case description
        domain: Domain name
        metadata: Test case metadata
        epochs: Maximum training epochs
        lr: Initial learning rate
        verbose: Print training progress

    Returns:
        Dictionary with results in format compatible with Pure LLM baseline
    """

    # =====================================================================
    # DATA PREPARATION
    # =====================================================================

    # Check if this is an extrapolation test
    is_extrapolation = metadata.get("extrapolation_test", False) if metadata else False

    # Split data: 60% train, 20% val, 20% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.4, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )

    # CRITICAL: Normalize data using StandardScaler
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    X_train_scaled = scaler_X.fit_transform(X_train)
    X_val_scaled = scaler_X.transform(X_val)
    X_test_scaled = scaler_X.transform(X_test)

    y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
    y_val_scaled = scaler_y.transform(y_val.reshape(-1, 1)).flatten()
    # Note: We don't scale y_test yet - we'll use original scale for metrics

    # Convert to PyTorch tensors
    X_train_t = torch.FloatTensor(X_train_scaled)
    y_train_t = torch.FloatTensor(y_train_scaled).reshape(-1, 1)
    X_val_t = torch.FloatTensor(X_val_scaled)
    y_val_t = torch.FloatTensor(y_val_scaled).reshape(-1, 1)
    X_test_t = torch.FloatTensor(X_test_scaled)

    # =====================================================================
    # MODEL SETUP
    # =====================================================================

    input_dim = X.shape[1]
    model = ImprovedNN(input_dim, hidden_dims=[128, 64, 32])

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)

    # Learning rate scheduler - reduce on plateau (FIXED: removed verbose parameter)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=15
    )

    # Early stopping
    early_stopping = EarlyStopping(patience=30, min_delta=1e-6)

    # =====================================================================
    # TRAINING LOOP
    # =====================================================================

    train_losses = []
    val_losses = []
    best_val_loss = float("inf")
    best_model_state = None

    for epoch in range(epochs):
        # Training phase
        model.train()
        optimizer.zero_grad()

        train_pred = model(X_train_t)
        train_loss = criterion(train_pred, y_train_t)

        train_loss.backward()
        optimizer.step()

        # Validation phase
        model.eval()
        with torch.no_grad():
            val_pred = model(X_val_t)
            val_loss = criterion(val_pred, y_val_t)

        train_losses.append(train_loss.item())
        val_losses.append(val_loss.item())

        # Save best model
        if val_loss.item() < best_val_loss:
            best_val_loss = val_loss.item()
            best_model_state = model.state_dict().copy()

        # Learning rate scheduling
        scheduler.step(val_loss)

        # Early stopping check
        early_stopping(val_loss.item())
        if early_stopping.early_stop:
            if verbose:
                print(f"  Early stopping at epoch {epoch + 1}")
            break

        # Print progress
        if verbose and (epoch + 1) % 50 == 0:
            print(
                f"  Epoch {epoch + 1}/{epochs} - "
                f"Train Loss: {train_loss.item():.6f}, "
                f"Val Loss: {val_loss.item():.6f}"
            )

    # Restore best model
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    # =====================================================================
    # EVALUATION ON TEST SET
    # =====================================================================

    model.eval()
    with torch.no_grad():
        # Get predictions on scaled test data
        y_pred_scaled = model(X_test_t).numpy().flatten()

        # Transform back to original scale
        y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

        # Use original scale y_test for metrics
        y_test_original = y_test

        # Calculate metrics on ORIGINAL scale (critical for fair comparison)
        mse = np.mean((y_test_original - y_pred) ** 2)
        mae = np.mean(np.abs(y_test_original - y_pred))
        rmse = np.sqrt(mse)

        # R² score
        ss_res = np.sum((y_test_original - y_pred) ** 2)
        ss_tot = np.sum((y_test_original - np.mean(y_test_original)) ** 2)

        if ss_tot > 1e-10:
            r2 = 1 - (ss_res / ss_tot)
        else:
            # Handle edge case where all y values are nearly identical
            r2 = 1.0 if ss_res < 1e-10 else 0.0

    # =====================================================================
    # EXTRAPOLATION ANALYSIS (if applicable)
    # =====================================================================

    extrapolation_stats = None
    if is_extrapolation:
        # For extrapolation tests, also evaluate on full dataset
        model.eval()
        with torch.no_grad():
            X_all_scaled = scaler_X.transform(X)
            X_all_t = torch.FloatTensor(X_all_scaled)
            y_all_pred_scaled = model(X_all_t).numpy().flatten()
            y_all_pred = scaler_y.inverse_transform(
                y_all_pred_scaled.reshape(-1, 1)
            ).flatten()

            extrapolation_stats = {
                "mean_prediction": float(np.mean(y_all_pred)),
                "std_prediction": float(np.std(y_all_pred)),
                "mean_error": float(np.mean(y_all_pred - y)),
                "extrapolation_quality": "poor"
                if abs(np.mean(y_all_pred - y)) > np.std(y)
                else "good",
            }

    # =====================================================================
    # RETURN RESULTS (compatible with Pure LLM format)
    # =====================================================================

    result = {
        "method": "neural_network",
        "architecture": "3-layer MLP [128, 64, 32] with BatchNorm and Dropout",
        "description": description,
        "domain": domain,
        "evaluation": {
            "r2": float(r2),
            "rmse": float(rmse),
            "mae": float(mae),
            "mse": float(mse),
            "success": True,
        },
        "training_info": {
            "epochs_trained": len(train_losses),
            "final_train_loss": float(train_losses[-1]),
            "final_val_loss": float(val_losses[-1]),
            "best_val_loss": float(best_val_loss),
            "early_stopped": early_stopping.early_stop,
        },
        "metadata": metadata,
        "timestamp": datetime.now().isoformat(),
    }

    if extrapolation_stats:
        result["extrapolation_stats"] = extrapolation_stats

    return result


def run_comprehensive_test(
    domains=None, num_samples=100, epochs=500, save_dir="results", verbose=False
):
    """
    Run comprehensive neural network baseline evaluation.

    Args:
        domains: List of domains to test (None = all)
        num_samples: Number of samples per test case
        epochs: Maximum training epochs
        save_dir: Directory to save results
        verbose: Print detailed training progress
    """

    protocol = DeFiExperimentProtocol()

    if domains is None:
        domains = protocol.get_all_domains()

    print("=" * 80)
    print("IMPROVED NEURAL NETWORK BASELINE - DEFI & RISK MANAGEMENT".center(80))
    print("=" * 80)
    print(f"Architecture: ImprovedNN [128, 64, 32] + BatchNorm + Dropout")
    print(f"Epochs: {epochs} (with early stopping)")
    print(f"Learning Rate: 0.001 (with scheduling)")
    print(f"Domains: {', '.join(domains)}")
    print(f"Samples per test: {num_samples}")
    print("=" * 80)

    all_results = []

    for domain in domains:
        print(f"\n{'=' * 80}")
        print(f"DOMAIN: {domain.upper()}".center(80))
        print(f"{protocol.get_domain_description(domain)}".center(80))
        print("=" * 80)

        test_cases = protocol.load_test_data(domain, num_samples=num_samples)

        for i, (description, X, y, var_names, metadata) in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {description}")
            print(f"  Variables: {', '.join(var_names)}")
            print(f"  Ground truth: {metadata.get('ground_truth', 'N/A')}")
            print(f"  Difficulty: {metadata.get('difficulty', 'N/A')}")
            print(f"  Shape: X={X.shape}, y={y.shape}")

            if metadata.get("extrapolation_test"):
                print(f"  ⚠️  EXTRAPOLATION TEST CASE")

            # Train and evaluate
            print(f"  Training neural network...")
            result = train_neural_network(
                X,
                y,
                description,
                domain,
                metadata,
                epochs=epochs,
                lr=0.001,
                verbose=verbose,
            )

            # Print results
            metrics = result["evaluation"]
            training = result["training_info"]

            print(f"  ✅ R² Score: {metrics['r2']:.6f}")
            print(f"  RMSE: {metrics['rmse']:.6f}")
            print(f"  MAE: {metrics['mae']:.6f}")
            print(f"  Final Train Loss: {training['final_train_loss']:.6f}")

            # Categorize performance
            r2 = metrics["r2"]
            if r2 > 0.99:
                print(f"  🎯 EXCELLENT FIT")
            elif r2 > 0.95:
                print(f"  ✓ Good fit")
            elif r2 > 0.80:
                print(f"  ⚠️  Moderate fit")
            else:
                print(f"  ❌ Poor fit")

            # Extrapolation info
            if result.get("extrapolation_stats"):
                ext_stats = result["extrapolation_stats"]
                print(f"  📊 Extrapolation: mean_error={ext_stats['mean_error']:.4f}")

            all_results.append(result)

    # =====================================================================
    # GENERATE COMPREHENSIVE REPORT
    # =====================================================================

    print("\n" + "=" * 80)
    print("GENERATING COMPREHENSIVE REPORT".center(80))
    print("=" * 80)

    report = protocol.generate_experiment_report(all_results)

    # Save results
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"{save_dir}/baseline_nn_defi_IMPROVED_{timestamp}.json"
    report_file = f"{save_dir}/report_nn_defi_IMPROVED_{timestamp}.json"

    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"✅ Results saved to: {results_file}")

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"✅ Report saved to: {report_file}")

    # =====================================================================
    # PRINT SUMMARY
    # =====================================================================

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
        if "min_r2" in overall:
            print(f"  Min R²: {overall['min_r2']:.6f}")
            print(f"  Max R²: {overall['max_r2']:.6f}")

    print(f"\n📈 By Domain:")
    for domain, stats in report["by_domain"].items():
        mean_r2_str = (
            f"R²: {stats.get('mean_r2', 0):.4f}"
            if stats.get("mean_r2") is not None
            else "N/A"
        )
        print(
            f"  {domain}: {stats['successful']}/{stats['total']} "
            f"({100 * stats['success_rate']:.1f}%) - {mean_r2_str}"
        )

    if report.get("extrapolation_tests"):
        print(f"\n🎯 Extrapolation Test Cases:")
        for test in report["extrapolation_tests"]:
            status = "✅" if test["success"] else "❌"
            r2_str = (
                f"R²: {test.get('r2', 0):.4f}"
                if test.get("r2") is not None
                else "Failed"
            )
            print(f"  {status} {test['description'][:60]}")
            print(f"     {r2_str}")

    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE".center(80))
    print("=" * 80)

    print("\n⚠️  Neural Network Limitations:")
    print("  • Black box model - no interpretable formula")
    print("  • May struggle with extrapolation beyond training range")
    print("  • Requires retraining for each new dataset")
    print("  • Cannot provide mathematical insights")
    print("\n✅ Neural Network Advantages:")
    print("  • Can learn complex non-linear patterns")
    print("  • No need for formula specification")
    print("  • Good for interpolation within training range")

    return report


def compare_with_llm_baseline(nn_report_file, llm_report_file):
    """
    Compare Neural Network results with Pure LLM baseline.

    Args:
        nn_report_file: Path to NN report JSON
        llm_report_file: Path to LLM report JSON
    """

    with open(nn_report_file, "r") as f:
        nn_report = json.load(f)

    with open(llm_report_file, "r") as f:
        llm_report = json.load(f)

    print("\n" + "=" * 80)
    print("COMPARISON: NEURAL NETWORK vs PURE LLM".center(80))
    print("=" * 80)

    print(f"\n{'Metric':<30} {'Neural Network':<20} {'Pure LLM':<20} {'Winner'}")
    print("-" * 80)

    nn_overall = nn_report["overall"]
    llm_overall = llm_report["overall"]

    # Overall R²
    nn_r2 = nn_overall.get("mean_r2", 0)
    llm_r2 = llm_overall.get("mean_r2", 0)
    winner = "NN 🏆" if nn_r2 > llm_r2 else "LLM 🏆" if llm_r2 > nn_r2 else "Tie"
    print(f"{'Mean R²':<30} {nn_r2:<20.4f} {llm_r2:<20.4f} {winner}")

    # Median R²
    nn_med = nn_overall.get("median_r2", 0)
    llm_med = llm_overall.get("median_r2", 0)
    winner = "NN 🏆" if nn_med > llm_med else "LLM 🏆" if llm_med > nn_med else "Tie"
    print(f"{'Median R²':<30} {nn_med:<20.4f} {llm_med:<20.4f} {winner}")

    # Success rate
    nn_success = nn_overall.get("success_rate", 0)
    llm_success = llm_overall.get("success_rate", 0)
    winner = (
        "NN 🏆"
        if nn_success > llm_success
        else "LLM 🏆"
        if llm_success > nn_success
        else "Tie"
    )
    print(f"{'Success Rate':<30} {nn_success:<20.2%} {llm_success:<20.2%} {winner}")

    print("\n" + "-" * 80)
    print("Domain-by-Domain Comparison:")
    print("-" * 80)

    for domain in nn_report["by_domain"].keys():
        if domain in llm_report["by_domain"]:
            nn_domain = nn_report["by_domain"][domain]
            llm_domain = llm_report["by_domain"][domain]

            nn_r2 = nn_domain.get("mean_r2", 0)
            llm_r2 = llm_domain.get("mean_r2", 0)

            winner = "NN" if nn_r2 > llm_r2 else "LLM" if llm_r2 > nn_r2 else "Tie"
            print(f"{domain:<15} NN: {nn_r2:>6.4f}  LLM: {llm_r2:>6.4f}  → {winner}")

    print("=" * 80)


if __name__ == "__main__":
    import sys

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("""
Usage:
  python baseline_neural_network_improved.py [options]

Options:
  --all                Run on all domains
  --domain <domains>   Run on specific domains (comma-separated)
  --quick              Run quick test on 2 domains
  --compare <nn> <llm> Compare NN results with LLM baseline
  --verbose            Show detailed training progress
  --epochs <n>         Set maximum epochs (default: 500)
  --samples <n>        Set samples per test (default: 100)

Examples:
  python baseline_neural_network_improved.py --all
  python baseline_neural_network_improved.py --domain amm,liquidation
  python baseline_neural_network_improved.py --quick --verbose
  python baseline_neural_network_improved.py --compare nn_report.json llm_report.json
""")
            sys.exit(0)

        elif sys.argv[1] == "--compare":
            if len(sys.argv) < 4:
                print("Error: --compare requires two file paths")
                sys.exit(1)
            compare_with_llm_baseline(sys.argv[2], sys.argv[3])
            sys.exit(0)

        elif sys.argv[1] == "--all":
            verbose = "--verbose" in sys.argv
            epochs = 500
            samples = 100

            if "--epochs" in sys.argv:
                idx = sys.argv.index("--epochs")
                epochs = int(sys.argv[idx + 1])

            if "--samples" in sys.argv:
                idx = sys.argv.index("--samples")
                samples = int(sys.argv[idx + 1])

            run_comprehensive_test(
                domains=None, num_samples=samples, epochs=epochs, verbose=verbose
            )

        elif sys.argv[1] == "--domain":
            if len(sys.argv) < 3:
                print("Error: --domain requires domain names")
                sys.exit(1)

            domains = sys.argv[2].split(",")
            verbose = "--verbose" in sys.argv
            run_comprehensive_test(domains=domains, verbose=verbose)

        elif sys.argv[1] == "--quick":
            verbose = "--verbose" in sys.argv
            run_comprehensive_test(
                domains=["amm", "risk_var"],
                num_samples=100,
                epochs=300,
                verbose=verbose,
            )

        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        # Default: run on all domains
        run_comprehensive_test(domains=None, num_samples=100, epochs=500)
