"""
Uniswap V3 Impermanent Loss Calculator
========================================
Calculate IL for concentrated liquidity positions with price ranges.

Key V3 Features:
- Concentrated liquidity within [price_lower, price_upper]
- Multiple fee tiers: 0.01%, 0.05%, 0.3%, 1%
- Positions only earn fees when price is in range
- Higher capital efficiency = higher IL risk
"""

import math
from decimal import Decimal, getcontext
from typing import Dict, List, Tuple

getcontext().prec = 28


class UniswapV3ILCalculator:
    """
    Impermanent Loss calculator for Uniswap V3 concentrated positions
    """

    # V3 Fee Tiers
    FEE_TIERS = {
        'STABLE': 0.0001,   # 0.01% for stablecoin pairs
        'LOW': 0.0005,      # 0.05% for correlated pairs
        'MEDIUM': 0.003,    # 0.3% for most pairs
        'HIGH': 0.01        # 1% for exotic/volatile pairs
    }

    def __init__(self, price_lower: float, price_upper: float,
                 price_initial: float, amount0: float, amount1: float,
                 fee_tier: float = 0.003):
        """
        Initialize V3 position

        Args:
            price_lower: Lower price bound (Pa)
            price_upper: Upper price bound (Pb)
            price_initial: Initial price when position created
            amount0: Initial token0 amount deposited
            amount1: Initial token1 amount deposited
            fee_tier: Fee tier (0.0001, 0.0005, 0.003, or 0.01)
        """
        self.Pa = Decimal(str(price_lower))
        self.Pb = Decimal(str(price_upper))
        self.P_initial = Decimal(str(price_initial))
        self.amount0_initial = Decimal(str(amount0))
        self.amount1_initial = Decimal(str(amount1))
        self.fee_tier = Decimal(str(fee_tier))

        # Validate range
        if not (self.Pa < self.Pb):
            raise ValueError("price_lower must be less than price_upper")

        if not (self.Pa <= self.P_initial <= self.Pb):
            print(f"WARNING: Initial price {price_initial} is outside range [{price_lower}, {price_upper}]")

        # Calculate initial liquidity
        self.liquidity = self._calculate_liquidity(
            self.amount0_initial, self.amount1_initial, self.P_initial
        )

        # Calculate initial value
        self.initial_value = self.amount0_initial * self.P_initial + self.amount1_initial

    def _sqrt_price(self, price: Decimal) -> Decimal:
        """Calculate square root of price"""
        return price.sqrt()

    def _calculate_liquidity(self, amount0: Decimal, amount1: Decimal,
                            price: Decimal) -> Decimal:
        """
        Calculate liquidity L for a V3 position

        Formulas:
        - If P <= Pa: L = Δx * √Pa * √Pb / (√Pb - √Pa)
        - If P >= Pb: L = Δy / (√Pb - √Pa)
        - If Pa < P < Pb: L = min(L0, L1) from both tokens
        """
        sqrt_Pa = self._sqrt_price(self.Pa)
        sqrt_Pb = self._sqrt_price(self.Pb)
        sqrt_P = self._sqrt_price(price)

        if price <= self.Pa:
            # All token0
            if amount0 > 0:
                liquidity = amount0 * sqrt_Pa * sqrt_Pb / (sqrt_Pb - sqrt_Pa)
            else:
                liquidity = Decimal('0')

        elif price >= self.Pb:
            # All token1
            if amount1 > 0:
                liquidity = amount1 / (sqrt_Pb - sqrt_Pa)
            else:
                liquidity = Decimal('0')

        else:
            # Both tokens - in range
            if amount0 > 0:
                L0 = amount0 * sqrt_P * sqrt_Pb / (sqrt_Pb - sqrt_P)
            else:
                L0 = Decimal('inf')

            if amount1 > 0:
                L1 = amount1 / (sqrt_P - sqrt_Pa)
            else:
                L1 = Decimal('inf')

            liquidity = min(L0, L1)

        return liquidity

    def _get_amounts_for_liquidity(self, price: Decimal) -> Tuple[Decimal, Decimal]:
        """
        Calculate token amounts for given liquidity and price

        Returns: (amount0, amount1)
        """
        sqrt_Pa = self._sqrt_price(self.Pa)
        sqrt_Pb = self._sqrt_price(self.Pb)
        sqrt_P = self._sqrt_price(price)

        if price <= self.Pa:
            # All token0
            amount0 = self.liquidity * (sqrt_Pb - sqrt_Pa) / (sqrt_Pa * sqrt_Pb)
            amount1 = Decimal('0')

        elif price >= self.Pb:
            # All token1
            amount0 = Decimal('0')
            amount1 = self.liquidity * (sqrt_Pb - sqrt_Pa)

        else:
            # Both tokens
            amount0 = self.liquidity * (sqrt_Pb - sqrt_P) / (sqrt_P * sqrt_Pb)
            amount1 = self.liquidity * (sqrt_P - sqrt_Pa)

        return amount0, amount1

    def calculate_il_at_price(self, current_price: float) -> Dict[str, float]:
        """
        Calculate IL at a specific current price

        Args:
            current_price: Current market price

        Returns:
            Dictionary with comprehensive IL metrics
        """
        P_current = Decimal(str(current_price))

        # Get current amounts in pool
        amount0_current, amount1_current = self._get_amounts_for_liquidity(P_current)

        # Calculate values
        pool_value = amount0_current * P_current + amount1_current
        hodl_value = self.amount0_initial * P_current + self.amount1_initial

        # Impermanent Loss
        il_absolute = pool_value - hodl_value
        il_percentage = (il_absolute / hodl_value * Decimal('100')) if hodl_value > 0 else Decimal('0')

        # Check if in range
        in_range = self.Pa <= P_current <= self.Pb

        # Price metrics
        price_change_pct = (P_current - self.P_initial) / self.P_initial * Decimal('100')

        # Range metrics
        range_width = (self.Pb - self.Pa) / self.Pa * Decimal('100')
        distance_to_lower = (P_current - self.Pa) / self.Pa * Decimal('100')
        distance_to_upper = (self.Pb - P_current) / self.Pb * Decimal('100')

        # Capital efficiency
        full_range_ratio = Decimal('100')  # Assume 100x would be "full range"
        actual_range_ratio = self.Pb / self.Pa
        capital_efficiency = full_range_ratio / actual_range_ratio

        return {
            'current_price': float(P_current),
            'initial_price': float(self.P_initial),
            'price_lower': float(self.Pa),
            'price_upper': float(self.Pb),
            'price_change_percent': float(price_change_pct),
            'in_range': in_range,
            'range_width_percent': float(range_width),
            'distance_to_lower_pct': float(distance_to_lower) if in_range else None,
            'distance_to_upper_pct': float(distance_to_upper) if in_range else None,
            'amount0_current': float(amount0_current),
            'amount1_current': float(amount1_current),
            'amount0_initial': float(self.amount0_initial),
            'amount1_initial': float(self.amount1_initial),
            'pool_value': float(pool_value),
            'hodl_value': float(hodl_value),
            'il_dollar': float(il_absolute),
            'il_percentage': float(il_percentage),
            'liquidity': float(self.liquidity),
            'capital_efficiency': float(capital_efficiency),
            'fee_tier_bps': float(self.fee_tier * Decimal('10000'))
        }

    def calculate_il_with_fees(self, current_price: float,
                               days_elapsed: float,
                               daily_volume: float,
                               pool_liquidity: float = None) -> Dict[str, float]:
        """
        Calculate IL including earned fees

        Args:
            current_price: Current price
            days_elapsed: Days since position opened
            daily_volume: Average daily trading volume in USD
            pool_liquidity: Total pool liquidity (if None, estimated from position)

        Returns:
            Dictionary with IL and fee data
        """
        # Get base IL calculation
        il_data = self.calculate_il_at_price(current_price)

        # Estimate time in range (simplified)
        # In reality, would need historical price data
        P_current = Decimal(str(current_price))

        # Simple heuristic: if price moved outside range, estimate time in range
        if self.Pa <= P_current <= self.Pb:
            time_in_range_pct = 100.0  # Currently in range
        else:
            # Estimate based on how far out of range
            if P_current < self.Pa:
                distance_out = float((self.Pa - P_current) / self.Pa * Decimal('100'))
            else:
                distance_out = float((P_current - self.Pb) / self.Pb * Decimal('100'))

            # Rough estimate: more distance = less time in range
            time_in_range_pct = max(0, 100 - distance_out)

        time_in_range_days = days_elapsed * (time_in_range_pct / 100)

        # Calculate fees earned
        # Fee share based on liquidity contribution
        if pool_liquidity is None:
            # Estimate: assume our position is 1% of pool
            position_share = 0.01
        else:
            position_tvl = il_data['pool_value']
            position_share = position_tvl / pool_liquidity if pool_liquidity > 0 else 0

        # Apply capital efficiency multiplier
        effective_share = position_share * il_data['capital_efficiency']

        # Total fees
        total_volume = daily_volume * time_in_range_days
        fees_earned = total_volume * float(self.fee_tier) * effective_share

        # Calculate APR from fees
        if days_elapsed > 0:
            fee_apr = (fees_earned / float(self.initial_value)) * (365 / days_elapsed) * 100
        else:
            fee_apr = 0

        # Net result
        net_result = fees_earned + il_data['il_dollar']
        net_percentage = (net_result / il_data['hodl_value']) * 100 if il_data['hodl_value'] > 0 else 0

        # Breakeven
        daily_fees = fees_earned / time_in_range_days if time_in_range_days > 0 else 0

        if daily_fees > 0 and il_data['il_dollar'] < 0:
            breakeven_days = abs(il_data['il_dollar']) / daily_fees
        else:
            breakeven_days = float('inf')

        return {
            **il_data,
            'days_elapsed': days_elapsed,
            'time_in_range_days': time_in_range_days,
            'time_in_range_percent': time_in_range_pct,
            'daily_volume': daily_volume,
            'fees_earned': fees_earned,
            'fee_apr': fee_apr,
            'net_result': net_result,
            'net_percentage': net_percentage,
            'breakeven_days': breakeven_days if breakeven_days != float('inf') else None,
            'profitable': net_result > 0
        }

    def compare_ranges(self, current_price: float,
                      range_scenarios: List[Dict]) -> List[Dict]:
        """
        Compare performance across different range scenarios

        Args:
            current_price: Current price
            range_scenarios: List of dicts with 'price_lower' and 'price_upper'

        Returns:
            List of results for each scenario
        """
        results = []

        for scenario in range_scenarios:
            calc = UniswapV3ILCalculator(
                price_lower=scenario['price_lower'],
                price_upper=scenario['price_upper'],
                price_initial=float(self.P_initial),
                amount0=float(self.amount0_initial),
                amount1=float(self.amount1_initial),
                fee_tier=float(self.fee_tier)
            )

            result = calc.calculate_il_with_fees(
                current_price=current_price,
                days_elapsed=scenario.get('days', 30),
                daily_volume=scenario.get('daily_volume', 1_000_000)
            )

            result['scenario_name'] = scenario.get('name', f"Range {scenario['price_lower']}-{scenario['price_upper']}")
            results.append(result)

        return results


