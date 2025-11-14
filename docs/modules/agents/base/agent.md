# Module: `agents/base/agent.py`

## Description

Base agent class

**Last Modified**: 2025-11-12T16:47:36.494831

## Dependencies

- `abc`
- `datetime`
- `typing`

## Classes

### `BaseAgent`

**Inherits from**: `ABC`

Abstract base class for all agents

**Methods**:

- `__init__(self, name: str, role: str, tools: Optional[List])`
- `execute(self, task: Dict[<ast.Tuple object at 0x7fa6f86e7050>]) -> Any`
  - Execute agent task
- `remember(self, item: Any)`
  - Store item in agent memory
- `recall(self, n: int) -> List`
  - Recall last n items from memory
- `clear_memory(self)`
  - Clear agent memory
- `__repr__(self)`
