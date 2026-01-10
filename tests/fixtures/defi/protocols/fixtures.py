"""DeFi protocol fixtures"""

import pytest


@pytest.fixture
def defi_protocols():
    """Sample DeFi protocol data"""
    return {
        "uniswap_v3": {
            "name": "Uniswap V3",
            "tvl": 3_500_000_000,
            "volume_24h": 1_200_000_000,
            "apy": 0.15,
            "type": "dex",
        },
        "aave_v3": {
            "name": "Aave V3",
            "tvl": 5_800_000_000,
            "volume_24h": 450_000_000,
            "apy": 0.03,
            "type": "lending",
        },
        "curve": {
            "name": "Curve Finance",
            "tvl": 4_200_000_000,
            "volume_24h": 800_000_000,
            "apy": 0.08,
            "type": "dex",
        },
    }


@pytest.fixture
def liquidity_pool_data():
    """Sample liquidity pool data"""
    return {
        "pool_id": "ETH-USDC-0.3",
        "token0": {"symbol": "ETH", "amount": 1000, "price": 2500},
        "token1": {"symbol": "USDC", "amount": 2_500_000, "price": 1},
        "fee_tier": 0.003,
        "tvl": 5_000_000,
        "volume_24h": 10_000_000,
    }
