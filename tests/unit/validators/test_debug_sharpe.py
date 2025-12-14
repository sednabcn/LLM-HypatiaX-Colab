#!/usr/bin/env python3
"""
Debug helper for Sharpe ratio tests.

Run from repo root:
python3 tools/validation/debug_sharpe.py
"""

import json
import pprint
import sys

import numpy as np

# adjust path if needed
sys.path.append("tools/validation")
from hypatiax.tools.validation.enhanced_domain_validator import EnhancedDomainValidator


def run_case(description, expr, var_defs, test_data):
    print("=== CASE:", description, "===")
    v = EnhancedDomainValidator(domain="finance")
    res = v.validate(expr, var_defs, None, test_data)
    # Pretty-print full result dict
    pprint.pprint(res)
    print("Validation history last entry (raw):")
    pprint.pprint(v.validation_history[-1] if v.validation_history else None)
    print("\n")


def main():
    # Valid Sharpe case
    expr = "(r - rf) / sigma"
    var_defs = {"r": "Return", "rf": "Risk-free rate", "sigma": "Volatility"}
    test_data_valid = {
        "r": np.array([0.10]),
        "rf": np.array([0.02]),
        "sigma": np.array([0.15]),
    }

    # Zero volatility case
    test_data_zero = {
        "r": np.array([0.10]),
        "rf": np.array([0.02]),
        "sigma": np.array([0.0]),
    }

    run_case("Sharpe valid (sigma=0.15)", expr, var_defs, test_data_valid)
    run_case("Sharpe zero volatility (sigma=0.0)", expr, var_defs, test_data_zero)


if __name__ == "__main__":
    main()
