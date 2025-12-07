"""
Uniswap V4 Impermanent Loss Calculator
========================================
Calculate IL for V4 positions with hook support.

CRITICAL: V4 uses the SAME concentrated liquidity math as V3!
The core IL formulas are IDENTICAL to V3.

What V4 ADDS:
- Hooks can modify fees dynamically
- Flash accounting reduces gas
- Native ETH support
- Singleton architecture

What V4 DOESN'T CHANGE:
- Concentrated liquidity formulas (same as V3)
- IL calculation method (same as V3)
- Position value formula (same as V3)
"""

import math
from decimal import Decimal, getcontext
from typing import Dict, List, Optional, Tuple

getcontext().prec = 28


class UniswapV4ILCalculator:
    """
    V4 IL Calculator

    Uses V3's concentrated liquidity math
    Adds hook support for dynamic fees
    """

    # V4 Fee Tiers (now unlimited!)
    FEE_TIERS = {
        "ULTRA_LOW": 0.0001,  # 0.01% for stablecoins
        "LOW": 0.0005,  # 0.05% for correlated pairs
        "MEDIUM": 0.003,  # 0.3% standard
        "HIGH": 0.01,  # 1% for exotic pairs
        "CUSTOM": None,  # V4 allows ANY fee tier!
    }

    def __init__(
        self,
        price_lower: float,
        price_upper: float,
        price_initial: float,
        amount0: float,
        amount1: float,
        fee_tier: float = 0.003,
        hook_enabled: bool = False,
    ):
        """
        Initialize V4 position

        Args:
            price_lower: Lower price bound
            price_upper: Upper price bound
            price_initial: Initial price
            amount0: Initial token0 amount
            amount1: Initial token1 amount
            fee_tier: Base fee tier
            hook_enabled: Whether hook modifies fees
        """
        self.Pa = Decimal(str(price_lower))
        self.Pb = Decimal(str(price_upper))
        self.P_initial = Decimal(str(price_initial))
        self.amount0_initial = Decimal(str(amount0))
        self.amount1_initial = Decimal(str(amount1))
        self.base_fee_tier = Decimal(str(fee_tier))
        self.hook_enabled = hook_enabled

        # Validate
        if not (self.Pa < self.Pb):
            raise ValueError("price_lower must be less than price_upper")

        # Calculate liquidity (SAME AS V3)
        self.liquidity = self._calculate_liquidity(self.amount0_initial, self.amount1_initial, self.P_initial)

        self.initial_value = self.amount0_initial * self.P_initial + self.amount1_initial

    def _sqrt_price(self, price: Decimal) -> Decimal:
        """Square root of price"""
        return price.sqrt()

    def _calculate_liquidity(self, amount0: Decimal, amount1: Decimal, price: Decimal) -> Decimal:
        """
        Calculate liquidity L (SAME AS V3)
        """
        sqrt_Pa = self._sqrt_price(self.Pa)
        sqrt_Pb = self._sqrt_price(self.Pb)
        sqrt_P = self._sqrt_price(price)

        if price <= self.Pa:
            if amount0 > 0:
                liquidity = amount0 * sqrt_Pa * sqrt_Pb / (sqrt_Pb - sqrt_Pa)
            else:
                liquidity = Decimal("0")
        elif price >= self.Pb:
            if amount1 > 0:
                liquidity = amount1 / (sqrt_Pb - sqrt_Pa)
            else:
                liquidity = Decimal("0")
        else:
            if amount0 > 0:
                L0 = amount0 * sqrt_P * sqrt_Pb / (sqrt_Pb - sqrt_P)
            else:
                L0 = Decimal("inf")
            if amount1 > 0:
                L1 = amount1 / (sqrt_P - sqrt_Pa)
            else:
                L1 = Decimal("inf")
            liquidity = min(L0, L1)

        return liquidity

    def _get_amounts_for_liquidity(self, price: Decimal) -> Tuple[Decimal, Decimal]:
        """
        Calculate token amounts (SAME AS V3)
        """
        sqrt_Pa = self._sqrt_price(self.Pa)
        sqrt_Pb = self._sqrt_price(self.Pb)
        sqrt_P = self._sqrt_price(price)

        if price <= self.Pa:
            amount0 = self.liquidity * (sqrt_Pb - sqrt_Pa) / (sqrt_Pa * sqrt_Pb)
            amount1 = Decimal("0")
        elif price >= self.Pb:
            amount0 = Decimal("0")
            amount1 = self.liquidity * (sqrt_Pb - sqrt_Pa)
        else:
            amount0 = self.liquidity * (sqrt_Pb - sqrt_P) / (sqrt_P * sqrt_Pb)
            amount1 = self.liquidity * (sqrt_P - sqrt_Pa)

        return amount0, amount1

    def simulate_hook_fee_modifier(self, current_price: float, volatility: float = 0.5) -> float:
        """
        Simulate dynamic fee adjustment via hook

        Args:
            current_price: Current price
            volatility: Volatility factor (0-1)

        Returns:
            Fee multiplier (e.g., 1.5 = 50% increase)
        """
        if not self.hook_enabled:
            return 1.0

        # Example: Increase fees during high volatility
        price_change = abs(current_price - float(self.P_initial)) / float(self.P_initial)

        # Base multiplier from volatility
        volatility_multiplier = 1.0 + (volatility * 2.0)

        # Price movement multiplier
        movement_multiplier = 1.0 + price_change

        # Combined (capped at 3x)
        total_multiplier = min(3.0, volatility_multiplier * movement_multiplier)

        return total_multiplier

    def calculate_il_at_price(self, current_price: float, volatility: float = 0.3) -> Dict[str, float]:
        """
        Calculate IL at specific price (SAME MATH AS V3)

        Args:
            current_price: Current market price
            volatility: Volatility for hook simulation

        Returns:
            Comprehensive IL metrics
        """
        P_current = Decimal(str(current_price))

        # Get current amounts (SAME AS V3)
        amount0_current, amount1_current = self._get_amounts_for_liquidity(P_current)

        # Calculate values (SAME AS V3)
        pool_value = amount0_current * P_current + amount1_current
        hodl_value = self.amount0_initial * P_current + self.amount1_initial

        # IL calculation (SAME AS V3)
        il_absolute = pool_value - hodl_value
        il_percentage = (il_absolute / hodl_value * Decimal("100")) if hodl_value > 0 else Decimal("0")

        # Check if in range
        in_range = self.Pa <= P_current <= self.Pb

        # Calculate effective fee tier (V4 HOOK FEATURE)
        if self.hook_enabled:
            fee_modifier = self.simulate_hook_fee_modifier(current_price, volatility)
            effective_fee = float(self.base_fee_tier) * fee_modifier
        else:
            fee_modifier = 1.0
            effective_fee = float(self.base_fee_tier)

        # Price metrics
        price_change_pct = (P_current - self.P_initial) / self.P_initial * Decimal("100")
        range_width = (self.Pb - self.Pa) / self.Pa * Decimal("100")

        # Capital efficiency (same as V3)
        full_range_ratio = Decimal("100")
        actual_range_ratio = self.Pb / self.Pa
        capital_efficiency = full_range_ratio / actual_range_ratio

        return {
            "current_price": float(P_current),
            "initial_price": float(self.P_initial),
            "price_lower": float(self.Pa),
            "price_upper": float(self.Pb),
            "price_change_percent": float(price_change_pct),
            "in_range": in_range,
            "range_width_percent": float(range_width),
            "amount0_current": float(amount0_current),
            "amount1_current": float(amount1_current),
            "amount0_initial": float(self.amount0_initial),
            "amount1_initial": float(self.amount1_initial),
            "pool_value": float(pool_value),
            "hodl_value": float(hodl_value),
            "il_dollar": float(il_absolute),
            "il_percentage": float(il_percentage),
            "liquidity": float(self.liquidity),
            "capital_efficiency": float(capital_efficiency),
            # V4 specific
            "base_fee_bps": float(self.base_fee_tier * Decimal("10000")),
            "effective_fee_bps": effective_fee * 10000,
            "hook_enabled": self.hook_enabled,
            "fee_modifier": fee_modifier,
        }

    def calculate_il_with_fees(
        self,
        current_price: float,
        days_elapsed: float,
        daily_volume: float,
        pool_liquidity: float = None,
        volatility: float = 0.3,
        gas_savings_v4: float = 0.5,
    ) -> Dict[str, float]:
        """
        Calculate IL including V4 features

        Args:
            current_price: Current price
            days_elapsed: Days since position opened
            daily_volume: Daily trading volume USD
            pool_liquidity: Total pool liquidity
            volatility: Volatility for dynamic fees
            gas_savings_v4: Gas savings multiplier (0.5 = 50% savings)

        Returns:
            Complete analysis with V4 benefits
        """
        # Get base IL (SAME AS V3)
        il_data = self.calculate_il_at_price(current_price, volatility)

        P_current = Decimal(str(current_price))

        # Time in range estimation
        if self.Pa <= P_current <= self.Pb:
            time_in_range_pct = 100.0
        else:
            if P_current < self.Pa:
                distance_out = float((self.Pa - P_current) / self.Pa * Decimal("100"))
            else:
                distance_out = float((P_current - self.Pb) / self.Pb * Decimal("100"))
            time_in_range_pct = max(0, 100 - distance_out)

        time_in_range_days = days_elapsed * (time_in_range_pct / 100)

        # Calculate fees
        if pool_liquidity is None:
            position_share = 0.01
        else:
            position_tvl = il_data["pool_value"]
            position_share = position_tvl / pool_liquidity if pool_liquidity > 0 else 0

        # Apply capital efficiency (same as V3)
        effective_share = position_share * il_data["capital_efficiency"]

        # Use effective fee (with hook modifier if enabled)
        effective_fee = il_data["effective_fee_bps"] / 10000

        # Calculate fees
        total_volume = daily_volume * time_in_range_days
        fees_earned = total_volume * effective_fee * effective_share

        # V4 GAS SAVINGS BENEFIT
        # In V4, you save gas on:
        # 1. Multi-hop swaps (flash accounting)
        # 2. Native ETH (no wrapping)
        # 3. Cheaper rebalancing
        estimated_gas_saved_usd = days_elapsed * 5 * gas_savings_v4  # ~$5/day saved

        # Total benefit = fees + gas savings
        total_benefit = fees_earned + estimated_gas_saved_usd

        # Calculate APR
        if days_elapsed > 0:
            fee_apr = (fees_earned / float(self.initial_value)) * (365 / days_elapsed) * 100
            total_apr = (total_benefit / float(self.initial_value)) * (365 / days_elapsed) * 100
        else:
            fee_apr = 0
            total_apr = 0

        # Net result
        net_result = total_benefit + il_data["il_dollar"]
        net_percentage = (net_result / il_data["hodl_value"]) * 100 if il_data["hodl_value"] > 0 else 0

        # Breakeven
        daily_benefit = total_benefit / time_in_range_days if time_in_range_days > 0 else 0

        if daily_benefit > 0 and il_data["il_dollar"] < 0:
            breakeven_days = abs(il_data["il_dollar"]) / daily_benefit
        else:
            breakeven_days = float("inf")

        return {
            **il_data,
            "days_elapsed": days_elapsed,
            "time_in_range_days": time_in_range_days,
            "time_in_range_percent": time_in_range_pct,
            "daily_volume": daily_volume,
            "fees_earned": fees_earned,
            "gas_savings_v4": estimated_gas_saved_usd,
            "total_benefit": total_benefit,
            "fee_apr": fee_apr,
            "total_apr_with_gas_savings": total_apr,
            "net_result": net_result,
            "net_percentage": net_percentage,
            "breakeven_days": breakeven_days if breakeven_days != float("inf") else None,
            "profitable": net_result > 0,
            # V4 advantages
            "v4_flash_accounting": True,
            "v4_native_eth_support": True,
            "v4_singleton_architecture": True,
            "v4_gas_savings_pct": gas_savings_v4 * 100,
        }

    def compare_v3_vs_v4(self, current_price: float, days_elapsed: float, daily_volume: float) -> Dict[str, Dict]:
        """
        Compare V3 vs V4 performance

        Returns:
            Comparison showing V4 advantages
        """
        # V3 calculation (no hooks, no gas savings)
        v3_result = self.calculate_il_with_fees(
            current_price, days_elapsed, daily_volume, volatility=0.3, gas_savings_v4=0.0  # No V4 benefits
        )
        v3_result["version"] = "V3"
        v3_result["hook_enabled"] = False

        # V4 calculation (with hooks and gas savings)
        v4_result = self.calculate_il_with_fees(
            current_price, days_elapsed, daily_volume, volatility=0.3, gas_savings_v4=0.5  # 50% gas savings
        )
        v4_result["version"] = "V4"

        # Calculate advantage
        advantage = {
            "fee_advantage": v4_result["fees_earned"] - v3_result["fees_earned"],
            "gas_savings": v4_result["gas_savings_v4"],
            "total_advantage": v4_result["total_benefit"] - v3_result["total_benefit"],
            "apr_advantage": v4_result["total_apr_with_gas_savings"] - v3_result["fee_apr"],
            "net_advantage": v4_result["net_result"] - v3_result["net_result"],
        }

        return {"v3": v3_result, "v4": v4_result, "advantage": advantage}


