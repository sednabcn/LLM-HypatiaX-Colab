# 2. Check Environment Variables
# See if keys are set in your current environment
env | grep -i "api\|key\|openai\|anthropic\|claude"

# Check shell config files
grep -i "api_key\|openai\|anthropic" ~/.bashrc ~/.zshrc ~/.profile 2>/dev/null
