"""NER sentence fixtures"""

import pytest


@pytest.fixture
def raw_sentences():
    """Plain text sentences for NER testing"""
    return [
        "Apple Inc. announced new products yesterday.",
        "John Smith works at Google in Mountain View, California.",
        "The S&P 500 rose 2.3% on Tuesday.",
        "Dr. Jane Doe published a paper on quantum computing.",
        "Tesla, Inc. opened a new factory in Austin, Texas.",
    ]


@pytest.fixture
def annotated_sentences():
    """Sentences with entity annotations"""
    return [
        {
            "text": "Apple Inc. announced new products yesterday.",
            "entities": [{"start": 0, "end": 10, "label": "ORG", "text": "Apple Inc."}],
        },
        {
            "text": "John Smith works at Google in Mountain View, California.",
            "entities": [
                {"start": 0, "end": 10, "label": "PERSON", "text": "John Smith"},
                {"start": 20, "end": 26, "label": "ORG", "text": "Google"},
                {"start": 30, "end": 43, "label": "GPE", "text": "Mountain View"},
                {"start": 45, "end": 55, "label": "GPE", "text": "California"},
            ],
        },
        {
            "text": "The S&P 500 rose 2.3% on Tuesday.",
            "entities": [
                {"start": 4, "end": 11, "label": "PRODUCT", "text": "S&P 500"},
                {"start": 25, "end": 32, "label": "DATE", "text": "Tuesday"},
            ],
        },
    ]


@pytest.fixture
def difficult_sentences():
    """Edge cases for NER testing"""
    return [
        "Dr. J.R.R. Tolkien wrote The Lord of the Rings.",  # Multiple periods
        "New York-based startup raised $10M.",  # Hyphenated, currency
        "Mr. O'Brien from McDonald's visited the U.S.",  # Apostrophes, abbreviations
        "€100,000 investment in AI/ML research.",  # Special chars, slash
        "Email support@company.com for info.",  # Email address
        "Visit https://example.com/path?query=value",  # URL
    ]


@pytest.fixture
def multilingual_sentences():
    """Sentences in different languages"""
    return {
        "spanish": "María García trabaja en Barcelona, España.",
        "chinese": "李明在北京工作。",
        "arabic": "محمد يعمل في دبي.",
        "mixed": "John works at 索尼 (Sony) in Tokyo.",
    }


@pytest.fixture
def sentence_test_cases():
    """Comprehensive test cases with expected results"""
    return {
        "simple_org": {
            "text": "Google is in California",
            "expected": [
                {"text": "Google", "label": "ORG"},
                {"text": "California", "label": "GPE"},
            ],
        },
        "ambiguous": {
            "text": "Apple released new products",  # Apple = company or fruit?
            "expected": [{"text": "Apple", "label": "ORG"}],
        },
        "nested": {
            "text": "Bank of America announced quarterly results",
            "expected": [{"text": "Bank of America", "label": "ORG"}],
        },
    }
