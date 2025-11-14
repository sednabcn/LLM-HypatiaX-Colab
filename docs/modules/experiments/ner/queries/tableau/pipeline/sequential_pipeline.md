# Module: `experiments/ner/queries/tableau/pipeline/sequential_pipeline.py`

## Description

Strategy 1: Sequential Pipeline for Description → Formula Generation
Input: Natural language description
Output: Mathematical formula

Pipeline Steps:
1. Description → Entities[Desc] (Supervised NER)
2. Formulas → Entities[Formula] (Supervised NER for training data)
3. (Desc, Entities[Desc]) → Mapping → (Formula, Entities[Formula]) (Supervised)
4. Entities[Formula] → Formula Generation (Classification/Rule-based)

Each step is evaluated independently with metrics.

**Last Modified**: 2025-11-11T10:48:43.466551

## Dependencies

- `numpy`
- `sklearn.metrics`
- `typing`

## Classes

### `DescriptionNER`

Step 1: Extract entities from natural language descriptions (Supervised)

**Methods**:

- `__init__(self)`
- `extract_entities(self, description: str) -> List[Dict]`
  - Extract entities from description using supervised model
- `evaluate(self, test_data: List[Tuple[<ast.Tuple object at 0x7fa6f854fb50>]]) -> Dict`
  - Evaluate NER on descriptions with multiple metrics

### `FormulaNER`

Step 2: Extract entities from mathematical formulas (Supervised)

**Methods**:

- `__init__(self)`
- `extract_entities(self, formula: str) -> List[Dict]`
  - Extract entities from formula using supervised model
- `evaluate(self, test_data: List[Tuple[<ast.Tuple object at 0x7fa6f889add0>]]) -> Dict`
  - Evaluate NER on formulas with multiple metrics

### `EntityMapper`

Step 3: Map (Description, Entities[Desc]) → (Formula, Entities[Formula]) (Supervised)

**Methods**:

- `__init__(self)`
- `map_entities(self, description: str, desc_entities: List[Dict]) -> Dict`
  - Map description entities to formula entities (supervised learning)
- `evaluate(self, test_data: List[Tuple[<ast.Tuple object at 0x7fa6f8881950>]]) -> Dict`
  - Evaluate mapping accuracy

### `FormulaGenerator`

Step 4: Generate formula string from entities (Classification + Rules)

**Methods**:

- `__init__(self)`
- `generate(self, formula_type: str, formula_entities: List[Dict]) -> str`
  - Generate formula from entities using classification/rules
- `_construct_from_entities(self, entities: List[Dict]) -> str`
  - Fallback construction from entities
- `evaluate(self, test_data: List[Tuple[<ast.Tuple object at 0x7fa6f851a710>]]) -> Dict`
  - Evaluate formula generation
