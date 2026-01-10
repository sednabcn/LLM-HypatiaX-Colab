"""
baseline_neural_network_defi_improved.py - ENHANCED (updated)
Integrated with hybrid/baseline evaluation shapes:
- Returns 'metrics' dict with keys: mse, mae, rmse, r2, success
- Exposes train_get_model() and get_predictions() for ensemble use
- train_and_evaluate() returns result dict with 'metrics' and 'evaluation' fields
- Handles extrapolation flag in metadata
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Ensure project root is importable for experiment protocol
import sys

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol


class ImprovedNN(nn.Module):
    """Improved neural network architecture with regularization."""

    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int] = [128, 64, 32],
        dropout: float = 0.2,
    ):
        super().__init__()
        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU(inplace=True))
            layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class NeuralNetworkBaseline:
    """Enhanced Neural Network baseline for DeFi formulas (hybrid-friendly)."""

    def __init__(
        self,
        hidden_dims: List[int] = [128, 64, 32],
        learning_rate: float = 0.001,
        epochs: int = 300,
        batch_size: int = 64,
        weight_decay: float = 1e-4,
        device: Optional[str] = None,
    ):
        self.hidden_dims = hidden_dims
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.weight_decay = weight_decay
        self.results = []
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    def _build_dataloader(
        self, X: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool = True
    ):
        X_t = torch.FloatTensor(X)
        y_t = torch.FloatTensor(y).reshape(-1, 1)
        ds = TensorDataset(X_t, y_t)
        return DataLoader(ds, batch_size=batch_size, shuffle=shuffle)

    def train_get_model(
        self,
        X: np.ndarray,
        y: np.ndarray,
        metadata: Optional[Dict] = None,
        is_extrapolation: bool = False,
        epochs: Optional[int] = None,
        verbose: bool = False,
    ) -> Tuple[nn.Module, Dict, StandardScaler, StandardScaler]:
        """
        Train and return (model, metrics, scaler_X, scaler_y).
        metrics keys: mse, mae, rmse, r2, success
        """
        epochs = epochs or self.epochs
        test_size = 0.3 if is_extrapolation else 0.2

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        X_train_s = scaler_X.fit_transform(X_train)
        X_test_s = scaler_X.transform(X_test)
        y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

        model = ImprovedNN(X.shape[1], hidden_dims=self.hidden_dims).to(self.device)
        optimizer = torch.optim.Adam(
            model.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay
        )
        criterion = nn.MSELoss()

        train_loader = self._build_dataloader(
            X_train_s, y_train_s, batch_size=self.batch_size, shuffle=True
        )

        model.train()
        best_val_loss = float("inf")
        patience = 40
        patience_counter = 0

        for epoch in range(epochs):
            epoch_losses = []
            for X_batch, y_batch in train_loader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)

                optimizer.zero_grad()
                pred = model(X_batch)
                loss = criterion(pred, y_batch)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                epoch_losses.append(loss.item())

            # validation on test set (scaled)
            model.eval()
            with torch.no_grad():
                X_test_t = torch.FloatTensor(X_test_s).to(self.device)
                y_pred_s = model(X_test_t).cpu().numpy().flatten()
            model.train()

            # simple early stopping on validation MSE (in scaled space)
            val_mse = float(
                np.mean(
                    (
                        y_test.reshape(-1)
                        - scaler_y.inverse_transform(y_pred_s.reshape(-1, 1)).flatten()
                    )
                    ** 2
                )
            )
            if val_mse < best_val_loss - 1e-9:
                best_val_loss = val_mse
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    if verbose:
                        print(f"  [NN] Early stopping at epoch {epoch + 1}")
                    break

            if verbose and ((epoch + 1) % 50 == 0 or epoch == 0):
                print(
                    f"  Epoch {epoch + 1}/{epochs}, train_loss={np.mean(epoch_losses):.6f}, val_mse={val_mse:.6f}"
                )

        # Final evaluation on test split (inverse scaled)
        model.eval()
        with torch.no_grad():
            X_test_t = torch.FloatTensor(X_test_s).to(self.device)
            y_pred_s = model(X_test_t).cpu().numpy().flatten()
            try:
                y_pred = scaler_y.inverse_transform(y_pred_s.reshape(-1, 1)).flatten()
            except Exception:
                y_pred = y_pred_s

        mse = float(np.mean((y_test - y_pred) ** 2))
        mae = float(np.mean(np.abs(y_test - y_pred)))
        rmse = float(np.sqrt(mse))
        ss_res = float(np.sum((y_test - y_pred) ** 2))
        ss_tot = float(np.sum((y_test - np.mean(y_test)) ** 2))
        r2 = float(1 - (ss_res / ss_tot)) if ss_tot > 1e-12 else 0.0

        metrics = {"mse": mse, "mae": mae, "rmse": rmse, "r2": r2, "success": r2 > 0.0}

        return model, metrics, scaler_X, scaler_y

    def get_predictions(
        self,
        model: nn.Module,
        scaler_X: StandardScaler,
        scaler_y: StandardScaler,
        X: np.ndarray,
    ) -> np.ndarray:
        """Return predictions for full dataset X using trained model and scalers."""
        model.eval()
        X_s = scaler_X.transform(X)
        X_t = torch.FloatTensor(X_s).to(self.device)
        with torch.no_grad():
            y_pred_s = model(X_t).cpu().numpy().flatten()
        try:
            y_pred = scaler_y.inverse_transform(y_pred_s.reshape(-1, 1)).flatten()
        except Exception:
            y_pred = y_pred_s
        return y_pred

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
        """
        Train and return a comprehensive result dict compatible with the hybrid system.
        Contains keys: method, description, domain, variables, architecture, training, metrics, evaluation, metadata, timestamp
        """
        is_extrapolation = bool(metadata and metadata.get("extrapolation_test", False))
        model, metrics, scaler_X, scaler_y = self.train_get_model(
            X,
            y,
            metadata=metadata,
            is_extrapolation=is_extrapolation,
            epochs=self.epochs,
            verbose=verbose,
        )

        # Full-dataset predictions for diagnostics
        y_full_pred = self.get_predictions(model, scaler_X, scaler_y, X)
        full_mse = float(np.mean((y - y_full_pred) ** 2))
        full_ss_res = float(np.sum((y - y_full_pred) ** 2))
        full_ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        full_r2 = float(1 - (full_ss_res / full_ss_tot)) if full_ss_tot > 1e-12 else 0.0

        result = {
            "method": "neural_network",
            "description": description,
            "domain": domain,
            "variables": var_names,
            "architecture": {
                "input_dim": X.shape[1],
                "hidden_dims": self.hidden_dims,
                "total_params": sum(
                    p.numel()
                    for p in ImprovedNN(X.shape[1], self.hidden_dims).parameters()
                ),
            },
            "training": {
                "epochs": self.epochs,
                "learning_rate": self.learning_rate,
                "batch_size": self.batch_size,
                "train_samples": int(
                    X.shape[0] * (1.0 - (0.3 if is_extrapolation else 0.2))
                ),
                "test_samples": int(X.shape[0] * (0.3 if is_extrapolation else 0.2)),
            },
            "metrics": metrics,
            "evaluation": {
                "test_r2": metrics["r2"],
                "test_rmse": metrics["rmse"],
                "test_mae": metrics["mae"],
                "full_dataset_r2": float(full_r2),
                "success": metrics["success"],
            },
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
        }

        # store results
        self.results.append(result)
        return result

    def save_results(self, filepath: str):
        """Save stored results to JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results saved: {filepath}")


