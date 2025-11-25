import csv
import math
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

# ============================================================================
# UNISWAP V3 MATHEMATICAL FORMULAS
# ============================================================================
"""
UNISWAP V3 KEY DIFFERENCES FROM V2:

1. CONCENTRATED LIQUIDITY:
   - Liquidity provided within specific price range [Pa, Pb]
   - Higher capital efficiency within range
   - Zero fees earned when price is out of range

2. TICK-BASED PRICING:
   - Prices are discrete: P(tick) = 1.0001^tick
   - Liquidity is aggregated at tick boundaries
   
3. LIQUIDITY CALCULATION:
   L = Δy / (√Pb - √Pa)  (when price is above range)
   L = Δx * √Pa * √Pb / (√Pb - √Pa)  (when price is below range)
   
4. TOKEN AMOUNTS AT PRICE P:
   x = L * (1/√P - 1/√Pb)  (amount of token0)
   y = L * (√P - √Pa)      (amount of token1)
   
5. IMPERMANENT LOSS (V3):
   IL depends on price range width and current price position
   More concentrated = higher IL risk but higher fee APR
   
6. FEE CALCULATION:
   Fees only earned when price is in range [Pa, Pb]
   Fee APR = (Volume * Fee_Tier * Time_In_Range) / Liquidity
"""

@dataclass
class V3Position:
    """Represents a concentrated liquidity position in Uniswap V3"""
    name: str
    price_lower: float  # Lower bound of price range
    price_upper: float  # Upper bound of price range
    price_current: float  # Current price
    amount0_deposited: float  # Token0 deposited
    amount1_deposited: float  # Token1 deposited
    fee_tier: float = 0.003  # 0.3% default
    days_elapsed: int = 30
    daily_volume_usd: float = 1_000_000
    pool_tvl_usd: float = 10_000_000

class UniswapV3Math:
    """Core Uniswap V3 mathematical functions"""
    
    @staticmethod
    def price_to_tick(price: float) -> int:
        """Convert price to tick (discrete price levels in V3)"""
        return int(math.log(price, 1.0001))
    
    @staticmethod
    def tick_to_price(tick: int) -> float:
        """Convert tick to price"""
        return 1.0001 ** tick
    
    @staticmethod
    def price_to_sqrt_price(price: float) -> float:
        """Convert price to sqrt price (V3 internal representation)"""
        return math.sqrt(price)
    
    @staticmethod
    def sqrt_price_to_price(sqrt_price: float) -> float:
        """Convert sqrt price to price"""
        return sqrt_price ** 2
    
    @staticmethod
    def calculate_liquidity(amount0: float, amount1: float, 
                          price_lower: float, price_upper: float,
                          price_current: float) -> float:
        """
        Calculate liquidity L for a V3 position
        
        The formula depends on where current price is relative to range
        """
        sqrt_price_lower = math.sqrt(price_lower)
        sqrt_price_upper = math.sqrt(price_upper)
        sqrt_price_current = math.sqrt(price_current)
        
        if price_current <= price_lower:
            # Price below range - only token0
            if amount0 > 0:
                liquidity = amount0 * sqrt_price_lower * sqrt_price_upper / (sqrt_price_upper - sqrt_price_lower)
            else:
                liquidity = 0
                
        elif price_current >= price_upper:
            # Price above range - only token1
            if amount1 > 0:
                liquidity = amount1 / (sqrt_price_upper - sqrt_price_lower)
            else:
                liquidity = 0
                
        else:
            # Price in range - both tokens
            liquidity_from_0 = amount0 * sqrt_price_current * sqrt_price_upper / (sqrt_price_upper - sqrt_price_current)
            liquidity_from_1 = amount1 / (sqrt_price_current - sqrt_price_lower)
            liquidity = min(liquidity_from_0, liquidity_from_1)
        
        return liquidity
    
    @staticmethod
    def calculate_amounts(liquidity: float, price_lower: float, 
                         price_upper: float, price_current: float) -> tuple:
        """
        Calculate token amounts from liquidity
        
        Returns: (amount0, amount1)
        """
        sqrt_price_lower = math.sqrt(price_lower)
        sqrt_price_upper = math.sqrt(price_upper)
        sqrt_price_current = math.sqrt(price_current)
        
        if price_current <= price_lower:
            # All token0
            amount0 = liquidity * (sqrt_price_upper - sqrt_price_lower) / (sqrt_price_lower * sqrt_price_upper)
            amount1 = 0
            
        elif price_current >= price_upper:
            # All token1
            amount0 = 0
            amount1 = liquidity * (sqrt_price_upper - sqrt_price_lower)
            
        else:
            # Both tokens
            amount0 = liquidity * (sqrt_price_upper - sqrt_price_current) / (sqrt_price_current * sqrt_price_upper)
            amount1 = liquidity * (sqrt_price_current - sqrt_price_lower)
        
        return amount0, amount1

