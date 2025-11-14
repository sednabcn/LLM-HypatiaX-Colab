# Module: `experiments/experiment_tracker.py`

## Description

Experiment tracking utility for HypatiaX
Registers and tracks experiments across all technologies

**Last Modified**: 2025-11-12T15:37:53.166909

## Dependencies

- `argparse`
- `dataclasses`
- `datetime`
- `enum`
- `json`
- `os`
- `pathlib`
- `typing`

## Constants

- `NER`
- `TRANSFORMER`
- `LLM`
- `AGENT`
- `HYBRID`
- `PLANNED`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `ARCHIVED`

## Classes

### `TechnologyType`

**Inherits from**: `Enum`

Types of technologies

### `ExperimentStatus`

**Inherits from**: `Enum`

Experiment status

### `Experiment`

Experiment metadata

**Decorators**: `dataclass`

### `ExperimentTracker`

Track experiments across all technologies

**Methods**:

- `__init__(self, experiments_dir: str)`
- `_load_registry(self) -> Dict[<ast.Tuple object at 0x7fa6f8689b90>]`
  - Load experiment registry from file
- `_save_registry(self)`
  - Save experiment registry to file
- `register_experiment(self, name: str, technology: TechnologyType, description: str, author: str, config: Dict[<ast.Tuple object at 0x7fa6f867d510>], tags: List[str]) -> str`
  - Register a new experiment
- `update_experiment(self, exp_id: str, status: Optional[ExperimentStatus], metrics: Optional[Dict[<ast.Tuple object at 0x7fa6f8892990>]], notes: Optional[str])`
  - Update experiment details
- `get_experiment(self, exp_id: str) -> Optional[Experiment]`
  - Get experiment by ID
- `list_experiments(self, technology: Optional[TechnologyType], status: Optional[ExperimentStatus], tags: Optional[List[str]]) -> List[Experiment]`
  - List experiments with optional filters
- `generate_report(self, output_file: str)`
  - Generate markdown report of all experiments