def calculate_optimal_range(price_current: float, volatility_annual: float,
                           fee_tier: float = 0.003) -> Dict[str, float]:
    """
    Calculate suggested optimal range based on volatility

    Args:
        price_current: Current price
        volatility_annual: Annual volatility (e.g., 0.80 for 80%)
        fee_tier: Fee tier

    Returns:
        Suggested price range
    """
    # Convert annual volatility to daily
    volatility_daily = volatility_annual / math.sqrt(365)

    # Use 2 standard deviations for range (95% confidence)
    # Adjust based on fee tier (higher fees = wider range tolerance)
    std_devs = 2.0 + (fee_tier / 0.003)  # More std devs for higher fee tiers

    # Calculate range
    price_lower = price_current * (1 - std_devs * volatility_daily * math.sqrt(30))
    price_upper = price_current * (1 + std_devs * volatility_daily * math.sqrt(30))

    range_width = ((price_upper - price_lower) / price_lower) * 100

    return {
        'price_lower': round(price_lower, 2),
        'price_upper': round(price_upper, 2),
        'range_width_percent': round(range_width, 2),
        'volatility_annual': volatility_annual * 100,
        'recommended_for': f"{fee_tier*100}% fee tier"
    }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("UNISWAP V3 CONCENTRATED LIQUIDITY IL CALCULATOR")
    print("=" * 70)
    print()

    # Example: ETH/USDC position
    print("Example: ETH/USDC Position")
    print("-" * 70)

    # Initialize position: ±10% range around $2000
    calculator = UniswapV3ILCalculator(
        price_lower=1800,    # $1800
        price_upper=2200,    # $2200
        price_initial=2000,  # $2000
        amount0=0.5,         # 0.5 ETH
        amount1=1000,        # $1000 USDC
        fee_tier=0.003       # 0.3%
    )

    print(f"Initial Setup:")
    print(f"  Price Range: $1800 - $2200")
    print(f"  Initial Price: $2000")
    print(f"  Deposit: 0.5 ETH + $1000 USDC")
    print(f"  Fee Tier: 0.3%")
    print(f"  Range Width: ±10%")
    print()

    # Scenario 1: Price stays in range
    print("Scenario 1: Price moves to $2100 (still in range)")
    result1 = calculator.calculate_il_with_fees(
        current_price=2100,
        days_elapsed=30,
        daily_volume=50_000_000,
        pool_liquidity=100_000_000
    )
    print(f"  In Range: {'Yes' if result1['in_range'] else 'No'}")
    print(f"  IL: {result1['il_percentage']:.2f}% (${result1['il_dollar']:.2f})")
    print(f"  Fees Earned: ${result1['fees_earned']:.2f}")
    print(f"  Net Result: ${result1['net_result']:.2f}")
    print(f"  Fee APR: {result1['fee_apr']:.1f}%")
    print()

    # Scenario 2: Price moves out of range
    print("Scenario 2: Price moves to $2500 (out of range)")
    result2 = calculator.calculate_il_with_fees(
        current_price=2500,
        days_elapsed=30,
        daily_volume=50_000_000,
        pool_liquidity=100_000_000
    )
    print(f"  In Range: {'Yes' if result2['in_range'] else 'No'}")
    print(f"  IL: {result2['il_percentage']:.2f}% (${result2['il_dollar']:.2f})")
    print(f"  Fees Earned: ${result2['fees_earned']:.2f}")
    print(f"  Net Result: ${result2['net_result']:.2f}")
    print(f"  Time In Range: {result2['time_in_range_percent']:.1f}%")
    print()

    # Compare different ranges
    print("Scenario 3: Comparing Different Range Strategies")
    print("-" * 70)

    scenarios = [
        {'name': 'Tight ±5%', 'price_lower': 1900, 'price_upper': 2100, 'days': 30, 'daily_volume': 50_000_000},
        {'name': 'Medium ±15%', 'price_lower': 1700, 'price_upper': 2300, 'days': 30, 'daily_volume': 50_000_000},
        {'name': 'Wide ±30%', 'price_lower': 1400, 'price_upper': 2600, 'days': 30, 'daily_volume': 50_000_000},
    ]

    comparison = calculator.compare_ranges(
        current_price=2100,
        range_scenarios=scenarios
    )

    print(f"{'Strategy':<15} {'In Range':<10} {'IL%':<10} {'Fees':<12} {'Net $':<12} {'APR%':<10}")
    print("-" * 70)
    for result in comparison:
        print(f"{result['scenario_name']:<15} "
              f"{'Yes' if result['in_range'] else 'No':<10} "
              f"{result['il_percentage']:<9.2f}% "
              f"${result['fees_earned']:<11,.0f} "
              f"${result['net_result']:<11,.0f} "
              f"{result['fee_apr']:<9.1f}%")

    print()
    print("=" * 70)
    print("KEY TAKEAWAYS FOR V3:")
    print("  • Tighter ranges = Higher fees BUT higher IL risk")
    print("  • Out of range positions earn ZERO fees")
    print("  • Optimal range depends on volatility expectations")
    print("  • Active management required to stay profitable")
    print("=" * 70)
