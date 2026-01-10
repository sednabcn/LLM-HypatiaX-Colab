"""
End-to-End Integration Tests for Hybrid Discovery System
Tests complete workflows with real validation and LLM integration
Week 2-3 Critical Priority
"""

import json
import os
import time
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pytest

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


class TestDeFiWorkflows:
    """Test complete DeFi formula discovery workflows"""

    @pytest.fixture
    def system(self):
        return HybridDiscoverySystem(
            domain="defi",
            primary_llm="anthropic",
            enable_fallback=True,
            use_rich_output=False,
        )

    @pytest.fixture
    def amm_data(self):
        """Generate AMM constant product data"""
        np.random.seed(123)
        n = 200
        reserve0 = np.random.uniform(100, 10000, n)
        reserve1 = np.random.uniform(100, 10000, n)

        # k = r0 * r1 (constant product)
        k = reserve0 * reserve1
        y = k + np.random.normal(0, k * 0.01, n)  # 1% noise

        X = np.column_stack([reserve0, reserve1])
        return X, y

    @pytest.fixture
    def il_data(self):
        """Generate impermanent loss data"""
        np.random.seed(456)
        n = 200
        price_ratio = np.random.uniform(0.1, 10.0, n)

        # IL = 2*sqrt(r)/(1+r) - 1
        il = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1
        y = il + np.random.normal(0, 0.01, n)

        X = price_ratio.reshape(-1, 1)
        return X, y

    @pytest.mark.integration
    def test_amm_constant_product_discovery(self, system, amm_data):
        """Test discovery of AMM constant product formula"""
        X, y = amm_data

        with patch.object(system, "_interpret_with_llm") as mock_llm:
            mock_llm.return_value = {
                "interpretation": "Constant product formula for AMM",
                "provider": "claude",
                "relationships": ["Product relationship between reserves"],
                "insights": ["Maintains constant k"],
                "use_cases": ["Uniswap V2", "DEX pricing"],
            }

            result = system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=["reserve0", "reserve1"],
                variable_descriptions={
                    "reserve0": "Token 0 reserve amount",
                    "reserve1": "Token 1 reserve amount",
                },
                variable_units={"reserve0": "tokens", "reserve1": "tokens"},
                description="AMM Constant Product Discovery",
                show_formatted=False,
            )

            # Verify high quality discovery
            assert result["discovery"]["r2_score"] > 0.95
            assert "reserve0" in result["discovery"]["expression"]
            assert "reserve1" in result["discovery"]["expression"]

            # Verify validation passed
            assert result["validation"]["total_score"] > 75.0

            # Verify interpretation
            assert result["interpretation"]["provider"] == "claude"
            assert "amm" in result["interpretation"]["interpretation"].lower()

    @pytest.mark.integration
    def test_impermanent_loss_discovery(self, system, il_data):
        """Test discovery of impermanent loss formula"""
        X, y = il_data

        with patch.object(system, "_interpret_with_llm") as mock_llm:
            mock_llm.return_value = {
                "interpretation": "Impermanent loss calculation",
                "provider": "gemini",
                "relationships": ["Non-linear function of price ratio"],
                "insights": ["Always negative for LPs"],
                "use_cases": ["LP profitability analysis"],
                "limitations": ["Assumes 50/50 pools"],
            }

            result = system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=["price_ratio"],
                variable_descriptions={
                    "price_ratio": "Ratio of current to initial price"
                },
                variable_units={"price_ratio": "dimensionless"},
                description="Impermanent Loss Discovery",
                show_formatted=False,
            )

            # Verify discovery quality
            assert result["discovery"]["r2_score"] > 0.90
            assert "price_ratio" in result["discovery"]["expression"]

            # Verify validation
            assert result["validation"]["valid"]

            # Verify interpretation
            assert (
                "impermanent loss" in result["interpretation"]["interpretation"].lower()
            )


