# Module: `tools/llm_providers/openai_provider.py`

## Description

OpenAI provider implementation

**Last Modified**: 2025-11-12T16:47:36.494831

## Dependencies

- `base_provider`
- `openai`
- `typing`

## Classes

### `OpenAIProvider`

**Inherits from**: `BaseLLMProvider`

OpenAI GPT provider

**Methods**:

- `__init__(self, api_key: str, model: str)`
- `generate(self, prompt: str) -> str`
  - Generate text from prompt
- `generate_with_tools(self, prompt: str, tools: List[Dict]) -> Dict[<ast.Tuple object at 0x7fa6f88af290>]`
  - Generate with tool calling
- `chat(self, messages: List[Dict[<ast.Tuple object at 0x7fa6f88ad710>]]) -> str`
  - Chat completion
