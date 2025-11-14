# Module: `tools/llm_providers/base_provider_.py`

**Last Modified**: 2025-11-13T21:59:29.793366

## Dependencies

- `abc`
- `typing`

## Classes

### `BaseLLMProvider`

**Inherits from**: `ABC`

Abstract base class for LLM providers

**Methods**:

- `generate(self, prompt: str) -> str`
  - Generate completion from prompt
- `batch_generate(self, prompts: list) -> list`
  - Generate completions for multiple prompts