class TestValidationIntegration:
    """Test integration between discovery, validation, and LLM"""

    @pytest.fixture
    def system(self):
        return HybridDiscoverySystem(
            domain="finance",
            primary_llm="anthropic",
            enable_fallback=True,
            use_rich_output=False,
            validation_weights={
                "symbolic": 0.30,
                "dimensional": 0.30,
                "domain": 0.25,
                "consistency": 0.15,
            },
        )

    def test_validation_gates_interpretation(self, system):
        """Test that failed validation blocks interpretation"""
        np.random.seed(789)
        X = np.random.randn(50, 2)
        y = np.random.randn(50)  # Random data - should fail validation

        with patch.object(system.validator, "validate_complete") as mock_validate:
            # Force validation failure
            mock_validate.return_value = {
                "valid": False,
                "total_score": 35.0,
                "layer_scores": {
                    "symbolic": 40.0,
                    "dimensional": 30.0,
                    "domain": 35.0,
                    "consistency": 35.0,
                },
                "errors": ["Dimensional mismatch", "Domain violation"],
                "warnings": ["Low quality"],
                "recommendations": ["Check units", "Improve data"],
            }

            result = system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=["x1", "x2"],
                variable_descriptions={"x1": "Input 1", "x2": "Input 2"},
                variable_units={"x1": "meters", "x2": "seconds"},
                description="Low quality test",
                validate_first=True,  # Should block interpretation
                show_formatted=False,
            )

            # Interpretation should be None
            assert result["interpretation"] is None
            assert not result["validation"]["valid"]
            assert len(result["validation"]["errors"]) > 0

    def test_validation_warnings_in_interpretation(self, system):
        """Test that validation warnings are included in context"""
        np.random.seed(101)
        X = np.random.uniform(1, 100, (100, 2))
        y = X[:, 0] + X[:, 1]

        with patch.object(system, "_interpret_with_llm") as mock_llm:

            def check_context(*args, **kwargs):
                # Verify validation info is in context
                context = kwargs.get("context", {})
                assert "validation" in context
                return {"interpretation": "Sum formula", "provider": "claude"}

            mock_llm.side_effect = check_context

            result = system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=["a", "b"],
                variable_descriptions={"a": "Value A", "b": "Value B"},
                variable_units={"a": "units", "b": "units"},
                validate_first=False,  # Don't gate interpretation
                show_formatted=False,
            )

            # Should call LLM with validation context
            assert mock_llm.called
            call_kwargs = mock_llm.call_args[1]
            assert "context" in call_kwargs


class TestMultiProviderScenarios:
    """Test scenarios with multiple LLM providers"""

    def test_anthropic_primary_gemini_fallback(self):
        """Test Anthropic primary with Gemini fallback"""
        system = HybridDiscoverySystem(
            domain="defi", primary_llm="anthropic", enable_fallback=True
        )

        with (
            patch.object(system, "_call_anthropic") as mock_claude,
            patch.object(system, "_call_gemini") as mock_gemini,
        ):

            # Claude fails, Gemini succeeds
            mock_claude.side_effect = Exception("Claude unavailable")
            mock_gemini.return_value = json.dumps(
                {
                    "interpretation": "Fallback interpretation",
                    "insights": ["From Gemini"],
                }
            )

            result = system._interpret_with_llm(
                expression="a * b",
                variables={"a": "Factor A", "b": "Factor B"},
                r2=0.92,
            )

            assert result["provider"] == "gemini"
            assert system.stats["fallback_count"] == 1
            assert system.stats["anthropic_failures"] >= 1

    def test_gemini_primary_anthropic_fallback(self):
        """Test Gemini primary with Anthropic fallback"""
        system = HybridDiscoverySystem(
            domain="defi", primary_llm="google", enable_fallback=True
        )

        with (
            patch.object(system, "_call_gemini") as mock_gemini,
            patch.object(system, "_call_anthropic") as mock_claude,
        ):

            # Gemini fails, Claude succeeds
            mock_gemini.side_effect = Exception("Gemini quota exceeded")
            mock_claude.return_value = json.dumps(
                {"interpretation": "Fallback from Claude", "insights": ["From Claude"]}
            )

            result = system._interpret_with_llm(
                expression="sqrt(x)", variables={"x": "Input value"}, r2=0.88
            )

            assert result["provider"] == "claude"
            assert system.stats["fallback_count"] == 1
            assert system.stats["google_failures"] >= 1

    def test_provider_selection_consistency(self):
        """Test that provider selection is consistent"""
        system = HybridDiscoverySystem(
            domain="defi", primary_llm="anthropic", enable_fallback=False
        )

        with patch.object(system, "_call_anthropic") as mock_claude:
            mock_claude.return_value = "Response"

            # Multiple calls should use same provider
            for _ in range(5):
                try:
                    system._interpret_with_llm(
                        expression="x + y", variables={"x": "a", "y": "b"}, r2=0.9
                    )
                except:
                    pass

            # Should only call Claude (primary)
            assert system.stats["anthropic_calls"] >= 5
            assert system.stats["google_calls"] == 0


