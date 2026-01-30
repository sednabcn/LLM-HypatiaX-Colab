# 1. Find Existing API Keys in Your Code

cd ~/Downloads/LLM-HypatiaX-OLD

# Search for API key references
rg -i "api_key|api-key|openai|anthropic|claude" --type py

# Check environment files
cat .env 2>/dev/null
cat .env.local 2>/dev/null
cat .env.example 2>/dev/null

# Check config files
find . -name "config*.py" -o -name "config*.json" -o -name "settings*.py" | xargs cat

# Check for credentials files
find . -name "*credentials*" -o -name "*secrets*" -o -name "*token*"
