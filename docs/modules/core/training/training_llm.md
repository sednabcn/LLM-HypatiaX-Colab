# Module: `core/training/training_llm.py`

## Description

Modern LLM Training for Formula Mapping (2025)
Primary approach: Few-shot prompting with prompt optimization
Features:
- Prompt caching for cost reduction
- Batch processing with rate limiting
- Automatic prompt optimization
- Structured output parsing
- Multi-provider support (OpenAI, Anthropic, local LLMs)

**Last Modified**: 2025-11-11T11:49:36.084081

## Dependencies

- `anthropic`
- `asyncio`
- `concurrent.futures`
- `dataclasses`
- `json`
- `openai`
- `os`
- `pathlib`
- `time`
- `typing`

## Classes

### `LLMConfig`

Configuration for modern LLM-based mapping

**Decorators**: `dataclass`

**Methods**:

- `__post_init__(self)`
  - Auto-detect API keys from environment

### `PromptOptimizer`

Optimizes few-shot prompts for maximum accuracy
2025 Best Practice: Dynamic example selection based on query similarity

**Methods**:

- `__init__(self, examples: List[Dict])`
- `select_best_examples(self, query: str, k: int) -> List[Dict]`
  - Select most relevant examples for query
- `build_system_prompt(self) -> str`
  - Modern system prompt with clear instructions
- `build_few_shot_prompt(self, query: str, examples: List[Dict]) -> str`
  - Build optimized few-shot prompt

### `LLMClient`

Unified client for multiple LLM providers
2025 Trend: Provider abstraction with automatic fallback

**Methods**:

- `__init__(self, config: LLMConfig)`
- `generate_anthropic(self, system_prompt: str, user_prompt: str) -> str`
  - Generate using Anthropic Claude
- `generate_openai(self, system_prompt: str, user_prompt: str) -> str`
  - Generate using OpenAI GPT
- `generate_with_retry(self, system_prompt: str, user_prompt: str) -> str`
  - Generate with automatic retry and fallback

### `ModernLLMTrainer`

Modern LLM Trainer (2025)
Primary approach: Few-shot prompting (no training needed!)

**Methods**:

- `__init__(self, config: LLMConfig)`
- `load_examples(self, examples_path: str)`
  - Load training examples (used for few-shot prompting)
- `generate_formula(self, query: str) -> Dict`
  - Generate formula for query using modern LLM approach
- `batch_generate(self, queries: List[str]) -> List[Dict]`
  - Batch generation with rate limiting
- `evaluate(self, test_data: List[Dict]) -> Dict`
  - Evaluate LLM performance
- `_normalize_formula(self, formula: str) -> str`
  - Normalize formula for comparison
- `save_config(self)`
  - Save configuration and examples
- `print_stats(self)`
  - Print performance statistics
