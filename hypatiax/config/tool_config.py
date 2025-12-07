"""External tool configurations"""


class ToolConfig:
    """Configuration for external tools"""

    # Symbolic computation
    USE_SYMPY = True
    USE_MATHEMATICA = False
    MATHEMATICA_PATH = None

    # Numerical computation
    USE_NUMPY = True
    USE_SCIPY = True

    # Formal verification
    USE_LEAN = False
    LEAN_PATH = None

    # Visualization
    DEFAULT_PLOT_BACKEND = "plotly"  # or "matplotlib"

    # Validation
    SYMBOLIC_VALIDATION = True
    NUMERICAL_VALIDATION = True
    DIMENSIONAL_VALIDATION = True
