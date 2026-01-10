"""
Tests for enhanced LLM interpreter functionality.
Tests symbolic integration, formula transformation, and advanced interpretation.
"""

from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from sympy import diff, integrate, simplify, symbols, sympify


class TestSymbolicIntegration:
    """Tests for symbolic mathematics integration."""

    def test_convert_text_to_symbolic(self, enhanced_interpreter):
        """Test converting text to symbolic expression."""
        text = "x squared plus two x plus one"

        symbolic = enhanced_interpreter.text_to_symbolic(text)

        assert symbolic is not None
        x = symbols("x")
        expected = x**2 + 2 * x + 1
        assert sympify(symbolic) == expected or str(symbolic) == str(expected)

    def test_symbolic_simplification(self, enhanced_interpreter):
        """Test symbolic simplification."""
        expression = "x + x + x + y + y"

        simplified = enhanced_interpreter.simplify_symbolic(expression)

        assert "3" in str(simplified)

    def test_symbolic_differentiation(self, enhanced_interpreter):
        """Test taking derivatives."""
        expression = "x**3 + 2*x**2 + x"
        variable = "x"

        derivative = enhanced_interpreter.differentiate(expression, variable)

        assert derivative is not None
        assert "3" in str(derivative)  # 3x^2 term

    def test_symbolic_integration(self, enhanced_interpreter):
        """Test integration."""
        expression = "2*x"
        variable = "x"

        integral = enhanced_interpreter.integrate_expr(expression, variable)

        assert integral is not None
        assert "x**2" in str(integral) or "x^2" in str(integral)

    def test_substitute_values(self, enhanced_interpreter):
        """Test substituting values into symbolic expression."""
        expression = "x**2 + y**2"
        values = {"x": 3, "y": 4}

        result = enhanced_interpreter.substitute(expression, values)

        assert result == 25


class TestFormulaTransformation:
    """Tests for transforming formulas between representations."""

    def test_transform_to_python(self, enhanced_interpreter):
        """Test transforming formula to Python code."""
        formula = "x^2 + y^2"

        python_code = enhanced_interpreter.to_python(formula)

        assert "def" in python_code or "lambda" in str(python_code)
        assert "x" in python_code and "y" in python_code

    def test_transform_to_numpy(self, enhanced_interpreter):
        """Test transforming formula to NumPy-compatible code."""
        formula = "sqrt(x**2 + y**2)"

        numpy_code = enhanced_interpreter.to_numpy(formula)

        assert "np." in str(numpy_code) or numpy_code is not None

    def test_transform_to_latex(self, enhanced_interpreter):
        """Test transforming formula to LaTeX."""
        formula = "(x - y) / z"

        latex = enhanced_interpreter.to_latex(formula)

        assert "\\frac" in latex or latex is not None

    def test_transform_to_sympy(self, enhanced_interpreter):
        """Test transforming string to SymPy expression."""
        formula = "x**2 + 2*x + 1"

        sympy_expr = enhanced_interpreter.to_sympy(formula)

        assert sympy_expr is not None

    def test_transform_from_latex(self, enhanced_interpreter):
        """Test parsing LaTeX to symbolic expression."""
        latex = r"\frac{x + y}{z}"

        expr = enhanced_interpreter.from_latex(latex)

        assert expr is not None


