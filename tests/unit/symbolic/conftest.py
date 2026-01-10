"""Symbolic unit test fixtures"""

import pytest


@pytest.fixture
def symbolic_engine():
    """Symbolic engine instance for unit tests"""
    from hypatiax.symbolic import SymbolicEngine

    return SymbolicEngine()


@pytest.fixture
def formula_parser():
    """Formula parser instance"""
    from hypatiax.symbolic import FormulaParser

    return FormulaParser()


@pytest.fixture
def validator():
    """Formula validator instance"""
    from hypatiax.symbolic import FormulaValidator

    return FormulaValidator()


@pytest.fixture
def ner_model():
    """Mock NER model for unit tests"""
    from unittest.mock import Mock

    model = Mock()
    model.extract.return_value = [
        {"text": "Apple Inc.", "label": "ORG", "start": 0, "end": 10}
    ]
    return model


@pytest.fixture
def tokenizer():
    """Mock tokenizer"""
    from unittest.mock import Mock

    tokenizer = Mock()
    tokenizer.tokenize.return_value = ["token1", "token2", "token3"]
    return tokenizer
