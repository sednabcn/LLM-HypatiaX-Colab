#!/usr/bin/env python3
"""
One-Time Julia Package Setup for PySR
======================================

Run this ONCE to install all Julia packages.
After this, your tests will run without package updates!

Usage:
    python setup_julia_packages.py
"""

import os
import sys
import time

# Suppress warnings during setup
os.environ["JULIA_PKG_PRECOMPILE_AUTO"] = "0"


def main():
    print("=" * 80)
    print("JULIA PACKAGE SETUP FOR PYSR")
    print("=" * 80)
    print()
    print("This will install all required Julia packages (one-time setup).")
    print("Expected time: 2-5 minutes")
    print()

    try:
        import numpy as np
        from pysr import PySRRegressor

        print("✓ Python packages installed")
        print()

        # Create simple test data
        print("Creating test data...")
        X = np.random.randn(20, 2)
        y = X[:, 0] * X[:, 1] + np.random.randn(20) * 0.1
        print("✓ Test data created")
        print()

        # Initialize and fit (this triggers package installation)
        print("Installing Julia packages...")
        print("(This will take a few minutes - watch for progress bar)")
        print()

        start_time = time.time()

        model = PySRRegressor(
            niterations=5,  # Very short run
            populations=2,
            binary_operators=["+", "*"],
            unary_operators=["sqrt"],
            maxsize=10,
            verbosity=1,  # Show progress
            parallelism="serial",
            deterministic=True,
        )

        model.fit(X, y)

        elapsed = time.time() - start_time

        print()
        print("=" * 80)
        print(f"✅ SETUP COMPLETE! (took {elapsed:.1f}s)")
        print("=" * 80)
        print()
        print("Julia packages are now installed.")
        print("Your subsequent PySR runs will be much faster and won't show")
        print("'Updating registry' or 'Precompiling packages' messages.")
        print()
        print("You can now run your tests:")
        print("  python experiments/generation/tests/8_new_all.py --all")
        print()

        return 0

    except ImportError as e:
        print("❌ ERROR: Missing Python packages")
        print()
        print(f"Error: {e}")
        print()
        print("Please install required packages:")
        print("  pip install pysr numpy")
        print()
        return 1

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ SETUP FAILED")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        print("This might happen if:")
        print("  1. Julia is not installed (PySR should install it automatically)")
        print("  2. Disk space is low")
        print("  3. Network connection issues")
        print()
        print("Try:")
        print("  1. Check internet connection")
        print("  2. Run again: python setup_julia_packages.py")
        print("  3. If still fails, reinstall PySR:")
        print("     pip uninstall pysr")
        print("     pip install pysr")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
