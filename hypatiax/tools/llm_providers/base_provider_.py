from abc import ABC, abstractmethod
from typing import Dict

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate completion from prompt"""
        pass
    
    @abstractmethod
    def batch_generate(self, prompts: list, **kwargs) -> list:
        """Generate completions for multiple prompts"""
        pass
