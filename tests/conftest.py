"""
Pytest configuration and shared fixtures for hypatiax tests.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import spacy

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_description_data():
    """Sample description data for testing."""
    return [
        ("Calculate the sum of sales", {"entities": [(13, 16, "FUNCTION"), (20, 25, "FIELD")]}),
        ("Get the average revenue", {"entities": [(8, 15, "FUNCTION"), (16, 23, "FIELD")]}),
        ("Filter by region", {"entities": [(0, 6, "FUNCTION"), (10, 16, "FIELD")]}),
    ]


@pytest.fixture
def sample_formula_data():
    """Sample formula data for testing."""
    return [
        ("SUM([Sales])", {"entities": [(0, 3, "FUNCTION"), (4, 11, "FIELD")]}),
        ("AVG([Revenue])", {"entities": [(0, 3, "FUNCTION"), (4, 13, "FIELD")]}),
        ("COUNT([Orders])", {"entities": [(0, 5, "FUNCTION"), (6, 14, "FIELD")]}),
    ]


@pytest.fixture
def sample_combined_data(sample_description_data, sample_formula_data):
    """Combined description and formula data."""
    return {
        'descriptions': sample_description_data,
        'formulas': sample_formula_data
    }


@pytest.fixture
def sample_dataframe():
    """Sample pandas DataFrame for testing."""
    return pd.DataFrame({
        'Description': ['Calculate sum', 'Get average', 'Filter data'],
        'Formulas': ['SUM([Field])', 'AVG([Field])', '[Field] > 100'],
        'Combined': ['SUM([Field]) - sum', 'AVG([Field]) - average', '[Field] - filter']
    })


# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture
def base_config():
    """Base configuration for testing."""
    return {
        'modules': 'datasets',
        'domain': 'queries',
        'sub_domain': 'tableau',
        'actions': 'training',
        'test_size': 0.2,
        'task_type': 'single',
    }


@pytest.fixture
def desc_config(base_config):
    """Configuration for description testing."""
    config = base_config.copy()
    config.update({
        'filename': 'formulas_nor.xlsx',
        'dtype': 'desc',
        'sizefile': 'sm',
        'ner_entity': 'ner_tableau_desc',
        'val_data': True,
        'option': None
    })
    return config


@pytest.fixture
def formula_config(base_config):
    """Configuration for formula testing."""
    config = base_config.copy()
    config.update({
        'filename': 'formulas_nor.xlsx',
        'dtype': 'formulas',
        'sizefile': 'sm',
        'ner_entity': 'ner_tableau_formulas',
        'val_data': True,
        'option': None
    })
    return config


@pytest.fixture
def combined_config(base_config):
    """Configuration for combined testing."""
    config = base_config.copy()
    config.update({
        'filename': 'formulas_nor_combined.xlsx',
        'dtype': 'both',
        'sizefile': 'bsm',
        'ner_entity': 'ner_tableau',
        'val_data': True,
        'option': 'split'
    })
    return config


@pytest.fixture
def training_config():
    """Training configuration for testing."""
    return {
        'domain': 'queries',
        'sub_domain': 'tableau',
        'dtype': 'desc',
        'output_model_name': 'Test_Model',
        'niter': 10,  # Small number for testing
        'drop': 0.5,
        'batchsize': 4,
        'patience': 3,
        'n_checkpoint': 5,
        'option': None
    }


# ============================================================================
# PATH FIXTURES
# ============================================================================

@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a temporary directory for test outputs."""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def temp_model_dir(tmp_path):
    """Provide a temporary directory for test models."""
    model_dir = tmp_path / "test_models"
    model_dir.mkdir()
    return model_dir


@pytest.fixture
def temp_data_dir(tmp_path):
    """Provide a temporary directory for test data."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return data_dir


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_spacy_doc():
    """Mock spaCy Doc object for testing."""
    try:
        nlp = spacy.blank("en")
        doc = nlp("SUM([Sales])")
        return doc
    except Exception:
        pytest.skip("spaCy not available")


@pytest.fixture
def mock_training_data():
    """Mock training data in spaCy format."""
    return [
        ("Calculate the sum", {"entities": [(13, 16, "FUNCTION")]}),
        ("Get the average", {"entities": [(8, 15, "FUNCTION")]}),
        ("Count all records", {"entities": [(0, 5, "FUNCTION")]}),
    ]


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", 
        "slow : marks tests as slow (deselect with '-m not slow')"
    )
    config.addinivalue_line(
        "markers", 
        "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", 
        "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", 
        "entity: marks tests related to entity extraction"
    )
    config.addinivalue_line(
        "markers", 
        "training: marks tests related to model training"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark based on path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Mark based on filename
        if "entity" in item.nodeid:
            item.add_marker(pytest.mark.entity)
        if "train" in item.nodeid or "training" in item.nodeid:
            item.add_marker(pytest.mark.training)
