# Module: `core/training/training_llm_.py`

## Description

LLM-based Formula Mapping
Uses GPT/Claude APIs with few-shot prompting

**Last Modified**: 2025-11-07T15:17:47.365345

## Dependencies

- `dataclasses`
- `json`
- `os`
- `pathlib`
- `requests`
- `time`
- `typing`

## Classes

### `LLMConfig`

Configuration for LLM-based mapping

**Decorators**: `dataclass`

### `PromptBuilder`

Build few-shot prompts for LLM

**Methods**:

- `build_few_shot_prompt(query: str, examples: List[Dict]) -> str`
  - Create few-shot prompt with examples
- `build_system_prompt() -> str`
  - Create system prompt

### `OpenAIClient`

OpenAI API client

**Methods**:

- `__init__(self, api_key: str, model: str)`
- `generate(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> str`
  - Generate completion

### `AnthropicClient`

Anthropic Claude API client

**Methods**:

- `__init__(self, api_key: str, model: str)`
- `generate(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> str`
  - Generate completion

### `LLMTrainer`

LLM-based formula mapping trainer

**Methods**:

- `__init__(self, config: LLMConfig)`
- `load_examples(self, examples_path: str)`
  - Load few-shot examples
- `select_examples(self, query: str, k: int) -> List[Dict]`
  - Select most relevant examples for few-shot prompting
- `generate_formula(self, query: str) -> str`
  - Generate formula for query using LLM
- `batch_generate(self, queries: List[str], delay: float) -> List[Dict]`
  - Generate formulas for multiple queries
- `save_results(self, results: List[Dict], output_path: str)`
  - Save generation results
