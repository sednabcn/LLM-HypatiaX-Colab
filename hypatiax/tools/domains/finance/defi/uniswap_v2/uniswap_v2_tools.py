"""
Uniswap V2 Protocol Tools
=========================
Tools for interacting with and analyzing Uniswap V2 liquidity pools.

This module provides utilities for:
- Price calculations
- Liquidity analysis
- Swap simulations
- Fee calculations
"""

from typing import Tuple, Optional, Dict, List
from decimal import Decimal, getcontext
import math

# Set precision for financial calculations
getcontext().prec = 28


class UniswapV2Pool:
    """
    Represents a Uniswap V2 liquidity pool.
    
    Implements the constant product formula: x * y = k
    where x and y are the reserves of the two tokens.
    """
    
    def __init__(self, reserve0: float, reserve1: float, fee: float = 0.003):
        """
        Initialize a Uniswap V2 pool.
        
        Args:
            reserve0: Reserve amount of token0
            reserve1: Reserve amount of token1
            fee: Trading fee (default 0.3% = 0.003)
        """
        self.reserve0 = Decimal(str(reserve0))
        self.reserve1 = Decimal(str(reserve1))
        self.fee = Decimal(str(fee))
        self.k = self.reserve0 * self.reserve1
        
    def get_spot_price(self, token_in: int = 0) -> float:
        """
        Get the current spot price.
        
        Args:
            token_in: 0 for token0->token1 price, 1 for token1->token0 price
            
        Returns:
            Current spot price
        """
        if token_in == 0:
            return float(self.reserve1 / self.reserve0)
        else:
            return float(self.reserve0 / self.reserve1)
    
    def get_amount_out(self, amount_in: float, token_in: int = 0) -> float:
        """
        Calculate output amount for a given input (including fees).
        
        Args:
            amount_in: Amount of input token
            token_in: 0 for token0 input, 1 for token1 input
            
        Returns:
            Amount of output token received
        """
        amount_in = Decimal(str(amount_in))
        
        if token_in == 0:
            reserve_in = self.reserve0
            reserve_out = self.reserve1
        else:
            reserve_in = self.reserve1
            reserve_out = self.reserve0
        
        # Apply fee
        amount_in_with_fee = amount_in * (Decimal('1') - self.fee)
        
        # Calculate output using constant product formula
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        amount_out = numerator / denominator
        
        return float(amount_out)
    
    def get_amount_in(self, amount_out: float, token_out: int = 1) -> float:
        """
        Calculate required input amount for a desired output (including fees).
        
        Args:
            amount_out: Desired amount of output token
            token_out: 1 for token1 output, 0 for token0 output
            
        Returns:
            Required amount of input token
        """
        amount_out = Decimal(str(amount_out))
        
        if token_out == 1:
            reserve_in = self.reserve0
            reserve_out = self.reserve1
        else:
            reserve_in = self.reserve1
            reserve_out = self.reserve0
        
        # Calculate input using constant product formula
        numerator = reserve_in * amount_out
        denominator = (reserve_out - amount_out) * (Decimal('1') - self.fee)
        amount_in = numerator / denominator
        
        return float(amount_in)
    
    def simulate_swap(self, amount_in: float, token_in: int = 0) -> Dict[str, float]:
        """
        Simulate a swap and return detailed information.
        
        Args:
            amount_in: Amount of input token
            token_in: 0 for token0 input, 1 for token1 input
            
        Returns:
            Dictionary with swap details including price impact
        """
        price_before = self.get_spot_price(token_in)
        amount_out = self.get_amount_out(amount_in, token_in)
        
        # Calculate new reserves after swap
        if token_in == 0:
            new_reserve0 = self.reserve0 + Decimal(str(amount_in))
            new_reserve1 = self.reserve1 - Decimal(str(amount_out))
        else:
            new_reserve0 = self.reserve0 - Decimal(str(amount_out))
            new_reserve1 = self.reserve1 + Decimal(str(amount_in))
        
        # Calculate price after swap
        if token_in == 0:
            price_after = float(new_reserve1 / new_reserve0)
        else:
            price_after = float(new_reserve0 / new_reserve1)
        
        # Calculate price impact
        price_impact = abs((price_after - price_before) / price_before) * 100
        
        # Calculate effective price
        effective_price = amount_out / amount_in if amount_in > 0 else 0
        
        return {
            'amount_in': amount_in,
            'amount_out': amount_out,
            'price_before': price_before,
            'price_after': price_after,
            'price_impact_percent': price_impact,
            'effective_price': effective_price,
            'fee_paid': float(Decimal(str(amount_in)) * self.fee)
        }
    
    def add_liquidity(self, amount0: float, amount1: float) -> Tuple[float, float, float]:
        """
        Calculate liquidity tokens minted for added liquidity.
        
        Args:
            amount0: Amount of token0 to add
            amount1: Amount of token1 to add
            
        Returns:
            Tuple of (liquidity_minted, actual_amount0, actual_amount1)
        """
        amount0 = Decimal(str(amount0))
        amount1 = Decimal(str(amount1))
        
        # Calculate optimal amounts based on current ratio
        ratio = self.reserve1 / self.reserve0
        optimal_amount1 = amount0 * ratio
        
        if optimal_amount1 <= amount1:
            actual_amount0 = amount0
            actual_amount1 = optimal_amount1
        else:
            actual_amount1 = amount1
            actual_amount0 = amount1 / ratio
        
        # Calculate liquidity tokens (simplified)
        total_liquidity = (self.reserve0 * self.reserve1).sqrt()
        liquidity_minted = (actual_amount0 * actual_amount1).sqrt()
        
        return (
            float(liquidity_minted),
            float(actual_amount0),
            float(actual_amount1)
        )
    
    def remove_liquidity(self, liquidity_amount: float) -> Tuple[float, float]:
        """
        Calculate tokens received when removing liquidity.
        
        Args:
            liquidity_amount: Amount of liquidity tokens to burn
            
        Returns:
            Tuple of (amount0, amount1) received
        """
        liquidity_amount = Decimal(str(liquidity_amount))
        total_liquidity = (self.reserve0 * self.reserve1).sqrt()
        
        share = liquidity_amount / total_liquidity
        amount0 = self.reserve0 * share
        amount1 = self.reserve1 * share
        
        return (float(amount0), float(amount1))
    
    def get_pool_info(self) -> Dict[str, float]:
        """
        Get comprehensive pool information.
        
        Returns:
            Dictionary with pool statistics
        """
        return {
            'reserve0': float(self.reserve0),
            'reserve1': float(self.reserve1),
            'k': float(self.k),
            'fee': float(self.fee),
            'price_0_to_1': self.get_spot_price(0),
            'price_1_to_0': self.get_spot_price(1),
            'total_liquidity': float((self.reserve0 * self.reserve1).sqrt())
        }