class TestErrorRecovery:
    """Test error recovery and resilience"""

    def test_recovery_from_transient_errors(self):
        """Test recovery from temporary API failures"""
        system = HybridDiscoverySystem(domain="defi", max_retries=3, retry_delay=0.1)

        with patch.object(system.anthropic_client.messages, "create") as mock_create:
            # Simulate transient errors followed by success
            mock_create.side_effect = [
                Exception("503 Service Unavailable"),
                Exception("429 Rate Limit"),
                Mock(content=[Mock(text="Success after retries")]),
            ]

            response = system._call_anthropic("test prompt")

            assert response == "Success after retries"
            assert mock_create.call_count == 3
            assert system.stats["anthropic_failures"] == 2  # 2 failures before success

    def test_graceful_degradation_no_llm(self):
        """Test graceful degradation when no LLM available"""
        system = HybridDiscoverySystem(
            domain="defi", primary_llm="anthropic", enable_fallback=False
        )

        # Disable both providers
        system.anthropic_client = None
        system.gemini_client = None

        np.random.seed(202)
        X = np.random.uniform(1, 100, (50, 2))
        y = X[:, 0] * X[:, 1]

        # Should complete without LLM
        result = system.discover_validate_interpret(
            X=X,
            y=y,
            variable_names=["x", "y"],
            variable_descriptions={"x": "Factor 1", "y": "Factor 2"},
            variable_units={"x": "units", "y": "units"},
            use_llm=False,  # Explicitly disable LLM
            show_formatted=False,
        )

        assert result["interpretation"] is None
        assert "discovery" in result
        assert "validation" in result


class TestPerformanceMetrics:
    """Test performance and monitoring"""

    def test_timing_measurements(self):
        """Test that timing is measured correctly"""
        system = HybridDiscoverySystem(domain="defi", use_rich_output=False)

        np.random.seed(303)
        X = np.random.uniform(1, 100, (50, 2))
        y = X[:, 0] + X[:, 1]

        with patch.object(system, "_interpret_with_llm") as mock_llm:
            mock_llm.return_value = {"interpretation": "Test", "provider": "claude"}

            start = time.time()
            result = system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=["a", "b"],
                variable_descriptions={"a": "A", "b": "B"},
                variable_units={"a": "u", "b": "u"},
                show_formatted=False,
            )
            elapsed = time.time() - start

            # Should complete in reasonable time (< 5 seconds with mocking)
            assert elapsed < 5.0
            assert "timestamp" in result

    def test_statistics_accuracy(self):
        """Test that statistics are tracked accurately"""
        system = HybridDiscoverySystem(domain="defi")

        initial_stats = system.get_statistics()
        assert initial_stats["total_runs"] == 0

        np.random.seed(404)
        X = np.random.uniform(1, 100, (50, 2))
        y = X[:, 0] * X[:, 1]

        with patch.object(system, "_interpret_with_llm") as mock_llm:
            mock_llm.return_value = {"provider": "claude", "interpretation": "Test"}

            # Run 3 workflows
            for i in range(3):
                system.discover_validate_interpret(
                    X=X,
                    y=y,
                    variable_names=["x", "y"],
                    variable_descriptions={"x": f"X{i}", "y": f"Y{i}"},
                    variable_units={"x": "u", "y": "u"},
                    show_formatted=False,
                )

        stats = system.get_statistics()
        assert stats["total_runs"] == 3
        assert "llm_usage" in stats


