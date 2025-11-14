# Module: `agents/workflows/hybrid_workflow.py`

## Description

Hybrid workflow combining multiple technologies

**Last Modified**: 2025-11-12T16:47:36.494831

## Dependencies

- `typing`

## Classes

### `HybridWorkflow`

Workflow that combines NER, Transformers, LLM, and Agents

**Methods**:

- `__init__(self)`
- `add_agent(self, agent)`
  - Add agent to workflow
- `execute(self, query: str) -> Dict[<ast.Tuple object at 0x7fa6f86f3850>]`
  - Execute hybrid workflow
- `get_history(self, n: int) -> List[Dict]`
  - Get last n executions