"""

🎯 Major V3 Changes:
1. Concentrated Liquidity

V2: Liquidity spread across entire price range (0 to ∞)
V3: Liquidity concentrated in [price_lower, price_upper] range

2. Capital Efficiency

Tighter ranges = Higher capital efficiency = More fees per dollar
Example: ±5% range can earn 20x more fees than full range!

3. Out of Range = No Fees

Critical difference: When price exits your range, you earn ZERO fees
Your position becomes 100% one token

4. Multiple Fee Tiers

0.01% - Stablecoins
0.05% - Correlated assets
0.3% - Most pairs (V2 default)
1% - Exotic/volatile pairs

5. IL Calculation Changes
V3 IL depends on:

Range width (tighter = more IL risk)
Where price is relative to range
Time spent in vs out of range

📊 What the Code Does:
uniswap_v3_formulas.py:

Core V3 math (sqrt pricing, liquidity calculations)
10 test scenarios comparing tight/medium/wide ranges
Shows impact of being in/out of range on fees

uniswap_v3_il_calculator.py:

Detailed IL calculations for concentrated positions
Fee earnings based on time in range
Range comparison tool
Optimal range suggestions based on volatility

🚀 Key Insights from Running:

Tight Range (±5%): High fees but risky - price easily moves out
Wide Range (±50%): Safer but lower capital efficiency
Out of Range: Position becomes 100% one token + NO fees earned
uniswap_v3_il_calculator.py:

Detailed IL calculations for concentrated positions
Fee earnings based on time in range
Range comparison tool
Optimal range suggestions based on volatility

🚀 Key Insights from Running:

Tight Range (±5%): High fees but risky - price easily moves out
Wide Range (±50%): Safer but lower capital efficiency
Out of Range: Position becomes 100% one token + NO fees earned
