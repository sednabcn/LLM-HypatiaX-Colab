"""
Root conftest.py - shared fixtures and configuration for all tests
"""

import os
import sys
from pathlib import Path

import pytest

# Add project root to Python path (parent of tests)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# -----------------------
# Ensure PySR uses system Julia
# -----------------------
# Adjust path if your Julia binary is elsewhere
os.environ["JULIA_EXE"] = "/usr/bin/julia"

try:
    import numpy as np
    import pysr

    # Minimal PySRRegressor run to precompile Julia packages
    # Only runs once per Python environment
    X = np.array([[0.0], [1.0]])
    y = np.array([0.0, 1.0])
    reg = pysr.PySRRegressor(niterations=1, maxsize=2)
    reg.fit(X, y)
except Exception:
    # Ignore if already precompiled or if in CI environment
    pass

# Import all fixtures from fixture modules
pytest_plugins = [
    #    "tests.fixtures.conftest",
]


@pytest.fixture(scope="session")
def project_root_dir():
    """Project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory"""
    return Path(__file__).parent / "fixtures" / "data"


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for test files"""
    return tmp_path


# Configure test environment
def pytest_configure(config):
    """Pytest configuration hook"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