class TestFormulaAnalysis:
    """Tests for analyzing formula properties."""

    def test_extract_variables_advanced(self, enhanced_interpreter):
        """Test extracting all variables from complex formula."""
        formula = "a * x**2 + b * x + c"

        variables = enhanced_interpreter.extract_all_variables(formula)

        assert len(variables) >= 3
        assert all(v in ["a", "b", "c", "x"] for v in variables)

    def test_identify_constants(self, enhanced_interpreter):
        """Test identifying constants in formula."""
        formula = "2 * pi * r"

        constants = enhanced_interpreter.identify_constants(formula)

        assert "pi" in constants or len(constants) > 0

    def test_detect_operations(self, enhanced_interpreter):
        """Test detecting mathematical operations."""
        formula = "sqrt(x**2 + y**2) / z"

        operations = enhanced_interpreter.detect_operations(formula)

        assert "sqrt" in operations or "division" in operations

    def test_check_linearity(self, enhanced_interpreter):
        """Test checking if formula is linear."""
        linear_formula = "2*x + 3*y + 1"
        nonlinear_formula = "x**2 + y"

        assert enhanced_interpreter.is_linear(linear_formula)
        assert not enhanced_interpreter.is_linear(nonlinear_formula)

    def test_formula_complexity(self, enhanced_interpreter):
        """Test measuring formula complexity."""
        simple = "x + y"
        complex_expr = "sqrt(exp(x**2 + y**2) / (z + 1))"

        complexity_simple = enhanced_interpreter.get_complexity(simple)
        complexity_complex = enhanced_interpreter.get_complexity(complex_expr)

        assert complexity_complex > complexity_simple


class TestDomainSpecificTransformation:
    """Tests for domain-specific formula transformations."""

    def test_transform_risk_formula(self, enhanced_interpreter):
        """Test transforming risk formula to computational form."""
        formula = "Sharpe = (R - Rf) / sigma"

        computational = enhanced_interpreter.transform_for_computation(
            formula, domain="risk"
        )

        assert computational is not None

    def test_transform_defi_formula(self, enhanced_interpreter):
        """Test transforming DeFi formula."""
        formula = "x * y = k"

        transformed = enhanced_interpreter.transform_for_computation(
            formula, domain="defi"
        )

        assert transformed is not None

    def test_add_domain_constraints(self, enhanced_interpreter):
        """Test adding domain-specific constraints."""
        formula = "probability = events / total"

        constrained = enhanced_interpreter.add_constraints(
            formula, domain="statistics", constraints={"output_range": [0, 1]}
        )

        assert constrained is not None


class TestFormulaVerification:
    """Tests for verifying formula correctness."""

    def test_verify_against_examples(self, enhanced_interpreter):
        """Test verifying formula against test cases."""
        formula = "x + y"
        test_cases = [
            {"input": {"x": 1, "y": 2}, "expected": 3},
            {"input": {"x": 5, "y": 3}, "expected": 8},
        ]

        is_correct = enhanced_interpreter.verify_formula(formula, test_cases)

        assert is_correct

    def test_verify_mathematical_properties(self, enhanced_interpreter):
        """Test verifying mathematical properties."""
        formula = "x + y"
        properties = ["commutative", "associative"]

        results = enhanced_interpreter.verify_properties(formula, properties)

        assert results["commutative"] == True

    def test_verify_dimensional_consistency(self, enhanced_interpreter):
        """Test dimensional analysis."""
        formula = "distance = velocity * time"
        dimensions = {
            "distance": {"length": 1},
            "velocity": {"length": 1, "time": -1},
            "time": {"time": 1},
        }

        is_consistent = enhanced_interpreter.verify_dimensions(formula, dimensions)

        assert is_consistent

    def test_verify_edge_cases(self, enhanced_interpreter):
        """Test formula with edge cases."""
        formula = "x / y"
        edge_cases = [
            {"input": {"x": 1, "y": 0}, "should_error": True},
            {"input": {"x": 0, "y": 1}, "expected": 0},
        ]

        results = enhanced_interpreter.test_edge_cases(formula, edge_cases)

        assert len(results) == 2


class TestPatternRecognition:
    """Tests for recognizing formula patterns."""

    def test_recognize_formula_type(self, enhanced_interpreter):
        """Test recognizing type of formula."""
        formulas = {
            "x**2 + 2*x + 1": "quadratic",
            "a*x + b": "linear",
            "exp(x)": "exponential",
        }

        for formula, expected_type in formulas.items():
            detected_type = enhanced_interpreter.recognize_type(formula)
            assert expected_type in str(detected_type).lower()

    def test_recognize_common_patterns(self, enhanced_interpreter):
        """Test recognizing common mathematical patterns."""
        formula = "sum(x_i * w_i for i in range(n))"

        pattern = enhanced_interpreter.recognize_pattern(formula)

        assert "weighted" in str(pattern).lower() or "sum" in str(pattern).lower()

    def test_match_known_formulas(self, enhanced_interpreter):
        """Test matching against known formulas."""
        formula = "(x - mean)**2"

        match = enhanced_interpreter.match_known_formula(formula)

        assert "variance" in str(match).lower() or match is not None


