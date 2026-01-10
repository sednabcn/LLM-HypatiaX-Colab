"""
Constants and Default Values

Centralized location for all constants used across HypatiaX.
"""

from typing import Dict, List, Set


class EntityLabels:
    """
    Entity labels for NER models.

    Usage:
        from hypatiax.config import EntityLabels

        labels = EntityLabels.TABLEAU_DESC
        all_labels = EntityLabels.get_all_labels()
    """

    # Tableau Description Labels
    TABLEAU_DESC = ["FUNCTION", "FIELD", "OPERATOR", "VALUE", "AGGREGATION"]

    # Tableau Formula Labels
    TABLEAU_FORMULAS = [
        "FUNCTION",
        "FIELD",
        "OPERATOR",
        "BRACKET",
        "NUMBER",
        "STRING",
        "LOGICAL",
    ]

    # Combined Labels (union of both)
    TABLEAU_COMBINED = list(set(TABLEAU_DESC + TABLEAU_FORMULAS))

    # Common entity types
    COMMON = ["FUNCTION", "FIELD", "OPERATOR"]

    @classmethod
    def get_all_labels(cls) -> Set[str]:
        """Get all unique entity labels"""
        return set(cls.TABLEAU_COMBINED)

    @classmethod
    def get_labels_for(cls, dtype: str) -> List[str]:
        """
        Get labels for specific data type.

        Args:
            dtype: 'desc', 'formulas', or 'combined'

        Returns:
            List of entity labels
        """
        if dtype == "desc":
            return cls.TABLEAU_DESC
        elif dtype == "formulas":
            return cls.TABLEAU_FORMULAS
        elif dtype == "combined":
            return cls.TABLEAU_COMBINED
        else:
            raise ValueError(f"Unknown dtype: {dtype}")


class FileFormats:
    """Supported file formats"""

    EXCEL = [".xlsx", ".xls"]
    CSV = [".csv"]
    TEXT = [".txt"]
    JSON = [".json"]
    JSONL = [".jsonl"]
    SPACY = [".spacy"]
    PICKLE = [".pkl", ".pickle"]

    # All supported formats
    ALL = EXCEL + CSV + TEXT + JSON + JSONL + SPACY + PICKLE

    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """Check if file format is supported"""
        return any(filename.endswith(ext) for ext in cls.ALL)

    @classmethod
    def get_type(cls, filename: str) -> str:
        """Get file type from filename"""
        if any(filename.endswith(ext) for ext in cls.EXCEL):
            return "excel"
        elif any(filename.endswith(ext) for ext in cls.CSV):
            return "csv"
        elif any(filename.endswith(ext) for ext in cls.TEXT):
            return "text"
        elif any(filename.endswith(ext) for ext in cls.JSON):
            return "json"
        elif any(filename.endswith(ext) for ext in cls.JSONL):
            return "jsonl"
        elif any(filename.endswith(ext) for ext in cls.SPACY):
            return "spacy"
        elif any(filename.endswith(ext) for ext in cls.PICKLE):
            return "pickle"
        else:
            return "unknown"


# Default stopwords for text processing
DEFAULT_STOPWORDS = [
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "from",
    "as",
    "is",
    "was",
    "are",
    "were",
    "been",
    "be",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "should",
    "could",
    "may",
    "might",
    "must",
    "can",
    "this",
    "that",
    "these",
    "those",
]


# Tableau-specific stopwords (symbols to ignore in formulas)
TABLEAU_STOPWORDS = [
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    ",",
    ";",
    ":",
    ".",
    "=",
    "==",
    "!=",
    ">",
    "<",
    ">=",
    "<=",
    "+",
    "-",
    "*",
    "/",
    "%",
    "^",
    "AND",
    "OR",
    "NOT",
    "IF",
    "THEN",
    "ELSE",
    "END",
]


# Model-specific constants
class ModelConstants:
    """Constants for model configuration"""

    # SpaCy model names
    SPACY_BASE_MODEL = "en_core_web_sm"
    SPACY_MEDIUM_MODEL = "en_core_web_md"
    SPACY_LARGE_MODEL = "en_core_web_lg"

    # Pipeline component names
    TOKENIZER = "tokenizer"
    NER = "ner"
    ENTITY_RULER = "entity_ruler"

    # Custom component names
    CUSTOM_DESC = "custom_tableau_desc_components"
    CUSTOM_FORMULAS = "custom_tableau_formulas_components"
    CUSTOM_COMBINED = "custom_tableau_components"

    # Ruler names
    RULER_ARG = "ruler_arg"
    RULER_DESC = "ruler_tableau_desc"
    RULER_FORMULAS = "ruler_tableau_formulas"


# Data processing patterns
class Patterns:
    """Regex patterns for data processing"""

    # Formula normalization patterns
    FUNCTION_PATTERN = r"(\w)\("  # Match function names
    OPEN_PAREN = r"\s*\(\s*"
    CLOSE_PAREN = r"\s*\)\s*"
    OPEN_BRACKET = r"\s*\[\s*"
    CLOSE_BRACKET = r"\s*\]\s*"
    OPEN_BRACE = r"\s*\{\s*"
    CLOSE_BRACE = r"\s*\}\s*"

    # Comparison operators
    EQUALS = r"(?<!\=)\s*\=\s*(?!=)"
    DOUBLE_EQUALS = r"\s*\==\s*"
    NOT_EQUALS = r"\s*\!=\s*"
    GREATER_EQUAL = r"\s*\>=\s*"
    LESS_EQUAL = r"\s*\<=\s*"
    GREATER_THAN = r"\s*\>\s*"
    LESS_THAN = r"\s*\<\s*"

    # Formula splitting pattern
    FORMULA_SPLIT = r"\(| = | >= | > | \[ | \) | \{ | \]"


# Default configurations
DEFAULT_CONFIG = {
    "modules": "datasets",
    "domain": "queries",
    "sub_domain": "tableau",
    "actions": "training",
    "test_size": 0.2,
    "task_type": "single",
    "val_data": True,
    "option": None,
}


# Version info
VERSION = "0.1.0"
PROJECT_NAME = "HypatiaX"
AUTHOR = "HypatiaX Team"


# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "hypatiax.log",
            "mode": "a",
        },
    },
    "loggers": {
        "hypatiax": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        }
    },
}
