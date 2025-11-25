"""
HypatiaX Domain Validator
tools/validation/domain_validator.py
"""

import numpy as np
from typing import Dict, List, Optional
from collections import deque


class DomainValidator:
    """
    Validates domain-specific constraints for mathematical expressions.
    Checks that formulas satisfy domain-specific rules (DeFi, Risk, Finance, ESG).
    """
    
    def __init__(self, domain: str, max_history: Optional[int] = 1000):
        """
        Initialize the domain validator.
        
        Args:
            domain: Domain context ('defi', 'risk', 'finance', 'esg')
            max_history: Maximum number of validation results to keep
        """
        self.domain = domain.lower()
        self.constraints = self._load_constraints()
        
        # Bounded validation history
        if max_history is not None:
            self.validation_history = deque(maxlen=max_history)
        else:
            self.validation_history = []
    
    def _load_constraints(self) -> Dict:
        """Load domain-specific constraints."""
        constraints = {
            'defi': {
                'positive_variables': [
                    'reserve', 'liquidity', 'price', 'amount', 
                    'balance', 'supply', 'token'
                ],
                'bounded_variables': {
                    'fee': (0, 1),
                    'slippage': (0, 1),
                    'utilization': (0, 1),
                    'ratio': (0, None)
                },
                'ratio_variables': ['price_ratio', 'reserve_ratio'],
                'special_checks': ['constant_product', 'no_negative_slippage']
            },
            'risk': {
                'positive_variables': [
                    'var', 'cvar', 'volatility', 'loss', 
                    'exposure', 'shortfall'
                ],
                'probability_variables': [
                    'prob', 'confidence', 'likelihood', 'probability'
                ],
                'bounded_variables': {
                    'confidence': (0, 1),
                    'probability': (0, 1),
                    'correlation': (-1, 1)
                },
                'special_checks': ['var_positive', 'confidence_valid']
            },
            'finance': {
                'positive_variables': [
                    'price', 'volume', 'market_cap', 'assets', 'nav'
                ],
                'bounded_variables': {
                    'return': (-1, None),  # Can lose 100%, no upper bound
                    'weight': (0, 1),
                    'allocation': (0, 1)
                },
                'percentage_variables': ['return', 'yield', 'rate', 'apy'],
                'special_checks': ['weights_sum_to_one']
            },
            'esg': {
                'bounded_variables': {
                    'score': (0, 100),
                    'rating': (0, 10),
                    'weight': (0, 1)
                },
                'positive_variables': [
                    'impact', 'emissions', 'carbon', 'footprint'
                ],
                'special_checks': ['score_range', 'weights_sum_to_one']
            }
        }
        
        return constraints.get(self.domain, {})
    
    def validate(
        self, 
        expression_str: str,
        variable_definitions: Dict[str, str],
        test_data: Optional[Dict[str, np.ndarray]] = None
    ) -> Dict:
        """
        Validate domain-specific constraints.
        
        Args:
            expression_str: The mathematical expression
            variable_definitions: Variable name to description mapping
            test_data: Optional test data for numerical validation
            
        Returns:
            {
                'valid': bool,
                'score': float,
                'errors': List[str],
                'warnings': List[str],
                'domain': str,
                'constraints_checked': List[str]
            }
        """
        result = {
            'valid': True,
            'score': 100.0,
            'errors': [],
            'warnings': [],
            'domain': self.domain,
            'constraints_checked': []
        }
        
        # Check positive variable constraints
        result = self._check_positive_variables(
            expression_str, test_data, result
        )
        
        # Check bounded variable constraints
        result = self._check_bounded_variables(
            expression_str, test_data, result
        )
        
        # Check probability variables (if applicable)
        if 'probability_variables' in self.constraints:
            result = self._check_probability_variables(
                expression_str, test_data, result
            )
        
        # Check special domain rules
        result = self._check_special_rules(
            expression_str, variable_definitions, test_data, result
        )
        
        # Determine overall validity
        if result['errors']:
            result['valid'] = False
        
        # Store in history
        self.validation_history.append(result)
        return result
    
    def _check_positive_variables(
        self, 
        expression_str: str,
        test_data: Optional[Dict[str, np.ndarray]],
        result: Dict
    ) -> Dict:
        """Check that variables that must be positive are indeed positive."""
        positive_vars = self.constraints.get('positive_variables', [])
        
        for var in positive_vars:
            if var in expression_str.lower():
                result['constraints_checked'].append(f'{var}_positive')
                
                if test_data and var in test_data:
                    values = test_data[var]
                    if np.any(values <= 0):
                        result['errors'].append(
                            f"Variable '{var}' must be positive (found {np.min(values):.6f})"
                        )
                        result['score'] -= 20
                else:
                    result['warnings'].append(
                        f"Variable '{var}' should be positive - add validation"
                    )
                    result['score'] -= 5
        
        return result
    
    def _check_bounded_variables(
        self,
        expression_str: str,
        test_data: Optional[Dict[str, np.ndarray]],
        result: Dict
    ) -> Dict:
        """Check that bounded variables are within their valid ranges."""
        bounded_vars = self.constraints.get('bounded_variables', {})
        
        for var, bounds in bounded_vars.items():
            if var in expression_str.lower():
                result['constraints_checked'].append(f'{var}_bounded')
                lower, upper = bounds
                
                if test_data and var in test_data:
                    values = test_data[var]
                    
                    # Check lower bound
                    if lower is not None and np.any(values < lower):
                        result['errors'].append(
                            f"Variable '{var}' below minimum {lower} "
                            f"(found {np.min(values):.6f})"
                        )
                        result['score'] -= 15
                    
                    # Check upper bound
                    if upper is not None and np.any(values > upper):
                        result['errors'].append(
                            f"Variable '{var}' above maximum {upper} "
                            f"(found {np.max(values):.6f})"
                        )
                        result['score'] -= 15
                else:
                    bound_str = f"[{lower}, {upper}]" if upper else f"≥ {lower}"
                    result['warnings'].append(
                        f"Variable '{var}' should be in range {bound_str}"
                    )
                    result['score'] -= 5
        
        return result
    
    def _check_probability_variables(
        self,
        expression_str: str,
        test_data: Optional[Dict[str, np.ndarray]],
        result: Dict
    ) -> Dict:
        """Check that probability variables are in [0, 1]."""
        prob_vars = self.constraints.get('probability_variables', [])
        
        for var in prob_vars:
            if var in expression_str.lower():
                result['constraints_checked'].append(f'{var}_probability')
                
                if test_data and var in test_data:
                    values = test_data[var]
                    
                    if np.any(values < 0) or np.any(values > 1):
                        result['errors'].append(
                            f"Probability variable '{var}' must be in [0, 1] "
                            f"(found range [{np.min(values):.3f}, {np.max(values):.3f}])"
                        )
                        result['score'] -= 25
                else:
                    result['warnings'].append(
                        f"Probability variable '{var}' should be in [0, 1]"
                    )
                    result['score'] -= 5
        
        return result
    
    def _check_special_rules(
        self,
        expression_str: str,
        variable_definitions: Dict[str, str],
        test_data: Optional[Dict[str, np.ndarray]],
        result: Dict
    ) -> Dict:
        """Check domain-specific special rules."""
        special_checks = self.constraints.get('special_checks', [])
        
        for check in special_checks:
            if check == 'constant_product':
                result = self._check_constant_product(
                    expression_str, test_data, result
                )
            elif check == 'no_negative_slippage':
                result = self._check_no_negative_slippage(
                    expression_str, test_data, result
                )
            elif check == 'var_positive':
                result = self._check_var_positive(
                    expression_str, test_data, result
                )
            elif check == 'confidence_valid':
                result = self._check_confidence_valid(
                    expression_str, test_data, result
                )
            elif check == 'weights_sum_to_one':
                result = self._check_weights_sum(
                    expression_str, variable_definitions, result
                )
            elif check == 'score_range':
                result = self._check_score_range(
                    expression_str, test_data, result
                )
        
        return result
    
    # Special rule implementations
    
    def _check_constant_product(
        self, expr_str: str, test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """Check DeFi constant product invariant."""
        if 'reserve' in expr_str.lower() and test_data:
            result['constraints_checked'].append('constant_product')
            result['warnings'].append(
                "Verify constant product invariant (x*y=k) is maintained"
            )
        return result
    
    def _check_no_negative_slippage(
        self, expr_str: str, test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """Check that slippage is non-negative."""
        if 'slippage' in expr_str.lower():
            result['constraints_checked'].append('no_negative_slippage')
            if test_data and 'slippage' in test_data:
                if np.any(test_data['slippage'] < 0):
                    result['errors'].append("Slippage cannot be negative")
                    result['score'] -= 20
        return result
    
    def _check_var_positive(
        self, expr_str: str, test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """Check that VaR (Value at Risk) is positive."""
        if 'var' in expr_str.lower():
            result['constraints_checked'].append('var_positive')
            result['warnings'].append("VaR should be positive")
        return result
    
    def _check_confidence_valid(
        self, expr_str: str, test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """Check that confidence level is valid."""
        if 'confidence' in expr_str.lower():
            result['constraints_checked'].append('confidence_valid')
            if test_data and 'confidence' in test_data:
                conf = test_data['confidence']
                if np.any(conf <= 0) or np.any(conf >= 1):
                    result['errors'].append(
                        "Confidence level must be in (0, 1) exclusive"
                    )
                    result['score'] -= 20
        return result
    
    def _check_weights_sum(
        self, expr_str: str, var_defs: Dict, result: Dict
    ) -> Dict:
        """Check that weight variables sum to 1."""
        weight_vars = [v for v in var_defs if 'weight' in v.lower()]
        if weight_vars:
            result['constraints_checked'].append('weights_sum_to_one')
            result['warnings'].append(
                f"Verify that weights {weight_vars} sum to 1"
            )
        return result
    
    def _check_score_range(
        self, expr_str: str, test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """Check that scores are in valid range."""
        if 'score' in expr_str.lower():
            result['constraints_checked'].append('score_range')
            if test_data and 'score' in test_data:
                scores = test_data['score']
                if np.any(scores < 0) or np.any(scores > 100):
                    result['errors'].append(
                        f"Scores must be in [0, 100] "
                        f"(found range [{np.min(scores):.1f}, {np.max(scores):.1f}])"
                    )
                    result['score'] -= 20
        return result
    
    # History management
    
    def clear_history(self):
        """Clear validation history."""
        if isinstance(self.validation_history, deque):
            self.validation_history.clear()
        else:
            self.validation_history = []
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get validation history."""
        history_list = list(self.validation_history)
        if limit is not None:
            return history_list[-limit:]
        return history_list
    
    def get_statistics(self) -> Dict:
        """Get statistics about validation history."""
        if not self.validation_history:
            return {
                'total_validations': 0,
                'success_rate': 0.0,
                'average_score': 0.0,
                'domain': self.domain
            }
        
        total = len(self.validation_history)
        valid_count = sum(1 for v in self.validation_history if v['valid'])
        avg_score = sum(v['score'] for v in self.validation_history) / total
        
        return {
            'total_validations': total,
            'success_rate': valid_count / total,
            'average_score': avg_score,
            'valid_count': valid_count,
            'invalid_count': total - valid_count,
            'domain': self.domain
        }


# Example usage
if __name__ == "__main__":
    # Test DeFi domain
    validator = DomainValidator(domain='defi')
    
    result = validator.validate(
        expression_str="reserve0 * reserve1 / liquidity",
        variable_definitions={
            'reserve0': 'Token 0 reserves',
            'reserve1': 'Token 1 reserves',
            'liquidity': 'Total liquidity'
        },
        test_data={
            'reserve0': np.array([100, 200, 300]),
            'reserve1': np.array([50, 100, 150]),
            'liquidity': np.array([1000, 2000, 3000])
        }
    )
    
    print(f"Valid: {result['valid']}")
    print(f"Score: {result['score']}")
    print(f"Warnings: {result['warnings']}")
    print(f"Constraints checked: {result['constraints_checked']}")
    
    # Get statistics
    stats = validator.get_statistics()
    print(f"\nStatistics: {stats}")