class TestDataExport:
    """Test result export functionality"""

    @pytest.fixture
    def system_with_results(self):
        system = HybridDiscoverySystem(domain="defi", use_rich_output=False)

        # Add mock results
        for i in range(5):
            system.results.append(
                {
                    "timestamp": f"2025-01-{i+1:02d}",
                    "description": f"Test {i+1}",
                    "domain": "defi",
                    "discovery": {
                        "expression": f"x{i} + y{i}",
                        "r2_score": 0.9 + i * 0.01,
                        "complexity": 10 + i,
                    },
                    "validation": {"valid": True, "total_score": 80.0 + i * 2},
                    "interpretation": {
                        "interpretation": f"Test interpretation {i+1}",
                        "provider": "claude",
                    },
                }
            )

        return system

    def test_json_export(self, system_with_results, tmp_path):
        """Test JSON export functionality"""
        export_path = tmp_path / "results.json"

        system_with_results.export_results(str(export_path), format="json")

        assert export_path.exists()

        with open(export_path) as f:
            data = json.load(f)

        assert len(data) == 5
        assert data[0]["description"] == "Test 1"

    def test_csv_export(self, system_with_results, tmp_path):
        """Test CSV export functionality"""
        import csv

        export_path = tmp_path / "results.csv"

        system_with_results.export_results(str(export_path), format="csv")

        assert export_path.exists()

        with open(export_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 5
        assert rows[0]["Description"] == "Test 1"


@pytest.mark.integration
@pytest.mark.slow
class TestStressTests:
    """Stress tests for system reliability"""

    def test_many_sequential_workflows(self):
        """Test many sequential workflow executions"""
        system = HybridDiscoverySystem(
            domain="defi", max_results=100, use_rich_output=False
        )

        np.random.seed(505)

        with patch.object(system, "_interpret_with_llm") as mock_llm:
            mock_llm.return_value = {"provider": "claude", "interpretation": "Test"}

            success_count = 0
            for i in range(20):
                try:
                    X = np.random.uniform(1, 100, (50, 2))
                    y = X[:, 0] + X[:, 1] + np.random.normal(0, 1, 50)

                    system.discover_validate_interpret(
                        X=X,
                        y=y,
                        variable_names=["a", "b"],
                        variable_descriptions={"a": "A", "b": "B"},
                        variable_units={"a": "u", "b": "u"},
                        show_formatted=False,
                    )
                    success_count += 1
                except Exception as e:
                    pytest.fail(f"Workflow {i+1} failed: {str(e)}")

            assert success_count == 20
            assert len(system.results) == 20

    def test_memory_management(self):
        """Test memory management with bounded results"""
        system = HybridDiscoverySystem(
            domain="defi", max_results=10, use_rich_output=False
        )  # Small limit

        np.random.seed(606)

        with patch.object(system, "_interpret_with_llm") as mock_llm:
            mock_llm.return_value = {"provider": "claude", "interpretation": "Test"}

            # Run more workflows than max_results
            for i in range(25):
                X = np.random.uniform(1, 100, (50, 2))
                y = X[:, 0] + X[:, 1]

                system.discover_validate_interpret(
                    X=X,
                    y=y,
                    variable_names=["x", "y"],
                    variable_descriptions={"x": "X", "y": "Y"},
                    variable_units={"x": "u", "y": "u"},
                    show_formatted=False,
                )

            # Should only keep last 10
            assert len(system.results) == 10
            stats = system.get_statistics()
            assert stats["total_runs"] == 10  # Only counts stored results


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])
