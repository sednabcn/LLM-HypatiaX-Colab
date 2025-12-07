# Module: `config/constants.py`

## Description

Constants and Default Values

Centralized location for all constants used across HypatiaX.

**Last Modified**: 2025-11-09T18:29:08.202364

## Dependencies

- `typing`

## Constants

- `DEFAULT_STOPWORDS`
- `TABLEAU_STOPWORDS`
- `DEFAULT_CONFIG`
- `VERSION`
- `PROJECT_NAME`
- `AUTHOR`
- `LOGGING_CONFIG`
- `TABLEAU_DESC`
- `TABLEAU_FORMULAS`
- `TABLEAU_COMBINED`
- `COMMON`
- `EXCEL`
- `CSV`
- `TEXT`
- `JSON`
- `JSONL`
- `SPACY`
- `PICKLE`
- `ALL`
- `SPACY_BASE_MODEL`
- `SPACY_MEDIUM_MODEL`
- `SPACY_LARGE_MODEL`
- `TOKENIZER`
- `NER`
- `ENTITY_RULER`
- `CUSTOM_DESC`
- `CUSTOM_FORMULAS`
- `CUSTOM_COMBINED`
- `RULER_ARG`
- `RULER_DESC`
- `RULER_FORMULAS`
- `FUNCTION_PATTERN`
- `OPEN_PAREN`
- `CLOSE_PAREN`
- `OPEN_BRACKET`
- `CLOSE_BRACKET`
- `OPEN_BRACE`
- `CLOSE_BRACE`
- `EQUALS`
- `DOUBLE_EQUALS`
- `NOT_EQUALS`
- `GREATER_EQUAL`
- `LESS_EQUAL`
- `GREATER_THAN`
- `LESS_THAN`
- `FORMULA_SPLIT`

## Classes

### `EntityLabels`

Entity labels for NER models.

Usage:
    from hypatiax.config import EntityLabels

    labels = EntityLabels.TABLEAU_DESC
    all_labels = EntityLabels.get_all_labels()

**Methods**:

- `get_all_labels(cls) -> Set[str]`
  - Get all unique entity labels
- `get_labels_for(cls, dtype: str) -> List[str]`
  - Get labels for specific data type.

### `FileFormats`

Supported file formats

**Methods**:

- `is_supported(cls, filename: str) -> bool`
  - Check if file format is supported
- `get_type(cls, filename: str) -> str`
  - Get file type from filename

### `ModelConstants`

Constants for model configuration

### `Patterns`

Regex patterns for data processing