class UniswapV2Router:
    """
    Router for calculating multi-hop swaps through Uniswap V2 pools.
    """
    
    def __init__(self):
        """Initialize the router with an empty pool registry."""
        self.pools = {}
    
    def add_pool(self, name: str, pool: UniswapV2Pool):
        """
        Add a pool to the router.
        
        Args:
            name: Identifier for the pool
            pool: UniswapV2Pool instance
        """
        self.pools[name] = pool
    
    def get_amounts_out(self, amount_in: float, path: List[str]) -> List[float]:
        """
        Calculate output amounts for a multi-hop swap.
        
        Args:
            amount_in: Initial input amount
            path: List of pool names to route through
            
        Returns:
            List of amounts at each step
        """
        amounts = [amount_in]
        
        for pool_name in path:
            if pool_name not in self.pools:
                raise ValueError(f"Pool {pool_name} not found")
            
            pool = self.pools[pool_name]
            amount_out = pool.get_amount_out(amounts[-1])
            amounts.append(amount_out)
        
        return amounts
    
    def find_arbitrage(self, amount: float, path: List[str]) -> Dict[str, any]:
        """
        Check for arbitrage opportunities in a circular path.
        
        Args:
            amount: Starting amount
            path: Circular path of pool names (must start and end at same token)
            
        Returns:
            Dictionary with arbitrage analysis
        """
        amounts = self.get_amounts_out(amount, path)
        final_amount = amounts[-1]
        profit = final_amount - amount
        profit_percent = (profit / amount) * 100 if amount > 0 else 0
        
        return {
            'initial_amount': amount,
            'final_amount': final_amount,
            'profit': profit,
            'profit_percent': profit_percent,
            'is_profitable': profit > 0,
            'amounts': amounts,
            'path': path
        }
    
    def find_best_path(self, amount_in: float, paths: List[List[str]]) -> Dict[str, any]:
        """
        Find the best path among multiple options.
        
        Args:
            amount_in: Input amount
            paths: List of possible paths (each path is a list of pool names)
            
        Returns:
            Dictionary with best path information
        """
        best_output = 0
        best_path = None
        best_amounts = None
        
        for path in paths:
            try:
                amounts = self.get_amounts_out(amount_in, path)
                output = amounts[-1]
                
                if output > best_output:
                    best_output = output
                    best_path = path
                    best_amounts = amounts
            except Exception as e:
                continue
        
        return {
            'best_path': best_path,
            'input_amount': amount_in,
            'output_amount': best_output,
            'amounts': best_amounts,
            'effective_price': best_output / amount_in if amount_in > 0 else 0
        }


