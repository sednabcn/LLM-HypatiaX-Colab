# tests/conftest.py
"""
Shared fixtures for all tests.
Provides reusable test data, configurations, and temporary resources.
"""

import pytest
import pandas as pd
from pathlib import Path


# ============================================================================
# DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_data():
    """Basic sample data for testing"""
    return [
        ("text 1", {"entities": [(0, 4, "LABEL1")]}),
        ("text 2", {"entities": [(0, 4, "LABEL2")]}),
    ]


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing"""
    return pd.DataFrame({
        'Description': ['Calculate sum', 'Get average'],
        'Formulas': ['SUM([Field])', 'AVG([Field])'],
    })


@pytest.fixture
def sample_text_list():
    """List of text samples"""
    return [
        "Calculate the sum of sales",
        "Get the average revenue",
        "Filter by region"
    ]


# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture
def base_config():
    """Base configuration for tests"""
    return {
        'modules': 'datasets',
        'domain': 'queries',
        'sub_domain': 'tableau',
        'test_size': 0.2,
    }


@pytest.fixture
def training_config(base_config):
    """Configuration for training tests"""
    config = base_config.copy()
    config.update({
        'niter': 5,  # Small for testing
        'batchsize': 2,
        'patience': 2,
    })
    return config


# ============================================================================
# FILE & DIRECTORY FIXTURES
# ============================================================================

@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary output directory (auto-cleaned)"""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def temp_model_dir(tmp_path):
    """Temporary model directory (auto-cleaned)"""
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    return model_dir


@pytest.fixture
def sample_file(tmp_path):
    """Create a temporary test file"""
    test_file = tmp_path / "test_data.txt"
    test_file.write_text("sample content")
    return test_file


# ============================================================================
# MOCK OBJECTS
# ============================================================================

@pytest.fixture
def mock_model():
    """Mock model for testing without training"""
    class MockModel:
        def predict(self, text):
            return {"entities": [(0, 3, "MOCK")]}
        
        def save(self, path):
            Path(path).mkdir(parents=True, exist_ok=True)
    
    return MockModel()


# ============================================================================
# SETUP/TEARDOWN FIXTURES
# ============================================================================

@pytest.fixture
def setup_test_environment():
    """Setup before test, cleanup after"""
    # Setup
    print("\nSetting up test environment...")
    test_env = {"initialized": True}
    
    yield test_env  # Test runs here
    
    # Teardown
    print("\nCleaning up test environment...")
    test_env.clear()


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Add custom markers"""
    config.addinivalue_line(
        "markers", 
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )
