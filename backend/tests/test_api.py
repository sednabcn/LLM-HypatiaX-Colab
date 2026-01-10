"""
API Endpoint Tester
Test all endpoints of the Unified Formula API
File: backend/test_api.py
"""

import json
from datetime import datetime

import requests

BASE_URL = "http://localhost:5000"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Testing: {method} {endpoint}")
    if description:
        print(f"   {description}")

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(
                url, json=data, headers={"Content-Type": "application/json"}
            )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print("   ✅ SUCCESS")
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)[:500]}...")
        else:
            print(f"   ❌ FAILED")
            print(f"   Error: {response.text}")

        return response

    except requests.exceptions.ConnectionError:
        print("   ❌ CONNECTION FAILED - Is the server running?")
        return None
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return None


def main():
    print("\n" + "🚀" * 40)
    print("  UNIFIED FORMULA API - ENDPOINT TESTER")
    print("🚀" * 40)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ========================================================================
    # ROOT & HEALTH ENDPOINTS
    # ========================================================================
    print_section("1. ROOT & HEALTH ENDPOINTS")

    test_endpoint("GET", "/", description="API documentation")
    test_endpoint("GET", "/api/health", description="Health check")

    # ========================================================================
    # HYPATIAX ENDPOINTS
    # ========================================================================
    print_section("2. HYPATIAX ENDPOINTS (Tableau Formula Mapping)")

    # Test single mapping
    test_endpoint(
        "POST",
        "/api/hypatiax/map",
        data={"description": "Calculate the total of Sales", "method": "vocab"},
        description="Map natural language to Tableau formula",
    )

    # Test with different queries
    test_endpoint(
        "POST",
        "/api/hypatiax/map",
        data={"description": "Average of Profit", "method": "vocab"},
        description="Test average operation",
    )

    test_endpoint(
        "POST",
        "/api/hypatiax/map",
        data={"description": "Count of Orders", "method": "vocab"},
        description="Test count operation",
    )

    # Test batch processing
    test_endpoint(
        "POST",
        "/api/hypatiax/batch",
        data={
            "descriptions": [
                "Sum of Sales",
                "Average of Profit",
                "Maximum of Price",
                "Minimum of Discount",
            ],
            "method": "vocab",
        },
        description="Batch process multiple descriptions",
    )

    # Test endpoint
    test_endpoint("GET", "/api/hypatiax/test", description="Run predefined test cases")

    # ========================================================================
    # NER ENDPOINTS
    # ========================================================================
    print_section("3. NER ENDPOINTS (Formula Extraction)")

    test_endpoint("GET", "/api/ner/health", description="NER service health check")

    test_endpoint(
        "POST",
        "/api/ner/extract-formula",
        data={
            "text": "The impermanent loss formula is IL = 2*sqrt(price_ratio)/(price_ratio+1) - 1",
            "domain": "defi",
            "extract_variables": True,
        },
        description="Extract mathematical formulas from text",
    )

    test_endpoint(
        "POST",
        "/api/ner/recognize-entities",
        data={
            "text": "Calculate daily fees using volume V and fee rate f",
            "entity_types": ["variable", "constant", "operator"],
        },
        description="Recognize mathematical entities",
    )

    test_endpoint(
        "POST",
        "/api/ner/convert-to-latex",
        data={"expression": "IL = 2*sqrt(r)/(r+1) - 1", "style": "inline"},
        description="Convert expression to LaTeX",
    )

    test_endpoint(
        "POST",
        "/api/ner/identify-domain",
        data={"text": "Calculate impermanent loss using price ratio"},
        description="Identify mathematical domain",
    )

    test_endpoint(
        "POST",
        "/api/ner/validate-syntax",
        data={"expression": "2 * sqrt(r) / (r + 1)", "strict": True},
        description="Validate expression syntax",
    )

    # ========================================================================
    # DEFI ENDPOINTS
    # ========================================================================
    print_section("4. DEFI ENDPOINTS (DeFi Analytics)")

    test_endpoint("GET", "/api/defi/health", description="DeFi service health check")

    test_endpoint(
        "POST",
        "/api/defi/calculate-il",
        data={"initial_price": 2000.0, "current_price": 2500.0},
        description="Calculate impermanent loss percentage",
    )

    test_endpoint(
        "POST",
        "/api/defi/calculate-quality-score",
        data={
            "daily_volume_usd": 1000000.0,
            "fee_rate": 0.003,
            "position_value": 10000.0,
            "pool_tvl": 5000000.0,
            "il_dollar": -150.0,
            "days_elapsed": 30,
        },
        description="Calculate pool quality score",
    )

    test_endpoint(
        "POST",
        "/api/defi/analyze-position",
        data={
            "initial_token_a": 1.0,
            "initial_token_b": 2000.0,
            "initial_price": 2000.0,
            "current_price": 2500.0,
            "days_elapsed": 30,
            "daily_volume": 1000000.0,
            "pool_tvl": 5000000.0,
            "fee_rate": 0.003,
        },
        description="Complete LP position analysis",
    )

    # ========================================================================
    # ERROR HANDLING
    # ========================================================================
    print_section("5. ERROR HANDLING TESTS")

    test_endpoint("GET", "/api/nonexistent", description="Test 404 handler")

    test_endpoint(
        "POST", "/api/hypatiax/map", data={}, description="Test missing required fields"
    )

    test_endpoint(
        "POST",
        "/api/defi/calculate-il",
        data={"initial_price": "invalid"},
        description="Test invalid data types",
    )

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_section("TESTING COMPLETE")
    print("\n✅ All endpoint tests completed!")
    print("\n💡 Next steps:")
    print("   1. Check server logs for any warnings")
    print("   2. Verify all services loaded correctly")
    print("   3. Test with your frontend application")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
