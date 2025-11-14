"""Base LLM provider interface"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate with tool/function calling"""
        pass
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Chat completion"""
        pass
    
    def set_config(self, **kwargs):
        """Update configuration"""
        self.config.update(kwargs)
