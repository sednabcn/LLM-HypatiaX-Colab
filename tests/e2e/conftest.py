"""E2E test fixtures"""

import pytest


@pytest.fixture(scope="session")
def e2e_test_environment():
    """Setup complete test environment for E2E tests"""
    # Setup: database, models, API clients, etc.
    env = {"db": setup_test_db(), "models": load_test_models(), "config": load_test_config()}

    yield env

    # Teardown
    cleanup_test_environment(env)


@pytest.fixture
def full_pipeline():
    """Complete processing pipeline for E2E tests"""
    from hypatiax.pipeline import Pipeline

    return Pipeline(ner_enabled=True, symbolic_enabled=True, llm_enabled=True)
