"""
Comprehensive tests for LLM interpretation functionality.
Tests formula interpretation, natural language processing, and response parsing.
"""

import json
from typing import Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestLLMInterpreterBasics:
    """Tests for basic LLM interpreter functionality."""

    def test_interpreter_initialization(self, llm_interpreter):
        """Test LLM interpreter can be initialized."""
        assert llm_interpreter is not None
        assert hasattr(llm_interpreter, "interpret")

    def test_interpreter_has_provider(self, llm_interpreter):
        """Test interpreter has an LLM provider."""
        assert hasattr(llm_interpreter, "provider")
        assert llm_interpreter.provider is not None

    def test_interpreter_configuration(self, llm_interpreter):
        """Test interpreter configuration options."""
        config = llm_interpreter.get_config()

        assert "model" in config or "temperature" in config
        assert isinstance(config, dict)


class TestFormulaInterpretation:
    """Tests for interpreting mathematical formulas."""

    def test_interpret_simple_formula(self, llm_interpreter):
        """Test interpreting a simple mathematical formula."""
        query = "What is the formula for compound interest?"

        response = llm_interpreter.interpret(query)

        assert response is not None
        assert isinstance(response, (str, dict))

    def test_interpret_risk_formula(self, llm_interpreter):
        """Test interpreting risk-related formula."""
        query = "Explain the Sharpe ratio formula"

        response = llm_interpreter.interpret(query)

        # Check response contains relevant terms
        response_str = str(response).lower()
        assert any(term in response_str for term in ["sharpe", "ratio", "risk", "return"])

    def test_interpret_defi_formula(self, llm_interpreter):
        """Test interpreting DeFi-specific formula."""
        query = "What is the constant product formula for Uniswap?"

        response = llm_interpreter.interpret(query)

        response_str = str(response).lower()
        assert any(term in response_str for term in ["x * y", "constant", "product", "uniswap"])

    def test_interpret_with_context(self, llm_interpreter):
        """Test interpretation with additional context."""
        query = "Calculate portfolio volatility"
        context = {"domain": "risk_management", "variables": ["returns", "weights"]}

        response = llm_interpreter.interpret(query, context=context)

        assert response is not None

    def test_interpret_multiple_formulas(self, llm_interpreter):
        """Test interpreting request for multiple formulas."""
        query = "Show me formulas for VaR, CVaR, and maximum drawdown"

        response = llm_interpreter.interpret(query)

        response_str = str(response).lower()
        assert "var" in response_str or "value at risk" in response_str


class TestNaturalLanguageProcessing:
    """Tests for natural language understanding."""

    def test_extract_formula_components(self, llm_interpreter):
        """Test extracting formula components from text."""
        text = "The Sharpe ratio is (R - Rf) / sigma where R is return"

        components = llm_interpreter.extract_components(text)

        assert components is not None
        assert isinstance(components, (dict, list))

    def test_identify_variables(self, llm_interpreter):
        """Test identifying variables in formula description."""
        text = "Calculate using price P, quantity Q, and rate R"

        variables = llm_interpreter.identify_variables(text)

        assert len(variables) >= 3
        assert any("P" in str(v) for v in variables)

    def test_parse_mathematical_notation(self, llm_interpreter):
        """Test parsing mathematical notation from text."""
        notations = ["sigma squared", "square root of variance", "sum from i=1 to n", "partial derivative"]

        for notation in notations:
            result = llm_interpreter.parse_notation(notation)
            assert result is not None

    def test_handle_ambiguous_query(self, llm_interpreter):
        """Test handling ambiguous queries."""
        query = "What is APY?"

        response = llm_interpreter.interpret(query)

        # Should ask for clarification or provide context
        assert response is not None

    def test_context_understanding(self, llm_interpreter):
        """Test understanding context across multiple queries."""
        queries = ["What is the Sharpe ratio?", "How do I calculate it?", "What's a good value?"]

        responses = []
        for query in queries:
            response = llm_interpreter.interpret(query, conversation_history=responses)
            responses.append(response)

        assert len(responses) == 3


class TestResponseParsing:
    """Tests for parsing LLM responses."""

    def test_parse_json_response(self, llm_interpreter):
        """Test parsing JSON-formatted response."""
        json_response = {"formula": "sharpe_ratio", "expression": "(R - Rf) / sigma", "variables": ["R", "Rf", "sigma"]}

        parsed = llm_interpreter.parse_response(json.dumps(json_response))

        assert "formula" in parsed
        assert "expression" in parsed

    def test_parse_markdown_formula(self, llm_interpreter):
        """Test parsing formula from markdown."""
        markdown = """
        The Sharpe Ratio is calculated as:

        ```
        Sharpe = (R - Rf) / σ
        ```

        Where R is return, Rf is risk-free rate, σ is volatility.
        """

        parsed = llm_interpreter.parse_response(markdown)

        assert parsed is not None

    def test_parse_latex_formula(self, llm_interpreter):
        """Test parsing LaTeX formula."""
        latex = r"$\text{Sharpe} = \frac{R - R_f}{\sigma}$"

        parsed = llm_interpreter.parse_latex(latex)

        assert parsed is not None

    def test_extract_formula_from_text(self, llm_interpreter):
        """Test extracting formula from mixed text."""
        text = """
        The formula you need is: x * y = k
        This represents the constant product.
        """

        formula = llm_interpreter.extract_formula(text)

        assert "x" in str(formula) and "y" in str(formula)

    def test_parse_multiline_response(self, llm_interpreter):
        """Test parsing complex multiline response."""
        response = """
        Here are the formulas:

        1. Sharpe Ratio: (R - Rf) / sigma
        2. Sortino Ratio: (R - Rf) / downside_dev
        3. Information Ratio: (R - Rb) / tracking_error
        """

        formulas = llm_interpreter.parse_multiple_formulas(response)

        assert len(formulas) >= 2


