# Module: `tools/validation/symbolic_validator.py`

## Description

Symbolic validation using SymPy

**Last Modified**: 2025-11-12T16:47:36.494831

## Dependencies

- `tools.symbolic.sympy_wrapper`
- `typing`

## Classes

### `SymbolicValidator`

Validate expressions using symbolic computation

**Methods**:

- `__init__(self)`
- `validate_equivalence(self, expr1: str, expr2: str) -> Dict[<ast.Tuple object at 0x7fa6f851f890>]`
  - Check if two expressions are equivalent
- `validate_derivative(self, expression: str, variable: str) -> Dict[<ast.Tuple object at 0x7fa6f851e8d0>]`
  - Validate if expression can be differentiated
