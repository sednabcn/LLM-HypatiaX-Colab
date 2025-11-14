# Module: `config/llm_config.py`

## Description

LLM provider configurations

**Last Modified**: 2025-11-12T16:47:36.486831

## Dependencies

- `os`
- `typing`

## Constants

- `OPENAI_MODEL`
- `ANTHROPIC_MODEL`
- `DEEPSEEK_MODEL`
- `TEMPERATURE`
- `MAX_TOKENS`
- `LLM_PROMPTS_DIR`
- `LLM_EXAMPLES_DIR`

## Classes

### `LLMConfig`

Configuration for LLM providers

**Methods**:

- `get_provider_config(cls, provider: str)`
  - Get configuration for specific provider
