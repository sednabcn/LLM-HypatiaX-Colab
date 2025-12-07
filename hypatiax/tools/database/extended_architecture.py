CLAUDE: FEEDBACK@MODELPHYSMAT.COM

# ============================================================================
# THE GRAPH - UNISWAP V3 GRAPHQL QUERIES
# ============================================================================

class TheGraphUniswapV3(DataSource):
    """
    The Graph - Uniswap V3 Subgraph
    Docs: https://thegraph.com/explorer/subgraphs/5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV
    """

    SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

    def __init__(self):
        super().__init__("The Graph - Uniswap V3")

    def fetch_data(self, query: str) -> Dict:
        """Execute GraphQL query"""
        self._log_request()
        response = requests.post(self.SUBGRAPH_URL, json={'query': query})
        response.raise_for_status()
        return response.json()

    def get_pool_data(self, pool_address: str) -> Dict:
        """
        Get V3 pool data with concentrated liquidity details

        Key V3 differences:
        - Concentrated liquidity (tick ranges)
        - Multiple fee tiers (0.01%, 0.05%, 0.3%, 1%)
        - sqrtPriceX96 instead of simple price
        """
        query = f"""
        {{
          pool(id: "{pool_address.lower()}") {{
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
            feeTier
            sqrtPrice
            tick
            liquidity
            token0Price
            token1Price
            volumeUSD
            txCount
            totalValueLockedUSD
            totalValueLockedToken0
            totalValueLockedToken1
            createdAtTimestamp
          }}
        }}
        """
        return self.fetch_data(query)

    def get_pool_ticks(self, pool_address: str, skip: int = 0) -> Dict:
        """
        Get tick data for concentrated liquidity positions
        V3-specific feature
        """
        query = f"""
        {{
          ticks(
            first: 100
            skip: {skip}
            where: {{ poolAddress: "{pool_address.lower()}" }}
            orderBy: tickIdx
            orderDirection: asc
          ) {{
            tickIdx
            liquidityGross
            liquidityNet
            price0
            price1
          }}
        }}
        """
        return self.fetch_data(query)

    def get_positions(self, pool_address: str, limit: int = 10) -> Dict:
        """
        Get liquidity provider positions
        V3-specific: Shows tick ranges and liquidity amounts
        """
        query = f"""
        {{
          positions(
            first: {limit}
            where: {{ pool: "{pool_address.lower()}" }}
            orderBy: liquidity
            orderDirection: desc
          ) {{
            id
            owner
            liquidity
            tickLower {{ tickIdx }}
            tickUpper {{ tickIdx }}
            depositedToken0
            depositedToken1
          }}
        }}
        """
        return self.fetch_data(query)

    def get_top_pools_by_fee_tier(self, fee_tier: int = 3000, limit: int = 10) -> Dict:
        """
        Get top pools filtered by fee tier
        V3 fee tiers: 100 (0.01%), 500 (0.05%), 3000 (0.3%), 10000 (1%)

        Args:
            fee_tier: Fee tier (100, 500, 3000, or 10000)
            limit: Number of pools
        """
        query = f"""
        {{
          pools(
            first: {limit}
            orderBy: totalValueLockedUSD
            orderDirection: desc
            where: {{ feeTier: "{fee_tier}" }}
          ) {{
            id
            token0 {{ symbol }}
            token1 {{ symbol }}
            feeTier
            totalValueLockedUSD
            volumeUSD
            token0Price
            token1Price
          }}
        }}
        """
        return self.fetch_data(query)


# ============================================================================
# THE GRAPH - UNISWAP V4 (HOOKS SYSTEM)
# ============================================================================