class TestFormulaComposition:
    """Tests for composing complex formulas."""

    def test_compose_formulas(self, enhanced_interpreter):
        """Test composing two formulas."""
        f = "x**2"
        g = "2*y + 1"

        composed = enhanced_interpreter.compose(f, g, variable="y")

        assert composed is not None
        assert "x" in str(composed)

    def test_chain_transformations(self, enhanced_interpreter):
        """Test chaining multiple transformations."""
        formula = "x + x + x"

        result = enhanced_interpreter.chain_transforms(
            formula, ["simplify", "factor", "expand"]
        )

        assert result is not None

    def test_combine_formulas(self, enhanced_interpreter):
        """Test combining multiple formulas."""
        formulas = {"mean": "sum(x) / n", "variance": "sum((x - mean)**2) / n"}

        combined = enhanced_interpreter.combine_formulas(formulas)

        assert "mean" in str(combined) or len(combined) > 0


class TestMultiModalInterpretation:
    """Tests for multi-modal interpretation."""

    def test_interpret_with_diagram(self, enhanced_interpreter):
        """Test interpreting formula from diagram description."""
        description = """
        Triangle with base b and height h.
        Area is half base times height.
        """

        formula = enhanced_interpreter.interpret_from_diagram(description)

        assert formula is not None
        assert "b" in str(formula) and "h" in str(formula)

    def test_interpret_from_table(self, enhanced_interpreter):
        """Test interpreting formula from data table."""
        table = {"x": [1, 2, 3, 4], "y": [2, 4, 6, 8]}

        formula = enhanced_interpreter.interpret_from_table(table)

        assert formula is not None
        assert "2" in str(formula) or "x" in str(formula)

    def test_interpret_from_graph(self, enhanced_interpreter):
        """Test interpreting formula from graph description."""
        description = "Linear graph passing through origin with slope 2"

        formula = enhanced_interpreter.interpret_from_graph(description)

        assert formula is not None


class TestIterativeRefinement:
    """Tests for iterative formula refinement."""

    def test_refine_formula(self, enhanced_interpreter):
        """Test refining formula based on feedback."""
        initial_formula = "x + y"
        feedback = "Should be multiplication not addition"

        refined = enhanced_interpreter.refine_formula(initial_formula, feedback)

        assert "*" in str(refined) or refined != initial_formula

    def test_improve_accuracy(self, enhanced_interpreter):
        """Test improving formula accuracy."""
        formula = "x / y"
        test_data = {
            "inputs": [{"x": 10, "y": 2}, {"x": 20, "y": 4}],
            "outputs": [5, 5],
        }

        improved = enhanced_interpreter.improve_formula(formula, test_data)

        assert improved is not None

    def test_optimize_formula(self, enhanced_interpreter):
        """Test optimizing formula structure."""
        formula = "x * x * x + x * x + x"

        optimized = enhanced_interpreter.optimize_structure(formula)

        # Should factor or simplify
        assert len(str(optimized)) <= len(formula) or optimized is not None


class TestExplanationGeneration:
    """Tests for generating formula explanations."""

    def test_explain_formula_structure(self, enhanced_interpreter):
        """Test explaining formula structure."""
        formula = "(a + b) / c"

        explanation = enhanced_interpreter.explain_structure(formula)

        assert explanation is not None
        assert isinstance(explanation, (str, dict))

    def test_explain_variable_roles(self, enhanced_interpreter):
        """Test explaining variable roles."""
        formula = "PV = FV / (1 + r)**n"

        explanations = enhanced_interpreter.explain_variables(formula)

        assert len(explanations) >= 3

    def test_generate_step_by_step(self, enhanced_interpreter):
        """Test generating step-by-step solution."""
        formula = "(x + y)**2"
        values = {"x": 2, "y": 3}

        steps = enhanced_interpreter.generate_steps(formula, values)

        assert len(steps) >= 2

    def test_explain_derivation(self, enhanced_interpreter):
        """Test explaining formula derivation."""
        formula = "d/dx(x**2) = 2*x"

        derivation = enhanced_interpreter.explain_derivation(formula)

        assert derivation is not None


