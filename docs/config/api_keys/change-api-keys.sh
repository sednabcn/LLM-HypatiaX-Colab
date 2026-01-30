# 7. Check for API Changes (Last Year)
# Check what OpenAI/Anthropic versions you're using
pip show openai anthropic

# Major changes in 2024:
# - OpenAI: Migration to v1.x (breaking changes from v0.x)
# - Anthropic: New Claude 3.5 models, API updates

# Update to latest
pip install --upgrade openai anthropic

# 8. Find API Usage in Your Code

# Search for API calls
rg "openai\.|anthropic\.|OpenAI\(|Anthropic\(" --type py

# Check imports
rg "^import openai|^from openai|^import anthropic|^from anthropic" --type py

# Find model names (to see what you're using)
rg "gpt-|claude-" --type py