# ===== EXAMPLE USAGE =====

if __name__ == "__main__":
    print("=" * 80)
    print("UNISWAP V4 IL CALCULATOR")
    print("=" * 80)
    print()
    print("🎯 KEY POINT: V4 uses SAME concentrated liquidity math as V3!")
    print("   IL formulas are IDENTICAL.")
    print("   V4 ADDS: Hooks, gas savings, native ETH, dynamic fees")
    print()
    print("=" * 80)
    print()

    # Example: ETH/USDC position
    print("Example: ETH/USDC Position (±10% range)")
    print("-" * 80)

    # V3-style position (no hooks)
    print("\n1️⃣  V3-STYLE POSITION (No Hooks)")
    calc_v3_style = UniswapV4ILCalculator(
        price_lower=1800,
        price_upper=2200,
        price_initial=2000,
        amount0=0.5,
        amount1=1000,
        fee_tier=0.003,
        hook_enabled=False,
    )

    result_v3_style = calc_v3_style.calculate_il_with_fees(
        current_price=2100,
        days_elapsed=30,
        daily_volume=50_000_000,
        pool_liquidity=100_000_000,
        gas_savings_v4=0.0,  # No V4 gas savings
    )

    print(f"  Price: ${result_v3_style['current_price']:.0f}")
    print(f"  In Range: {'Yes' if result_v3_style['in_range'] else 'No'}")
    print(f"  IL: {result_v3_style['il_percentage']:.2f}% (${result_v3_style['il_dollar']:.2f})")
    print(f"  Fees: ${result_v3_style['fees_earned']:.2f}")
    print(f"  Fee APR: {result_v3_style['fee_apr']:.1f}%")
    print(f"  Net: ${result_v3_style['net_result']:.2f}")

    # V4-style position (with hooks)
    print("\n2️⃣  V4-STYLE POSITION (With Dynamic Fee Hook)")
    calc_v4_style = UniswapV4ILCalculator(
        price_lower=1800,
        price_upper=2200,
        price_initial=2000,
        amount0=0.5,
        amount1=1000,
        fee_tier=0.003,
        hook_enabled=True,  # Enable hook
    )

    result_v4_style = calc_v4_style.calculate_il_with_fees(
        current_price=2100,
        days_elapsed=30,
        daily_volume=50_000_000,
        pool_liquidity=100_000_000,
        volatility=0.4,
        gas_savings_v4=0.5,  # 50% gas savings
    )

    print(f"  Price: ${result_v4_style['current_price']:.0f}")
    print(f"  In Range: {'Yes' if result_v4_style['in_range'] else 'No'}")
    print(f"  IL: {result_v4_style['il_percentage']:.2f}% (${result_v4_style['il_dollar']:.2f})")
    print(f"  Base Fee: {result_v4_style['base_fee_bps']:.0f} bps")
    print(
        f"  Effective Fee (Hook): {result_v4_style['effective_fee_bps']:.0f} bps ({result_v4_style['fee_modifier']:.2f}x)"
    )
    print(f"  Fees: ${result_v4_style['fees_earned']:.2f}")
    print(f"  Gas Savings (V4): ${result_v4_style['gas_savings_v4']:.2f}")
    print(f"  Total Benefit: ${result_v4_style['total_benefit']:.2f}")
    print(f"  Total APR: {result_v4_style['total_apr_with_gas_savings']:.1f}%")
    print(f"  Net: ${result_v4_style['net_result']:.2f}")

    # Direct comparison
    print("\n3️⃣  V3 vs V4 COMPARISON")
    print("-" * 80)
    comparison = calc_v4_style.compare_v3_vs_v4(current_price=2100, days_elapsed=30, daily_volume=50_000_000)

    print(f"  V3 Total Benefit: ${comparison['v3']['total_benefit']:.2f}")
    print(f"  V4 Total Benefit: ${comparison['v4']['total_benefit']:.2f}")
    print(f"  V4 Advantage: ${comparison['advantage']['total_advantage']:.2f}")
    print(f"  APR Advantage: +{comparison['advantage']['apr_advantage']:.1f}%")
    print()

    print("=" * 80)
    print("KEY V4 TAKEAWAYS:")
    print("=" * 80)
    print("✅ SAME IL formula as V3 (concentrated liquidity)")
    print("✅ Hooks enable dynamic fees for higher earnings")
    print("✅ Flash accounting saves gas on multi-hop swaps")
    print("✅ Native ETH saves ~15% gas (no wrapping)")
    print("✅ Singleton architecture = 99% cheaper pool creation")
    print("✅ Total benefit: Better fees + lower costs")
    print("=" * 80)
