"""SymPy integration wrapper"""
import sympy as sp
from typing import Any, Optional

class SymPyWrapper:
    """Wrapper for SymPy symbolic computation"""
    
    def __init__(self):
        self.symbols_cache = {}
    
    def parse_expression(self, expr_string: str) -> Optional[sp.Expr]:
        """Parse string to SymPy expression"""
        try:
            return sp.sympify(expr_string)
        except Exception as e:
            print(f"Failed to parse expression: {e}")
            return None
    
    def simplify(self, expression: Any) -> Any:
        """Simplify expression"""
        if isinstance(expression, str):
            expression = self.parse_expression(expression)
        return sp.simplify(expression)
    
    def differentiate(self, expression: Any, variable: str = 'x') -> Any:
        """Compute derivative"""
        if isinstance(expression, str):
            expression = self.parse_expression(expression)
        var = sp.Symbol(variable)
        return sp.diff(expression, var)
    
    def integrate(self, expression: Any, variable: str = 'x', 
                 lower: Optional[float] = None, upper: Optional[float] = None) -> Any:
        """Compute integral"""
        if isinstance(expression, str):
            expression = self.parse_expression(expression)
        var = sp.Symbol(variable)
        
        if lower is not None and upper is not None:
            return sp.integrate(expression, (var, lower, upper))
        return sp.integrate(expression, var)
    
    def validate_expression(self, expr1: str, expr2: str) -> bool:
        """Check if two expressions are equivalent"""
        try:
            e1 = self.parse_expression(expr1)
            e2 = self.parse_expression(expr2)
            return sp.simplify(e1 - e2) == 0
        except:
            return False