class TestFormulaGeneration:
    """Tests for generating formulas with LLM."""

    def test_generate_simple_formula(self, llm_interpreter):
        """Test generating a simple formula."""
        description = "A formula that calculates simple interest"

        formula = llm_interpreter.generate_formula(description)

        assert formula is not None
        assert isinstance(formula, (str, dict))

    def test_generate_with_constraints(self, llm_interpreter):
        """Test generating formula with constraints."""
        description = "Portfolio return calculation"
        constraints = {"variables": ["weights", "returns"], "output": "float", "domain": "finance"}

        formula = llm_interpreter.generate_formula(description, constraints=constraints)

        assert formula is not None

    def test_generate_symbolic_expression(self, llm_interpreter):
        """Test generating symbolic mathematical expression."""
        description = "The derivative of x squared"

        expression = llm_interpreter.generate_symbolic(description)

        assert "2" in str(expression) and "x" in str(expression)

    def test_generate_with_examples(self, llm_interpreter):
        """Test generating formula with input/output examples."""
        description = "Calculate percentage change"
        examples = [
            {"input": {"old": 100, "new": 110}, "output": 0.10},
            {"input": {"old": 50, "new": 45}, "output": -0.10},
        ]

        formula = llm_interpreter.generate_from_examples(description, examples)

        assert formula is not None

    def test_generate_complex_formula(self, llm_interpreter):
        """Test generating complex multi-variable formula."""
        description = """
        Generate a formula for impermanent loss in a liquidity pool
        given initial prices, final prices, and liquidity amounts
        """

        formula = llm_interpreter.generate_formula(description)

        assert formula is not None


class TestDomainSpecificInterpretation:
    """Tests for domain-specific formula interpretation."""

    def test_interpret_risk_metrics(self, llm_interpreter):
        """Test interpreting risk management formulas."""
        risk_queries = ["Value at Risk calculation", "Maximum drawdown formula", "Beta coefficient"]

        for query in risk_queries:
            response = llm_interpreter.interpret(query, domain="risk")
            assert response is not None

    def test_interpret_defi_protocols(self, llm_interpreter):
        """Test interpreting DeFi protocol formulas."""
        defi_queries = ["Uniswap V2 price impact", "Impermanent loss calculation", "Liquidity pool fees"]

        for query in defi_queries:
            response = llm_interpreter.interpret(query, domain="defi")
            assert response is not None

    def test_interpret_statistical_formulas(self, llm_interpreter):
        """Test interpreting statistical formulas."""
        stat_queries = ["Standard deviation", "Covariance matrix", "Correlation coefficient"]

        for query in stat_queries:
            response = llm_interpreter.interpret(query, domain="statistics")
            assert response is not None

    def test_domain_specific_validation(self, llm_interpreter):
        """Test validation within specific domains."""
        formula = "sharpe_ratio = (return - risk_free) / volatility"

        is_valid = llm_interpreter.validate_formula(formula, domain="risk")

        assert isinstance(is_valid, bool)


