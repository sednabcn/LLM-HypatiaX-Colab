#!/usr/bin/env python3
import os
import sys

print("🔍 Checking LLM API Setup...\n")

# Check environment variables
keys = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
}

for name, value in keys.items():
    if value:
        masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
        print(f"✅ {name}: {masked}")
    else:
        print(f"❌ {name}: Not set")

print("\n📦 Checking installed packages...\n")

try:
    import openai
    print(f"✅ openai: {openai.__version__}")
except ImportError:
    print("❌ openai: Not installed")

try:
    import anthropic
    print(f"✅ anthropic: {anthropic.__version__}")
except ImportError:
    print("❌ anthropic: Not installed")

print("\n💡 To get API keys:")
print("   OpenAI:    https://platform.openai.com/api-keys")
print("   Anthropic: https://console.anthropic.com/settings/keys")
