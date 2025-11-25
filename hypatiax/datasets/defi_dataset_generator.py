"""
DeFi Formula Discovery Dataset Generator
Generates and validates DeFi formulas using the Hybrid Discovery System
"""

import numpy as np
from hypatiax.tools.hybrid_system import HybridDiscoverySystem
import os
from datetime import datetime
from typing import Dict, Tuple


class DeFiFormulaGenerator:
    """Generate synthetic DeFi data and discover formulas."""
    
    def __init__(self, domain: str = 'defi', seed: int = 42):
        """
        Initialize the generator.
        
        Args:
            domain: Domain for validation
            seed: Random seed for reproducibility
        """
        self.system = HybridDiscoverySystem(domain=domain, max_results=100)
        self.seed = seed
        np.random.seed(seed)
        
    def generate_impermanent_loss(self, n_samples: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate impermanent loss data.
        
        Formula: IL = 2*sqrt(price_ratio)/(price_ratio + 1) - 1
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Tuple of (X, y) arrays
        """
        print("\n" + "="*70)
        print("Generating Formula 1: Impermanent Loss")
        print("="*70)
        
        # Generate price ratios from 0.1x to 10x
        price_ratios = np.random.uniform(0.1, 10, (n_samples, 1))
        
        # True impermanent loss formula
        il = 2 * np.sqrt(price_ratios[:, 0]) / (price_ratios[:, 0] + 1) - 1
        
        # Add realistic noise
        il += np.random.normal(0, 0.01, n_samples)
        
        print(f"Generated {n_samples} samples")
        print(f"Price ratio range: [{price_ratios.min():.2f}, {price_ratios.max():.2f}]")
        print(f"IL range: [{il.min():.4f}, {il.max():.4f}]")
        
        return price_ratios, il
    
    def generate_amm_swap_output(self, n_samples: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate AMM swap output data (Uniswap V2 style).
        
        Formula: output = (amount_in * 0.997 * reserve_out) / (reserve_in + amount_in * 0.997)
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Tuple of (X, y) arrays
        """
        print("\n" + "="*70)
        print("Generating Formula 2: AMM Swap Output (Uniswap V2)")
        print("="*70)
        
        # Generate swap parameters
        amount_in = np.random.uniform(1, 100, n_samples)
        reserve_in = np.random.uniform(1000, 10000, n_samples)
        reserve_out = np.random.uniform(1000, 10000, n_samples)
        
        X_data = np.column_stack([amount_in, reserve_in, reserve_out])
        
        # Uniswap V2 formula with 0.3% fee (0.997 multiplier)
        y_out = (amount_in * 0.997 * reserve_out) / (reserve_in + amount_in * 0.997)
        
        # Add realistic noise
        y_out += np.random.normal(0, 0.5, n_samples)
        
        print(f"Generated {n_samples} samples")
        print(f"Amount in range: [{amount_in.min():.2f}, {amount_in.max():.2f}]")
        print(f"Output range: [{y_out.min():.2f}, {y_out.max():.2f}]")
        
        return X_data, y_out
    
    def generate_utilization_rate(self, n_samples: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate lending pool utilization rate data.
        
        Formula: utilization = borrowed / supplied
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Tuple of (X, y) arrays
        """
        print("\n" + "="*70)
        print("Generating Formula 3: Lending Pool Utilization Rate")
        print("="*70)
        
        # Generate borrowed amounts
        borrowed = np.random.uniform(0, 1000, n_samples)
        
        # Generate supplied (always >= borrowed, with utilization 30-90%)
        utilization_target = np.random.uniform(0.3, 0.9, n_samples)
        supplied = borrowed / utilization_target
        
        X_util = np.column_stack([borrowed, supplied])
        
        # True utilization rate
        util = borrowed / supplied
        
        # Add minimal noise
        util += np.random.normal(0, 0.01, n_samples)
        
        print(f"Generated {n_samples} samples")
        print(f"Borrowed range: [{borrowed.min():.2f}, {borrowed.max():.2f}]")
        print(f"Supplied range: [{supplied.min():.2f}, {supplied.max():.2f}]")
        print(f"Utilization range: [{util.min():.4f}, {util.max():.4f}]")
        
        return X_util, util
    
    def generate_liquidity_value(self, n_samples: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate liquidity pool value data.
        
        Formula: value = 2 * sqrt(reserve0 * reserve1)
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Tuple of (X, y) arrays
        """
        print("\n" + "="*70)
        print("Generating Formula 4: Liquidity Pool Value")
        print("="*70)
        
        # Generate reserves
        reserve0 = np.random.uniform(100, 10000, n_samples)
        reserve1 = np.random.uniform(100, 10000, n_samples)
        
        X_data = np.column_stack([reserve0, reserve1])
        
        # Constant product pool value
        value = 2 * np.sqrt(reserve0 * reserve1)
        
        # Add noise
        value += np.random.normal(0, 10, n_samples)
        
        print(f"Generated {n_samples} samples")
        print(f"Reserve0 range: [{reserve0.min():.2f}, {reserve0.max():.2f}]")
        print(f"Reserve1 range: [{reserve1.min():.2f}, {reserve1.max():.2f}]")
        print(f"Value range: [{value.min():.2f}, {value.max():.2f}]")
        
        return X_data, value
    
    def run_all_formulas(self, n_samples: int = 100):
        """
        Generate and discover all DeFi formulas.
        
        Args:
            n_samples: Number of samples per formula
        """
        print("\n" + "#"*70)
        print("# DeFi Formula Discovery Dataset Generation")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Samples per formula: {n_samples}")
        print(f"# Random seed: {self.seed}")
        print("#"*70)
        
        # Formula 1: Impermanent Loss
        try:
            X, y = self.generate_impermanent_loss(n_samples)
            self.system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=['price_ratio'],
                variable_descriptions={
                    'price_ratio': 'Ratio of current price to initial price'
                },
                variable_units={'price_ratio': 'dimensionless'},
                description="Impermanent Loss in AMM Pool"
            )
        except Exception as e:
            print(f"❌ Error in Impermanent Loss: {str(e)}")
        
        # Formula 2: AMM Swap Output
        try:
            X, y = self.generate_amm_swap_output(n_samples)
            self.system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=['amount_in', 'reserve_in', 'reserve_out'],
                variable_descriptions={
                    'amount_in': 'Input token amount',
                    'reserve_in': 'Input token reserve in pool',
                    'reserve_out': 'Output token reserve in pool'
                },
                variable_units={
                    'amount_in': 'tokens',
                    'reserve_in': 'tokens',
                    'reserve_out': 'tokens'
                },
                description="Uniswap V2 Swap Output with 0.3% Fee"
            )
        except Exception as e:
            print(f"❌ Error in AMM Swap: {str(e)}")
        
        # Formula 3: Utilization Rate
        try:
            X, y = self.generate_utilization_rate(n_samples)
            self.system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=['borrowed', 'supplied'],
                variable_descriptions={
                    'borrowed': 'Total amount borrowed from pool',
                    'supplied': 'Total amount supplied to pool'
                },
                variable_units={'borrowed': 'USD', 'supplied': 'USD'},
                description="Lending Pool Utilization Rate"
            )
        except Exception as e:
            print(f"❌ Error in Utilization Rate: {str(e)}")
        
        # Formula 4: Liquidity Pool Value
        try:
            X, y = self.generate_liquidity_value(n_samples)
            self.system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=['reserve0', 'reserve1'],
                variable_descriptions={
                    'reserve0': 'Reserve amount of token 0',
                    'reserve1': 'Reserve amount of token 1'
                },
                variable_units={'reserve0': 'USD', 'reserve1': 'USD'},
                description="Constant Product Pool Total Value"
            )
        except Exception as e:
            print(f"❌ Error in Liquidity Value: {str(e)}")
    
    def save_results(self, output_dir: str = 'data'):
        """
        Save results to files.
        
        Args:
            output_dir: Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON
        json_path = os.path.join(output_dir, f'defi_formulas_{timestamp}.json')
        self.system.export_results(json_path, format='json')
        
        # Save CSV summary
        csv_path = os.path.join(output_dir, f'defi_summary_{timestamp}.csv')
        self.system.export_results(csv_path, format='csv')
        
        return json_path, csv_path
    
    def print_summary(self):
        """Print summary of all discovered formulas."""
        print("\n" + "="*70)
        print("FINAL SUMMARY")
        print("="*70)
        
        stats = self.system.get_statistics()
        
        print(f"\nTotal formulas: {stats['total_runs']}")
        print(f"Valid formulas: {stats['valid_count']}")
        print(f"Invalid formulas: {stats['invalid_count']}")
        print(f"Success rate: {stats['success_rate']:.1%}")
        print(f"Average R² score: {stats['average_r2']:.4f}")
        print(f"Average validation score: {stats['average_validation_score']:.1f}/100")
        
        # Show individual results
        print("\nIndividual Results:")
        print("-" * 70)
        for i, result in enumerate(self.system.get_results(), 1):
            discovery = result.get('discovery', {})
            validation = result.get('validation', {})
            
            valid_symbol = "✓" if validation.get('valid') else "✗"
            
            print(f"\n{i}. {result.get('description', 'Unknown')}")
            print(f"   Expression: {discovery.get('expression', 'N/A')}")
            print(f"   R² Score: {discovery.get('r2_score', 0):.4f}")
            print(f"   Validation: {valid_symbol} {validation.get('total_score', 0):.1f}/100")
            
            if validation.get('errors'):
                print(f"   Errors: {len(validation['errors'])}")
                for error in validation['errors'][:2]:
                    print(f"     - {error}")
        
        print("\n" + "="*70)


def main():
    """Main execution function."""
    # Initialize generator
    generator = DeFiFormulaGenerator(domain='defi', seed=42)
    
    # Generate all formulas
    generator.run_all_formulas(n_samples=100)
    
    # Save results
    json_path, csv_path = generator.save_results(output_dir='data')
    
    # Print summary
    generator.print_summary()
    
    print(f"\n✓ Complete! Results saved to:")
    print(f"  JSON: {json_path}")
    print(f"  CSV:  {csv_path}")


if __name__ == "__main__":
    main()
