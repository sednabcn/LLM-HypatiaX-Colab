import math


class UniswapV2Pool:
    """Simplified Uniswap V2 pool for LP token calculations"""

    def __init__(self):
        self.reserve0 = 0  # Token0 (e.g., ETH)
        self.reserve1 = 0  # Token1 (e.g., USDC)
        self.total_supply = 0  # Total LP tokens
        self.MINIMUM_LIQUIDITY = 1000  # Burned on first mint

    def mint_lp_tokens(self, amount0, amount1):
        """
        Calculate LP tokens to mint when adding liquidity

        Args:
            amount0: Amount of token0 to deposit
            amount1: Amount of token1 to deposit

        Returns:
            Number of LP tokens to mint
        """

        if self.total_supply == 0:
            # First liquidity provision
            liquidity = math.sqrt(amount0 * amount1)
            self.MINIMUM_LIQUIDITY = min(
                min(amount0, amount1) / 10, self.MINIMUM_LIQUIDITY
            )

            # Uniswap burns MINIMUM_LIQUIDITY tokens on first mint
            # This protects against inflation attacks
            liquidity -= self.MINIMUM_LIQUIDITY

            # Update pool state
            self.reserve0 = amount0
            self.reserve1 = amount1
            self.total_supply = liquidity + self.MINIMUM_LIQUIDITY

            return liquidity

        else:
            # Subsequent liquidity provision
            # Calculate based on proportion to existing reserves
            liquidity0 = (amount0 * self.total_supply) / self.reserve0
            liquidity1 = (amount1 * self.total_supply) / self.reserve1

            # Take minimum to maintain pool ratio
            liquidity = min(liquidity0, liquidity1)

            # Update pool state
            self.reserve0 += amount0
            self.reserve1 += amount1
            self.total_supply += liquidity

            return liquidity

    def burn_lp_tokens(self, lp_tokens):
        """
        Calculate token amounts when removing liquidity

        Args:
            lp_tokens: Number of LP tokens to burn

        Returns:
            Tuple of (amount0, amount1) to withdraw
        """

        # Calculate proportional share
        amount0 = (lp_tokens * self.reserve0) / self.total_supply
        amount1 = (lp_tokens * self.reserve1) / self.total_supply

        # Update pool state
        self.reserve0 -= amount0
        self.reserve1 -= amount1
        self.total_supply -= lp_tokens

        return amount0, amount1

    def get_pool_state(self):
        """Get current pool state"""
        return {
            "reserve0": self.reserve0,
            "reserve1": self.reserve1,
            "total_supply": self.total_supply,
            "k": self.reserve0 * self.reserve1,  # Constant product
        }


# Example usage
def example_liquidity_provision():
    """Example of adding liquidity to Uniswap V2 pool"""

    pool = UniswapV2Pool()

    print("=" * 60)
    print("FIRST LIQUIDITY PROVISION (Pool Creation)")
    print("=" * 60)

    # Alice creates the pool
    eth_amount = 10
    usdc_amount = 20000

    alice_lp = pool.mint_lp_tokens(eth_amount, usdc_amount)

    print(f"Alice deposits: {eth_amount} ETH + {usdc_amount} USDC")
    print(f"Alice receives: {alice_lp:.2f} LP tokens")
    print(f"Pool state: {pool.get_pool_state()}")
    print(f"Alice's pool share: {alice_lp / pool.total_supply * 100:.2f}%")

    print("\n" + "=" * 60)
    print("SECOND LIQUIDITY PROVISION")
    print("=" * 60)

    # Bob adds liquidity
    bob_eth = 5
    bob_usdc = 10000

    bob_lp = pool.mint_lp_tokens(bob_eth, bob_usdc)

    print(f"Bob deposits: {bob_eth} ETH + {bob_usdc} USDC")
    print(f"Bob receives: {bob_lp:.2f} LP tokens")
    print(f"Pool state: {pool.get_pool_state()}")
    print(f"Bob's pool share: {bob_lp / pool.total_supply * 100:.2f}%")
    print(f"Alice's pool share: {alice_lp / pool.total_supply * 100:.2f}%")

    print("\n" + "=" * 60)
    print("REMOVING LIQUIDITY")
    print("=" * 60)

    # Alice removes half her liquidity
    alice_withdraw_lp = alice_lp / 2
    eth_out, usdc_out = pool.burn_lp_tokens(alice_withdraw_lp)

    print(f"Alice burns: {alice_withdraw_lp:.2f} LP tokens")
    print(f"Alice receives: {eth_out:.4f} ETH + {usdc_out:.2f} USDC")
    print(f"Pool state: {pool.get_pool_state()}")

    # Calculate position values
    eth_price = 2000
    print("\n" + "=" * 60)
    print("POSITION VALUES (ETH @ $2000)")
    print("=" * 60)

    alice_remaining_lp = alice_lp - alice_withdraw_lp

    def calculate_position_value(lp_tokens, pool):
        share = lp_tokens / pool.total_supply
        eth_value = share * pool.reserve0 * eth_price
        usdc_value = share * pool.reserve1
        return eth_value + usdc_value

    alice_value = calculate_position_value(alice_remaining_lp, pool)
    bob_value = calculate_position_value(bob_lp, pool)

    print(f"Alice's remaining position: ${alice_value:,.2f}")
    print(f"Bob's position: ${bob_value:,.2f}")
    print(f"Total pool value: ${(pool.reserve0 * eth_price + pool.reserve1):,.2f}")


# Run example
if __name__ == "__main__":
    example_liquidity_provision()
