# Module: `tools/symbolic/sympy_wrapper.py`

## Description

SymPy integration wrapper

**Last Modified**: 2025-11-12T16:47:36.494831

## Dependencies

- `sympy`
- `typing`

## Classes

### `SymPyWrapper`

Wrapper for SymPy symbolic computation

**Methods**:

- `__init__(self)`
- `parse_expression(self, expr_string: str) -> Optional[sp.Expr]`
  - Parse string to SymPy expression
- `simplify(self, expression: Any) -> Any`
  - Simplify expression
- `differentiate(self, expression: Any, variable: str) -> Any`
  - Compute derivative
- `integrate(self, expression: Any, variable: str, lower: Optional[float], upper: Optional[float]) -> Any`
  - Compute integral
- `validate_expression(self, expr1: str, expr2: str) -> bool`
  - Check if two expressions are equivalent
