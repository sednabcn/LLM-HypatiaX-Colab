"""
UNISWAP V4 FORMULAS AND CALCULATIONS
=====================================

V4 KEY INNOVATIONS:
1. HOOKS - Custom logic at lifecycle points
2. SINGLETON - All pools in one contract (99% gas savings)
3. FLASH ACCOUNTING - Net settlement only (EIP-1153)
4. NATIVE ETH - No wrapping needed
5. DYNAMIC FEES - Unlimited fee tiers

IMPORTANT: V4 inherits V3's concentrated liquidity model!
The core math is the SAME as V3, but with hooks adding customization.
"""

import csv
import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional

# ============================================================================
# UNISWAP V4 MATHEMATICAL FORMULAS (SAME AS V3 + HOOKS)
# ============================================================================
"""
V4 CONCENTRATED LIQUIDITY FORMULAS (INHERITED FROM V3):

1. LIQUIDITY CALCULATION:
   L = Δy / (√Pb - √Pa)  [when P > Pb]
   L = Δx * √Pa * √Pb / (√Pb - √Pa)  [when P < Pa]

2. TOKEN AMOUNTS:
   x = L * (1/√P - 1/√Pb)  [amount of token0]
   y = L * (√P - √Pa)      [amount of token1]

3. IMPERMANENT LOSS:
   pool_value = amount0 * P + amount1
   hodl_value = initial_amount0 * P + initial_amount1
   IL = pool_value - hodl_value

4. HOOKS EXECUTION:
   beforeInitialize → initialize → afterInitialize
   beforeSwap → swap → afterSwap
   beforeAddLiquidity → addLiquidity → afterAddLiquidity
   beforeRemoveLiquidity → removeLiquidity → afterRemoveLiquidity

5. FLASH ACCOUNTING:
   All operations track deltas
   Only final net balance requires token transfer
   Dramatically reduces gas for multi-hop swaps

6. DYNAMIC FEES:
   Hooks can modify fee on every swap
   Fee can be 0% to 100% (unlimited)
   Enables fee optimization, MEV capture, etc.
"""


class HookPermissions(Enum):
    """Hook permission flags"""

    BEFORE_INITIALIZE = "beforeInitialize"
    AFTER_INITIALIZE = "afterInitialize"
    BEFORE_SWAP = "beforeSwap"
    AFTER_SWAP = "afterSwap"
    BEFORE_ADD_LIQUIDITY = "beforeAddLiquidity"
    AFTER_ADD_LIQUIDITY = "afterAddLiquidity"
    BEFORE_REMOVE_LIQUIDITY = "beforeRemoveLiquidity"
    AFTER_REMOVE_LIQUIDITY = "afterRemoveLiquidity"
    BEFORE_DONATE = "beforeDonate"
    AFTER_DONATE = "afterDonate"


@dataclass
class V4PoolConfig:
    """V4 Pool configuration with hook"""

    token0: str
    token1: str
    fee: float
    tick_spacing: int
    hook_address: Optional[str] = None
    hook_permissions: List[HookPermissions] = None


@dataclass
class V4Position:
    """V4 Position (same as V3 but with hook context)"""

    name: str
    price_lower: float
    price_upper: float
    price_current: float
    amount0_deposited: float
    amount1_deposited: float
    fee_tier: float = 0.003
    days_elapsed: int = 30
    daily_volume_usd: float = 1_000_000
    pool_tvl_usd: float = 10_000_000
    # V4 specific
    hook_fee_modifier: float = 1.0  # Hook can modify fees
    custom_logic_applied: bool = False