class TheGraphUniswapV4(DataSource):
    """
    The Graph - Uniswap V4 Subgraph
    V4 Features: Hooks, Custom Pools, Singleton Contract
    Note: V4 launched in 2024, subgraph may still be in development
    """

    # V4 subgraph URL (update when available)
    SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v4"

    def __init__(self):
        super().__init__("The Graph - Uniswap V4")

    def fetch_data(self, query: str) -> Dict:
        """Execute GraphQL query"""
        self._log_request()
        response = requests.post(self.SUBGRAPH_URL, json={'query': query})
        response.raise_for_status()
        return response.json()

    def get_pool_data(self, pool_key: str) -> Dict:
        """
        Get V4 pool data

        V4 Key Changes:
        - PoolKey instead of address (currency0, currency1, fee, tickSpacing, hooks)
        - Hooks contract address
        - Singleton architecture
        """
        query = f"""
        {{
          pool(id: "{pool_key.lower()}") {{
            id
            poolKey {{
              currency0
              currency1
              fee
              tickSpacing
              hooks
            }}
            liquidity
            sqrtPriceX96
            tick
            volumeUSD
            totalValueLockedUSD
            txCount
          }}
        }}
        """
        return self.fetch_data(query)

    def get_pools_with_hooks(self, limit: int = 10) -> Dict:
        """
        Get pools that use hooks
        V4-specific: Hooks allow custom logic
        """
        query = f"""
        {{
          pools(
            first: {limit}
            where: {{ hooks_not: "0x0000000000000000000000000000000000000000" }}
            orderBy: totalValueLockedUSD
            orderDirection: desc
          ) {{
            id
            poolKey {{
              currency0 {{ symbol }}
              currency1 {{ symbol }}
              hooks
            }}
            totalValueLockedUSD
            volumeUSD
          }}
        }}
        """
        return self.fetch_data(query)

    def get_hook_info(self, hook_address: str) -> Dict:
        """
        Get information about a specific hook contract
        V4-specific feature
        """
        query = f"""
        {{
          hook(id: "{hook_address.lower()}") {{
            id
            poolCount
            totalValueLockedUSD
            volumeUSD
            pools {{
              id
              poolKey {{
                currency0 {{ symbol }}
                currency1 {{ symbol }}
              }}
            }}
          }}
        }}
        """
        return self.fetch_data(query)

    class TheGraphUniswap(DataSource):
    """
    Unified Uniswap class supporting V2, V3, and V4
    """

    SUBGRAPH_URLS = {
        'v2': "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2",
        'v3': "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
        'v4': "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v4"
    }

    def __init__(self, version: str = 'v3'):
        super().__init__(f"The Graph - Uniswap {version.upper()}")
        self.version = version
        self.subgraph_url = self.SUBGRAPH_URLS[version]

    def fetch_data(self, query: str) -> Dict:
        """Execute GraphQL query"""
        self._log_request()
        response = requests.post(self.subgraph_url, json={'query': query})
        response.raise_for_status()
        return response.json()

    def get_pool_data(self, pool_identifier: str) -> Dict:
        """
        Get pool data (version-aware)

        Args:
            pool_identifier: Pool address (V2/V3) or pool key (V4)
        """
        if self.version == 'v2':
            return self._get_v2_pool(pool_identifier)
        elif self.version == 'v3':
            return self._get_v3_pool(pool_identifier)
        elif self.version == 'v4':
            return self._get_v4_pool(pool_identifier)

class DeFiDataManager:
    """
    Master class - now supports V2, V3, and V4
    """

    def __init__(self, rpc_url: Optional[str] = None, uniswap_versions: List[str] = None):
        self.coingecko = CoinGeckoAPI()

        # Initialize requested Uniswap versions
        if uniswap_versions is None:
            uniswap_versions = ['v2', 'v3']  # Default to V2 and V3

        self.uniswap = {}
        for version in uniswap_versions:
            if version == 'v2':
                self.uniswap['v2'] = TheGraphUniswapV2()
            elif version == 'v3':
                self.uniswap['v3'] = TheGraphUniswapV3()
            elif version == 'v4':
                self.uniswap['v4'] = TheGraphUniswapV4()

        self.rpc = RPCProvider(rpc_url, "Infura/Alchemy") if rpc_url else None
        self.db = LocalDatabaseManager()

        print("="*60)
        print("🚀 DeFi Data Manager Initialized")
        print("="*60)
        print("Available sources:")
        print("  ✅ CoinGecko API (Price data)")
        for version in self.uniswap.keys():
            print(f"  ✅ Uniswap {version.upper()} (The Graph)")
        print(f"  {'✅' if self.rpc else '❌'} RPC Provider (Blockchain)")
        print("  ✅ Local Database (Storage)")
        print("="*60)

    def fetch_pool(self, pool_address: str, version: str = 'v3'):
        """
        Fetch pool data from specified Uniswap version

        Args:
            pool_address: Pool address/key
            version: 'v2', 'v3', or 'v4'
        """
        if version not in self.uniswap:
            raise ValueError(f"Uniswap {version} not initialized")

        return self.uniswap[version].get_pool_data(pool_address)


🚀 Usage Example

# Initialize with all versions
manager = DeFiDataManager(uniswap_versions=['v2', 'v3', 'v4'])

# V2 pool
v2_pool = manager.fetch_pool("0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc", version='v2')

# V3 pool with 0.3% fee tier
v3_pool = manager.fetch_pool("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8", version='v3')

# V4 pool (when available)
v4_pool = manager.fetch_pool("pool_key_hash", version='v4')

# Compare liquidity across versions
for version in ['v2', 'v3', 'v4']:
    pools = manager.uniswap[version].get_top_pools(limit=5)
    print(f"{version.upper()}: {len(pools)} top pools")
