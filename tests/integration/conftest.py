"""Integration test level fixtures"""

import os

import pytest


@pytest.fixture(scope="module")
def integration_test_db():
    """Test database for integration tests"""
    # Setup
    db = create_test_database()
    yield db
    # Teardown
    db.cleanup()


@pytest.fixture
def skip_if_no_api_key():
    """Skip test if API keys not configured"""

    def _skip(key_name):
        if not os.getenv(key_name):
            pytest.skip(f"{key_name} not set")

    return _skip
