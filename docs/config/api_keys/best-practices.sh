10. Security Best Practices

# Never commit API keys to git
git log -p | grep -i "sk-" && echo "⚠️  WARNING: Keys might be in git history!"

# Check if keys are exposed
rg "sk-[a-zA-Z0-9]{20,}" . --type py

# Use environment variables or secret managers
# Add to .bashrc/.zshrc:
echo 'export OPENAI_API_KEY="your-key"' >> ~/.bashrc

Start here:
bashcd ~/Downloads/LLM-HypatiaX-OLD
rg -i "openai|anthropic|api_key" --type py | head -20
cat .env 2>/dev/null || echo "No .env file found"
This will show you if and how the project uses LLM APIs.