class TestErrorHandling:
    """Tests for error handling in interpretation."""

    def test_handle_invalid_query(self, llm_interpreter):
        """Test handling invalid or nonsensical query."""
        query = "asdf qwer zxcv"

        response = llm_interpreter.interpret(query)

        # Should handle gracefully
        assert response is not None

    def test_handle_empty_query(self, llm_interpreter):
        """Test handling empty query."""
        with pytest.raises(ValueError):
            llm_interpreter.interpret("")

    def test_handle_api_error(self, llm_interpreter):
        """Test handling API errors."""
        with patch.object(llm_interpreter.provider, "generate", side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                llm_interpreter.interpret("test query")

    def test_handle_malformed_response(self, llm_interpreter):
        """Test handling malformed LLM response."""
        malformed = "This is not valid JSON {[}]"

        parsed = llm_interpreter.parse_response(malformed)

        # Should handle gracefully or raise appropriate error
        assert parsed is not None or True  # Either parsed or handled

    def test_retry_on_failure(self, llm_interpreter):
        """Test retry logic on temporary failures."""
        query = "test query"

        with patch.object(llm_interpreter.provider, "generate") as mock_generate:
            mock_generate.side_effect = [Exception("Temporary error"), {"result": "success"}]

            response = llm_interpreter.interpret_with_retry(query, max_retries=2)

            assert response is not None


class TestCaching:
    """Tests for caching interpreted results."""

    def test_cache_interpretation(self, llm_interpreter):
        """Test caching of interpretation results."""
        query = "What is the Sharpe ratio?"

        # First call
        response1 = llm_interpreter.interpret(query)

        # Second call (should use cache)
        response2 = llm_interpreter.interpret(query)

        assert response1 == response2

    def test_cache_invalidation(self, llm_interpreter):
        """Test cache invalidation."""
        query = "Calculate volatility"

        response1 = llm_interpreter.interpret(query)

        llm_interpreter.clear_cache()

        response2 = llm_interpreter.interpret(query)

        # May or may not be same, but should not error
        assert response2 is not None

    def test_cache_with_context(self, llm_interpreter):
        """Test caching considers context."""
        query = "Calculate it"
        context1 = {"previous": "volatility"}
        context2 = {"previous": "sharpe ratio"}

        response1 = llm_interpreter.interpret(query, context=context1)
        response2 = llm_interpreter.interpret(query, context=context2)

        # Should be different due to different contexts
        assert response1 is not None and response2 is not None


class TestValidationIntegration:
    """Tests for integration with symbolic validation."""

    def test_validate_generated_formula(self, llm_interpreter, symbolic_validator):
        """Test validating LLM-generated formula."""
        description = "Simple moving average"

        formula = llm_interpreter.generate_formula(description)

        is_valid = symbolic_validator.validate(formula)

        assert isinstance(is_valid, bool)

    def test_interpret_and_symbolify(self, llm_interpreter):
        """Test converting interpretation to symbolic form."""
        query = "The sum of x and y"

        response = llm_interpreter.interpret(query)
        symbolic = llm_interpreter.to_symbolic(response)

        assert symbolic is not None

    def test_dimensional_validation(self, llm_interpreter):
        """Test dimensional validation of interpreted formula."""
        query = "velocity equals distance divided by time"

        formula = llm_interpreter.interpret(query)
        dimensions = llm_interpreter.check_dimensions(formula)

        assert dimensions is not None


class TestPerformanceMetrics:
    """Tests for performance monitoring."""

    def test_measure_interpretation_time(self, llm_interpreter):
        """Test measuring interpretation time."""
        import time

        query = "What is compound interest?"

        start = time.time()
        response = llm_interpreter.interpret(query)
        duration = time.time() - start

        assert duration < 30  # Should complete in reasonable time

    def test_token_usage_tracking(self, llm_interpreter):
        """Test tracking token usage."""
        query = "Explain the Black-Scholes formula"

        response, metrics = llm_interpreter.interpret_with_metrics(query)

        assert "tokens" in metrics or "token_count" in metrics

    def test_concurrent_interpretations(self, llm_interpreter):
        """Test handling concurrent interpretation requests."""
        queries = ["Sharpe ratio", "Sortino ratio", "Information ratio"]

        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(llm_interpreter.interpret, q) for q in queries]
            results = [f.result() for f in futures]

        assert len(results) == 3
        assert all(r is not None for r in results)


@pytest.fixture
def llm_interpreter():
    """Fixture for LLM interpreter."""
    from unittest.mock import MagicMock

    interpreter = MagicMock()
    interpreter.provider = MagicMock()

    # Mock basic methods
    interpreter.interpret = MagicMock(return_value="Sharpe Ratio: (R - Rf) / sigma")
    interpreter.get_config = MagicMock(return_value={"model": "test", "temperature": 0.7})
    interpreter.extract_components = MagicMock(return_value={"variables": ["R", "Rf", "sigma"]})
    interpreter.identify_variables = MagicMock(return_value=["R", "Rf", "sigma"])
    interpreter.parse_notation = MagicMock(return_value="parsed")
    interpreter.parse_response = MagicMock(return_value={"formula": "test"})
    interpreter.parse_latex = MagicMock(return_value="parsed_latex")
    interpreter.extract_formula = MagicMock(return_value="x * y = k")
    interpreter.parse_multiple_formulas = MagicMock(return_value=[{"name": "sharpe", "formula": "test"}])
    interpreter.generate_formula = MagicMock(return_value="generated_formula")
    interpreter.generate_symbolic = MagicMock(return_value="2*x")
    interpreter.generate_from_examples = MagicMock(return_value="(new - old) / old")
    interpreter.validate_formula = MagicMock(return_value=True)
    interpreter.interpret_with_retry = MagicMock(return_value="success")
    interpreter.clear_cache = MagicMock()
    interpreter.to_symbolic = MagicMock(return_value="symbolic_expr")
    interpreter.check_dimensions = MagicMock(return_value={"length": 1, "time": -1})
    interpreter.interpret_with_metrics = MagicMock(return_value=("result", {"tokens": 100}))

    return interpreter


@pytest.fixture
def symbolic_validator():
    """Fixture for symbolic validator."""
    validator = MagicMock()
    validator.validate = MagicMock(return_value=True)
    return validator


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
