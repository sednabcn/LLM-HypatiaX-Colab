4. Get NEW API Keys
OpenAI API:
bash# 1. Go to: https://platform.openai.com/api-keys
# 2. Log in with your account
# 3. Click "Create new secret key"
# 4. Copy and save it (you won't see it again!)

# Test if existing key works:
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"
Anthropic (Claude) API:
bash# 1. Go to: https://console.anthropic.com/settings/keys
# 2. Log in or create account
# 3. Click "Create Key"
# 4. Copy and save it

# Test if existing key works:
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_API_KEY_HERE" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":1024,"messages":[{"role":"us
