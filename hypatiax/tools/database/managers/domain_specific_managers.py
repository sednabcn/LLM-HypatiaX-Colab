# ============================================================================
# DOMAIN-SPECIFIC MANAGERS
# ============================================================================

class PriceDataManager:
    """Manages all price-related data sources"""

    def __init__(self):
        self.coingecko = CoinGeckoAPI()
        self.binance = BinanceAPI()  # Future
        self.coinbase = CoinbaseAPI()  # Future

    def get_price(self, symbol: str, source: str = 'coingecko') -> float:
        """Get current price from specified source"""
        if source == 'coingecko':
            return self.coingecko.fetch_data(symbol)
        # ... other sources

    def get_historical(self, symbol: str, days: int = 90,
                      source: str = 'coingecko') -> List[Dict]:
        """Get historical prices"""
        if source == 'coingecko':
            return self.coingecko.get_historical_prices(symbol, days)


class DEXDataManager:
    """Manages all DEX protocol data"""

    def __init__(self, protocols: List[str] = None):
        self.protocols = {}

        if protocols is None:
            protocols = ['uniswap_v2', 'uniswap_v3']

        # Initialize requested protocols
        if 'uniswap_v2' in protocols:
            self.protocols['uniswap_v2'] = TheGraphUniswapV2()
        if 'uniswap_v3' in protocols:
            self.protocols['uniswap_v3'] = TheGraphUniswapV3()
        if 'uniswap_v4' in protocols:
            self.protocols['uniswap_v4'] = TheGraphUniswapV4()
        if 'sushiswap' in protocols:
            self.protocols['sushiswap'] = TheGraphSushiSwap()
        if 'curve' in protocols:
            self.protocols['curve'] = CurveAPI()

    def get_pool(self, address: str, protocol: str = 'uniswap_v3'):
        """Get pool data from specified protocol"""
        if protocol not in self.protocols:
            raise ValueError(f"Protocol {protocol} not initialized")
        return self.protocols[protocol].get_pool_data(address)

    def compare_pools(self, addresses: List[str], protocols: List[str]):
        """Compare same pool across different protocols"""
        results = {}
        for protocol in protocols:
            for address in addresses:
                results[f"{protocol}_{address}"] = self.get_pool(address, protocol)
        return results


class BlockchainDataManager:
    """Manages direct blockchain queries"""

    def __init__(self, rpc_url: str):
        self.rpc = RPCProvider(rpc_url)

    def get_contract_data(self, address: str, abi: str, method: str):
        """Call contract method"""
        # Contract interaction logic
        pass


class StorageManager:
    """Manages data persistence and queries"""

    def __init__(self, db_type: str = 'sqlite'):
        self.db_type = db_type
        self.db = LocalDatabaseManager()
        # Could support PostgreSQL, MongoDB, etc.

    def store(self, table: str, data: Any):
        """Store data to appropriate table"""
        pass

    def query(self, table: str, filters: Dict):
        """Query with filters"""
        pass


# ============================================================================
# ORCHESTRATOR (Facade Pattern)
# ============================================================================

class DeFiDataOrchestrator:
    """
    High-level facade that coordinates all managers
    Users can use this OR use managers directly
    """

    def __init__(self, config: Dict = None):
        config = config or {}

        # Initialize only requested managers
        self.prices = PriceDataManager()
        self.dex = DEXDataManager(protocols=config.get('dex_protocols'))
        self.blockchain = BlockchainDataManager(config.get('rpc_url')) if config.get('rpc_url') else None
        self.storage = StorageManager(config.get('db_type', 'sqlite'))

    def fetch_and_store_prices(self, symbol: str, days: int = 90):
        """Workflow: Fetch prices → Store in DB"""
        prices = self.prices.get_historical(symbol, days)
        self.storage.store('prices', prices)
        return prices

    def analyze_pool(self, address: str, protocol: str = 'uniswap_v3'):
        """Workflow: Fetch pool → Fetch prices → Analyze → Store"""
        # Pool data
        pool = self.dex.get_pool(address, protocol)

        # Token prices
        token0_prices = self.prices.get_historical(pool['token0']['symbol'])
        token1_prices = self.prices.get_historical(pool['token1']['symbol'])

        # Analysis logic
        analysis = {
            'pool': pool,
            'token0_prices': token0_prices,
            'token1_prices': token1_prices,
            # ... more analysis
        }

        # Store results
        self.storage.store('pool_analysis', analysis)

        return analysis
```

---

## 📊 **Comparison: Single vs Multiple Managers**

| Aspect | Single Manager | Multiple Managers |
|--------|----------------|-------------------|
| **Simplicity** | ✅ Easy for beginners | ⚠️ More initial complexity |
| **Testability** | ❌ Hard to test | ✅ Easy to mock/test |
| **Scalability** | ❌ Gets bloated | ✅ Add protocols easily |
| **Reusability** | ❌ All-or-nothing | ✅ Use only what you need |
| **Separation of Concerns** | ❌ Mixed | ✅ Clear boundaries |
| **Maintenance** | ❌ Single large file | ✅ Modular files |

---

## 🎯 **Recommended Architecture**
```
src/data/
├── __init__.py
├── managers/
│   ├── __init__.py
│   ├── price_manager.py      # PriceDataManager
│   ├── dex_manager.py         # DEXDataManager
│   ├── blockchain_manager.py  # BlockchainDataManager
│   └── storage_manager.py     # StorageManager
├── sources/
│   ├── __init__.py
│   ├── coingecko.py          # CoinGeckoAPI
│   ├── the_graph_v2.py       # TheGraphUniswapV2
│   ├── the_graph_v3.py       # TheGraphUniswapV3
│   ├── the_graph_v4.py       # TheGraphUniswapV4
│   └── rpc_provider.py       # RPCProvider
└── orchestrator.py           # DeFiDataOrchestrator (Facade)
