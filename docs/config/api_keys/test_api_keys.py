# Create test_api_keys.py
import os
from pathlib import Path


# Try to find and test keys
def test_openai():
    try:
        import openai

        openai.api_key = os.getenv("OPENAI_API_KEY")
        if openai.api_key:
            # Test the key
            client = openai.OpenAI()
            models = client.models.list()
            print("✅ OpenAI API key is valid")
            return True
        else:
            print("❌ No OpenAI API key found")
            return False
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False


def test_anthropic():
    try:
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            client = anthropic.Anthropic(api_key=api_key)
            # Simple test
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            print("✅ Anthropic API key is valid")
            return True
        else:
            print("❌ No Anthropic API key found")
            return False
    except Exception as e:
        print(f"❌ Anthropic API error: {e}")
        return False


if __name__ == "__main__":
    print("Testing API Keys...\n")
    test_openai()
    test_anthropic()