class UniswapV3Calculator:
    """Advanced V3 calculations including concentrated liquidity IL"""
    
    @staticmethod
    def calculate_v3_il(position: V3Position) -> Dict:
        """
        Calculate impermanent loss for V3 concentrated position
        
        V3 IL is more complex due to price ranges:
        - IL is 0 when price stays in range
        - IL increases as price moves out of range
        - More concentrated positions have higher IL
        """
        Pa = position.price_lower
        Pb = position.price_upper
        P = position.price_current
        
        # Calculate initial deposit value
        initial_value = position.amount0_deposited * P + position.amount1_deposited
        
        # Calculate liquidity
        math_helper = UniswapV3Math()
        L = math_helper.calculate_liquidity(
            position.amount0_deposited,
            position.amount1_deposited,
            Pa, Pb, P
        )
        
        # Calculate current amounts in pool
        amount0_now, amount1_now = math_helper.calculate_amounts(L, Pa, Pb, P)
        
        # Current pool value
        current_value = amount0_now * P + amount1_now
        
        # HODL value (if never deposited)
        hodl_value = position.amount0_deposited * P + position.amount1_deposited
        
        # Impermanent Loss
        il_dollar = current_value - hodl_value
        il_percent = (il_dollar / hodl_value * 100) if hodl_value > 0 else 0
        
        # Check if position is in range
        in_range = Pa <= P <= Pb
        
        # Calculate time in range (simplified - assumes always in range for this example)
        time_in_range_percent = 100 if in_range else 0
        
        # Fee calculations
        # Fees only earned when in range
        if in_range:
            position_tvl = current_value
            pool_share = position_tvl / position.pool_tvl_usd if position.pool_tvl_usd > 0 else 0
            
            # V3 concentrates liquidity, so effective share is higher
            range_factor = calculate_range_factor(Pa, Pb, P)
            effective_share = pool_share * range_factor
            
            daily_fees = position.daily_volume_usd * position.fee_tier * effective_share
            total_fees = daily_fees * position.days_elapsed
        else:
            daily_fees = 0
            total_fees = 0
        
        # Net result
        net_result = total_fees + il_dollar  # il_dollar is negative for loss
        
        # Breakeven
        if daily_fees > 0 and il_dollar < 0:
            breakeven_days = abs(il_dollar) / daily_fees
        else:
            breakeven_days = float('inf')
        
        # Calculate range width
        range_width_percent = ((Pb - Pa) / Pa) * 100
        
        return {
            'position_name': position.name,
            'price_lower': Pa,
            'price_upper': Pb,
            'price_current': P,
            'in_range': in_range,
            'range_width_percent': round(range_width_percent, 2),
            'liquidity': round(L, 2),
            'amount0_current': round(amount0_now, 6),
            'amount1_current': round(amount1_now, 2),
            'current_value': round(current_value, 2),
            'hodl_value': round(hodl_value, 2),
            'il_dollar': round(il_dollar, 2),
            'il_percent': round(il_percent, 4),
            'daily_fees': round(daily_fees, 2),
            'total_fees': round(total_fees, 2),
            'net_result': round(net_result, 2),
            'breakeven_days': round(breakeven_days, 2) if breakeven_days != float('inf') else 'N/A',
            'profitable': 'Yes' if net_result > 0 else 'No',
            'fee_tier': position.fee_tier * 100  # Convert to percentage
        }

