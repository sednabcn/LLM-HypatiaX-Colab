import requests
import pandas as pd
from datetime import datetime, timedelta

# CoinGecko coin IDs mapping
COINGECKO_IDS = {
    'ETH': 'ethereum',
    'DAI': 'dai',
    'USDT': 'tether',
    'USDC': 'usd-coin',
    'BTC': 'bitcoin',
    'UNI': 'uniswap',
    'LINK': 'chainlink',
    'WBTC': 'wrapped-bitcoin',
    'SHIB': 'shiba-inu',
    'AAVE': 'aave',
    'CURVE': 'curve-dao-token',
    'FRAX': 'frax',
    'LUSD': 'liquity-usd',
    'MIM': 'magic-internet-money',
}

def get_historical_prices(coin_symbol, days=90, vs_currency='usd'):
    """
    Fetch historical price data from CoinGecko for any coin
    
    Args:
        coin_symbol: Coin symbol (e.g., 'ETH', 'DAI', 'USDT')
        days: Number of days of history (default 90)
        vs_currency: Currency to compare against (default 'usd')
    
    Returns:
        DataFrame with columns: ['date', 'price']
    """
    
    # Get CoinGecko ID
    coin_id = COINGECKO_IDS.get(coin_symbol.upper())
    
    if not coin_id:
        print(f"❌ Coin '{coin_symbol}' not found in mapping!")
        print(f"Available coins: {list(COINGECKO_IDS.keys())}")
        return None
    
    print(f"📊 Fetching {coin_symbol} price history ({days} days)...")
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': vs_currency,
        'days': days,
        'interval': 'daily'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract prices
        prices = data['prices']
        
        # Convert to DataFrame
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df[['date', 'price']]
        df['date'] = df['date'].dt.date
        
        print(f"✅ Fetched {len(df)} days of {coin_symbol} price data")
        print(f"   Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {coin_symbol}: {e}")
        return None


def get_multiple_coins_prices(coin_symbols, days=90, vs_currency='usd'):
    """
    Fetch historical prices for multiple coins at once
    
    Args:
        coin_symbols: List of coin symbols (e.g., ['ETH', 'DAI', 'USDT'])
        days: Number of days of history
        vs_currency: Currency to compare against
    
    Returns:
        Dictionary with coin symbol as key, DataFrame as value
    """
    
    results = {}
    
    for symbol in coin_symbols:
        df = get_historical_prices(symbol, days, vs_currency)
        if df is not None:
            results[symbol] = df
    
    return results


def get_pair_prices(token0_symbol, token1_symbol, days=90):
    """
    Fetch prices for a trading pair (e.g., ETH/DAI)
    
    Args:
        token0_symbol: First token (e.g., 'ETH')
        token1_symbol: Second token (e.g., 'DAI')
        days: Number of days
    
    Returns:
        DataFrame with columns: ['date', 'price_token0', 'price_token1', 'pair_price']
    """
    
    print(f"📊 Fetching {token0_symbol}/{token1_symbol} pair prices ({days} days)...")
    
    # Get both prices in USD
    df_token0 = get_historical_prices(token0_symbol, days)
    df_token1 = get_historical_prices(token1_symbol, days)
    
    if df_token0 is None or df_token1 is None:
        return None
    
    # Merge on date
    df_pair = pd.merge(df_token0, df_token1, on='date', suffixes=('_token0', '_token1'))
    
    # Calculate pair price (token0 price in terms of token1)
    df_pair['pair_price'] = df_pair['price_token0'] / df_pair['price_token1']
    
    print(f"✅ Fetched {token0_symbol}/{token1_symbol} pair data")
    
    return df_pair


# ============================================================
# EXAMPLES
# ============================================================

if __name__ == "__main__":
    print("=" * 80)
    print("COINGECKO MULTI-COIN PRICE FETCHER")
    print("=" * 80)
    
    # Example 1: Single coin
    print("\n1️⃣  Fetch single coin (ETH)")
    print("-" * 80)
    eth_prices = get_historical_prices('ETH', days=30)
    if eth_prices is not None:
        print(eth_prices.head(10))
    
    # Example 2: Stablecoin
    print("\n2️⃣  Fetch stablecoin (DAI)")
    print("-" * 80)
    dai_prices = get_historical_prices('DAI', days=30)
    if dai_prices is not None:
        print(dai_prices.head(10))
    
    # Example 3: Multiple coins
    print("\n3️⃣  Fetch multiple coins")
    print("-" * 80)
    coins_to_fetch = ['ETH', 'DAI', 'USDT', 'USDC']
    multi_prices = get_multiple_coins_prices(coins_to_fetch, days=7)
    
    for symbol, df in multi_prices.items():
        print(f"\n{symbol}:")
        print(df.head(3))
    
    # Example 4: Trading pair
    print("\n4️⃣  Fetch trading pair (ETH/DAI)")
    print("-" * 80)
    eth_dai_pair = get_pair_prices('ETH', 'DAI', days=30)
    if eth_dai_pair is not None:
        print(eth_dai_pair.head(10))
        print(f"\nCurrent {eth_dai_pair['pair_price'].iloc[-1]:.2f} DAI per ETH")
    
    # Example 5: Stablecoin pair
    print("\n5️⃣  Fetch stablecoin pair (USDT/USDC)")
    print("-" * 80)
    usdt_usdc_pair = get_pair_prices('USDT', 'USDC', days=30)
    if usdt_usdc_pair is not None:
        print(usdt_usdc_pair.head(10))
        print(f"\nPrice deviation: {usdt_usdc_pair['pair_price'].std():.6f}")
    
    print("\n" + "=" * 80)
    print("Available coins:")
    print(list(COINGECKO_IDS.keys()))
    print("=" * 80)


"""
Key Features:

Single coin fetch:

pythoneth_prices = get_historical_prices('ETH', days=90)
dai_prices = get_historical_prices('DAI', days=90)

Multiple coins at once:

pythonprices = get_multiple_coins_prices(['ETH', 'DAI', 'USDT'], days=90)

Trading pairs:

python# Get ETH price in terms of DAI
eth_dai = get_pair_prices('ETH', 'DAI', days=90)

Add more coins:
Simply add to COINGECKO_IDS dictionary:

pythonCOINGECKO_IDS = {
    'ETH': 'ethereum',
    'DAI': 'dai',
    'USDT': 'tether',
    # Add more...
    'YOUR_COIN': 'coingecko-id',
}
Find CoinGecko IDs:
Go to https://api.coingecko.com/api/v3/coins/list and search for your coin!
Run it and test different coins! 🚀

"""
