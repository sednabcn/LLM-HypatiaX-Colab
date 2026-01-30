# Day 2 Deliverable: Live API at <https://api.yourcompany.com> with auth

# api/auth.py

from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

security = HTTPBearer()

# Simple API key check (upgrade to JWT later)

VALID_KEYS = {
    "test_key_123": {"user": "demo", "tier": "free", "limit": 100},
    # Load from database in production
}

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API key."""
    api_key = credentials.credentials

    if api_key not in VALID_KEYS:
        raise HTTPException(401, "Invalid API key")

    return VALID_KEYS[api_key]

# Add to endpoints

@app.post("/defi/impermanent-loss")
async def calculate_il(req: ILRequest, user=Depends(verify_api_key)):
    # Check rate limit
    if not check_rate_limit(user):
        raise HTTPException(429, "Rate limit exceeded")
    # ... rest of code
