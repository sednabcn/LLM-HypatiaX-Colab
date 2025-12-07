"""
Unit tests for data operations.
Path: tests/unit/data/test_data_operations.py
"""

import json
from typing import Any, Dict, List
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest


class TestDataLoading:
    """Test data loading functionality."""

    def test_load_json_file(self):
        """Test loading JSON data."""
        mock_data = {"key": "value", "number": 42}
        mock_file = json.dumps(mock_data)

        with patch("builtins.open", mock_open(read_data=mock_file)):
            with open("test.json", "r") as f:
                data = json.load(f)

        assert data["key"] == "value"
        assert data["number"] == 42

    def test_load_csv_data(self):
        """Test loading CSV data."""
        csv_data = "col1,col2,col3\n1,2,3\n4,5,6"

        with patch("builtins.open", mock_open(read_data=csv_data)):
            df = pd.read_csv("test.csv")

        assert len(df) == 2
        assert list(df.columns) == ["col1", "col2", "col3"]

    def test_load_with_error_handling(self):
        """Test data loading with error handling."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                with open("nonexistent.json", "r") as f:
                    pass

    def test_load_malformed_json(self):
        """Test handling malformed JSON."""
        bad_json = "{key: value"  # Missing closing brace

        with patch("builtins.open", mock_open(read_data=bad_json)):
            with pytest.raises(json.JSONDecodeError):
                with open("bad.json", "r") as f:
                    json.load(f)


class TestDataTransformation:
    """Test data transformation operations."""

    def test_normalize_data(self):
        """Test data normalization."""
        data = [1, 2, 3, 4, 5]
        min_val = min(data)
        max_val = max(data)

        normalized = [(x - min_val) / (max_val - min_val) for x in data]

        assert normalized[0] == 0.0
        assert normalized[-1] == 1.0
        assert all(0 <= x <= 1 for x in normalized)

    def test_standardize_data(self):
        """Test data standardization (z-score)."""
        data = [1, 2, 3, 4, 5]
        mean = sum(data) / len(data)
        std = (sum((x - mean) ** 2 for x in data) / len(data)) ** 0.5

        standardized = [(x - mean) / std for x in data]

        # Mean should be close to 0
        assert abs(sum(standardized) / len(standardized)) < 0.01

    def test_filter_outliers(self):
        """Test outlier filtering."""
        data = [1, 2, 3, 4, 5, 100]  # 100 is an outlier

        mean = sum(data) / len(data)
        std = (sum((x - mean) ** 2 for x in data) / len(data)) ** 0.5

        # Keep values within 2 standard deviations
        filtered = [x for x in data if abs(x - mean) <= 2 * std]

        assert 100 not in filtered
        assert len(filtered) < len(data)

    def test_reshape_data(self):
        """Test data reshaping."""
        flat_data = list(range(12))
        rows, cols = 3, 4

        reshaped = [flat_data[i:i+cols] for i in range(0, len(flat_data), cols)]

        assert len(reshaped) == rows
        assert len(reshaped[0]) == cols
        assert reshaped[0][0] == 0
        assert reshaped[-1][-1] == 11

    def test_aggregate_data(self):
        """Test data aggregation."""
        data = [
            {"category": "A", "value": 10},
            {"category": "B", "value": 20},
            {"category": "A", "value": 15},
            {"category": "B", "value": 25}
        ]

        aggregated = {}
        for item in data:
            cat = item["category"]
            if cat not in aggregated:
                aggregated[cat] = []
            aggregated[cat].append(item["value"])

        sums = {k: sum(v) for k, v in aggregated.items()}

        assert sums["A"] == 25
        assert sums["B"] == 45


class TestDataValidation:
    """Test data validation functionality."""

    def test_validate_schema(self):
        """Test schema validation."""
        schema = {"name": str, "age": int, "email": str}

        valid_data = {"name": "John", "age": 30, "email": "john@example.com"}
        invalid_data = {"name": "Jane", "age": "thirty", "email": "jane@example.com"}

        def validate(data, schema):
            for key, expected_type in schema.items():
                if key