def calculate_range_factor(price_lower: float, price_upper: float, 
                          price_current: float) -> float:
    """
    Calculate capital efficiency factor for concentrated liquidity
    
    Tighter ranges = higher capital efficiency = more fees per dollar
    """
    # Full range would be price_upper / price_lower approaching infinity
    # Typical full range might be 100x
    full_range_ratio = 100
    actual_range_ratio = price_upper / price_lower
    
    # Capital efficiency is inversely proportional to range width
    range_factor = full_range_ratio / actual_range_ratio
    
    return min(range_factor, 100)  # Cap at 100x

# ============================================================================
# TEST POSITIONS: V3 SCENARIOS
# ============================================================================

def generate_v3_test_positions() -> List[V3Position]:
    """Generate realistic V3 positions with different strategies"""
    
    positions = [
        # 1. Tight Range (±5%) - High risk, high reward
        V3Position(
            name="ETH/USDC: Tight ±5% Range",
            price_lower=1900,
            price_upper=2100,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            pool_tvl_usd=100_000_000
        ),
        
        # 2. Medium Range (±20%)
        V3Position(
            name="ETH/USDC: Medium ±20% Range",
            price_lower=1600,
            price_upper=2400,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            pool_tvl_usd=100_000_000
        ),
        
        # 3. Wide Range (±50%)
        V3Position(
            name="ETH/USDC: Wide ±50% Range",
            price_lower=1000,
            price_upper=3000,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            pool_tvl_usd=100_000_000
        ),
        
        # 4. Out of Range (above)
        V3Position(
            name="ETH/USDC: Out of Range (Price Too High)",
            price_lower=1000,
            price_upper=1500,
            price_current=2000,
            amount0_deposited=0,
            amount1_deposited=2000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            pool_tvl_usd=100_000_000
        ),
        
        # 5. Out of Range (below)
        V3Position(
            name="ETH/USDC: Out of Range (Price Too Low)",
            price_lower=2500,
            price_upper=3500,
            price_current=2000,
            amount0_deposited=1.0,
            amount1_deposited=0,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            pool_tvl_usd=100_000_000
        ),
        
        # 6. Stablecoin Tight Range
        V3Position(
            name="USDC/USDT: Ultra-Tight ±0.1%",
            price_lower=0.999,
            price_upper=1.001,
            price_current=1.0,
            amount0_deposited=10000,
            amount1_deposited=10000,
            fee_tier=0.0001,  # 0.01% fee tier
            days_elapsed=90,
            daily_volume_usd=500_000_000,
            pool_tvl_usd=1_000_000_000
        ),
        
        # 7. High Fee Tier Position
        V3Position(
            name="SHIB/USDC: High Vol ±100% (1% fee)",
            price_lower=0.0005,
            price_upper=0.0015,
            price_current=0.001,
            amount0_deposited=1_000_000,
            amount1_deposited=1000,
            fee_tier=0.01,  # 1% fee tier
            days_elapsed=20,
            daily_volume_usd=20_000_000,
            pool_tvl_usd=50_000_000
        ),
        
        # 8. Price at Lower Bound
        V3Position(
            name="ETH/USDC: At Lower Bound",
            price_lower=2000,
            price_upper=3000,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            pool_tvl_usd=100_000_000
        ),
        
        # 9. Price at Upper Bound
        V3Position(
            name="ETH/USDC: At Upper Bound",
            price_lower=1000,
            price_upper=2000,
            price_current=2000,
            amount0_deposited=0,
            amount1_deposited=2000,
            fee_tier=0.003,
            days_elapsed=30,
            daily_volume_usd=50_000_000,
            pool_tvl_usd=100_000_000
        ),
        
        # 10. Asymmetric Range
        V3Position(
            name="ETH/USDC: Asymmetric Range",
            price_lower=1800,
            price_upper=2600,
            price_current=2000,
            amount0_deposited=0.5,
            amount1_deposited=1000,
            fee_tier=0.0005,  # 0.05% fee tier
            days_elapsed=45,
            daily_volume_usd=75_000_000,
            pool_tvl_usd=150_000_000
        ),
    ]
    
    return positions

