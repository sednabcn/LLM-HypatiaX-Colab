# api/auto_register.py
"""
Automatically register formulas from your CSV/JSON generators
"""

import numpy as np
import pandas as pd
from formula_registry import FormulaInput, FormulaMetadata, FormulaRegistry


def parse_formula_to_lambda(formula_str: str, input_names: List[str]):
    """
    Convert analytical formula string to executable lambda.

    Example:
        "2*sqrt(p)/(p+1) - 1" → lambda p: 2*np.sqrt(p)/(p+1) - 1
    """
    # Replace mathematical notation with numpy
    formula_python = formula_str
    formula_python = formula_python.replace("sqrt", "np.sqrt")
    formula_python = formula_python.replace("exp", "np.exp")
    formula_python = formula_python.replace("log", "np.log")
    formula_python = formula_python.replace("^", "**")

    # Create lambda function
    lambda_str = f"lambda {', '.join(input_names)}: {formula_python}"

    try:
        return eval(lambda_str)
    except:
        return None


def extract_variables(formula_str: str) -> List[str]:
    """
    Extract variable names from formula.

    Example: "2*sqrt(p)/(p+1) - 1" → ["p"]
    """
    import re

    # Find all words that aren't functions
    vars = re.findall(r"\b[a-z_][a-z0-9_]*\b", formula_str.lower())

    # Remove function names
    functions = ["sqrt", "exp", "log", "sin", "cos", "tan", "abs", "min", "max"]
    vars = [v for v in vars if v not in functions]

    return list(set(vars))


def load_from_generator(csv_path: str, domain: str, registry: FormulaRegistry):
    """
    Load formulas from your generator CSV and register them.
    """
    df = pd.read_csv(csv_path)

    for idx, row in df.iterrows():
        # Extract variables from formula
        variables = extract_variables(row["analytical_formula"])

        # Create inputs (you'll need to add unit/range info manually or via mapping)
        inputs = []
        for var in variables:
            inputs.append(
                FormulaInput(
                    name=var,
                    description=f"Variable {var}",
                    unit="dimensionless",  # TODO: Add unit mapping
                    type="float",
                    min_value=0.0,
                    required=True,
                )
            )

        # Parse formula to lambda
        implementation = parse_formula_to_lambda(row["analytical_formula"], variables)

        if implementation:
            formula = FormulaMetadata(
                id=f"{domain}_{idx}",
                name=row["description"],
                description=row["description"],
                category=row["category"],
                formula_latex=row["analytical_formula"],
                formula_python=row["analytical_formula"],
                inputs=inputs,
                output_unit="dimensionless",  # TODO: Add output unit mapping
                implementation=implementation,
                domain=domain,
                constraints=[f"{var} > 0" for var in variables],  # Default constraint
                examples=[],  # TODO: Generate test cases
            )

            registry.register(formula)
            print(f"✓ Registered: {formula.id}")


# Usage
if __name__ == "__main__":
    registry = FormulaRegistry()

    # Load from your generators
    load_from_generator("../defi_queries_280.csv", "defi", registry)
    load_from_generator("../risk_queries_comprehensive.csv", "risk", registry)

    print(f"\n✓ Total formulas registered: {len(registry.formulas)}")
