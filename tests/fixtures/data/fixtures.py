"""Data fixtures"""

import pytest


@pytest.fixture
def sample_csv_data():
    """Sample CSV data"""
    return "name,value\nitem1,100\nitem2,200\nitem3,300"


@pytest.fixture
def sample_dataframe_data():
    """Sample data for DataFrame creation"""
    return {"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35], "score": [85.5, 92.0, 78.5]}
