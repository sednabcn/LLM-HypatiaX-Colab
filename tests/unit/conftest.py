"""Unit test level fixtures"""

import pytest


@pytest.fixture
def mock_logger():
    """Mock logger for unit tests"""
    from unittest.mock import Mock

    return Mock()


@pytest.fixture
def unit_test_config():
    """Standard config for unit tests"""
    return {"timeout": 5, "strict_mode": True, "verbose": False}
