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

        reshaped = [flat_data[i : i + cols] for i in range(0, len(flat_data), cols)]

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
            {"category": "B", "value": 25},
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
                if key not in data:
                    return False
                if not isinstance(data[key], expected_type):
                    return False
            return True

        assert validate(valid_data, schema) is True
        assert validate(invalid_data, schema) is False

    def test_validate_required_fields(self):
        """Test validation of required fields."""
        required_fields = ["id", "name", "email"]

        complete_data = {"id": 1, "name": "John", "email": "john@example.com"}
        incomplete_data = {"id": 1, "name": "John"}

        def has_required_fields(data, required):
            return all(field in data for field in required)

        assert has_required_fields(complete_data, required_fields) is True
        assert has_required_fields(incomplete_data, required_fields) is False

    def test_validate_email_format(self):
        """Test email format validation."""
        import re

        def is_valid_email(email):
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            return re.match(pattern, email) is not None

        assert is_valid_email("user@example.com") is True
        assert is_valid_email("user.name@example.co.uk") is True
        assert is_valid_email("invalid.email") is False
        assert is_valid_email("@example.com") is False
        assert is_valid_email("user@") is False

    def test_validate_range(self):
        """Test numeric range validation."""

        def validate_range(value, min_val, max_val):
            return min_val <= value <= max_val

        assert validate_range(50, 0, 100) is True
        assert validate_range(0, 0, 100) is True
        assert validate_range(100, 0, 100) is True
        assert validate_range(-1, 0, 100) is False
        assert validate_range(101, 0, 100) is False

    def test_validate_not_empty(self):
        """Test non-empty validation."""

        def is_not_empty(value):
            if isinstance(value, str):
                return len(value.strip()) > 0
            elif isinstance(value, (list, dict)):
                return len(value) > 0
            return value is not None

        assert is_not_empty("valid") is True
        assert is_not_empty("  ") is False
        assert is_not_empty([1, 2, 3]) is True
        assert is_not_empty([]) is False
        assert is_not_empty({"key": "value"}) is True
        assert is_not_empty({}) is False
        assert is_not_empty(None) is False


class TestDataSerialization:
    """Test data serialization and deserialization."""

    def test_serialize_to_json(self):
        """Test serializing data to JSON."""
        data = {"name": "Alice", "age": 25, "scores": [95, 87, 92]}

        json_string = json.dumps(data)
        deserialized = json.loads(json_string)

        assert deserialized == data
        assert deserialized["name"] == "Alice"
        assert deserialized["scores"][0] == 95

    def test_serialize_with_custom_encoder(self):
        """Test JSON serialization with custom encoder."""
        from datetime import datetime

        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        data = {"timestamp": datetime(2024, 1, 1, 12, 0, 0), "value": 42}
        json_string = json.dumps(data, cls=DateTimeEncoder)

        assert "2024-01-01T12:00:00" in json_string

    def test_handle_special_characters(self):
        """Test handling special characters in serialization."""
        data = {"text": "Hello\nWorld\t!", "unicode": "café"}

        json_string = json.dumps(data, ensure_ascii=False)
        deserialized = json.loads(json_string)

        assert deserialized["text"] == "Hello\nWorld\t!"
        assert deserialized["unicode"] == "café"

    def test_pretty_print_json(self):
        """Test pretty-printing JSON."""
        data = {"nested": {"key": "value"}, "list": [1, 2, 3]}

        pretty_json = json.dumps(data, indent=4)

        assert "\n" in pretty_json
        assert "    " in pretty_json


class TestDataCleaning:
    """Test data cleaning operations."""

    def test_remove_duplicates(self):
        """Test removing duplicate entries."""
        data = [1, 2, 2, 3, 4, 4, 5]
        unique_data = list(dict.fromkeys(data))

        assert len(unique_data) == 5
        assert unique_data == [1, 2, 3, 4, 5]

    def test_handle_missing_values(self):
        """Test handling missing values."""
        data = [1, 2, None, 4, None, 6]

        # Remove None values
        cleaned = [x for x in data if x is not None]
        assert len(cleaned) == 4
        assert None not in cleaned

        # Replace None with default
        filled = [x if x is not None else 0 for x in data]
        assert len(filled) == 6
        assert filled == [1, 2, 0, 4, 0, 6]

    def test_trim_whitespace(self):
        """Test trimming whitespace from strings."""
        data = ["  hello  ", "world  ", "  test"]
        trimmed = [s.strip() for s in data]

        assert trimmed == ["hello", "world", "test"]

    def test_convert_data_types(self):
        """Test data type conversion."""
        string_numbers = ["1", "2", "3", "4", "5"]
        integers = [int(x) for x in string_numbers]

        assert all(isinstance(x, int) for x in integers)
        assert integers == [1, 2, 3, 4, 5]

    def test_handle_invalid_conversions(self):
        """Test handling invalid type conversions."""
        mixed_data = ["1", "2", "invalid", "4"]

        def safe_int_convert(value):
            try:
                return int(value)
            except ValueError:
                return None

        converted = [safe_int_convert(x) for x in mixed_data]

        assert converted[0] == 1
        assert converted[2] is None
        assert converted[3] == 4


