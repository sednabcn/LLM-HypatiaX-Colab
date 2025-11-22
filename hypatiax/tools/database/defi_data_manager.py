"""
DeFi Data Manager - Comprehensive Database & Query Pattern System
Supports: CoinGecko, The Graph, RPC Providers, Local DB Storage
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
from abc import ABC, abstractmethod


# ============================================================================
# BASE DATA SOURCE CLASS (Abstract)
# ============================================================================

class DataSource(ABC):
    """Abstract base class for all data sources"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_request_time = None
        self.request_count = 0
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> Dict:
        """Fetch data from source - must be implemented by subclasses"""
        pass
    
    def _log_request(self):
        """Track API requests"""
        self.request_count += 1
        self.last_request_time = datetime.now()
        print(f"[{self.name}] Request #{self.request_count} at {self.last_request_time}")


# ============================================================================
# 1. COINGECKO API - PRICE DATA
# ============================================================================

class CoinGeckoAPI(DataSource):
    """
    CoinGecko API - Free historical and current price data
    Docs: https://www.coingecko.com/en/api/documentation
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        super().__init__("CoinGecko")
    
    def fetch_data(self, coin_id: str = "ethereum", **kwargs) -> Dict:
        """Fetch current price data"""
        endpoint = f"{self.BASE_URL}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }
        
        self._log_request()
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_historical_prices(self, coin_id: str = "ethereum", 
                            days: int = 90, interval: str = "daily") -> List[Dict]:
        """
        Fetch historical price data
        
        Args:
            coin_id: Coin identifier (e.g., 'ethereum', 'bitcoin')
            days: Number of days (1, 7, 14, 30, 90, 180, 365, max)
            interval: 'daily' or 'hourly'
        """
        endpoint = f"{self.BASE_URL}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': interval
        }
        
        self._log_request()
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Transform to structured format
        prices = []
        for timestamp, price in data.get('prices', []):
            prices.append({
                'timestamp': timestamp,
                'date': datetime.fromtimestamp(timestamp / 1000),
                'price_usd': price,
                'coin_id': coin_id
            })
        
        return prices
    
    def get_market_data(self, coin_id: str = "ethereum") -> Dict:
        """Get comprehensive market data for a coin"""
        endpoint = f"{self.BASE_URL}/coins/{coin_id}"
        params = {
            'localization': 'false',
            'tickers': 'false',
            'community_data': 'false',
            'developer_data': 'false'
        }
        
        self._log_request()
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()


# ============================================================================
# 2. THE GRAPH - UNISWAP V2 GRAPHQL QUERIES
# ============================================================================

class TheGraphUniswapV2(DataSource):
    """
    The Graph - Uniswap V2 Subgraph
    Query indexed blockchain data using GraphQL
    Docs: https://thegraph.com/hosted-service/subgraph/uniswap/uniswap-v2
    """
    
    SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    
    def __init__(self):
        super().__init__("The Graph - Uniswap V2")
    
    def fetch_data(self, query: str) -> Dict:
        """Execute GraphQL query"""
        self._log_request()
        response = requests.post(self.SUBGRAPH_URL, json={'query': query})
        response.raise_for_status()
        return response.json()
    
    def get_pool_data(self, pool_address: str) -> Dict:
        """
        Get detailed data for a specific liquidity pool
        
        Args:
            pool_address: Ethereum address of the pool (e.g., ETH/USDC pair)
        """
        query = f"""
        {{
          pair(id: "{pool_address.lower()}") {{
            id
            token0 {{
              id
              symbol
              name
              decimals
            }}
            token1 {{
              id
              symbol
              name
              decimals
            }}
            reserve0
            reserve1
            reserveUSD
            volumeUSD
            token0Price
            token1Price
            txCount
            createdAtTimestamp
            liquidityProviderCount
          }}
        }}
        """
        return self.fetch_data(query)
    
    def get_top_pools(self, limit: int = 10, min_liquidity: float = 1000000) -> Dict:
        """
        Get top liquidity pools by TVL
        
        Args:
            limit: Number of pools to return
            min_liquidity: Minimum liquidity in USD
        """
        query = f"""
        {{
          pairs(
            first: {limit}
            orderBy: reserveUSD
            orderDirection: desc
            where: {{ reserveUSD_gt: "{min_liquidity}" }}
          ) {{
            id
            token0 {{ symbol }}
            token1 {{ symbol }}
            reserveUSD
            volumeUSD
            token0Price
            token1Price
            txCount
          }}
        }}
        """
        return self.fetch_data(query)
    
    def get_pool_daily_data(self, pool_address: str, days: int = 7) -> Dict:
        """
        Get daily historical data for a pool
        
        Args:
            pool_address: Pool address
            days: Number of days to fetch
        """
        timestamp_start = int((datetime.now() - timedelta(days=days)).timestamp())
        
        query = f"""
        {{
          pairDayDatas(
            first: {days}
            orderBy: date
            orderDirection: desc
            where: {{ pairAddress: "{pool_address.lower()}", date_gt: {timestamp_start} }}
          ) {{
            date
            dailyVolumeUSD
            reserveUSD
            totalSupply
            dailyTxns
          }}
        }}
        """
        return self.fetch_data(query)
    
    def search_pools_by_token(self, token_symbol: str, limit: int = 5) -> Dict:
        """
        Search for pools containing a specific token
        
        Args:
            token_symbol: Token symbol (e.g., 'ETH', 'USDC', 'DAI')
        """
        query = f"""
        {{
          pairs(
            first: {limit}
            orderBy: reserveUSD
            orderDirection: desc
            where: {{
              or: [
                {{ token0_: {{ symbol_contains: "{token_symbol}" }} }}
                {{ token1_: {{ symbol_contains: "{token_symbol}" }} }}
              ]
            }}
          ) {{
            id
            token0 {{ symbol name }}
            token1 {{ symbol name }}
            reserveUSD
            volumeUSD
          }}
        }}
        """
        return self.fetch_data(query)


# ============================================================================
# 3. RPC PROVIDER - DIRECT BLOCKCHAIN QUERIES
# ============================================================================

class RPCProvider(DataSource):
    """
    RPC Provider - Direct blockchain queries
    Supports: Infura, Alchemy, QuickNode, or any Ethereum RPC endpoint
    """
    
    def __init__(self, rpc_url: str, provider_name: str = "RPC"):
        super().__init__(provider_name)
        self.rpc_url = rpc_url
    
    def fetch_data(self, method: str, params: List = None) -> Dict:
        """
        Make RPC call to Ethereum node
        
        Args:
            method: JSON-RPC method (e.g., 'eth_blockNumber', 'eth_call')
            params: Method parameters
        """
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        self._log_request()
        response = requests.post(self.rpc_url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_block_number(self) -> int:
        """Get latest block number"""
        result = self.fetch_data("eth_blockNumber")
        return int(result['result'], 16)
    
    def get_balance(self, address: str) -> float:
        """Get ETH balance of address"""
        result = self.fetch_data("eth_getBalance", [address, "latest"])
        balance_wei = int(result['result'], 16)
        return balance_wei / 1e18  # Convert Wei to ETH
    
    def call_contract(self, contract_address: str, data: str) -> str:
        """
        Call smart contract function (read-only)
        
        Args:
            contract_address: Contract address
            data: Encoded function call data
        """
        result = self.fetch_data("eth_call", [
            {"to": contract_address, "data": data},
            "latest"
        ])
        return result['result']


# ============================================================================
# 4. LOCAL DATABASE STORAGE (SQL Pattern)
# ============================================================================

class LocalDatabaseManager:
    """
    Local database manager for storing fetched data
    Simulates PostgreSQL/SQLite patterns
    """
    
    def __init__(self, db_name: str = "defi_data.db"):
        self.db_name = db_name
        self.tables = {
            'prices': [],
            'pools': [],
            'transactions': []
        }
        print(f"[LocalDB] Initialized: {db_name}")
    
    def insert_price_data(self, data: List[Dict]):
        """INSERT INTO prices"""
        self.tables['prices'].extend(data)
        print(f"[LocalDB] Inserted {len(data)} price records")
    
    def insert_pool_data(self, data: Dict):
        """INSERT INTO pools"""
        self.tables['pools'].append(data)
        print(f"[LocalDB] Inserted pool record: {data.get('id', 'unknown')}")
    
    def query_prices(self, coin_id: str = None, start_date: datetime = None) -> pd.DataFrame:
        """
        SELECT * FROM prices WHERE coin_id = ? AND date >= ?
        
        Simulates SQL query pattern
        """
        df = pd.DataFrame(self.tables['prices'])
        
        if df.empty:
            return df
        
        # Apply filters
        if coin_id:
            df = df[df['coin_id'] == coin_id]
        
        if start_date:
            df = df[df['date'] >= start_date]
        
        print(f"[LocalDB] Query returned {len(df)} rows")
        return df
    
    def query_pools(self, min_tvl: float = None) -> pd.DataFrame:
        """
        SELECT * FROM pools WHERE tvl > ?
        """
        df = pd.DataFrame(self.tables['pools'])
        
        if df.empty:
            return df
        
        if min_tvl and 'reserveUSD' in df.columns:
            df = df[pd.to_numeric(df['reserveUSD'], errors='coerce') > min_tvl]
        
        print(f"[LocalDB] Query returned {len(df)} pools")
        return df
    
    def export_to_excel(self, filename: str):
        """Export all tables to Excel workbook"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for table_name, data in self.tables.items():
                if data:
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=table_name, index=False)
                    print(f"[LocalDB] Exported {table_name} to {filename}")
        
        print(f"✅ Excel workbook saved: {filename}")


