# Module: `mappings/agent_mapping.py`

## Description

Agent-based expression mapping

**Last Modified**: 2025-11-12T16:47:36.498831

## Dependencies

- `agents.base.agent`
- `typing`

## Classes

### `AgentMapper`

Map queries using AI agents

**Methods**:

- `__init__(self, agents: List[BaseAgent])`
- `add_agent(self, agent: BaseAgent)`
  - Add agent to mapper
- `map(self, query: str) -> Dict[<ast.Tuple object at 0x7fa6f86f68d0>]`
  - Map query using agent workflow
