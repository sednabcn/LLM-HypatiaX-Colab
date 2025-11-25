from pysr import PySRRegressor
import numpy as np
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class DiscoveryConfig:
    niterations: int = 40
    populations: int = 15
    binary_operators: List[str] = None
    unary_operators: List[str] = None
    
    def __post_init__(self):
        if self.binary_operators is None:
            self.binary_operators = ["+", "-", "*", "/", "^"]
        if self.unary_operators is None:
            self.unary_operators = ["sqrt", "exp", "log"]

class SymbolicEngine:
    def __init__(self, config: DiscoveryConfig):
        self.config = config
        self.model = None
        
    def discover(self, X: np.ndarray, y: np.ndarray, 
                 variable_names: List[str] = None) -> Dict:
        if variable_names is None:
            variable_names = [f"x{i}" for i in range(X.shape[1])]
            
        self.model = PySRRegressor(
            niterations=self.config.niterations,
            populations=self.config.populations,
            binary_operators=self.config.binary_operators,
            unary_operators=self.config.unary_operators,
            model_selection="best",
            parsimony=0.01,
            verbosity=0
        )
        
        self.model.fit(X, y, variable_names=variable_names)
        
        best_expr = str(self.model.sympy())
        y_pred = self.model.predict(X)
        r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)
        
        return {
            'expression': best_expr,
            'sympy_expr': self.model.sympy(),
            'r2_score': r2,
            'complexity': self.model.get_best().complexity,
            'variable_names': variable_names,
            'predictions': y_pred
        }

# Test
if __name__ == "__main__":
    X = np.random.uniform(-10, 10, (100, 1))
    y = 2 * X[:, 0] + 3 + np.random.normal(0, 0.5, 100)
    
    config = DiscoveryConfig(niterations=20)
    engine = SymbolicEngine(config)
    result = engine.discover(X, y, variable_names=['x'])
    
    print(f"Discovered: {result['expression']}")
    print(f"R² score: {result['r2_score']:.4f}")