# ============================================================================
# 5. UNIFIED DATA MANAGER - ORCHESTRATES ALL SOURCES
# ============================================================================

class DeFiDataManager:
    """
    Master class that orchestrates all data sources
    Use this as your main interface
    """
    
    def __init__(self, rpc_url: Optional[str] = None):
        self.coingecko = CoinGeckoAPI()
        self.the_graph = TheGraphUniswapV2()
        self.rpc = RPCProvider(rpc_url, "Infura/Alchemy") if rpc_url else None
        self.db = LocalDatabaseManager()
        
        print("="*60)
        print("🚀 DeFi Data Manager Initialized")
        print("="*60)
        print("Available sources:")
        print("  ✅ CoinGecko API (Price data)")
        print("  ✅ The Graph (Uniswap V2)")
        print(f"  {'✅' if self.rpc else '❌'} RPC Provider (Blockchain)")
        print("  ✅ Local Database (Storage)")
        print("="*60)
    
    def fetch_and_store_prices(self, coin_id: str = "ethereum", days: int = 90):
        """
        Complete workflow: Fetch from CoinGecko → Store in local DB
        """
        print(f"\n📊 Fetching {days} days of {coin_id} prices...")
        
        # Fetch from API
        prices = self.coingecko.get_historical_prices(coin_id, days)
        
        # Store in database
        self.db.insert_price_data(prices)
        
        print(f"✅ Stored {len(prices)} price records")
        return prices
    
    def fetch_and_store_pool(self, pool_address: str):
        """
        Complete workflow: Fetch from The Graph → Store in local DB
        """
        print(f"\n🏊 Fetching pool data for {pool_address}...")
        
        # Fetch from The Graph
        result = self.the_graph.get_pool_data(pool_address)
        pool_data = result.get('data', {}).get('pair')
        
        if pool_data:
            # Store in database
            self.db.insert_pool_data(pool_data)
            print(f"✅ Stored pool: {pool_data['token0']['symbol']}/{pool_data['token1']['symbol']}")
            return pool_data
        else:
            print("❌ Pool not found")
            return None
    
    def analyze_pool_with_prices(self, pool_address: str, coin_id: str = "ethereum", days: int = 90):
        """
        Complete workflow: Fetch pool + prices → Analyze → Export
        """
        print(f"\n🔍 Complete Analysis: Pool + Price Data")
        print("-"*60)
        
        # 1. Fetch pool data
        pool_data = self.fetch_and_store_pool(pool_address)
        
        # 2. Fetch historical prices
        prices = self.fetch_and_store_prices(coin_id, days)
        
        # 3. Query from local DB
        price_df = self.db.query_prices(coin_id)
        
        # 4. Create analysis summary
        if not price_df.empty:
            summary = {
                'pool_address': pool_address,
                'tokens': f"{pool_data['token0']['symbol']}/{pool_data['token1']['symbol']}" if pool_data else "Unknown",
                'tvl_usd': float(pool_data['reserveUSD']) if pool_data else 0,
                'avg_price': price_df['price_usd'].mean(),
                'min_price': price_df['price_usd'].min(),
                'max_price': price_df['price_usd'].max(),
                'price_volatility': price_df['price_usd'].std(),
                'data_points': len(price_df)
            }
            
            print("\n📈 Analysis Summary:")
            for key, value in summary.items():
                print(f"  {key}: {value}")
            
            return summary
        
        return None
    
    def export_all_data(self, filename: str = None):
        """Export all collected data to Excel"""
        if filename is None:
            filename = f"defi_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        self.db.export_to_excel(filename)
        return filename


