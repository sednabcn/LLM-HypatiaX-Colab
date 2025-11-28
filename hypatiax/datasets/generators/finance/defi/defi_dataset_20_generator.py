"""
DeFi Formula Discovery Dataset Generator - Extended to 20 Formulas
"""

import numpy as np
from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem
import os
from datetime import datetime
from typing import Dict, Tuple

class DeFiFormulaGenerator:
    """Generate synthetic DeFi data and discover formulas."""
    
    def __init__(self, domain: str = 'defi', seed: int = 42):
        self.system = HybridDiscoverySystem(domain=domain, max_results=100)
        self.seed = seed
        np.random.seed(seed)
        self.results = []
        
    def generate_formula(self, formula_num, n_samples=100):
        """Generate data for each formula."""
        
        if formula_num == 1:  # Impermanent Loss
            print("\n1. Impermanent Loss")
            price_ratios = np.random.uniform(0.1, 10, (n_samples, 1))
            il = 2 * np.sqrt(price_ratios[:, 0]) / (price_ratios[:, 0] + 1) - 1
            il += np.random.normal(0, 0.01, n_samples)
            
            self.system.discover_validate_interpret(
                X=price_ratios, y=il,
                variable_names=['price_ratio'],
                variable_descriptions={'price_ratio': 'Ratio of current price to initial price'},
                variable_units={'price_ratio': 'dimensionless'},
                description="Impermanent Loss in AMM Pool",
                validate_first=False
            )
            
        elif formula_num == 2:  # AMM Swap Output
            print("\n2. AMM Swap Output")
            amount_in = np.random.uniform(1, 100, n_samples)
            reserve_in = np.random.uniform(1000, 10000, n_samples)
            reserve_out = np.random.uniform(1000, 10000, n_samples)
            X = np.column_stack([amount_in, reserve_in, reserve_out])
            y_out = (amount_in * 0.997 * reserve_out) / (reserve_in + amount_in * 0.997)
            y_out += np.random.normal(0, 0.5, n_samples)
            
            # Normalize
            X[:, 0] /= np.mean(X[:, 0])
            X[:, 1] /= np.mean(X[:, 1])
            X[:, 2] /= np.mean(X[:, 2])
            
            self.system.discover_validate_interpret(
                X=X, y=y_out,
                variable_names=['amount_in_ratio', 'reserve_in_ratio', 'reserve_out_ratio'],
                variable_descriptions={'amount_in_ratio': 'Input amount (normalized)', 
                                      'reserve_in_ratio': 'Input reserve ratio',
                                      'reserve_out_ratio': 'Output reserve ratio'},
                variable_units={'amount_in_ratio': 'dimensionless', 'reserve_in_ratio': 'dimensionless', 
                               'reserve_out_ratio': 'dimensionless'},
                description="Uniswap V2 Swap Output with 0.3% Fee",
                validate_first=False
            )
            
        elif formula_num == 3:  # Utilization Rate
            print("\n3. Utilization Rate")
            borrowed = np.random.uniform(0, 1000, n_samples)
            utilization_target = np.random.uniform(0.3, 0.9, n_samples)
            supplied = borrowed / utilization_target
            X = np.column_stack([borrowed, supplied])
            util = borrowed / supplied + np.random.normal(0, 0.01, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=util,
                variable_names=['borrowed', 'supplied'],
                variable_descriptions={'borrowed': 'Total borrowed', 'supplied': 'Total supplied'},
                variable_units={'borrowed': 'dimensionless', 'supplied': 'dimensionless'},
                description="Lending Pool Utilization Rate",
                validate_first=False
            )
            
        elif formula_num == 4:  # Liquidity Pool Value
            print("\n4. Liquidity Pool Value")
            reserve0 = np.random.uniform(100, 10000, n_samples)
            reserve1 = np.random.uniform(100, 10000, n_samples)
            X = np.column_stack([reserve0, reserve1])
            value = 2 * np.sqrt(reserve0 * reserve1) + np.random.normal(0, 10, n_samples)
            
            X[:, 0] /= np.mean(X[:, 0])
            X[:, 1] /= np.mean(X[:, 1])
            
            self.system.discover_validate_interpret(
                X=X, y=value,
                variable_names=['reserve0_ratio', 'reserve1_ratio'],
                variable_descriptions={'reserve0_ratio': 'Reserve 0 (normalized)', 'reserve1_ratio': 'Reserve 1 (normalized)'},
                variable_units={'reserve0_ratio': 'dimensionless', 'reserve1_ratio': 'dimensionless'},
                description="Constant Product Pool Total Value",
                validate_first=False
            )
            
        elif formula_num == 5:  # Compound Interest Rate
            print("\n5. Compound Interest Rate")
            base_rate = np.random.uniform(0.02, 0.05, n_samples)
            utilization = np.random.uniform(0.3, 0.9, n_samples)
            slope = np.random.uniform(0.05, 0.15, n_samples)
            X = np.column_stack([base_rate, utilization, slope])
            rate = base_rate + slope * utilization + np.random.normal(0, 0.001, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=rate,
                variable_names=['base_rate', 'utilization', 'slope'],
                variable_descriptions={'base_rate': 'Base interest rate', 'utilization': 'Pool utilization', 'slope': 'Rate slope'},
                variable_units={'base_rate': 'dimensionless', 'utilization': 'dimensionless', 'slope': 'dimensionless'},
                description="Compound-style Interest Rate Model",
                validate_first=False
            )
            
        elif formula_num == 6:  # Collateral Ratio
            print("\n6. Collateral Ratio")
            collateral_value = np.random.uniform(1000, 10000, n_samples)
            debt_value = collateral_value * np.random.uniform(0.3, 0.8, n_samples)
            X = np.column_stack([collateral_value, debt_value])
            col_ratio = collateral_value / debt_value + np.random.normal(0, 0.01, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=col_ratio,
                variable_names=['collateral', 'debt'],
                variable_descriptions={'collateral': 'Collateral value', 'debt': 'Debt value'},
                variable_units={'collateral': 'dimensionless', 'debt': 'dimensionless'},
                description="Collateralization Ratio",
                validate_first=False
            )
            
        elif formula_num == 7:  # Liquidation Price
            print("\n7. Liquidation Price")
            entry_price = np.random.uniform(100, 1000, n_samples)
            liq_threshold = np.random.uniform(1.2, 1.5, n_samples)
            X = np.column_stack([entry_price, liq_threshold])
            liq_price = entry_price / liq_threshold + np.random.normal(0, 1, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=liq_price,
                variable_names=['entry_price', 'liq_threshold'],
                variable_descriptions={'entry_price': 'Position entry price', 'liq_threshold': 'Liquidation threshold ratio'},
                variable_units={'entry_price': 'dimensionless', 'liq_threshold': 'dimensionless'},
                description="Liquidation Price for Leveraged Position",
                validate_first=False
            )
            
        elif formula_num == 8:  # Yield Farming APY
            print("\n8. Yield Farming APY")
            rewards_per_block = np.random.uniform(0.1, 5, n_samples)
            blocks_per_year = np.full(n_samples, 2102400)  # ~13s blocks
            total_staked = np.random.uniform(1000, 100000, n_samples)
            X = np.column_stack([rewards_per_block, blocks_per_year, total_staked])
            apy = (rewards_per_block * blocks_per_year) / total_staked + np.random.normal(0, 0.01, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=apy,
                variable_names=['rewards_per_block', 'blocks_per_year', 'total_staked'],
                variable_descriptions={'rewards_per_block': 'Rewards per block', 'blocks_per_year': 'Blocks per year', 
                                      'total_staked': 'Total staked amount'},
                variable_units={'rewards_per_block': 'dimensionless', 'blocks_per_year': 'dimensionless', 
                               'total_staked': 'dimensionless'},
                description="Yield Farming APY Calculation",
                validate_first=False
            )
            
        elif formula_num == 9:  # Slippage
            print("\n9. Slippage")
            amount_in = np.random.uniform(1, 100, n_samples)
            reserve = np.random.uniform(1000, 10000, n_samples)
            X = np.column_stack([amount_in, reserve])
            slippage = amount_in / (reserve + amount_in) + np.random.normal(0, 0.001, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=slippage,
                variable_names=['amount_in', 'reserve'],
                variable_descriptions={'amount_in': 'Input amount', 'reserve': 'Pool reserve'},
                variable_units={'amount_in': 'dimensionless', 'reserve': 'dimensionless'},
                description="Trade Slippage in AMM",
                validate_first=False
            )
            
        elif formula_num == 10:  # LP Token Share
            print("\n10. LP Token Share")
            deposit_amount = np.random.uniform(100, 5000, n_samples)
            total_liquidity = np.random.uniform(10000, 100000, n_samples)
            total_shares = np.random.uniform(1000, 10000, n_samples)
            X = np.column_stack([deposit_amount, total_liquidity, total_shares])
            lp_tokens = (deposit_amount / total_liquidity) * total_shares + np.random.normal(0, 1, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=lp_tokens,
                variable_names=['deposit', 'total_liquidity', 'total_shares'],
                variable_descriptions={'deposit': 'Deposit amount', 'total_liquidity': 'Total pool liquidity', 
                                      'total_shares': 'Total LP shares'},
                variable_units={'deposit': 'dimensionless', 'total_liquidity': 'dimensionless', 'total_shares': 'dimensionless'},
                description="LP Token Share Calculation",
                validate_first=False
            )
            
        elif formula_num == 11:  # Health Factor
            print("\n11. Health Factor")
            collateral = np.random.uniform(1000, 10000, n_samples)
            liquidation_threshold = np.random.uniform(0.75, 0.85, n_samples)
            debt = collateral * np.random.uniform(0.5, 0.9, n_samples)
            X = np.column_stack([collateral, liquidation_threshold, debt])
            health = (collateral * liquidation_threshold) / debt + np.random.normal(0, 0.01, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=health,
                variable_names=['collateral', 'liq_threshold', 'debt'],
                variable_descriptions={'collateral': 'Collateral value', 'liq_threshold': 'Liquidation threshold', 
                                      'debt': 'Debt amount'},
                variable_units={'collateral': 'dimensionless', 'liq_threshold': 'dimensionless', 'debt': 'dimensionless'},
                description="Aave-style Health Factor",
                validate_first=False
            )
            
        elif formula_num == 12:  # Funding Rate
            print("\n12. Funding Rate")
            mark_price = np.random.uniform(100, 1000, n_samples)
            index_price = mark_price * np.random.uniform(0.98, 1.02, n_samples)
            funding_interval = np.full(n_samples, 8)  # 8 hours
            X = np.column_stack([mark_price, index_price, funding_interval])
            funding = (mark_price - index_price) / index_price / funding_interval + np.random.normal(0, 0.0001, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=funding,
                variable_names=['mark_price', 'index_price', 'interval'],
                variable_descriptions={'mark_price': 'Perpetual mark price', 'index_price': 'Spot index price', 
                                      'interval': 'Funding interval (hours)'},
                variable_units={'mark_price': 'dimensionless', 'index_price': 'dimensionless', 'interval': 'dimensionless'},
                description="Perpetual Swap Funding Rate",
                validate_first=False
            )
            
        elif formula_num == 13:  # Price Impact
            print("\n13. Price Impact")
            trade_size = np.random.uniform(10, 500, n_samples)
            liquidity = np.random.uniform(5000, 50000, n_samples)
            X = np.column_stack([trade_size, liquidity])
            impact = (trade_size / liquidity) ** 0.5 + np.random.normal(0, 0.001, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=impact,
                variable_names=['trade_size', 'liquidity'],
                variable_descriptions={'trade_size': 'Trade size', 'liquidity': 'Available liquidity'},
                variable_units={'trade_size': 'dimensionless', 'liquidity': 'dimensionless'},
                description="Price Impact Estimation",
                validate_first=False
            )
            
        elif formula_num == 14:  # Staking Rewards
            print("\n14. Staking Rewards")
            staked_amount = np.random.uniform(100, 5000, n_samples)
            reward_rate = np.random.uniform(0.05, 0.20, n_samples)
            time_staked = np.random.uniform(1, 365, n_samples)
            X = np.column_stack([staked_amount, reward_rate, time_staked])
            rewards = staked_amount * reward_rate * (time_staked / 365) + np.random.normal(0, 1, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=rewards,
                variable_names=['staked', 'rate', 'time_days'],
                variable_descriptions={'staked': 'Staked amount', 'rate': 'Annual reward rate', 'time_days': 'Days staked'},
                variable_units={'staked': 'dimensionless', 'rate': 'dimensionless', 'time_days': 'dimensionless'},
                description="Staking Rewards Calculation",
                validate_first=False
            )
            
        elif formula_num == 15:  # Bonding Curve Price
            print("\n15. Bonding Curve Price")
            supply = np.random.uniform(100, 10000, n_samples)
            reserve_ratio = np.random.uniform(0.1, 0.5, n_samples)
            X = np.column_stack([supply, reserve_ratio])
            price = supply * reserve_ratio + np.random.normal(0, 1, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=price,
                variable_names=['supply', 'reserve_ratio'],
                variable_descriptions={'supply': 'Token supply', 'reserve_ratio': 'Reserve ratio'},
                variable_units={'supply': 'dimensionless', 'reserve_ratio': 'dimensionless'},
                description="Linear Bonding Curve Price",
                validate_first=False
            )
            
        elif formula_num == 16:  # Flash Loan Fee
            print("\n16. Flash Loan Fee")
            loan_amount = np.random.uniform(1000, 100000, n_samples)
            fee_rate = np.random.uniform(0.0005, 0.001, n_samples)
            X = np.column_stack([loan_amount, fee_rate])
            fee = loan_amount * fee_rate + np.random.normal(0, 0.1, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=fee,
                variable_names=['loan_amount', 'fee_rate'],
                variable_descriptions={'loan_amount': 'Flash loan amount', 'fee_rate': 'Fee rate'},
                variable_units={'loan_amount': 'dimensionless', 'fee_rate': 'dimensionless'},
                description="Flash Loan Fee Calculation",
                validate_first=False
            )
            
        elif formula_num == 17:  # Vesting Schedule
            print("\n17. Vesting Schedule")
            total_tokens = np.random.uniform(1000, 100000, n_samples)
            time_elapsed = np.random.uniform(0, 365, n_samples)
            vesting_period = np.full(n_samples, 365)
            X = np.column_stack([total_tokens, time_elapsed, vesting_period])
            vested = total_tokens * (time_elapsed / vesting_period) + np.random.normal(0, 10, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=vested,
                variable_names=['total', 'elapsed', 'period'],
                variable_descriptions={'total': 'Total tokens', 'elapsed': 'Time elapsed (days)', 'period': 'Vesting period (days)'},
                variable_units={'total': 'dimensionless', 'elapsed': 'dimensionless', 'period': 'dimensionless'},
                description="Linear Vesting Schedule",
                validate_first=False
            )
            
        elif formula_num == 18:  # Arbitrage Profit
            print("\n18. Arbitrage Profit")
            price_a = np.random.uniform(100, 1000, n_samples)
            price_b = price_a * np.random.uniform(0.98, 1.05, n_samples)
            trade_size = np.random.uniform(10, 100, n_samples)
            X = np.column_stack([price_a, price_b, trade_size])
            profit = (price_b - price_a) * trade_size + np.random.normal(0, 1, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=profit,
                variable_names=['price_a', 'price_b', 'size'],
                variable_descriptions={'price_a': 'Price on exchange A', 'price_b': 'Price on exchange B', 'size': 'Trade size'},
                variable_units={'price_a': 'dimensionless', 'price_b': 'dimensionless', 'size': 'dimensionless'},
                description="Cross-Exchange Arbitrage Profit",
                validate_first=False
            )
            
        elif formula_num == 19:  # Gas Cost ROI
            print("\n19. Gas Cost ROI")
            profit = np.random.uniform(10, 1000, n_samples)
            gas_cost = np.random.uniform(5, 100, n_samples)
            X = np.column_stack([profit, gas_cost])
            roi = (profit - gas_cost) / gas_cost + np.random.normal(0, 0.01, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=roi,
                variable_names=['profit', 'gas_cost'],
                variable_descriptions={'profit': 'Transaction profit', 'gas_cost': 'Gas cost'},
                variable_units={'profit': 'dimensionless', 'gas_cost': 'dimensionless'},
                description="Gas-Adjusted ROI",
                validate_first=False
            )
            
        elif formula_num == 20:  # Concentrated Liquidity Position Value
            print("\n20. Concentrated Liquidity Position Value")
            liquidity = np.random.uniform(1000, 100000, n_samples)
            sqrt_price_current = np.random.uniform(10, 100, n_samples)
            sqrt_price_lower = sqrt_price_current * 0.9
            sqrt_price_upper = sqrt_price_current * 1.1
            X = np.column_stack([liquidity, sqrt_price_current, sqrt_price_lower, sqrt_price_upper])
            amount0 = liquidity * (sqrt_price_upper - sqrt_price_current) / (sqrt_price_current * sqrt_price_upper)
            amount0 += np.random.normal(0, 1, n_samples)
            
            self.system.discover_validate_interpret(
                X=X, y=amount0,
                variable_names=['liquidity', 'sqrt_p', 'sqrt_p_lower', 'sqrt_p_upper'],
                variable_descriptions={'liquidity': 'Position liquidity', 'sqrt_p': 'Current sqrt price', 
                                      'sqrt_p_lower': 'Lower tick sqrt price', 'sqrt_p_upper': 'Upper tick sqrt price'},
                variable_units={'liquidity': 'dimensionless', 'sqrt_p': 'dimensionless', 
                               'sqrt_p_lower': 'dimensionless', 'sqrt_p_upper': 'dimensionless'},
                description="Uniswap V3 Concentrated Liquidity Position",
                validate_first=False
            )
    
    def run_all_formulas(self, n_samples: int = 100):
        """Generate and discover all 20 DeFi formulas."""
        print("\n" + "#"*70)
        print("# DeFi Formula Discovery - 20 Formulas")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Samples per formula: {n_samples}")
        print("#"*70)
        
        for i in range(1, 21):
            try:
                self.generate_formula(i, n_samples)
                print(f"✅ Formula {i} completed")
            except Exception as e:
                print(f"❌ Error in Formula {i}: {str(e)}")
    
    def save_results(self, output_dir: str = 'hypatiax/data/finance/defi'):
        """Save results to files."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        json_path = os.path.join(output_dir, f'defi_formulas_20_{timestamp}.json')
        csv_path = os.path.join(output_dir, f'defi_summary_20_{timestamp}.csv')
        
        self.system.export_results(json_path, format='json')
        self.system.export_results(csv_path, format='csv')
        
        return json_path, csv_path
    
    def print_summary(self):
        """Print summary statistics."""
        print("\n" + "="*70)
        print("FINAL SUMMARY")
        print("="*70)
        
        stats = self.system.get_statistics()
        print(f"\nTotal formulas: {stats['total_runs']}")
        print(f"Valid formulas: {stats['valid_count']}")
        print(f"Success rate: {stats['success_rate']:.1%}")
        print(f"Average R² score: {stats['average_r2']:.4f}")


def main():
    """Main execution function."""
    print("\n" + "█"*70)
    print("█  DeFi Formula Discovery - Extended to 20 Formulas  █")
    print("█"*70)
    
    generator = DeFiFormulaGenerator(domain='defi', seed=42)
    generator.run_all_formulas(n_samples=100)
    json_path, csv_path = generator.save_results()
    generator.print_summary()
    
    print(f"\n✅ Results saved to:")
    print(f"  JSON: {json_path}")
    print(f"  CSV:  {csv_path}")


if __name__ == "__main__":
    main()