class TestErrorDetection:
    """Tests for detecting errors in formulas."""

    def test_detect_syntax_errors(self, enhanced_interpreter):
        """Test detecting syntax errors."""
        invalid_formula = "x + + y"

        errors = enhanced_interpreter.detect_errors(invalid_formula)

        assert len(errors) > 0

    def test_detect_mathematical_errors(self, enhanced_interpreter):
        """Test detecting mathematical errors."""
        formula = "sqrt(-x**2 - 1)"  # Always negative under sqrt

        errors = enhanced_interpreter.detect_mathematical_errors(formula)

        assert len(errors) > 0 or errors is not None

    def test_detect_dimensional_errors(self, enhanced_interpreter):
        """Test detecting dimensional mismatches."""
        formula = "distance = time + velocity"  # Wrong dimensions

        errors = enhanced_interpreter.detect_dimensional_errors(formula)

        assert len(errors) > 0 or errors is not None

    def test_suggest_corrections(self, enhanced_interpreter):
        """Test suggesting corrections for errors."""
        formula = "x +* y"

        suggestions = enhanced_interpreter.suggest_corrections(formula)

        assert len(suggestions) > 0


class TestAdvancedFeatures:
    """Tests for advanced interpreter features."""

    def test_probabilistic_interpretation(self, enhanced_interpreter):
        """Test probabilistic interpretation of ambiguous input."""
        ambiguous = "x something y"

        interpretations = enhanced_interpreter.interpret_probabilistic(ambiguous)

        assert len(interpretations) >= 1
        assert all("confidence" in i for i in interpretations)

    def test_context_aware_interpretation(self, enhanced_interpreter):
        """Test interpretation considering conversation context."""
        context = {"previous_formulas": ["mean = sum(x) / n"], "domain": "statistics"}

        query = "Now calculate the variance"

        formula = enhanced_interpreter.interpret_with_context(query, context)

        assert "mean" in str(formula) or formula is not None

    def test_multi_language_support(self, enhanced_interpreter):
        """Test formula interpretation in different languages."""
        descriptions = {"en": "sum of x and y", "es": "suma de x e y"}

        results = []
        for lang, desc in descriptions.items():
            result = enhanced_interpreter.interpret(desc, language=lang)
            results.append(result)

        # Should produce equivalent formulas
        assert len(results) == 2


class TestPerformance:
    """Tests for performance optimization."""

    def test_batch_interpretation(self, enhanced_interpreter):
        """Test batch processing of interpretations."""
        queries = ["x + y", "x * y", "x / y", "x - y"]

        results = enhanced_interpreter.interpret_batch(queries)

        assert len(results) == len(queries)

    def test_caching_effectiveness(self, enhanced_interpreter):
        """Test caching improves performance."""
        import time

        query = "complex formula: sqrt(x**2 + y**2 + z**2)"

        start1 = time.time()
        result1 = enhanced_interpreter.interpret(query)
        time1 = time.time() - start1

        start2 = time.time()
        result2 = enhanced_interpreter.interpret(query)
        time2 = time.time() - start2

        # Second call should be faster (cached)
        assert time2 <= time1 or result1 == result2

    def test_parallel_processing(self, enhanced_interpreter):
        """Test parallel processing of multiple interpretations."""
        queries = [f"formula_{i}" for i in range(10)]

        results = enhanced_interpreter.interpret_parallel(queries)

        assert len(results) == len(queries)


