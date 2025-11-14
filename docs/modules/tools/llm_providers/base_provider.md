# Module: `tools/llm_providers/base_provider.py`

## Description

Base LLM provider interface

**Last Modified**: 2025-11-12T16:47:36.494831

## Dependencies

- `abc`
- `typing`

## Classes

### `BaseLLMProvider`

**Inherits from**: `ABC`

Abstract base class for LLM providers

**Methods**:

- `__init__(self, api_key: Optional[str])`
- `generate(self, prompt: str) -> str`
  - Generate text from prompt
- `generate_with_tools(self, prompt: str, tools: List[Dict]) -> Dict[<ast.Tuple object at 0x7fa6f889cd50>]`
  - Generate with tool/function calling
- `chat(self, messages: List[Dict[<ast.Tuple object at 0x7fa6f889f8d0>]]) -> str`
  - Chat completion
- `set_config(self)`
  - Update configuration