class TestDataMerging:
    """Test data merging operations."""

    def test_merge_dictionaries(self):
        """Test merging dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}

        merged = {**dict1, **dict2}

        assert len(merged) == 4
        assert merged["a"] == 1
        assert merged["d"] == 4

    def test_merge_with_conflicts(self):
        """Test merging with key conflicts."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}

        merged = {**dict1, **dict2}

        # dict2 values should overwrite dict1
        assert merged["b"] == 3

    def test_merge_lists(self):
        """Test merging lists."""
        list1 = [1, 2, 3]
        list2 = [4, 5, 6]

        merged = list1 + list2

        assert len(merged) == 6
        assert merged == [1, 2, 3, 4, 5, 6]

    def test_join_data_on_key(self):
        """Test joining data structures on a common key."""
        users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

        orders = [
            {"user_id": 1, "product": "Widget"},
            {"user_id": 2, "product": "Gadget"},
        ]

        # Simple join
        joined = []
        for order in orders:
            user = next((u for u in users if u["id"] == order["user_id"]), None)
            if user:
                joined.append({**user, **order})

        assert len(joined) == 2
        assert joined[0]["name"] == "Alice"
        assert joined[0]["product"] == "Widget"


class TestDataSorting:
    """Test data sorting operations."""

    def test_sort_numeric_data(self):
        """Test sorting numeric data."""
        data = [5, 2, 8, 1, 9, 3]
        sorted_data = sorted(data)

        assert sorted_data == [1, 2, 3, 5, 8, 9]

    def test_sort_string_data(self):
        """Test sorting string data."""
        data = ["banana", "apple", "cherry", "date"]
        sorted_data = sorted(data)

        assert sorted_data == ["apple", "banana", "cherry", "date"]

    def test_sort_by_custom_key(self):
        """Test sorting with custom key function."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ]

        sorted_by_age = sorted(data, key=lambda x: x["age"])

        assert sorted_by_age[0]["name"] == "Bob"
        assert sorted_by_age[-1]["name"] == "Charlie"

    def test_sort_descending(self):
        """Test descending sort."""
        data = [5, 2, 8, 1, 9, 3]
        sorted_desc = sorted(data, reverse=True)

        assert sorted_desc == [9, 8, 5, 3, 2, 1]

    def test_sort_with_none_values(self):
        """Test sorting with None values."""
        data = [3, None, 1, None, 5, 2]

        # Sort, treating None as lowest
        sorted_data = sorted(data, key=lambda x: (x is None, x))

        assert sorted_data[-2:] == [None, None]
        assert sorted_data[:4] == [1, 2, 3, 5]


class TestDataFiltering:
    """Test data filtering operations."""

    def test_filter_by_condition(self):
        """Test filtering data by condition."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        evens = [x for x in data if x % 2 == 0]

        assert evens == [2, 4, 6, 8, 10]

    def test_filter_complex_objects(self):
        """Test filtering complex objects."""
        users = [
            {"name": "Alice", "age": 25, "active": True},
            {"name": "Bob", "age": 30, "active": False},
            {"name": "Charlie", "age": 35, "active": True},
        ]

        active_users = [u for u in users if u["active"]]

        assert len(active_users) == 2
        assert all(u["active"] for u in active_users)

    def test_filter_multiple_conditions(self):
        """Test filtering with multiple conditions."""
        data = [
            {"score": 85, "passed": True},
            {"score": 45, "passed": False},
            {"score": 92, "passed": True},
            {"score": 55, "passed": False},
        ]

        high_scorers = [d for d in data if d["score"] >= 80 and d["passed"]]

        assert len(high_scorers) == 2
        assert all(d["score"] >= 80 for d in high_scorers)

    def test_filter_with_function(self):
        """Test filtering using filter() function."""
        data = range(1, 11)
        evens = list(filter(lambda x: x % 2 == 0, data))

        assert evens == [2, 4, 6, 8, 10]