# Convenience standalone function for hybrid system compatibility
def train_neural_network(
    X: np.ndarray,
    y: np.ndarray,
    hidden_dims: List[int] = [128, 64, 32],
    epochs: int = 300,
    batch_size: int = 64,
    learning_rate: float = 0.001,
) -> Tuple[nn.Module, Dict, StandardScaler, StandardScaler]:
    baseline = NeuralNetworkBaseline(
        hidden_dims=hidden_dims,
        learning_rate=learning_rate,
        epochs=epochs,
        batch_size=batch_size,
    )
    model, metrics, scaler_X, scaler_y = baseline.train_get_model(
        X, y, is_extrapolation=False, epochs=epochs, verbose=False
    )
    return model, metrics, scaler_X, scaler_y


# Quick CLI for local testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    protocol = DeFiExperimentProtocol()
    # Example: pick an available liquidity test case
    desc, X, y, var_names, meta = protocol.load_test_data(
        "liquidity", num_samples=args.samples
    )[0]
    nn = NeuralNetworkBaseline(epochs=200, batch_size=32)
    res = nn.train_and_evaluate(
        X,
        y,
        description=desc,
        domain="liquidity",
        var_names=var_names,
        metadata=meta,
        verbose=args.verbose,
    )
    print(json.dumps(res, indent=2)[:1600])
