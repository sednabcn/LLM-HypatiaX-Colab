---
"""LLM provider configurations"""

import os
from typing import Optional


class LLMConfig:
    """Configuration for LLM providers"""

    # API Keys (should be in .env)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")

    # Default models
    OPENAI_MODEL = "gpt-4-turbo-preview"
    ANTHROPIC_MODEL = "claude-3-opus-20240229"
    DEEPSEEK_MODEL = "deepseek-math-7b-instruct"

    # Generation parameters
    TEMPERATURE = 0.0  # Deterministic for math
    MAX_TOKENS = 2000

    # Paths
    LLM_PROMPTS_DIR = "models/queries/tableau/llm/prompt_templates"
    LLM_EXAMPLES_DIR = "models/queries/tableau/llm/few_shot_examples"

    @classmethod
    def get_provider_config(cls, provider: str = "openai"):
        """Get configuration for specific provider"""
        configs = {
            "openai": {
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.OPENAI_MODEL,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS,
            },
            "anthropic": {
                "api_key": cls.ANTHROPIC_API_KEY,
                "model": cls.ANTHROPIC_MODEL,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS,
            },
            "deepseek": {
                "api_key": cls.DEEPSEEK_API_KEY,
                "model": cls.DEEPSEEK_MODEL,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS,
            },
        }
        return configs.get(provider, configs["openai"])
