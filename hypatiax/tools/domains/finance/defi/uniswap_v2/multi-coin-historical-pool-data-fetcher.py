from datetime import datetime

import requests

# CoinGecko coin IDs mapping
COINGECKO_IDS = {
    "ETH": "ethereum",
    "DAI": "dai",
    "USDT": "tether",
    "USDC": "usd-coin",
    "BTC": "bitcoin",
    "UNI": "uniswap",
    "LINK": "chainlink",
    "WBTC": "wrapped-bitcoin",
    "SHIB": "shiba-inu",
}


def get_coin_historical_prices(coin_symbol, days=90):
    """Fetch historical price data for any coin from CoinGecko"""

    coin_id = COINGECKO_IDS.get(coin_symbol.upper())

    if not coin_id:
        print(f"❌ Coin '{coin_symbol}' not found!")
        return []

    print(f"📊 Fetching {coin_symbol} prices ({days} days)...")

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        prices = []
        for timestamp, price in data["prices"]:
            prices.append(
                {"timestamp": timestamp, "date": datetime.fromtimestamp(timestamp / 1000), "price_usd": price}
            )

        print(f"✅ Fetched {len(prices)} days of {coin_symbol}")
        return prices

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def get_eth_historical_prices(days=90):
    """Fetch ETH price history (backwards compatible)"""
    return get_coin_historical_prices("ETH", days)


def get_dai_historical_prices(days=90):
    """Fetch DAI price history"""
    return get_coin_historical_prices("DAI", days)


def get_usdt_historical_prices(days=90):
    """Fetch USDT price history"""
    return get_coin_historical_prices("USDT", days)


def get_usdc_historical_prices(days=90):
    """Fetch USDC price history"""
    return get_coin_historical_prices("USDC", days)


def get_btc_historical_prices(days=90):
    """Fetch BTC price history"""
    return get_coin_historical_prices("BTC", days)


def get_multiple_coins_prices(coin_symbols, days=90):
    """Fetch prices for multiple coins"""

    results = {}
    for symbol in coin_symbols:
        prices = get_coin_historical_prices(symbol, days)
        if prices:
            results[symbol] = prices

    return results


# ============================================================
# UNISWAP POOL DATA FUNCTIONS
# ============================================================


def get_uniswap_pool_data(pool_address):
    """Get Uniswap V2 pool data from The Graph"""

    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    query = f"""
    {{
      pair(id: "{pool_address.lower()}") {{
        id
        token0 {{ symbol decimals }}
        token1 {{ symbol decimals }}
        reserve0
        reserve1
        reserveUSD
        volumeUSD
        txCount
      }}
    }}
    """

    try:
        print(f"📊 Fetching pool: {pool_address}")
        response = requests.post(url, json={"query": query}, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            print(f"❌ Error: {data['errors']}")
            return None

        print(f"✅ Pool data fetched")
        return data

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_uniswap_pair_by_symbol(token0, token1, first=1):
    """Get Uniswap pair data by token symbols"""

    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    query = f"""
    {{
      pairs(where: {{token0: "{token0.lower()}", token1: "{token1.lower()}"}}, first: {first}) {{
        id
        token0 {{ symbol decimals }}
        token1 {{ symbol decimals }}
        reserve0
        reserve1
        reserveUSD
        volumeUSD
        txCount
      }}
    }}
    """

    try:
        print(f"📊 Fetching {token0}/{token1} pair...")
        response = requests.post(url, json={"query": query}, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            print(f"❌ Error: {data['errors']}")
            return None

        print(f"✅ Pair data fetched")
        return data

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_multiple_pools_data(pool_addresses):
    """Get data for multiple Uniswap pools"""

    results = {}
    for address in pool_addresses:
        data = get_uniswap_pool_data(address)
        if data:
            results[address] = data

    return results


# ============================================================
# USAGE EXAMPLES
# ============================================================

if __name__ == "__main__":
    print("=" * 80)
    print("MULTI-COIN & UNISWAP DATA FETCHER")
    print("=" * 80)

    # Example 1: Single coin
    print("\n1️⃣  ETH prices")
    eth = get_eth_historical_prices(days=5)
    if eth:
        print(f"Latest: ${eth[-1]['price_usd']:.2f}")

    # Example 2: DAI prices
    print("\n2️⃣  DAI prices")
    dai = get_dai_historical_prices(days=5)
    if dai:
        print(f"Latest: ${dai[-1]['price_usd']:.4f}")

    # Example 3: Multiple coins
    print("\n3️⃣  Multiple coins")
    multi = get_multiple_coins_prices(["ETH", "BTC", "DAI"], days=5)
    for symbol, prices in multi.items():
        if prices:
            print(f"{symbol}: ${prices[-1]['price_usd']:.2f}")

    # Example 4: Pool by address
    print("\n4️⃣  Pool data")
    pool_addr = "0xa478c2975ab1ea89e8196811f51a7b7ade33eb11"
    pool = get_uniswap_pool_data(pool_addr)
    if pool and pool.get("data", {}).get("pair"):
        pair = pool["data"]["pair"]
        print(f"TVL: ${pair['reserveUSD']}")
        print(f"Volume: ${pair['volumeUSD']}")


# ======================================
# USAGE
# ======================================
"""
Key Changes:

Generalized coin function:

python

get_coin_historical_prices('ETH', days=90)
get_coin_historical_prices('DAI', days=90)
get_coin_historical_prices('USDT', days=90)

Backwards compatible convenience functions:

python

get_eth_historical_prices(days=90)  # Works as before
get_dai_historical_prices(days=90)
get_usdt_historical_prices(days=90)

Fetch multiple coins at once:

pythonprices = get_multiple_coins_prices(['ETH', 'DAI', 'BTC'], days=90)

Uniswap pool functions:

python# By address (original)
get_uniswap_pool_data('0xa478...')

# By token symbols (new)
get_uniswap_pair_data('WETH', 'DAI')

# Multiple pools
get_multiple_pools_data([addr1, addr2, addr3])

"""
