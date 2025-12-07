import json
import os

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split


class SimpleNN(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.network(x)


def train_and_evaluate(X, y, description, ground_truth_fn=None):
    """
    Train and evaluate a simple neural network.

    Args:
        X: Input features
        y: Target values
        description: Description of the task
        ground_truth_fn: Optional function to compute true values for extrapolation test
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = SimpleNN(X.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    X_train_t = torch.FloatTensor(X_train)
    y_train_t = torch.FloatTensor(y_train).reshape(-1, 1)

    # Train
    for epoch in range(100):
        optimizer.zero_grad()
        pred = model(X_train_t)
        loss = criterion(pred, y_train_t)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 20 == 0:
            print(f"Epoch {epoch+1}/100, Loss: {loss.item():.6f}")

    # Evaluate
    model.eval()
    with torch.no_grad():
        X_test_t = torch.FloatTensor(X_test)
        y_pred = model(X_test_t).numpy().flatten()

        # R² score on test set
        r2 = 1 - np.sum((y_test - y_pred) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2)

        # Test extrapolation (2x beyond training range)
        X_extrap = X_test * 2
        X_extrap_t = torch.FloatTensor(X_extrap)
        y_extrap_pred = model(X_extrap_t).numpy().flatten()

        # Compute extrapolation error if ground truth function is provided
        if ground_truth_fn is not None:
            y_extrap_true = ground_truth_fn(X_extrap)
            extrap_error = np.mean(np.abs(y_extrap_pred - y_extrap_true))
        else:
            # Use prediction magnitude as proxy (not ideal but placeholder)
            extrap_error = np.mean(np.abs(y_extrap_pred))

    print(f"\n{description}")
    print(f"R² (test): {r2:.4f}")
    print(f"Extrapolation error: {extrap_error:.4f}\n")

    return {
        "method": "neural_network",
        "description": description,
        "r2_test": float(r2),
        "extrapolation_error": float(extrap_error),
    }


def run_nn_baseline():
    """Run neural network baseline on impermanent loss."""
    print("=" * 60)
    print("Neural Network Baseline Evaluation")
    print("=" * 60 + "\n")

    results = []

    # Test on impermanent loss
    np.random.seed(42)
    price_ratios = np.random.uniform(0.1, 10, (200, 1))

    # Ground truth impermanent loss formula
    def il_formula(price_ratios):
        return 2 * np.sqrt(price_ratios[:, 0]) / (price_ratios[:, 0] + 1) - 1

    il = il_formula(price_ratios)

    result = train_and_evaluate(price_ratios, il, "Impermanent Loss", ground_truth_fn=il_formula)
    results.append(result)

    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)

    # Save results
    output_path = "results/baseline_neural_network.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {output_path}")
    print("\nSummary:")
    print(f"  Method: Neural Network (3-layer MLP)")
    print(f"  R² Score: {result['r2_test']:.4f}")
    print(f"  Extrapolation Error: {result['extrapolation_error']:.4f}")


if __name__ == "__main__":
    run_nn_baseline()
