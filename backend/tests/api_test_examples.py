#!/bin/bash
# API Testing Examples for DeFi Formula API

BASE_URL="http://localhost:5000"

echo "=================================="
echo "DeFi Formula API - Test Examples"
echo "=================================="

# 1. Health Check
echo -e "\n1. Health Check:"
curl -X GET "$BASE_URL/health"

# 2. Calculate IL Percentage Only
echo -e "\n\n2. Calculate IL Percentage (ETH $2k → $3k):"
curl -X POST "$BASE_URL/defi/il-percentage" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_price": 2000,
    "current_price": 3000
  }'

# 3. Calculate Quality Score
echo -e "\n\n3. Calculate Quality Score:"
curl -X POST "$BASE_URL/defi/quality-score" \
  -H "Content-Type: application/json" \
  -d '{
    "daily_volume_usd": 500000,
    "fee_rate": 0.003,
    "position_value": 5000,
    "pool_tvl": 10000000,
    "il_dollar": -101,
    "days_elapsed": 30
  }'

# 4. Complete Position Analysis
echo -e "\n\n4. Complete Position Analysis (ETH/USDC):"
curl -X POST "$BASE_URL/defi/analyze-position" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_token_a": 1.0,
    "initial_token_b": 2000,
    "initial_price": 2000,
    "current_price": 3000,
    "days_elapsed": 30,
    "daily_volume_usd": 500000,
    "pool_tvl_usd": 10000000,
    "fee_rate": 0.003
  }'

# 5. DAI/USDC Position (Stablecoin)
echo -e "\n\n5. DAI/USDC Stablecoin Analysis:"
curl -X POST "$BASE_URL/defi/analyze-position" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_token_a": 5000,
    "initial_token_b": 5000,
    "initial_price": 1.0,
    "current_price": 0.995,
    "days_elapsed": 60,
    "daily_volume_usd": 5000000,
    "pool_tvl_usd": 200000000,
    "fee_rate": 0.003
  }'

# 6. Batch Analysis (Multiple Positions)
echo -e "\n\n6. Batch Analysis (3 positions):"
curl -X POST "$BASE_URL/defi/batch-analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "positions": [
      {
        "name": "ETH/USDC 50% Up",
        "initial_token_a": 1.0,
        "initial_token_b": 2000,
        "initial_price": 2000,
        "current_price": 3000,
        "days_elapsed": 30,
        "daily_volume_usd": 500000,
        "pool_tvl_usd": 10000000
      },
      {
        "name": "DAI/USDC Stable",
        "initial_token_a": 5000,
        "initial_token_b": 5000,
        "initial_price": 1.0,
        "current_price": 0.995,
        "days_elapsed": 60,
        "daily_volume_usd": 5000000,
        "pool_tvl_usd": 200000000
      },
      {
        "name": "ETH/USDC 100% Up",
        "initial_token_a": 1.0,
        "initial_token_b": 2000,
        "initial_price": 2000,
        "current_price": 4000,
        "days_elapsed": 60,
        "daily_volume_usd": 1000000,
        "pool_tvl_usd": 50000000
      }
    ]
  }'

echo -e "\n\n=================================="
echo "Tests Complete!"
echo "=================================="
