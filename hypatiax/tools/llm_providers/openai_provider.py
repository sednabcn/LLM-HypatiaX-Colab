"""OpenAI provider implementation"""

from typing import Any, Dict, List

from .base_provider import BaseLLMProvider

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", **kwargs):
        super().__init__(api_key, **kwargs)
        if OpenAI is None:
            raise ImportError(
                "openai package not installed. Install: pip install openai"
            )
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.0),
            max_tokens=kwargs.get("max_tokens", 2000),
        )
        return response.choices[0].message.content

    def generate_with_tools(
        self, prompt: str, tools: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """Generate with tool calling"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
            temperature=kwargs.get("temperature", 0.0),
            max_tokens=kwargs.get("max_tokens", 2000),
        )

        message = response.choices[0].message
        return {
            "content": message.content,
            "tool_calls": (
                message.tool_calls if hasattr(message, "tool_calls") else None
            ),
        }

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.0),
            max_tokens=kwargs.get("max_tokens", 2000),
        )
        return response.choices[0].message.content
