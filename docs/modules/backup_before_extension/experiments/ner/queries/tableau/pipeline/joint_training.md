# Module: `backup_before_extension/experiments/ner/queries/tableau/pipeline/joint_training.py`

## Description

Strategy 2: Joint Training on (Description, Formula) Pairs
End-to-end training with realistic error propagation

**Last Modified**: 2025-11-10T18:46:22.563448

## Dependencies

- `collections`
- `numpy`
- `typing`

## Classes

### `JointEntityExtractor`

Extract entities from both description and formula simultaneously

**Methods**:

- `__init__(self)`
- `extract_pair_entities(self, description: str, formula: str) -> Dict`
  - Extract entities from both description and formula

### `JointMappingModel`

Learn end-to-end mapping from (description, formula) pairs

**Methods**:

- `__init__(self)`
- `train(self, training_data: List[Tuple[<ast.Tuple object at 0x7fa6f8599b10>]])`
  - Train on (description, formula) pairs
- `_create_pattern_key(self, desc_entities: List[Dict]) -> str`
  - Create pattern key from description entities
- `predict(self, description: str) -> str`
  - Predict formula from description
- `evaluate(self, test_data: List[Tuple[<ast.Tuple object at 0x7fa6f848e990>]]) -> Dict`
  - Evaluate on test data with error propagation

### `ErrorPropagationAnalyzer`

Analyze how errors propagate through the pipeline

**Methods**:

- `analyze(model: JointMappingModel, test_case: Tuple[<ast.Tuple object at 0x7fa6f8664b90>])`
  - Detailed analysis of a single prediction
