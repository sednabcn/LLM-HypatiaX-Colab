"""Symbolic expression fixtures"""

import pytest


@pytest.fixture
def simple_expressions():
    """Simple mathematical expressions"""
    return ["2 + 2", "10 - 3", "5 * 4", "20 / 4"]
