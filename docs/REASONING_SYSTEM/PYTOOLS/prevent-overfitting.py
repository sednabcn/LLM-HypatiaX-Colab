"""
Overfitting Prevention Strategies for Physics-Aware Symbolic Regressor

KEY IMPROVEMENTS TO PREVENT OVERFITTING:
1. Train/validation split with early stopping
2. Increased parsimony coefficient
3. Complexity penalties
4. Cross-validation support
5. Expression size limits
6. Regularization on coefficients
7. Out-of-sample validation
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import sympy as sp
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split, KFold


class OverfittingPreventionMixin:
    """Mixin class with overfitting prevention methods."""

    def fit_with_validation(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str],
        validation_split: float = 0.2,
        early_stopping_rounds: int = 15,
        **kwargs,
    ):
        """
        Fit with train/validation split and early stopping.

        Args:
            validation_split: Fraction of data for validation
            early_stopping_rounds: Stop if no improvement for N generations
        """
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )

        if self.verbose:
            print(f"📊 Train: {len(X_train)}, Validation: {len(X_val)}")

        # Track validation performance
        best_val_fitness = -np.inf
        best_val_expression = None
        no_improvement_count = 0

        # Modified generation loop
        population = self._initialize_smart_population(
            variable_names,
            self._analyze_variables(X_train, y_train, variable_names, None),
        )

        for generation in range(self.generations):
            # Evaluate on TRAINING data
            fitness_scores = self._evaluate_population(
                population, X_train, y_train, variable_names
            )

            # Find best on training
            best_train_idx = np.argmax(fitness_scores)
            best_train_expr = population[best_train_idx]

            # Evaluate on VALIDATION data
            val_fitness = self._evaluate_fitness(
                best_train_expr, X_val, y_val, variable_names
            )

            # Track best validation performance
            if val_fitness > best_val_fitness:
                best_val_fitness = val_fitness
                best_val_expression = best_train_expr
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            if self.verbose and generation % 10 == 0:
                print(
                    f"Gen {generation}: Train R²={fitness_scores[best_train_idx]:.4f}, Val R²={val_fitness:.4f}"
                )

            # Early stopping based on validation
            if no_improvement_count >= early_stopping_rounds:
                if self.verbose:
                    print(
                        f"⏹️ Early stopping at generation {generation} (no val improvement)"
                    )
                break

            # Continue evolution
            var_stats = self._analyze_variables(X_train, y_train, variable_names, None)
            population = self._evolve_population(
                population, fitness_scores, variable_names, var_stats, generation
            )

        self.best_expression_ = best_val_expression
        self.best_fitness_ = best_val_fitness

        # Final evaluation on full dataset
        final_train_r2 = self._evaluate_fitness(
            best_val_expression, X_train, y_train, variable_names
        )
        final_val_r2 = self._evaluate_fitness(
            best_val_expression, X_val, y_val, variable_names
        )

        if self.verbose:
            print(
                f"\n✅ Final - Train R²: {final_train_r2:.4f}, Val R²: {final_val_r2:.4f}"
            )
            print(f"📉 Overfitting gap: {final_train_r2 - final_val_r2:.4f}")

        return self

    def cross_validate(
        self, X: np.ndarray, y: np.ndarray, variable_names: List[str], n_folds: int = 5
    ) -> Dict[str, float]:
        """
        Perform k-fold cross-validation.

        Returns:
            Dictionary with mean and std of R² scores
        """
        kfold = KFold(n_splits=n_folds, shuffle=True, random_state=42)
        scores = []

        for fold, (train_idx, val_idx) in enumerate(kfold.split(X)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            # Fit on training fold
            var_stats = self._analyze_variables(X_train, y_train, variable_names, None)
            population = self._initialize_smart_population(variable_names, var_stats)

            best_expr = None
            best_fitness = -np.inf

            for gen in range(min(50, self.generations)):  # Reduced for speed
                fitness_scores = self._evaluate_population(
                    population, X_train, y_train, variable_names
                )

                best_idx = np.argmax(fitness_scores)
                if fitness_scores[best_idx] > best_fitness:
                    best_fitness = fitness_scores[best_idx]
                    best_expr = population[best_idx]

                population = self._evolve_population(
                    population, fitness_scores, variable_names, var_stats, gen
                )

            # Evaluate on validation fold
            val_r2 = self._evaluate_fitness(best_expr, X_val, y_val, variable_names)
            scores.append(val_r2)

            if self.verbose:
                print(f"Fold {fold + 1}/{n_folds}: R² = {val_r2:.4f}")

        return {"mean_r2": np.mean(scores), "std_r2": np.std(scores), "scores": scores}

    def _evaluate_fitness_with_complexity_penalty(self, expr, X, y, variable_names):
        """
        Enhanced fitness with stronger complexity penalties.
        """
        try:
            symbols = [sp.Symbol(v) for v in variable_names]
            func = sp.lambdify(symbols, expr, modules=["numpy"])
            y_pred = func(*[X[:, i] for i in range(X.shape[1])])

            if np.isscalar(y_pred):
                y_pred = np.full_like(y, y_pred)
            else:
                y_pred = np.asarray(y_pred)

            if y_pred.shape != y.shape or not np.all(np.isfinite(y_pred)):
                return -np.inf
            if np.any(np.abs(y_pred) > 1e10):
                return -np.inf

            r2 = r2_score(y, y_pred)
            if r2 < -10:
                return -np.inf

            # Multiple complexity metrics
            tree_size = len(list(sp.preorder_traversal(expr)))
            num_operations = len(
                [
                    n
                    for n in sp.preorder_traversal(expr)
                    if isinstance(n, (sp.Add, sp.Mul, sp.Pow, sp.exp, sp.log))
                ]
            )
            max_depth = self._get_expression_depth(expr)

            # Stronger penalties for overly complex expressions
            complexity_penalty = (
                self.parsimony_coefficient * tree_size
                + 0.001 * num_operations
                + 0.002 * max_depth**2  # Quadratic penalty for depth
            )

            # Additional penalty for very large expressions
            if tree_size > 50:
                complexity_penalty += 0.1 * (tree_size - 50)

            return r2 - complexity_penalty

        except:
            return -np.inf

    def _get_expression_depth(self, expr, depth=0):
        """Calculate maximum depth of expression tree."""
        if not expr.args:
            return depth
        return max(self._get_expression_depth(arg, depth + 1) for arg in expr.args)

    def _enforce_expression_limits(self, expr, max_size: int = 50, max_depth: int = 8):
        """
        Reject expressions that are too complex.
        """
        tree_size = len(list(sp.preorder_traversal(expr)))
        depth = self._get_expression_depth(expr)

        if tree_size > max_size or depth > max_depth:
            return None  # Signal to reject this expression
        return expr

    def _regularized_coefficient_optimization(
        self, expr, X, y, variable_names, alpha=0.01
    ):
        """
        Optimize coefficients with L2 regularization to prevent overfitting.
        """
        try:
            from scipy.optimize import minimize

            coeffs = [
                a
                for a in expr.atoms(sp.Float, sp.Integer, sp.Rational)
                if a not in [0, 1]
            ]
            if not coeffs or len(coeffs) > 10:
                return None

            coeff_syms = [sp.Symbol(f"c{i}") for i in range(len(coeffs))]
            param_expr = expr
            for old, new in zip(coeffs, coeff_syms):
                param_expr = param_expr.subs(old, new)

            all_syms = [sp.Symbol(v) for v in variable_names] + coeff_syms
            func = sp.lambdify(all_syms, param_expr, modules=["numpy"])

            def objective(c_vals):
                try:
                    args = [X[:, i] for i in range(X.shape[1])] + list(c_vals)
                    y_pred = func(*args)
                    if not np.all(np.isfinite(y_pred)):
                        return 1e10

                    # MSE + L2 regularization
                    mse = np.mean((y - y_pred) ** 2)
                    l2_penalty = alpha * np.sum(c_vals**2)
                    return mse + l2_penalty
                except:
                    return 1e10

            x0 = [float(c) for c in coeffs]

            # Add bounds to prevent extreme coefficients
            bounds = [(-100, 100) for _ in coeffs]

            result = minimize(
                objective, x0, method="L-BFGS-B", bounds=bounds, options={"maxiter": 50}
            )

            if result.success:
                optimized = expr
                for old, new_val in zip(coeffs, result.x):
                    optimized = optimized.subs(old, float(new_val))
                return optimized
        except:
            pass
        return None


# RECOMMENDED PARAMETER SETTINGS TO PREVENT OVERFITTING
RECOMMENDED_PARAMS = {
    "parsimony_coefficient": 0.005,  # 10x higher than default
    "population_size": 100,  # Smaller population
    "generations": 100,  # Fewer generations
    "tournament_size": 3,  # Smaller tournaments (less selection pressure)
    "min_r2": 0.90,  # Lower target (don't overfit to 0.99+)
}

# EXAMPLE USAGE
"""
from physics_aware_regressor_v10 import PhysicsAwareRegressor

