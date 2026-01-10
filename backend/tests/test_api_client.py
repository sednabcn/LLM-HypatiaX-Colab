"""
Python client for testing DeFi Formula API
Save as: test_api_client.py
Run: python test_api_client.py
"""

import json
from typing import Any, Dict

import requests


class DeFiAPIClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method for POST requests"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _get(self, endpoint: str) -> Dict[str, Any]:
        """Helper method for GET requests"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._get("/health")

    def calculate_il_percentage(
        self, initial_price: float, current_price: float
    ) -> Dict[str, Any]:
        """Calculate impermanent loss percentage"""
        return self._post(
            "/defi/il-percentage",
            {"initial_price": initial_price, "current_price": current_price},
        )

    def calculate_quality_score(
        self,
        daily_volume_usd: float,
        position_value: float,
        pool_tvl: float,
        il_dollar: float,
        days_elapsed: int,
        fee_rate: float = 0.003,
    ) -> Dict[str, Any]:
        """Calculate pool quality score"""
        return self._post(
            "/defi/quality-score",
            {
                "daily_volume_usd": daily_volume_usd,
                "fee_rate": fee_rate,
                "position_value": position_value,
                "pool_tvl": pool_tvl,
                "il_dollar": il_dollar,
                "days_elapsed": days_elapsed,
            },
        )

    def analyze_position(
        self,
        initial_token_a: float,
        initial_token_b: float,
        initial_price: float,
        current_price: float,
        days_elapsed: int,
        daily_volume_usd: float,
        pool_tvl_usd: float,
        fee_rate: float = 0.003,
    ) -> Dict[str, Any]:
        """Complete LP position analysis"""
        return self._post(
            "/defi/analyze-position",
            {
                "initial_token_a": initial_token_a,
                "initial_token_b": initial_token_b,
                "initial_price": initial_price,
                "current_price": current_price,
                "days_elapsed": days_elapsed,
                "daily_volume_usd": daily_volume_usd,
                "pool_tvl_usd": pool_tvl_usd,
                "fee_rate": fee_rate,
            },
        )

    def batch_analyze(self, positions: list) -> Dict[str, Any]:
        """Analyze multiple positions"""
        return self._post("/defi/batch-analyze", {"positions": positions})


def print_result(title: str, result: Dict[str, Any]):
    """Pretty print results"""
    print("\n" + "=" * 80)
    print(f"📊 {title}")
    print("=" * 80)
    print(json.dumps(result, indent=2))


def main():
    # Initialize client
    client = DeFiAPIClient()

    print("🚀 Testing DeFi Formula API")
    print("=" * 80)

    # 1. Health Check
    health = client.health_check()
    print_result("Health Check", health)

    # 2. IL Percentage (ETH $2k → $3k)
    il_result = client.calculate_il_percentage(initial_price=2000, current_price=3000)
    print_result("IL Percentage (ETH 50% Increase)", il_result)

    # 3. Quality Score
    quality_result = client.calculate_quality_score(
        daily_volume_usd=500000,
        position_value=5000,
        pool_tvl=10000000,
        il_dollar=-101,
        days_elapsed=30,
    )
    print_result("Quality Score", quality_result)

    # 4. Complete ETH/USDC Analysis
    eth_usdc_result = client.analyze_position(
        initial_token_a=1.0,
        initial_token_b=2000,
        initial_price=2000,
        current_price=3000,
        days_elapsed=30,
        daily_volume_usd=500000,
        pool_tvl_usd=10000000,
    )
    print_result("ETH/USDC Position Analysis", eth_usdc_result)

    # 5. DAI/USDC (Stablecoin) Analysis
    dai_usdc_result = client.analyze_position(
        initial_token_a=5000,
        initial_token_b=5000,
        initial_price=1.0,
        current_price=0.995,
        days_elapsed=60,
        daily_volume_usd=5000000,
        pool_tvl_usd=200000000,
    )
    print_result("DAI/USDC Stablecoin Analysis", dai_usdc_result)

    # 6. Batch Analysis
    batch_positions = [
        {
            "name": "ETH/USDC 50% Up",
            "initial_token_a": 1.0,
            "initial_token_b": 2000,
            "initial_price": 2000,
            "current_price": 3000,
            "days_elapsed": 30,
            "daily_volume_usd": 500000,
            "pool_tvl_usd": 10000000,
        },
        {
            "name": "DAI/USDC Stable",
            "initial_token_a": 5000,
            "initial_token_b": 5000,
            "initial_price": 1.0,
            "current_price": 0.995,
            "days_elapsed": 60,
            "daily_volume_usd": 5000000,
            "pool_tvl_usd": 200000000,
        },
        {
            "name": "ETH/USDC 100% Up (High IL)",
            "initial_token_a": 1.0,
            "initial_token_b": 2000,
            "initial_price": 2000,
            "current_price": 4000,
            "days_elapsed": 60,
            "daily_volume_usd": 1000000,
            "pool_tvl_usd": 50000000,
        },
        {
            "name": "USDC/USDT Ultra-Stable",
            "initial_token_a": 10000,
            "initial_token_b": 10000,
            "initial_price": 1.0,
            "current_price": 1.001,
            "days_elapsed": 90,
            "daily_volume_usd": 50000000,
            "pool_tvl_usd": 500000000,
        },
    ]

    batch_result = client.batch_analyze(batch_positions)
    print_result("Batch Analysis (4 Positions)", batch_result)

    # 7. Summary Report
    if "summary" in batch_result and batch_result["summary"]:
        summary = batch_result["summary"]
        print("\n" + "=" * 80)
        print("📈 SUMMARY REPORT")
        print("=" * 80)
        print(f"Total Positions:      {summary['total_positions']}")
        print(
            f"Profitable:           {summary['profitable_count']}/{summary['successful']}"
        )
        print(
            f"Good Quality:         {summary['good_quality_count']}/{summary['successful']}"
        )
        print(f"Average IL:           {summary['average_il_percent']}%")
        print(f"Average Quality:      {summary['average_quality_score']}")
        print(f"Total Net Result:     ${summary['total_net_result']:,.2f}")
        print("=" * 80)

    print("\n✅ All tests completed!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