class UniswapV4Math:
    """
    Core V4 Mathematical Functions

    NOTE: The concentrated liquidity math is IDENTICAL to V3!
    V4 adds hooks and optimization, but doesn't change the core formulas.
    """

    @staticmethod
    def price_to_tick(price: float, tick_spacing: int = 1) -> int:
        """Convert price to tick (same as V3)"""
        tick = int(math.log(price, 1.0001))
        # Round to nearest valid tick based on spacing
        return (tick // tick_spacing) * tick_spacing

    @staticmethod
    def tick_to_price(tick: int) -> float:
        """Convert tick to price (same as V3)"""
        return 1.0001**tick

    @staticmethod
    def get_sqrt_price_x96(price: float) -> int:
        """
        Convert price to sqrtPriceX96 (V4 internal format)
        Q64.96 fixed point number
        """
        sqrt_price = math.sqrt(price)
        return int(sqrt_price * (2**96))

    @staticmethod
    def calculate_liquidity(
        amount0: float, amount1: float, price_lower: float, price_upper: float, price_current: float
    ) -> float:
        """Calculate liquidity L (SAME AS V3)"""
        sqrt_Pa = math.sqrt(price_lower)
        sqrt_Pb = math.sqrt(price_upper)
        sqrt_P = math.sqrt(price_current)

        if price_current <= price_lower:
            if amount0 > 0:
                L = amount0 * sqrt_Pa * sqrt_Pb / (sqrt_Pb - sqrt_Pa)
            else:
                L = 0
        elif price_current >= price_upper:
            if amount1 > 0:
                L = amount1 / (sqrt_Pb - sqrt_Pa)
            else:
                L = 0
        else:
            if amount0 > 0:
                L0 = amount0 * sqrt_P * sqrt_Pb / (sqrt_Pb - sqrt_P)
            else:
                L0 = float("inf")
            if amount1 > 0:
                L1 = amount1 / (sqrt_P - sqrt_Pa)
            else:
                L1 = float("inf")
            L = min(L0, L1)

        return L

    @staticmethod
    def calculate_amounts(L: float, price_lower: float, price_upper: float, price_current: float) -> tuple:
        """Calculate token amounts from liquidity (SAME AS V3)"""
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


class V4HookSimulator:
    """
    Simulate hook behavior in V4

    Hooks can modify:
    - Fees dynamically
    - Swap amounts
    - Access control
    - Add custom logic
    """

    def __init__(self, name: str, permissions: List[HookPermissions]):
        self.name = name
        self.permissions = permissions
        self.call_count = {perm: 0 for perm in permissions}

    def before_swap(self, amount_in: float, current_price: float) -> Dict:
        """Hook logic before swap"""
        if HookPermissions.BEFORE_SWAP not in self.permissions:
            return {"modified_amount": amount_in, "fee_modifier": 1.0}

        self.call_count[HookPermissions.BEFORE_SWAP] += 1

        # Example: Dynamic fee based on volatility
        # Higher price = higher fee
        volatility_factor = current_price / 2000  # Assume 2000 is baseline
        fee_modifier = min(2.0, max(0.5, volatility_factor))

        return {
            "modified_amount": amount_in,
            "fee_modifier": fee_modifier,
            "custom_data": f"Hook {self.name} modified fee by {fee_modifier:.2f}x",
        }

    def after_swap(self, amount_out: float) -> Dict:
        """Hook logic after swap"""
        if HookPermissions.AFTER_SWAP not in self.permissions:
            return {"final_amount": amount_out}

        self.call_count[HookPermissions.AFTER_SWAP] += 1

        # Example: Take protocol fee
        protocol_fee = amount_out * 0.0005  # 0.05% protocol fee

        return {"final_amount": amount_out - protocol_fee, "protocol_fee": protocol_fee}

    def before_add_liquidity(self, amount0: float, amount1: float) -> Dict:
        """Hook logic before adding liquidity"""
        if HookPermissions.BEFORE_ADD_LIQUIDITY not in self.permissions:
            return {"allowed": True}

        self.call_count[HookPermissions.BEFORE_ADD_LIQUIDITY] += 1

        # Example: Minimum deposit check
        min_deposit_usd = 1000
        total_value = amount0 * 2000 + amount1  # Assume ETH = $2000

        return {
            "allowed": total_value >= min_deposit_usd,
            "reason": f"Minimum ${min_deposit_usd} required" if total_value < min_deposit_usd else "OK",
        }


class UniswapV4Calculator:
    """
    V4 Calculator with Hook Support

    Core IL calculation is SAME AS V3
    But hooks can modify fees and add custom logic
    """

    @staticmethod
    def calculate_v4_il_with_hooks(position: V4Position, hook: Optional[V4HookSimulator] = None) -> Dict:
        """
        Calculate IL for V4 position (same math as V3, but with hooks)
        """
        Pa = position.price_lower
        Pb = position.price_upper
        P = position.price_current

        # Calculate liquidity (SAME AS V3)
        L = UniswapV4Math.calculate_liquidity(position.amount0_deposited, position.amount1_deposited, Pa, Pb, P)

        # Calculate current amounts (SAME AS V3)
        amount0_now, amount1_now = UniswapV4Math.calculate_amounts(L, Pa, Pb, P)

        # Calculate values (SAME AS V3)
        current_value = amount0_now * P + amount1_now
        hodl_value = position.amount0_deposited * P + position.amount1_deposited

        # IL calculation (SAME AS V3)
        il_dollar = current_value - hodl_value
        il_percent = (il_dollar / hodl_value * 100) if hodl_value > 0 else 0

        # Check if in range
        in_range = Pa <= P <= Pb

        # Fee calculation with V4 HOOK MODIFIER
        base_fee_tier = position.fee_tier

        # If hook exists and modifies fees
        if hook and HookPermissions.BEFORE_SWAP in hook.permissions:
            hook_data = hook.before_swap(1000, P)  # Simulate swap
            effective_fee_tier = base_fee_tier * hook_data["fee_modifier"]
        else:
            effective_fee_tier = base_fee_tier

        # Calculate fees earned
        if in_range:
            position_tvl = current_value
            pool_share = position_tvl / position.pool_tvl_usd if position.pool_tvl_usd > 0 else 0

            # V4 concentrates liquidity (same as V3)
            range_factor = 100 / (Pb / Pa) if Pa > 0 else 1
            effective_share = pool_share * min(range_factor, 50)

            daily_fees = position.daily_volume_usd * effective_fee_tier * effective_share
            total_fees = daily_fees * position.days_elapsed
        else:
            daily_fees = 0
            total_fees = 0

        # Net result
        net_result = total_fees + il_dollar

        # Breakeven
        if daily_fees > 0 and il_dollar < 0:
            breakeven_days = abs(il_dollar) / daily_fees
        else:
            breakeven_days = float("inf")

        return {
            "position_name": position.name,
            "price_lower": Pa,
            "price_upper": Pb,
            "price_current": P,
            "in_range": in_range,
            "liquidity": round(L, 2),
            "amount0_current": round(amount0_now, 6),
            "amount1_current": round(amount1_now, 2),
            "current_value": round(current_value, 2),
            "hodl_value": round(hodl_value, 2),
            "il_dollar": round(il_dollar, 2),
            "il_percent": round(il_percent, 4),
            "base_fee_tier": base_fee_tier * 100,
            "effective_fee_tier": effective_fee_tier * 100,
            "daily_fees": round(daily_fees, 2),
            "total_fees": round(total_fees, 2),
            "net_result": round(net_result, 2),
            "breakeven_days": round(breakeven_days, 2) if breakeven_days != float("inf") else "N/A",
            "profitable": "Yes" if net_result > 0 else "No",
            "hook_applied": hook is not None,
            "hook_name": hook.name if hook else "None",
        }


# ============================================================================
# TEST SCENARIOS: V4 WITH DIFFERENT HOOKS
# ============================================================================


def generate_v4_test_positions() -> List[V4Position]:
    """Generate V4 positions with various configurations"""

    positions = [
        # 1. Standard V3-like position (no hook)
        V4Position(
            name="ETH/USDC: Standard (No Hook)",
            price_lower=1900,
            price_upper=2100,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
        ),
        # 2. Dynamic fee hook
        V4Position(
            name="ETH/USDC: Dynamic Fee Hook",
            price_lower=1900,
            price_upper=2100,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            hook_fee_modifier=1.5,  # Hook increases fees 50%
        ),
        # 3. Low fee tier (0.01% - stablecoin)
        V4Position(
            name="USDC/USDT: Ultra Low Fee",
            price_lower=0.999,
            price_upper=1.001,
            price_current=1.0,
            amount0_deposited=10000,
            amount1_deposited=10000,
            fee_tier=0.0001,  # 0.01%
            days_elapsed=90,
            daily_volume_usd=500_000_000,
        ),
        # 4. High fee tier (1% - exotic)
        V4Position(
            name="SHIB/USDC: High Fee Exotic",
            price_lower=0.0005,
            price_upper=0.0015,
            price_current=0.001,
            amount0_deposited=1_000_000,
            amount1_deposited=1000,
            fee_tier=0.01,  # 1%
            days_elapsed=20,
            daily_volume_usd=20_000_000,
        ),
        # 5. Native ETH pool (V4 advantage)
        V4Position(
            name="ETH/USDC: Native ETH (15% gas savings)",
            price_lower=1800,
            price_upper=2200,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
        ),
        # 6. MEV protection hook
        V4Position(
            name="ETH/USDC: MEV Protection Hook",
            price_lower=1900,
            price_upper=2100,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            custom_logic_applied=True,
        ),
        # 7. TWAMM Hook (Time-Weighted AMM)
        V4Position(
            name="ETH/USDC: TWAMM Hook (Long-term orders)",
            price_lower=1800,
            price_upper=2200,
            price_current=2000,
            amount0_deposited=1.0,
            amount1_deposited=2000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            custom_logic_applied=True,
        ),
        # 8. Limit Order Hook
        V4Position(
            name="ETH/USDC: Limit Order Hook",
            price_lower=1950,
            price_upper=2050,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            custom_logic_applied=True,
        ),
        # 9. Volatility Oracle Hook
        V4Position(
            name="ETH/USDC: Volatility Oracle Hook",
            price_lower=1700,
            price_upper=2300,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            hook_fee_modifier=0.8,  # Lower fees when low volatility
        ),
        # 10. Full Range (V2-like via hook)
        V4Position(
            name="ETH/USDC: Full Range Hook (V2 style)",
            price_lower=100,
            price_upper=10000,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            custom_logic_applied=True,
        ),
    ]

    return positions


def export_results_to_csv(results: List[Dict], filename: str = "uniswap_v4_results.csv"):
    """Export V4 results to CSV"""
    if not results:
        return

    keys = results[0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n✅ Results exported to {filename}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 120)
    print("UNISWAP V4 - HOOKS + CONCENTRATED LIQUIDITY CALCULATOR")
    print("=" * 120)
    print()
    print("KEY V4 FEATURES:")
    print("  🪝 HOOKS: Custom logic at any lifecycle point")
    print("  🎯 SINGLETON: All pools in one contract (99% cheaper deployment)")
    print("  ⚡ FLASH ACCOUNTING: Net settlement only (massive gas savings)")
    print("  💎 NATIVE ETH: No wrapping needed (15% gas savings)")
    print("  📊 DYNAMIC FEES: Unlimited fee tiers + hooks can modify")
    print()
    print("IMPORTANT: V4 uses SAME concentrated liquidity math as V3!")
    print("           Hooks add customization WITHOUT changing core formulas.")
    print("=" * 120)
    print()

    # Create hook simulators
    dynamic_fee_hook = V4HookSimulator("DynamicFeeHook", [HookPermissions.BEFORE_SWAP, HookPermissions.AFTER_SWAP])

    # Generate positions
    positions = generate_v4_test_positions()
    calculator = UniswapV4Calculator()

    # Analyze positions
    results = []
    print(f"{'Position':<45} {'Range':>15} {'Fee%':>8} {'IL%':>10} {'Fees$':>12} {'Net$':>12} {'Hook':>20}")
    print("-" * 135)

    for idx, position in enumerate(positions):
        # Apply hook to some positions
        hook = dynamic_fee_hook if position.hook_fee_modifier != 1.0 else None

        result = calculator.calculate_v4_il_with_hooks(position, hook)
        results.append(result)

        range_str = f"${result['price_lower']:.0f}-${result['price_upper']:.0f}"

        print(
            f"{result['position_name']:<45} {range_str:>15} "
            f"{result['effective_fee_tier']:>7.2f}% "
            f"{result['il_percent']:>9.2f}% "
            f"${result['total_fees']:>11,.0f} "
            f"${result['net_result']:>11,.0f} "
            f"{result['hook_name']:>20}"
        )

    print("-" * 135)
    print()

    # Summary
    profitable_count = sum(1 for r in results if r["profitable"] == "Yes")
    with_hooks = sum(1 for r in results if r["hook_applied"])
    avg_fee_tier = sum(r["effective_fee_tier"] for r in results) / len(results)

    print("SUMMARY STATISTICS (UNISWAP V4)")
    print(f"  Total Positions: {len(results)}")
    print(f"  Positions with Hooks: {with_hooks}/{len(results)}")
    print(f"  Profitable Positions: {profitable_count}/{len(results)}")
    print(f"  Average Effective Fee: {avg_fee_tier:.3f}%")
    print()

    print("KEY V4 ADVANTAGES OVER V3:")
    print("  ✅ 99% cheaper pool creation (singleton)")
    print("  ✅ Massive gas savings on multi-hop swaps (flash accounting)")
    print("  ✅ Native ETH support (15% gas savings, no wrapping)")
    print("  ✅ Unlimited fee tiers (not just 0.01%, 0.05%, 0.3%, 1%)")
    print("  ✅ Hooks enable: MEV protection, TWAMM, limit orders, dynamic fees, etc.")
    print("  ✅ SAME concentrated liquidity math as V3 (proven and tested)")
    print()

    # Export
    export_results_to_csv(results)
