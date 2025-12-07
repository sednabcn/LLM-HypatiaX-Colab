# In hypatiax/core/training/training_llm.py

import cohere
from config.api_key_manager import APIKeyManager


class ModernLLMTrainer:
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()

        # Get Cohere key
        key_manager = APIKeyManager()
        cohere_key = key_manager.get_api_key("COHERE")

        if cohere_key:
            self.cohere_client = cohere.Client(cohere_key)
            print("✅ Cohere client initialized")
        else:
            print("⚠️ Cohere API key not found")

    def generate_with_cohere(self, prompt: str) -> str:
        """Generate using Cohere"""
        if not hasattr(self, "cohere_client"):
            return "Error: Cohere not configured"

        try:
            response = self.cohere_client.generate(
                prompt=prompt, max_tokens=256, temperature=0.1, model="command"  # or "command-light", "command-nightly"
            )
            return response.generations[0].text
        except Exception as e:
            return f"Error: {e}"
