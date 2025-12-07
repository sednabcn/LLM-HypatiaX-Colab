"""Common fixtures shared across all domains"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_file(tmp_path):
    """Temporary file for testing"""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content")
    return file_path


@pytest.fixture
def temp_json_file(tmp_path):
    """Temporary JSON file"""
    import json

    file_path = tmp_path / "test.json"
    data = {"key": "value", "number": 42}
    file_path.write_text(json.dumps(data))
    return file_path


@pytest.fixture
def temp_csv_file(tmp_path):
    """Temporary CSV file"""
    file_path = tmp_path / "test.csv"
    content = "name,value\nitem1,100\nitem2,200\n"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def mock_config():
    """Mock configuration object"""
    return {"api_timeout": 30, "max_retries": 3, "batch_size": 32, "enable_caching": True}
