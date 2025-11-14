# Module: `experiments/ner/queries/tableau/custom_ner/entities_mapping.py`

## Description

Strategy 1 - Point 2 & 3 Implementation
Point 2: Entities[Desc] → Entities[Formula] (Entity Mapping)
Point 3: Entities[Formula] → Formula String (Formula Generation)

**Last Modified**: 2025-11-07T13:17:57.739070

## Dependencies

- `json`
- `typing`

## Classes

### `EntityMapper`

Maps Description Entities to Formula Entities
This is the CRITICAL step that learns the transformation

**Methods**:

- `__init__(self)`
- `map_single_entity(self, entity: Dict) -> Dict`
  - Map a single description entity to formula entity
- `map_entities(self, desc_entities: List[Dict]) -> List[Dict]`
  - POINT 2 IMPLEMENTATION: Map description entities to formula entities
- `_pattern_based_mapping(self, desc_entities: List[Dict]) -> Optional[List[Dict]]`
  - Use pattern matching to find formula template
- `_vocab_based_mapping(self, desc_entities: List[Dict]) -> List[Dict]`
  - Map entities one-by-one using vocabulary mapping
- `_ml_based_mapping(self, desc_entities: List[Dict]) -> List[Dict]`
  - Placeholder for ML-based entity mapping
- `train_from_pairs(self, training_pairs: List[Tuple[<ast.Tuple object at 0x7fa6f8633f90>]])`
  - Learn mappings from (desc_entities, formula_entities) pairs

### `FormulaGenerator`

Generate formula string from formula entities
This is the final step that produces human-readable output

**Methods**:

- `__init__(self)`
- `generate(self, formula_entities: List[Dict]) -> str`
  - POINT 3 IMPLEMENTATION: Generate formula string from entities
- `_needs_space_before(self, entity_type: str, value: str) -> bool`
  - Determine if space is needed before this token
- `_needs_space_after(self, entity_type: str, value: str) -> bool`
  - Determine if space is needed after this token
- `generate_with_validation(self, formula_entities: List[Dict]) -> Tuple[<ast.Tuple object at 0x7fa6f8880b90>]`
  - Generate formula with validation
