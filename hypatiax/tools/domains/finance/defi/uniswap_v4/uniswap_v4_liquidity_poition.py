"""
Uniswap V4 Liquidity Position Management
=========================================
Manage V4 positions with hooks and singleton architecture.

KEY POINTS:
- V4 uses SAME concentrated liquidity math as V3 (NFT positions)
- V4 adds: Hooks, flash accounting, native ETH, gas savings
- Position calculations are IDENTICAL to V3
- Hooks add customization WITHOUT changing core formulas
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class HookFlags(Enum):
    """V4 Hook permission flags"""

    BEFORE_INITIALIZE = 1 << 0
    AFTER_INITIALIZE = 1 << 1
    BEFORE_SWAP = 1 << 2
    AFTER_SWAP = 1 << 3
    BEFORE_ADD_LIQUIDITY = 1 << 4
    AFTER_ADD_LIQUIDITY = 1 << 5
    BEFORE_REMOVE_LIQUIDITY = 1 << 6
    AFTER_REMOVE_LIQUIDITY = 1 << 7
    BEFORE_DONATE = 1 << 8
    AFTER_DONATE = 1 << 9


@dataclass
class V4PositionInfo:
    """V4 Position (same as V3, but with hook context)"""

    token_id: int
    price_lower: float
    price_upper: float
    liquidity: float
    token0_owed: float = 0
    token1_owed: float = 0
    hook_address: Optional[str] = None
    custom_data: Optional[Dict] = None


@dataclass
class PoolKey:
    """V4 Pool Key (includes hook)"""

    token0: str
    token1: str
    fee: int  # Fee in hundredths of a bip (e.g., 3000 = 0.3%)
    tick_spacing: int
    hook_address: Optional[str] = None


class UniswapV4Singleton:
    """
    V4 Singleton PoolManager

    In V4, ALL pools live in ONE contract!
    This enables:
    - 99% cheaper pool creation
    - Flash accounting across pools
    - Efficient multi-hop routing

    But position math is SAME AS V3
    """

    def __init__(self):
        """Initialize V4 Singleton PoolManager"""
        self.pools = {}  # PoolKey -> Pool state
        self.positions = {}  # Position ID -> Position info
        self.next_position_id = 1

        # Flash accounting (EIP-1153 transient storage simulation)
        self.flash_deltas = {}  # token -> net delta
        self.is_locked = False

        # Gas tracking
        self.gas_saved = 0

    def _get_pool_key_hash(self, pool_key: PoolKey) -> str:
        """Generate unique hash for pool"""
        return f"{pool_key.token0}_{pool_key.token1}_{pool_key.fee}_{pool_key.tick_spacing}_{pool_key.hook_address}"

    def initialize_pool(self, pool_key: PoolKey, initial_price: float) -> Dict:
        """
        Initialize a new pool (99% cheaper than V3!)

        V3: Deploy new contract (~2M gas)
        V4: State update in singleton (~20k gas)
        """
        pool_hash = self._get_pool_key_hash(pool_key)

        if pool_hash in self.pools:
            raise ValueError("Pool already exists")

        # Calculate sqrt price X96
        sqrt_price_x96 = int(math.sqrt(initial_price) * (2**96))

        self.pools[pool_hash] = {
            "pool_key": pool_key,
            "sqrt_price_x96": sqrt_price_x96,
            "liquidity": 0,
            "tick": self._price_to_tick(initial_price),
            "fee_growth_global0": 0,
            "fee_growth_global1": 0,
        }

        # V4 gas savings: 99% cheaper than V3!
        v3_gas_cost = 2_000_000
        v4_gas_cost = 20_000
        self.gas_saved += v3_gas_cost - v4_gas_cost

        return {
            "pool_hash": pool_hash,
            "sqrt_price_x96": sqrt_price_x96,
            "gas_saved": v3_gas_cost - v4_gas_cost,
            "hook_address": pool_key.hook_address,
        }

    def _price_to_tick(self, price: float, tick_spacing: int = 1) -> int:
        """Convert price to tick (SAME AS V3)"""
        tick = int(math.log(price, 1.0001))
        return (tick // tick_spacing) * tick_spacing

    def _tick_to_price(self, tick: int) -> float:
        """Convert tick to price (SAME AS V3)"""
        return 1.0001**tick

    def _calculate_liquidity(
        self, amount0: float, amount1: float, price_lower: float, price_upper: float, price_current: float
    ) -> float:
        """Calculate liquidity (SAME AS V3)"""
        sqrt_Pa = math.sqrt(price_lower)
        sqrt_Pb = math.sqrt(price_upper)
        sqrt_P = math.sqrt(price_current)

        if price_current <= price_lower:
            L = amount0 * sqrt_Pa * sqrt_Pb / (sqrt_Pb - sqrt_Pa) if amount0 > 0 else 0
        elif price_current >= price_upper:
            L = amount1 / (sqrt_Pb - sqrt_Pa) if amount1 > 0 else 0
        else:
            L0 = amount0 * sqrt_P * sqrt_Pb / (sqrt_Pb - sqrt_P) if amount0 > 0 else float("inf")
            L1 = amount1 / (sqrt_P - sqrt_Pa) if amount1 > 0 else float("inf")
            L = min(L0, L1)

        return L

    def _calculate_amounts(
        self, L: float, price_lower: float, price_upper: float, price_current: float
    ) -> Tuple[float, float]:
        """Calculate amounts from liquidity (SAME AS V3)"""
        sqrt_Pa = math.sqrt(price_lower)
        sqrt_Pb = math.sqrt(price_upper)
        sqrt_P = math.sqrt(price_current)

        if price_current <= price_lower:
            amount0 = L * (sqrt_Pb - sqrt_Pa) / (sqrt_Pa * sqrt_Pb)
            amount1 = 0
        elif price_current >= price_upper:
            amount0 = 0
            amount1 = L * (sqrt_Pb - sqrt_Pa)
        else:
            amount0 = L * (sqrt_Pb - sqrt_P) / (sqrt_P * sqrt_Pb)
            amount1 = L * (sqrt_P - sqrt_Pa)

        return amount0, amount1

    def mint_position(
        self,
        pool_key: PoolKey,
        price_current: float,
        tick_lower: int,
        tick_upper: int,
        amount0_desired: float,
        amount1_desired: float,
        hook_data: Optional[bytes] = None,
    ) -> Dict:
        """
        Mint V4 position (NFT, SAME AS V3)

        V4 adds: Hook callbacks, flash accounting
        """
        pool_hash = self._get_pool_key_hash(pool_key)

        if pool_hash not in self.pools:
            raise ValueError("Pool not initialized")

        pool = self.pools[pool_hash]

        # Convert ticks to prices
        price_lower = self._tick_to_price(tick_lower)
        price_upper = self._tick_to_price(tick_upper)

        # HOOK: beforeAddLiquidity
        if pool_key.hook_address:
            hook_result = self._call_hook_before_add_liquidity(pool_key, amount0_desired, amount1_desired, hook_data)
            if not hook_result["allowed"]:
                raise ValueError(f"Hook rejected: {hook_result.get('reason', 'Unknown')}")

        # Calculate liquidity (SAME AS V3)
        L = self._calculate_liquidity(amount0_desired, amount1_desired, price_lower, price_upper, price_current)

        # Calculate actual amounts needed (SAME AS V3)
        amount0, amount1 = self._calculate_amounts(L, price_lower, price_upper, price_current)

        # Create position NFT
        position_id = self.next_position_id
        self.next_position_id += 1

        position = V4PositionInfo(
            token_id=position_id,
            price_lower=price_lower,
            price_upper=price_upper,
            liquidity=L,
            hook_address=pool_key.hook_address,
        )

        self.positions[position_id] = position

        # Update pool liquidity
        pool["liquidity"] += L

        # FLASH ACCOUNTING: Track deltas
        self.flash_deltas["token0"] = self.flash_deltas.get("token0", 0) + amount0
        self.flash_deltas["token1"] = self.flash_deltas.get("token1", 0) + amount1

        # HOOK: afterAddLiquidity
        if pool_key.hook_address:
            self._call_hook_after_add_liquidity(pool_key, position_id, L)

        return {
            "position_id": position_id,
            "liquidity": L,
            "amount0_deposited": amount0,
            "amount1_deposited": amount1,
            "amount0_refunded": amount0_desired - amount0,
            "amount1_refunded": amount1_desired - amount1,
            "tick_lower": tick_lower,
            "tick_upper": tick_upper,
            "price_lower": price_lower,
            "price_upper": price_upper,
            "hook_address": pool_key.hook_address,
        }

    def _call_hook_before_add_liquidity(
        self, pool_key: PoolKey, amount0: float, amount1: float, hook_data: Optional[bytes]
    ) -> Dict:
        """Simulate hook call before adding liquidity"""
        # This would call actual hook contract in real V4
        # Here we simulate simple checks

        # Example: Minimum deposit check
        min_deposit = 1000  # $1000 minimum
        total_value = amount0 * 2000 + amount1  # Assume token0 = $2000

        if total_value < min_deposit:
            return {"allowed": False, "reason": f"Minimum ${min_deposit} required"}

        return {"allowed": True}

    def _call_hook_after_add_liquidity(self, pool_key: PoolKey, position_id: int, liquidity: float):
        """Simulate hook call after adding liquidity"""
        # Hook could track liquidity events, update rewards, etc.
        pass

    def get_position_value(self, position_id: int, price_current: float) -> Dict:
        """
        Get current position value (SAME CALCULATION AS V3)
        """
        if position_id not in self.positions:
            raise ValueError(f"Position {position_id} not found")

        position = self.positions[position_id]

        # Calculate current amounts (SAME AS V3)
        amount0, amount1 = self._calculate_amounts(
            position.liquidity, position.price_lower, position.price_upper, price_current
        )

        # Calculate values
        value_token0 = amount0 * price_current
        value_token1 = amount1
        total_value = value_token0 + value_token1

        # In range check
        in_range = position.price_lower <= price_current <= position.price_upper

        return {
            "position_id": position_id,
            "price_current": price_current,
            "price_lower": position.price_lower,
            "price_upper": position.price_upper,
            "in_range": in_range,
            "liquidity": position.liquidity,
            "amount0": amount0,
            "amount1": amount1,
            "value_token0": value_token0,
            "value_token1": value_token1,
            "total_value": total_value,
            "fees_owed_0": position.token0_owed,
            "fees_owed_1": position.token1_owed,
            "hook_address": position.hook_address,
        }

    def burn_position(self, position_id: int, price_current: float) -> Dict:
        """
        Burn (remove) position (SAME AS V3)

        V4 adds: Hook callbacks, flash accounting
        """
        if position_id not in self.positions:
            raise ValueError(f"Position {position_id} not found")

        position = self.positions[position_id]

        # HOOK: beforeRemoveLiquidity
        # (would call hook contract here)

        # Get position value
        value_data = self.get_position_value(position_id, price_current)

        # Remove position
        del self.positions[position_id]

        # FLASH ACCOUNTING: Track deltas
        self.flash_deltas["token0"] = self.flash_deltas.get("token0", 0) - value_data["amount0"]
        self.flash_deltas["token1"] = self.flash_deltas.get("token1", 0) - value_data["amount1"]

        # HOOK: afterRemoveLiquidity
        # (would call hook contract here)

        return {
            "position_id": position_id,
            "amount0_withdrawn": value_data["amount0"],
            "amount1_withdrawn": value_data["amount1"],
            "fees_token0": position.token0_owed,
            "fees_token1": position.token1_owed,
            "total_value": value_data["total_value"],
        }

    def swap(self, pool_key: PoolKey, amount_in: float, zero_for_one: bool) -> Dict:
        """
        Perform swap with V4 flash accounting

        V4 advantage: Multi-hop swaps only settle net balances!
        """
        pool_hash = self._get_pool_key_hash(pool_key)

        if pool_hash not in self.pools:
            raise ValueError("Pool not initialized")

        # HOOK: beforeSwap (could modify fee, amount, etc.)
        if pool_key.hook_address:
            hook_result = self._call_hook_before_swap(pool_key, amount_in)
            amount_in = hook_result.get("modified_amount", amount_in)
            fee_modifier = hook_result.get("fee_modifier", 1.0)
        else:
            fee_modifier = 1.0

        # Calculate swap (simplified)
        fee = (pool_key.fee / 1_000_000) * fee_modifier
        amount_in_after_fee = amount_in * (1 - fee)

        # Simplified output calculation
        amount_out = amount_in_after_fee * 0.995  # Simplified

        # FLASH ACCOUNTING: Only track deltas!
        # No actual token transfer yet
        if zero_for_one:
            self.flash_deltas["token0"] = self.flash_deltas.get("token0", 0) + amount_in
            self.flash_deltas["token1"] = self.flash_deltas.get("token1", 0) - amount_out
        else:
            self.flash_deltas["token1"] = self.flash_deltas.get("token1", 0) + amount_in
            self.flash_deltas["token0"] = self.flash_deltas.get("token0", 0) - amount_out

        # HOOK: afterSwap
        if pool_key.hook_address:
            self._call_hook_after_swap(pool_key, amount_out)

        # V4 gas savings on multi-hop
        # V3: Transfer tokens between pools
        # V4: Just track deltas
        self.gas_saved += 50_000  # ~50k gas saved per hop

        return {
            "amount_in": amount_in,
            "amount_out": amount_out,
            "fee": amount_in * fee,
            "fee_modifier": fee_modifier,
            "gas_saved": 50_000,
        }

    def _call_hook_before_swap(self, pool_key: PoolKey, amount_in: float) -> Dict:
        """Simulate hook before swap (dynamic fee example)"""
        # Hook could modify fee based on volatility, price, etc.
        # Example: Higher fee during high volatility
        volatility_factor = 1.2  # Simulated

        return {"modified_amount": amount_in, "fee_modifier": volatility_factor}

    def _call_hook_after_swap(self, pool_key: PoolKey, amount_out: float):
        """Simulate hook after swap"""
        # Hook could take protocol fee, update oracle, etc.
        pass

    def settle_flash_accounting(self) -> Dict:
        """
        Settle all flash accounting deltas

        V4 MAGIC: Only settle NET balances at end!
        """
        settled = {}
        for token, delta in self.flash_deltas.items():
            if delta != 0:
                # This is where actual token transfer would happen
                settled[token] = delta

        # Clear deltas
        self.flash_deltas = {}

        return settled

    def get_gas_savings_report(self) -> Dict:
        """Get V4 gas savings report"""
        return {
            "total_gas_saved": self.gas_saved,
            "pool_creation_savings": "99%",
            "flash_accounting_enabled": True,
            "native_eth_support": True,
        }


# ===== EXAMPLE USAGE =====


def example_v4_position_lifecycle():
    """Complete V4 position lifecycle example"""

    print("=" * 80)
    print("UNISWAP V4 SINGLETON ARCHITECTURE + POSITION MANAGEMENT")
    print("=" * 80)
    print()
    print("🔑 KEY POINTS:")
    print("   • V4 uses SAME position math as V3 (concentrated liquidity)")
    print("   • All pools in ONE contract (singleton)")
    print("   • Flash accounting = only settle net balances")
    print("   • Hooks = custom logic without changing core")
    print()
    print("=" * 80)
    print()

    # Initialize V4 Singleton
    v4_singleton = UniswapV4Singleton()

    # Define pool with hook
    pool_key = PoolKey(
        token0="ETH", token1="USDC", fee=3000, tick_spacing=60, hook_address="0x1234...5678"  # 0.3%  # Dynamic fee hook
    )

    current_price = 2000

    print("STEP 1: CREATE POOL (99% CHEAPER IN V4!)")
    print("-" * 80)
    pool_init = v4_singleton.initialize_pool(pool_key, current_price)
    print(f"  Pool Hash: {pool_init['pool_hash'][:20]}...")
    print(f"  Initial Price: ${current_price}")
    print(f"  Gas Saved vs V3: {pool_init['gas_saved']:,} gas (99%!)")
    print(f"  Hook: {pool_init['hook_address']}")
    print()

    print("STEP 2: MINT POSITION (SAME AS V3)")
    print("-" * 80)
    tick_lower = v4_singleton._price_to_tick(1900)
    tick_upper = v4_singleton._price_to_tick(2100)

    position = v4_singleton.mint_position(
        pool_key=pool_key,
        price_current=current_price,
        tick_lower=tick_lower,
        tick_upper=tick_upper,
        amount0_desired=1.0,  # 1 ETH
        amount1_desired=2000,  # 2000 USDC
    )

    print(f"  Position NFT ID: #{position['position_id']}")
    print(f"  Range: ${position['price_lower']:.0f} - ${position['price_upper']:.0f}")
    print(f"  Deposited: {position['amount0_deposited']:.4f} ETH + ${position['amount1_deposited']:.2f} USDC")
    print(f"  Liquidity: {position['liquidity']:.2f}")
    print(f"  Hook: {position['hook_address']}")
    print()

    print("STEP 3: PERFORM SWAP WITH FLASH ACCOUNTING")
    print("-" * 80)
    swap_result = v4_singleton.swap(pool_key=pool_key, amount_in=100, zero_for_one=False)  # 100 USDC

    print(f"  Swap: 100 USDC → {swap_result['amount_out']:.4f} ETH")
    print(f"  Fee Modifier (Hook): {swap_result['fee_modifier']:.2f}x")
    print(f"  Gas Saved (Flash Accounting): {swap_result['gas_saved']:,} gas")
    print(f"  💡 In V3, tokens would transfer NOW")
    print(f"  ⚡ In V4, just tracking deltas (settle at end)")
    print()

    print("STEP 4: CHECK POSITION VALUE")
    print("-" * 80)
    new_price = 2050
    value = v4_singleton.get_position_value(position["position_id"], new_price)

    print(f"  Price: ${value['price_current']:.0f}")
    print(f"  In Range: {value['in_range']}")
    print(f"  Current: {value['amount0']:.4f} ETH + ${value['amount1']:.2f} USDC")
    print(f"  Total Value: ${value['total_value']:.2f}")
    print()

    print("STEP 5: SETTLE FLASH ACCOUNTING")
    print("-" * 80)
    settled = v4_singleton.settle_flash_accounting()
    print(f"  Net balances to settle:")
    for token, delta in settled.items():
        print(f"    {token}: {delta:+.4f}")
    print(f"  💡 Only these net amounts actually transfer!")
    print(f"  ⚡ V3 would have transferred every intermediate step")
    print()

    print("STEP 6: REMOVE POSITION")
    print("-" * 80)
    withdraw = v4_singleton.burn_position(position["position_id"], new_price)

    print(f"  Withdrew: {withdraw['amount0_withdrawn']:.4f} ETH + ${withdraw['amount1_withdrawn']:.2f} USDC")
    print(f"  Total Value: ${withdraw['total_value']:.2f}")
    print()

    print("STEP 7: V4 GAS SAVINGS REPORT")
    print("-" * 80)
    report = v4_singleton.get_gas_savings_report()
    print(f"  Total Gas Saved: {report['total_gas_saved']:,} gas")
    print(f"  Pool Creation: {report['pool_creation_savings']} cheaper")
    print(f"  Flash Accounting: {report['flash_accounting_enabled']}")
    print(f"  Native ETH Support: {report['native_eth_support']}")
    print()

    print("=" * 80)
    print("V4 KEY ADVANTAGES SUMMARY:")
    print("=" * 80)
    print("✅ SAME concentrated liquidity math as V3 (proven model)")
    print("✅ Singleton: 99% cheaper pool creation (1 contract not 1000s)")
    print("✅ Flash accounting: Massive gas savings (only net transfers)")
    print("✅ Native ETH: 15% gas savings (no WETH wrapping)")
    print("✅ Hooks: Unlimited customization (without changing core)")
    print("✅ Dynamic fees: Optimize earnings via hooks")
    print("=" * 80)


if __name__ == "__main__":
    example_v4_position_lifecycle()