def export_results_to_csv(results: List[Dict], filename: str = "uniswap_v3_results.csv"):
    """Export V3 analysis results to CSV"""
    if not results:
        return
    
    keys = results[0].keys()
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n✅ Results exported to {filename}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*100)
    print("UNISWAP V3 - CONCENTRATED LIQUIDITY IL CALCULATOR")
    print("="*100)
    print()
    
    # Generate V3 test positions
    positions = generate_v3_test_positions()
    calculator = UniswapV3Calculator()
    
    # Analyze all positions
    results = []
    print(f"{'Position':<40} {'Range':>12} {'In?':>5} {'IL %':>10} {'IL $':>12} {'Fees':>12} {'Net $':>12} {'Result':>10}")
    print("-" * 135)
    
    for position in positions:
        result = calculator.calculate_v3_il(position)
        results.append(result)
        
        range_str = f"{result['price_lower']:.0f}-{result['price_upper']:.0f}"
        in_range_str = "✓" if result['in_range'] else "✗"
        
        print(f"{result['position_name']:<40} {range_str:>12} {in_range_str:>5} "
              f"{result['il_percent']:>9.2f}% ${result['il_dollar']:>11,.2f} "
              f"${result['total_fees']:>11,.2f} ${result['net_result']:>11,.2f} "
              f"{result['profitable']:>10}")
    
    print("-" * 135)
    print()
    
    # Summary statistics
    in_range_positions = sum(1 for r in results if r['in_range'])
    profitable_count = sum(1 for r in results if r['profitable'] == 'Yes')
    avg_il = sum(r['il_percent'] for r in results) / len(results)
    avg_fees = sum(r['total_fees'] for r in results) / len(results)
    avg_net = sum(r['net_result'] for r in results) / len(results)
    
    print(f"SUMMARY STATISTICS (UNISWAP V3)")
    print(f"  Total Positions: {len(results)}")
    print(f"  Positions In Range: {in_range_positions}/{len(results)}")
    print(f"  Profitable Positions: {profitable_count}/{len(results)}")
    print(f"  Average IL: {avg_il:.2f}%")
    print(f"  Average Fees Earned: ${avg_fees:,.2f}")
    print(f"  Average Net Result: ${avg_net:,.2f}")
    print()
    
    print("KEY V3 INSIGHTS:")
    print("  • Tighter ranges = Higher capital efficiency = More fees per $")
    print("  • Tighter ranges = Higher IL risk if price moves out of range")
    print("  • Out of range positions earn ZERO fees")
    print("  • Optimal range depends on: volatility, fee tier, rebalancing cost")
    print()
    
    # Export to CSV
    export_results_to_csv(results)

"""
uniswap_v3_formulas.py:

Core V3 math (sqrt pricing, liquidity calculations)
10 test scenarios comparing tight/medium/wide ranges
Shows impact of being in/out of range on fees
I'll help you update these Uniswap V2 scripts to V3. Uniswap V3 introduces concentrated liquidity, which fundamentally changes the math. Here are the key differences:
Key Changes from V2 to V3:

Concentrated Liquidity: LPs can provide liquidity within custom price ranges
Multiple Fee Tiers: 0.01%, 0.05%, 0.3%, 1%
Non-Fungible Positions: Each position is unique (NFT-based)
Different IL Calculations: IL depends on price range, not just price ratio
Active/Inactive Liquidity: Positions can be "in range" or "out of range"
"""
