"""
HypatiaX Dimensional Validator
tools/validation/dimensional_validator.py
"""

from pint import UnitRegistry
from typing import Dict, List, Optional
from collections import deque
import sympy as sp


class DimensionalValidator:
    """
    Validates dimensional consistency of mathematical expressions.
    Uses Pint for unit analysis.
    """
    
    def __init__(self, max_history: Optional[int] = 1000):
        """
        Initialize the dimensional validator.
        
        Args:
            max_history: Maximum number of validation results to keep.
        """
        self.ureg = UnitRegistry()
        
        # Bounded validation history
        if max_history is not None:
            self.validation_history = deque(maxlen=max_history)
        else:
            self.validation_history = []
    
    def validate(
        self, 
        expression_str: str,
        variable_units: Dict[str, str]
    ) -> Dict:
        """
        Validate dimensional consistency.
        
        Args:
            expression_str: The mathematical expression
            variable_units: Dict mapping variable names to unit strings
                          e.g., {'price': 'USD', 'volume': 'USD**3'}
            
        Returns:
            {
                'valid': bool,
                'score': float,
                'errors': List[str],
                'warnings': List[str],
                'dimensionally_consistent': bool,
                'variable_dimensions': Dict
            }
        """
        result = {
            'valid': True,
            'score': 100.0,
            'errors': [],
            'warnings': [],
            'dimensionally_consistent': True,
            'variable_dimensions': {}
        }
        
        try:
            # Parse units for each variable
            var_quantities = {}
            for var_name, unit_str in variable_units.items():
                try:
                    if unit_str.lower() in ['dimensionless', 'none', '']:
                        var_quantities[var_name] = self.ureg.dimensionless
                        result['variable_dimensions'][var_name] = 'dimensionless'
                    else:
                        quantity = self.ureg(unit_str)
                        var_quantities[var_name] = quantity
                        result['variable_dimensions'][var_name] = str(quantity.units)
                except Exception as e:
                    result['errors'].append(
                        f"Invalid unit for '{var_name}': '{unit_str}' - {str(e)}"
                    )
                    result['score'] -= 15
                    result['valid'] = False
            
            # Parse expression to SymPy for structural analysis
            try:
                expr = sp.sympify(expression_str)
                
                # Check dimensional consistency of operations
                consistency_check = self._check_operation_consistency(
                    expr, var_quantities
                )
                
                result['errors'].extend(consistency_check['errors'])
                result['warnings'].extend(consistency_check['warnings'])
                result['score'] -= consistency_check['penalty']
                
                if consistency_check['errors']:
                    result['valid'] = False
                    result['dimensionally_consistent'] = False
                
            except Exception as e:
                result['warnings'].append(
                    f"Could not parse expression for dimensional analysis: {str(e)}"
                )
                result['score'] -= 10
            
        except Exception as e:
            result['valid'] = False
            result['score'] = 0
            result['errors'].append(f"Dimensional validation error: {str(e)}")
        
        # Store in history
        self.validation_history.append(result)
        return result
    
    def _check_operation_consistency(
        self, 
        expr, 
        var_quantities: Dict
    ) -> Dict:
        """
        Check dimensional consistency of operations in the expression.
        
        Returns:
            Dict with 'errors', 'warnings', and 'penalty'
        """
        errors = []
        warnings = []
        penalty = 0
        
        # Check additions and subtractions
        if expr.is_Add:
            terms = expr.args
            term_units = []
            
            for term in terms:
                vars_in_term = [str(s) for s in term.free_symbols]
                
                # Get representative unit for this term
                if vars_in_term:
                    first_var = vars_in_term[0]
                    if first_var in var_quantities:
                        term_units.append(var_quantities[first_var])
            
            # Check if all terms have compatible dimensions
            if len(term_units) > 1:
                base_unit = term_units[0]
                for i, unit in enumerate(term_units[1:], 1):
                    if not self._units_compatible(base_unit, unit):
                        errors.append(
                            f"Incompatible units in addition/subtraction: "
                            f"{base_unit.units} vs {unit.units}"
                        )
                        penalty += 20
        
        # Check multiplications
        if expr.is_Mul:
            warnings.append(
                "Multiplication detected - verify resulting dimensions are correct"
            )
            penalty += 2
        
        # Check powers
        if expr.is_Pow:
            base, exp = expr.args
            
            # If exponent is not a number, it's problematic
            if not exp.is_Number:
                warnings.append(
                    "Non-numeric exponent - dimensional analysis not possible"
                )
                penalty += 10
            elif exp.is_Rational and exp.q != 1:
                # Fractional exponent
                warnings.append(
                    f"Fractional exponent ({exp}) - verify dimensional consistency"
                )
                penalty += 5
        
        # Check functions
        if expr.has(sp.log) or expr.has(sp.exp):
            warnings.append(
                "Logarithmic/exponential functions require dimensionless arguments"
            )
            penalty += 5
        
        if expr.has(sp.sin) or expr.has(sp.cos) or expr.has(sp.tan):
            warnings.append(
                "Trigonometric functions require dimensionless (radian) arguments"
            )
            penalty += 5
        
        return {
            'errors': errors,
            'warnings': warnings,
            'penalty': penalty
        }
    
    def _units_compatible(self, unit1, unit2) -> bool:
        """Check if two units are dimensionally compatible."""
        try:
            # Try to convert unit2 to unit1
            test_quantity = 1 * unit2
            test_quantity.to(unit1)
            return True
        except Exception:
            return False
    
    def clear_history(self):
        """Clear validation history."""
        if isinstance(self.validation_history, deque):
            self.validation_history.clear()
        else:
            self.validation_history = []
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get validation history.
        
        Args:
            limit: Maximum number of most recent validations to return
            
        Returns:
            List of validation result dictionaries
        """
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
                'average_score': 0.0
            }
        
        total = len(self.validation_history)
        valid_count = sum(1 for v in self.validation_history if v['valid'])
        avg_score = sum(v['score'] for v in self.validation_history) / total
        
        return {
            'total_validations': total,
            'success_rate': valid_count / total,
            'average_score': avg_score,
            'valid_count': valid_count,
            'invalid_count': total - valid_count
        }


# Example usage
if __name__ == "__main__":
    validator = DimensionalValidator()
    
    # Test case 1: Compatible units
    result1 = validator.validate(
        expression_str="price1 + price2",
        variable_units={'price1': 'USD', 'price2': 'USD'}
    )
    print(f"Test 1 - Valid: {result1['valid']}, Score: {result1['score']}")
    
    # Test case 2: Incompatible units
    result2 = validator.validate(
        expression_str="price + volume",
        variable_units={'price': 'USD', 'volume': 'USD**3'}
    )
    print(f"\nTest 2 - Valid: {result2['valid']}, Score: {result2['score']}")
    print(f"Errors: {result2['errors']}")
    
    # Get statistics
    stats = validator.get_statistics()
    print(f"\nStatistics: {stats}")