# ============================================================================
# 6. EXAMPLE USAGE & QUERY PATTERNS
# ============================================================================

def example_usage():
    """
    Demonstration of all query patterns
    """
    
    print("\n" + "="*60)
    print("📚 DeFi Data Manager - Example Usage")
    print("="*60)
    
    # Initialize manager
    manager = DeFiDataManager()
    
    # ===== PATTERN 1: CoinGecko API =====
    print("\n1️⃣ COINGECKO - Fetch ETH prices")
    print("-"*60)
    
    prices = manager.fetch_and_store_prices("ethereum", days=30)
    print(f"Sample: {prices[0]}")
    
    # ===== PATTERN 2: The Graph GraphQL =====
    print("\n2️⃣ THE GRAPH - Query Uniswap pools")
    print("-"*60)
    
    # ETH/USDC pool on Uniswap V2
    eth_usdc_pool = "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc"
    pool = manager.fetch_and_store_pool(eth_usdc_pool)
    
    # Query top pools
    print("\nTop 5 pools by TVL:")
    top_pools = manager.the_graph.get_top_pools(limit=5)
    for pool in top_pools.get('data', {}).get('pairs', []):
        print(f"  {pool['token0']['symbol']}/{pool['token1']['symbol']}: ${float(pool['reserveUSD']):,.0f}")
    
    # ===== PATTERN 3: Local Database Queries =====
    print("\n3️⃣ LOCAL DATABASE - SQL-style queries")
    print("-"*60)
    
    # Query stored prices
    recent_prices = manager.db.query_prices(
        coin_id="ethereum",
        start_date=datetime.now() - timedelta(days=7)
    )
    print(f"Prices from last 7 days: {len(recent_prices)} records")
    
    # Query stored pools
    high_tvl_pools = manager.db.query_pools(min_tvl=1000000)
    print(f"Pools with TVL > $1M: {len(high_tvl_pools)} pools")
    
    # ===== PATTERN 4: Complete Analysis Workflow =====
    print("\n4️⃣ COMPLETE WORKFLOW - Fetch, Store, Analyze, Export")
    print("-"*60)
    
    analysis = manager.analyze_pool_with_prices(
        pool_address=eth_usdc_pool,
        coin_id="ethereum",
        days=90
    )
    
    # ===== PATTERN 5: Export to Excel =====
    print("\n5️⃣ EXPORT - Save to Excel workbook")
    print("-"*60)
    
    excel_file = manager.export_all_data()
    print(f"\n🎉 All data exported to: {excel_file}")
    
    return manager


# ============================================================================
# RUN EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Run complete example
    manager = example_usage()
    
    print("\n" + "="*60)
    print("✅ DeFi Data Manager Demo Complete!")
    print("="*60)
    print("\nYou can now:")
    print("  • Query historical prices")
    print("  • Analyze Uniswap pools")
    print("  • Store data locally")
    print("  • Export to Excel")
    print("  • Apply DeFi formulas to real data")
    print("="*60)
