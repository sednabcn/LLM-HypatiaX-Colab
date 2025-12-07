# Option 1: Use Individual Managers (Flexible)

# Use only what you need
from src.data.managers import DEXDataManager, PriceDataManager

# Just prices
prices = PriceDataManager()
eth_prices = prices.get_historical('ethereum', 90)

# Just DEX data
dex = DEXDataManager(protocols=['uniswap_v3', 'sushiswap'])
pool_v3 = dex.get_pool(address, 'uniswap_v3')
pool_sushi = dex.get_pool(address, 'sushiswap')


# Option 2: Use Orchestrator (Convenient)

# Easy for workflows
from src.data.orchestrator import DeFiDataOrchestrator

orchestrator = DeFiDataOrchestrator({
    'dex_protocols': ['uniswap_v2', 'uniswap_v3', 'sushiswap'],
    'rpc_url': 'https://mainnet.infura.io/v3/YOUR_KEY'
})

# High-level workflows
analysis = orchestrator.analyze_pool(pool_address)

✅ Best Practice: Hybrid Approach

# Keep both!

# 1. Individual managers for flexibility
class PriceDataManager: pass
class DEXDataManager: pass
class BlockchainDataManager: pass
class StorageManager: pass

# 2. Orchestrator as convenience facade
class DeFiDataOrchestrator:
    """
    Convenience wrapper for common workflows.
    Advanced users can bypass this and use managers directly.
    """
    def __init__(self, config: Dict = None):
        self.prices = PriceDataManager()
        self.dex = DEXDataManager()
        self.blockchain = BlockchainDataManager()
        self.storage = StorageManager()



🎓 Design Principles Applied

Single Responsibility Principle ✅

Each manager handles ONE domain (prices, DEX, blockchain, storage)


Open/Closed Principle ✅

Add new protocols without modifying existing managers


Dependency Inversion ✅

Managers depend on abstractions (DataSource base class)


Facade Pattern ✅

Orchestrator provides simple interface for complex subsystem


Composition over Inheritance ✅

Managers compose data sources, don't inherit from them




💡 Conclusion: Use Multiple Managers
Yes, it's better to have separate managers! Here's why:
✅ Testability - Mock individual managers easily
✅ Flexibility - Use only what you need
✅ Scalability - Add protocols without bloat
✅ Maintainability - Clear file structure
✅ Reusability - Share managers across projects
Keep the orchestrator for convenience, but don't force users to use it. Let them compose managers as needed.

🔧 Migration Path

Week 1-2: Keep current DeFiDataManager (working MVP)
Week 3-4: Refactor into separate managers
v1.1: Release with both (backward compatible)
v2.0: Deprecate monolithic manager, promote separate managers

This gives users time to migrate without breaking existing code!
