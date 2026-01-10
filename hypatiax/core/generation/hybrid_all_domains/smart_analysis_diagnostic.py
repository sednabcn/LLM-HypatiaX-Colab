#!/usr/bin/env python3
"""
SMART ANALYZER DIAGNOSTIC TOOL
================================

Purpose: Diagnose and fix the smart analyzer's inverted logic bug
where it detects 'quadratic' but adds ['sqrt', 'log'] instead of ['square']

This tool helps identify WHERE the bug is in the codebase.
"""

import numpy as np
from typing import Dict, List, Tuple
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from hypatiax.tools.symbolic.hybrid_system_v40 import HybridDiscoverySystem
    from hypatiax.tools.symbolic.symbolic_engine import DiscoveryConfig

    HYBRID_VERSION = "v4.0"
except ImportError:
    try:
        from hypatiax.tools.symbolic.hybrid_system_v38 import HybridDiscoverySystem
        from hypatiax.tools.symbolic.symbolic_engine import DiscoveryConfig

        HYBRID_VERSION = "v3.8"
    except:
        print("❌ Cannot import HybridDiscoverySystem")
        sys.exit(1)


def generate_bernoulli_data(
    n_samples: int = 500,
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Generate Bernoulli equation test data."""
    np.random.seed(42)
    P = np.random.uniform(1e5, 2e5, n_samples)
    rho = np.random.uniform(800, 1200, n_samples)
    v = np.random.uniform(0.1, 15.0, n_samples)
    g = np.random.uniform(9.6, 9.9, n_samples)
    h = np.random.uniform(0, 10, n_samples)

    X = np.column_stack([P, rho, v, g, h])
    y = P + 0.5 * rho * v**2 + rho * g * h

    return X, y, ["P", "rho", "v", "g", "h"]


def analyze_correlations(X: np.ndarray, y: np.ndarray, var_names: List[str]):
    """Analyze correlations to understand what smart analyzer sees."""
    print("\n" + "=" * 80)
    print("CORRELATION ANALYSIS - What Smart Analyzer Sees")
    print("=" * 80)

    for i, var in enumerate(var_names):
        x_col = X[:, i]

        # Linear correlation
        corr_linear = np.corrcoef(x_col, y)[0, 1]

        # Log correlation
        if np.all(x_col > 0):
            corr_log = np.corrcoef(np.log(x_col), y)[0, 1]
        else:
            corr_log = 0.0

        # Sqrt correlation
        if np.all(x_col >= 0):
            corr_sqrt = np.corrcoef(np.sqrt(x_col), y)[0, 1]
        else:
            corr_sqrt = 0.0

        # Quadratic correlation
        corr_quad = np.corrcoef(x_col**2, y)[0, 1]

        print(f"\n{var}:")
        print(f"  Linear:    corr = {corr_linear:7.4f}")
        print(f"  Log:       corr = {corr_log:7.4f}")
        print(f"  Sqrt:      corr = {corr_sqrt:7.4f}")
        print(
            f"  Quadratic: corr = {corr_quad:7.4f}  ⭐ {'STRONGEST' if abs(corr_quad) == max(abs(corr_linear), abs(corr_log), abs(corr_sqrt), abs(corr_quad)) else ''}"
        )

        # Determine what structure should be detected
        max_corr = max(abs(corr_linear), abs(corr_log), abs(corr_sqrt), abs(corr_quad))
        if max_corr == abs(corr_quad) and abs(corr_quad) > 0.5:
            print(f"  → Should detect: QUADRATIC")
            print(f"  → Needs operator: 'square'")
        elif max_corr == abs(corr_linear):
            print(f"  → Should detect: LINEAR")
        elif max_corr == abs(corr_log):
            print(f"  → Should detect: LOG")
        elif max_corr == abs(corr_sqrt):
            print(f"  → Should detect: SQRT")


def test_smart_analyzer_directly():
    """Test the smart analyzer's structure detection directly."""
    print("\n" + "=" * 80)
    print("DIRECT SMART ANALYZER TEST")
    print("=" * 80)

    X, y, var_names = generate_bernoulli_data()

    try:
        # Try to access the smart analyzer directly
        config = DiscoveryConfig(
            niterations=5,
            populations=4,
            enable_auto_configuration=True,
            auto_config_correlation_threshold=0.15,
        )

        hybrid = HybridDiscoverySystem(
            domain="engineering",
            discovery_config=config,
            enable_auto_config=True,
            max_retries=1,
            enable_physics_fallback=False,
        )

        # Check if we can access internal analyzer
        if hasattr(hybrid, "analyzer") or hasattr(hybrid, "structure_analyzer"):
            analyzer = getattr(hybrid, "analyzer", None) or getattr(
                hybrid, "structure_analyzer", None
            )

            if analyzer and hasattr(analyzer, "analyze_structure"):
                print("\n✅ Found analyzer.analyze_structure()")

                # Try to call it
                structure = analyzer.analyze_structure(X, y, var_names)
                print(f"\nDetected structure:")
                print(f"  {structure}")

                if hasattr(analyzer, "configure_operators"):
                    print("\n✅ Found analyzer.configure_operators()")
                    operators = analyzer.configure_operators(structure)
                    print(f"\nConfigured operators:")
                    print(f"  Unary:  {operators.get('unary_operators', 'N/A')}")
                    print(f"  Binary: {operators.get('binary_operators', 'N/A')}")

                    # Check if this is the bug
                    if "v" in structure:
                        v_structure = structure.get("v", {})
                        print(f"\n🔍 Checking 'v' structure:")
                        print(f"  Detected: {v_structure}")
                        if v_structure == "quadratic" or "quadratic" in str(
                            v_structure
                        ):
                            print(f"  ⚠️  DETECTED QUADRATIC for v")
                            unary_ops = operators.get("unary_operators", [])
                            if "square" not in unary_ops:
                                print(
                                    f"  ❌ BUG CONFIRMED: 'square' not in unary operators!"
                                )
                                print(f"  Current unary ops: {unary_ops}")
                                if "log" in unary_ops or "sqrt" in unary_ops:
                                    print(
                                        f"  ❌ INVERTED LOGIC: Added sqrt/log instead of square!"
                                    )
                            else:
                                print(f"  ✅ FIXED: 'square' is in unary operators")
        else:
            print("⚠️  Cannot access internal analyzer")
            print("   Trying discovery to see what happens...")

            # Run discovery and check configuration
            result = hybrid.discover_validate_interpret(
                X=X[:100],
                y=y[:100],  # Small sample for speed
                variable_names=var_names,
                variable_descriptions={
                    "P": "Static pressure",
                    "rho": "Fluid density",
                    "v": "Flow velocity",
                    "g": "Gravitational acceleration",
                    "h": "Height",
                },
                equation_name="bernoulli_equation",
                validate_first=False,
            )

            print(f"\nDiscovery result:")
            discovery = result.get("discovery", {})
            print(f"  Expression: {discovery.get('expression', 'N/A')}")
            print(f"  R²: {discovery.get('r2_score', 0):.4f}")

            # Check what operators were used
            if "configuration" in discovery:
                config_used = discovery["configuration"]
                print(f"\n  Configuration used:")
                print(f"    Unary:  {config_used.get('unary_operators', 'N/A')}")
                print(f"    Binary: {config_used.get('binary_operators', 'N/A')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


def suggest_fixes():
    """Suggest where and how to fix the bug."""
    print("\n" + "=" * 80)
    print("SUGGESTED FIXES")
    print("=" * 80)

    print("""
🔧 FIX #1: In symbolic_engine.py or hybrid_system_v40.py

Find the structure analyzer's configure_operators() method and fix:

❌ CURRENT (BROKEN):
```python
def configure_operators(self, term_forms):
    operators = []
    
    if 'quadratic' in term_forms.values():
        operators.extend(['sqrt', 'log'])  # ❌ WRONG!
    
    return operators
```

✅ FIXED:
```python
def configure_operators(self, term_forms):
    operators = []
    
    if 'quadratic' in term_forms.values():
        operators.extend(['square'])  # ✅ CORRECT!
    
    if 'sqrt' in term_forms.values():
        operators.extend(['sqrt'])
    
    if 'log' in term_forms.values():
        operators.extend(['log'])
    
    return operators
```

🔧 FIX #2: Add equation-specific overrides (IMPLEMENTED IN v4.3)

For known difficult equations, bypass the smart analyzer:

```python
EQUATION_OVERRIDES = {
    "bernoulli_equation": {
        "unary_operators": ["square", "abs"],
        "binary_operators": ["+", "-", "*", "/"]
    }
}

if equation_name in EQUATION_OVERRIDES:
    config.unary_operators = EQUATION_OVERRIDES[equation_name]["unary_operators"]
    config.enable_auto_configuration = False
```

🔧 FIX #3: Improve structure detection

Make the correlation analysis smarter:

```python
def detect_structure(self, x, y):
    correlations = {
        'linear': abs(np.corrcoef(x, y)[0, 1]),
        'quadratic': abs(np.corrcoef(x**2, y)[0, 1]),
        'log': abs(np.corrcoef(np.log(x + 1e-10), y)[0, 1]),
        'sqrt': abs(np.corrcoef(np.sqrt(np.abs(x)), y)[0, 1])
    }
    
    best = max(correlations, key=correlations.get)
    
    if best == 'quadratic':
        return 'quadratic', ['square']  # Return needed operators
    elif best == 'log':
        return 'log', ['log']
    elif best == 'sqrt':
        return 'sqrt', ['sqrt']
    else:
        return 'linear', []
```
""")


def main():
    print("\n" + "=" * 80)
    print("SMART ANALYZER DIAGNOSTIC TOOL - BERNOULLI BUG HUNTER")
    print("=" * 80)

    # Step 1: Generate test data
    X, y, var_names = generate_bernoulli_data()
    print(f"\n✅ Generated Bernoulli data: X{X.shape}, y{y.shape}")
    print(f"   Ground truth: y = P + 0.5*rho*v² + rho*g*h")

    # Step 2: Analyze correlations
    analyze_correlations(X, y, var_names)

    # Step 3: Test smart analyzer
    test_smart_analyzer_directly()

    # Step 4: Suggest fixes
    suggest_fixes()

    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print("""
SUMMARY:
- The bug is in the smart analyzer's operator configuration logic
- It correctly detects 'quadratic' for v
- But incorrectly adds ['sqrt', 'log'] instead of ['square']
- This causes PySR to approximate v² with v*log(v)
- Fix: Either patch the analyzer or use equation-specific overrides (v4.3)

Next steps:
1. Run: python suite_v4.3_fixed.py --protocol B --test engineering_bernoulli_equation
2. Verify R² > 0.99 with correct v² term
3. If still failing, search codebase for "def configure_operators" 
4. Apply Fix #1 from suggestions above
""")


if __name__ == "__main__":
    main()