# Create regressor with overfitting prevention
regressor = PhysicsAwareRegressor(
    domain="biology",
    parsimony_coefficient=0.005,  # Stronger complexity penalty
    population_size=100,
    generations=100,
    min_r2=0.90,  # Don't aim for perfect fit
    verbose=True
)

# Method 1: Train/validation split with early stopping
regressor.fit_with_validation(
    X, y,
    variable_names=['Vmax', 'Km', 'S'],
    validation_split=0.2,
    early_stopping_rounds=15
)

# Method 2: Cross-validation
cv_results = regressor.cross_validate(
    X, y,
    variable_names=['Vmax', 'Km', 'S'],
    n_folds=5
)
print(f"CV Mean R²: {cv_results['mean_r2']:.4f} ± {cv_results['std_r2']:.4f}")

# Check for overfitting
# If train R² >> validation R², you're overfitting
# Aim for train R² ≈ validation R² (within 0.05)
"""

"""
Key Strategies to Prevent Overfitting:
1. Train/Validation Split (Most Important)

Split your data into training (80%) and validation (20%) sets
Evaluate fitness on training, but track performance on validation
Use early stopping when validation performance stops improving

2. Stronger Parsimony Coefficient

Increase from 0.0005 to 0.005 (10x higher)
Penalizes complex expressions more heavily
Favors simpler, more generalizable models

3. Expression Complexity Limits

Maximum tree size (e.g., 50 nodes)
Maximum depth (e.g., 8 levels)
Reject overly complex candidates during evolution

4. Cross-Validation

Use k-fold CV (5 folds) to assess generalization
Average performance across multiple train/test splits
More robust evaluation than single split

5. Regularized Coefficient Optimization

Add L2 penalty when optimizing coefficients
Prevents extreme coefficient values
Bounds on coefficient ranges (-100 to 100)

6. Lower Target R²

Don't aim for perfect fit (0.99+)
Target 0.90-0.95 instead
Perfect fit on training often means overfitting

7. Reduced Evolution Pressure

Smaller population sizes
Fewer generations
Less aggressive selection

The artifact includes a mixin class you can integrate into your existing code, plus recommended parameter settings and usage examples. The train/validation split with early stopping is typically the most effective approach.
"""
