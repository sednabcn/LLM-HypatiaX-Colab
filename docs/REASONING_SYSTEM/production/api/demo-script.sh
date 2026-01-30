# 1. Fast calculation (existing formula)
curl -X POST https://api.hypatiax.com/calculate/fast \
  -d '{"formula_id": "defi_il_basic", "inputs": {"price_ratio": 2.0}}'

# Response in 50ms:
# {"result": -0.0572, "formula": "2√p/(p+1)-1"}

# 2. Discover NEW formula (AI-powered)
curl -X POST https://api.hypatiax.com/discover \
  -d '{
    "description": "Calculate optimal LP fee for high-volatility period",
    "domain": "defi",
    "variable_names": ["volume", "volatility", "liquidity"],
    "variable_descriptions": {...},
    "variable_units": {...}
  }'

# Response in 18 seconds:
# {
#   "expression": "0.003 + 0.002 * sqrt(volatility * volume / liquidity)",
#   "r2_score": 0.94,
#   "validation_score": 87,
#   "interpretation": "Fee should increase with volatility..."
# }

# 3. Register for future fast access
curl -X POST https://api.hypatiax.com/discover-and-register \
  -d '{...same as above...}'

# Response:
# {
#   "formula_id": "defi_custom_abc123",
#   "registered": true,
#   "message": "Formula added to registry. Use /calculate/fast with this ID."
# }

# 4. Now use it fast
curl -X POST https://api.hypatiax.com/calculate/fast \
  -d '{"formula_id": "defi_custom_abc123", "inputs": {...}}'

# Response in 50ms!