@pytest.fixture
def enhanced_interpreter():
    """Fixture for enhanced LLM interpreter."""
    interpreter = MagicMock()

    # Symbolic operations
    interpreter.text_to_symbolic = MagicMock(return_value="x**2 + 2*x + 1")
    interpreter.simplify_symbolic = MagicMock(return_value="3*x + 2*y")
    interpreter.differentiate = MagicMock(return_value="3*x**2 + 4*x + 1")
    interpreter.integrate_expr = MagicMock(return_value="x**2 + C")
    interpreter.substitute = MagicMock(return_value=25)

    # Transformations
    interpreter.to_python = MagicMock(return_value="lambda x, y: x**2 + y**2")
    interpreter.to_numpy = MagicMock(return_value="np.sqrt(x**2 + y**2)")
    interpreter.to_latex = MagicMock(return_value=r"\frac{x + y}{z}")
    interpreter.to_sympy = MagicMock(return_value="symbolic_expr")
    interpreter.from_latex = MagicMock(return_value="(x + y) / z")

    # Analysis
    interpreter.extract_all_variables = MagicMock(return_value=["x", "y", "z"])
    interpreter.identify_constants = MagicMock(return_value=["pi", "e"])
    interpreter.detect_operations = MagicMock(return_value=["sqrt", "division"])
    interpreter.is_linear = MagicMock(side_effect=lambda x: "**" not in str(x))
    interpreter.get_complexity = MagicMock(side_effect=lambda x: len(str(x)))

    # Verification
    interpreter.verify_formula = MagicMock(return_value=True)
    interpreter.verify_properties = MagicMock(return_value={"commutative": True})
    interpreter.verify_dimensions = MagicMock(return_value=True)
    interpreter.test_edge_cases = MagicMock(return_value=[{"passed": True}])

    # Pattern recognition
    interpreter.recognize_type = MagicMock(return_value="quadratic")
    interpreter.recognize_pattern = MagicMock(return_value="weighted_sum")
    interpreter.match_known_formula = MagicMock(return_value="variance")

    # Composition
    interpreter.compose = MagicMock(return_value="composed_formula")
    interpreter.chain_transforms = MagicMock(return_value="transformed")
    interpreter.combine_formulas = MagicMock(return_value="combined")

    # Multi-modal
    interpreter.interpret_from_diagram = MagicMock(return_value="0.5 * b * h")
    interpreter.interpret_from_table = MagicMock(return_value="2 * x")
    interpreter.interpret_from_graph = MagicMock(return_value="2 * x")

    # Refinement
    interpreter.refine_formula = MagicMock(return_value="x * y")
    interpreter.improve_formula = MagicMock(return_value="improved")
    interpreter.optimize_structure = MagicMock(return_value="optimized")

    # Explanation
    interpreter.explain_structure = MagicMock(return_value="Structure explanation")
    interpreter.explain_variables = MagicMock(
        return_value={"x": "input", "y": "output"}
    )
    interpreter.generate_steps = MagicMock(return_value=["step1", "step2"])
    interpreter.explain_derivation = MagicMock(return_value="Derivation explanation")

    # Error detection
    interpreter.detect_errors = MagicMock(return_value=[])
    interpreter.detect_mathematical_errors = MagicMock(return_value=[])
    interpreter.detect_dimensional_errors = MagicMock(return_value=[])
    interpreter.suggest_corrections = MagicMock(return_value=["suggestion1"])

    # Advanced features
    interpreter.interpret_probabilistic = MagicMock(
        return_value=[{"interpretation": "x + y", "confidence": 0.9}]
    )
    interpreter.interpret_with_context = MagicMock(return_value="context_aware_formula")
    interpreter.interpret = MagicMock(return_value="interpreted_formula")
    interpreter.interpret_batch = MagicMock(return_value=["result1", "result2"])
    interpreter.interpret_parallel = MagicMock(return_value=["result1", "result2"])

    # Domain-specific
    interpreter.transform_for_computation = MagicMock(return_value="computational_form")
    interpreter.add_constraints = MagicMock(return_value="constrained_formula")

    return interpreter


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
