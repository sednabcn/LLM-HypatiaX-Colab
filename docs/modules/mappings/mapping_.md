# Module: `mappings/mapping_.py`

## Description

Improved Description-to-Formula Mapping System
Supports multiple strategies: vocab mapping, sentence mapping, regex, NER-based, and ML models

**Last Modified**: 2025-11-07T11:44:54.756299

## Dependencies

- `abc`
- `re`
- `typing`

## Classes

### `MappingStrategy`

**Inherits from**: `ABC`

Abstract base class for mapping strategies

**Methods**:

- `map(self, description: str, ner_entities: Optional[List]) -> str`
  - Map description to formula

### `VocabToVocabStrategy`

**Inherits from**: `MappingStrategy`

Map vocabulary terms directly (e.g., 'average' -> 'AVG')

**Methods**:

- `__init__(self)`
- `map(self, description: str, ner_entities: Optional[List]) -> str`
- `_extract_column_name(self, description: str) -> Optional[str]`
  - Extract column name from description

### `SentenceToSentenceStrategy`

**Inherits from**: `MappingStrategy`

Map complete sentences using pattern matching

**Methods**:

- `__init__(self)`
- `map(self, description: str, ner_entities: Optional[List]) -> str`

### `RegexStrategy`

**Inherits from**: `MappingStrategy`

Use regex patterns to extract components and build formulas

**Methods**:

- `__init__(self)`
- `map(self, description: str, ner_entities: Optional[List]) -> str`

### `NERBasedStrategy`

**Inherits from**: `MappingStrategy`

Use NER entities to construct formulas

**Methods**:

- `__init__(self)`
- `map(self, description: str, ner_entities: Optional[List]) -> str`

### `MLModelStrategy`

**Inherits from**: `MappingStrategy`

Use machine learning model for mapping (placeholder for trained models)

**Methods**:

- `__init__(self, model_type: str)`
- `map(self, description: str, ner_entities: Optional[List]) -> str`
  - Placeholder for ML-based mapping

### `MapDescriptionToFormula`

Main class for mapping descriptions to formulas

**Methods**:

- `__init__(self, description: str, rules: Dict, ner_entities: Optional[List])`
- `map(self, description: str, strategy: str, ner_entities: Optional[List]) -> str`
  - Map description to formula using specified strategy
- `map_with_fallback(self, description: str, strategies: List[str]) -> Tuple[<ast.Tuple object at 0x7fa6f85a4cd0>]`
  - Try multiple strategies in order until one succeeds
- `__call__(self, description: str, option: str) -> str`
  - Backward compatibility with original interface