def calculate_price_impact(reserve_in: float, reserve_out: float, 
                          amount_in: float, fee: float = 0.003) -> float:
    """
    Calculate price impact for a swap without creating a pool object.
    
    Args:
        reserve_in: Reserve of input token
        reserve_out: Reserve of output token
        amount_in: Amount being swapped
        fee: Trading fee (default 0.3%)
        
    Returns:
        Price impact as a percentage
    """
    reserve_in = Decimal(str(reserve_in))
    reserve_out = Decimal(str(reserve_out))
    amount_in = Decimal(str(amount_in))
    fee = Decimal(str(fee))
    
    price_before = reserve_out / reserve_in
    
    amount_in_with_fee = amount_in * (Decimal('1') - fee)
    amount_out = (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)
    
    new_reserve_in = reserve_in + amount_in
    new_reserve_out = reserve_out - amount_out
    price_after = new_reserve_out / new_reserve_in
    
    price_impact = abs((price_after - price_before) / price_before) * Decimal('100')
    
    return float(price_impact)


def calculate_minimum_liquidity(amount0: float, amount1: float) -> float:
    """
    Calculate minimum liquidity tokens for initial pool creation.
    
    Args:
        amount0: Amount of token0
        amount1: Amount of token1
        
    Returns:
        Minimum liquidity tokens (sqrt of product)
    """
    amount0 = Decimal(str(amount0))
    amount1 = Decimal(str(amount1))
    
    return float((amount0 * amount1).sqrt())


def calculate_optimal_amounts(desired_amount0: float, desired_amount1: float,
                              reserve0: float, reserve1: float) -> Tuple[float, float]:
    """
    Calculate optimal token amounts for adding liquidity.
    
    Args:
        desired_amount0: Desired amount of token0
        desired_amount1: Desired amount of token1
        reserve0: Current reserve of token0
        reserve1: Current reserve of token1
        
    Returns:
        Tuple of (optimal_amount0, optimal_amount1)
    """
    desired_amount0 = Decimal(str(desired_amount0))
    desired_amount1 = Decimal(str(desired_amount1))
    reserve0 = Decimal(str(reserve0))
    reserve1 = Decimal(str(reserve1))
    
    # Calculate required ratio
    ratio = reserve1 / reserve0
    optimal_amount1 = desired_amount0 * ratio
    
    if optimal_amount1 <= desired_amount1:
        return (float(desired_amount0), float(optimal_amount1))
    else:
        optimal_amount0 = desired_amount1 / ratio
        return (float(optimal_amount0), float(desired_amount1))


# Example usage
if __name__ == "__main__":
    print("Uniswap V2 Pool Simulator")
    print("=" * 60)
    print()
    
    # Create a pool with 1000 ETH and 2,000,000 USDC
    pool = UniswapV2Pool(reserve0=1000, reserve1=2000000, fee=0.003)
    
    print("Pool Info:")
    info = pool.get_pool_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()
    
    # Simulate swapping 10 ETH for USDC
    print("Simulating swap of 10 ETH for USDC:")
    swap_result = pool.simulate_swap(amount_in=10, token_in=0)
    for key, value in swap_result.items():
        print(f"  {key}: {value}")
    print()
    
    # Calculate price impact for different trade sizes
    print("Price Impact Analysis:")
    for amount in [1, 10, 50, 100]:
        impact = calculate_price_impact(1000, 2000000, amount)
        print(f"  {amount} ETH: {impact:.4f}% price impact")
    print()
    
    # Test liquidity operations
    print("Liquidity Operations:")
    liq_minted, amt0, amt1 = pool.add_liquidity(10, 20000)
    print(f"  Adding 10 ETH + 20,000 USDC")
    print(f"  Liquidity minted: {liq_minted:.4f}")
    print(f"  Actual amounts: {amt0:.4f} ETH, {amt1:.4f} USDC")
    print()
    
    # Router example
    print("Multi-hop Routing:")
    router = UniswapV2Router()
    
    # Create ETH->USDC and USDC->DAI pools
    pool_eth_usdc = UniswapV2Pool(1000, 2000000)
    pool_usdc_dai = UniswapV2Pool(2000000, 2000000)
    
    router.add_pool("ETH-USDC", pool_eth_usdc)
    router.add_pool("USDC-DAI", pool_usdc_dai)
    
    amounts = router.get_amounts_out(10, ["ETH-USDC", "USDC-DAI"])
    print(f"  Swapping 10 ETH through ETH->USDC->DAI:")
    print(f"  ETH -> USDC: {amounts[1]:.2f}")
    print(f"  USDC -> DAI: {amounts[2]:.2f}")

