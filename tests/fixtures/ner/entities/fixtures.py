"""NER entity fixtures"""

import pytest


@pytest.fixture
def sample_organizations():
    """Sample organization names"""
    return [
        "Apple Inc.",
        "Google LLC",
        "Microsoft Corporation",
        "Tesla, Inc.",
        "Amazon.com",
        "JPMorgan Chase & Co.",
        "Goldman Sachs",
        "Y Combinator",
    ]


@pytest.fixture
def sample_persons():
    """Sample person names"""
    return [
        "John Smith",
        "Dr. Jane Doe",
        "Mr. Robert Johnson Jr.",
        "María García",
        "李明",  # Chinese
        "Mohammed Al-Rashid",
        "Prof. Elizabeth Warren",
    ]


@pytest.fixture
def sample_locations():
    """Sample location names"""
    return [
        "New York City",
        "San Francisco, California",
        "London, UK",
        "Mount Everest",
        "Pacific Ocean",
        "Silicon Valley",
        "Wall Street",
    ]


@pytest.fixture
def entity_types():
    """Standard NER entity types"""
    return {
        "PERSON": "People, including fictional",
        "ORG": "Companies, agencies, institutions",
        "GPE": "Countries, cities, states",
        "LOC": "Non-GPE locations, mountain ranges, bodies of water",
        "PRODUCT": "Objects, vehicles, foods, etc.",
        "DATE": "Absolute or relative dates or periods",
        "TIME": "Times smaller than a day",
        "MONEY": "Monetary values",
        "PERCENT": "Percentage values",
    }
