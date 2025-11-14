# Module: `agents/specialists/parser_agent.py`

## Description

Parser agent for query understanding

**Last Modified**: 2025-11-12T16:47:36.494831

## Dependencies

- `agents.base.agent`
- `typing`

## Classes

### `ParserAgent`

**Inherits from**: `BaseAgent`

Agent specialized in parsing mathematical queries

**Methods**:

- `__init__(self, ner_extractor)`
- `execute(self, task: Dict[<ast.Tuple object at 0x7fa6f86e6a50>]) -> Dict[<ast.Tuple object at 0x7fa6f8663190>]`
  - Parse query and extract mathematical intent
- `_analyze_intent(self, query: str, entities: list) -> Dict[<ast.Tuple object at 0x7fa6f88980d0>]`
  - Analyze mathematical intent from query
- `_estimate_complexity(self, query: str, entities: list) -> str`
  - Estimate query complexity
