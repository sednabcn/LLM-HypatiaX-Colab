# tests/unit/test_[module_name].py
"""
Unit tests for [module_name].
Tests individual functions in isolation with mock data.
"""

import pytest
from hypatiax.[module_path] import function_to_test


class TestFunctionName:
    """Tests for function_to_test()"""
    
    def test_basic_functionality(self):
        """Test basic case with valid input"""
        # Arrange (setup)
        input_data = "test input"
        expected_output = "expected result"
        
        # Act (execute)
        result = function_to_test(input_data)
        
        # Assert (verify)
        assert result == expected_output
    
    def test_edge_case_empty_input(self):
        """Test with empty input"""
        result = function_to_test("")
        assert result == [] or result is None
    
    def test_edge_case_invalid_input(self):
        """Test with invalid input"""
        with pytest.raises(ValueError):
            function_to_test(None)
    
    def test_with_fixture(self, sample_data):
        """Test using fixture from conftest.py"""
        result = function_to_test(sample_data)
        assert len(result) > 0


# Standalone test functions (alternative to class)
def test_another_function():
    """Test another_function with simple assertion"""
    assert another_function(5) == 10


def test_with_multiple_assertions():
    """Test with multiple checks"""
    result = complex_function(input_data)
    
    assert result is not None
    assert len(result) == 3
    assert result[0] == "expected"
