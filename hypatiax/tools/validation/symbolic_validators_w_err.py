#!/usr/bin/env python3
"""
Symbolic Validation for Generated Formulas
Uses SymPy for mathematical validation
Part of HypatiaX tools/validation/
"""
import sympy as sp
from sympy import sympify, simplify
from sympy.parsing.latex import parse_latex
from typing import Dict, Any, List, Optional
from collections import deque
import re


class SymbolicValidator:
    """
    Validates generated formulas mathematically
    
    Uses:
        - SymPy for symbolic mathematics
        - Numerical stability analysis
        - Dimensional consistency
        - Domain-specific constraints
    """
    
    def __init__(self, max_history: Optional[int] = 1000):
        """
        Initialize the validator.
        
        Args:
            max_history: Maximum number of validation results to keep in history.
                        If None, no limit. Defaults to 1000.
        """
        self.domain_rules = {
            'defi': self._defi_rules,
            'finance': self._finance_rules,
            'esg': self._esg_rules,
            'risk': self._risk_rules
        }
        
        # Bounded validation history
        if max_history is not None:
            self.validation_history = deque(maxlen=max_history)
        else:
            self.validation_history = []
    
    def validate(
        self, 
        expression: str,
        variable_definitions: Dict[str, str],
        domain: str = "defi",
        from_latex: bool = False
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of a mathematical expression.
        
        Args:
            expression: The mathematical expression (string or LaTeX)
            variable_definitions: Dict mapping variable names to descriptions
            domain: Domain context ('defi', 'finance', 'esg', 'risk')
            from_latex: Whether the expression is in LaTeX format
            
        Returns:
            {
                'valid': bool,
                'syntactically_valid': bool,
                'dimensionally_consistent': bool,
                'domain_valid': bool,
                'numerically_stable': bool,
                'sympy_expr': SymPy expression object,
                'canonical_form': str (simplified form),
                'errors': [list of error messages],
                'warnings': [list of warnings],
                'score': 0-100
            }
        """
        results = {
            'valid': True,
            'syntactically_valid': False,
            'dimensionally_consistent': False,
            'domain_valid': False,
            'numerically_stable': False,
            'errors': [],
            'warnings': [],
            'sympy_expr': None,
            'canonical_form': None
        }
        
        try:
            # 1. Parse expression
            if from_latex:
                expr = self._safe_parse_latex(expression)
            else:
                expr = sympify(expression)
            
            if expr is None:
                results['errors'].append("Cannot parse expression")
                results['valid'] = False
                return self._finalize_results(results)
            
            results['syntactically_valid'] = True
            results['sympy_expr'] = expr
            
            # 2. Check for undefined variables
            free_vars = expr.free_symbols
            undefined_vars = [str(v) for v in free_vars 
                            if str(v) not in variable_definitions]
            if undefined_vars:
                results['errors'].append(f"Undefined variables: {undefined_vars}")
                results['valid'] = False
            
            # 3. Check for mathematical issues
            if expr.has(sp.zoo):  # Complex infinity
                results['errors'].append("Contains complex infinity")
                results['valid'] = False
            
            if expr.has(sp.oo):  # Infinity
                results['warnings'].append("Contains infinity - verify limits")
            
            if expr.has(sp.nan):  # Not a number
                results['errors'].append("Contains NaN (not a number)")
                results['valid'] = False
            
            # 4. Simplification
            try:
                simplified = simplify(expr)
                results['canonical_form'] = str(simplified)
                
                if expr != simplified:
                    results['warnings'].append(
                        f"Can be simplified to: {simplified}"
                    )
            except Exception as e:
                results['warnings'].append(f"Simplification failed: {str(e)}")
                results['canonical_form'] = str(expr)
            
            # 5. Dimensional consistency
            if self._check_dimensions(expr, variable_definitions):
                results['dimensionally_consistent'] = True
            else:
                results['errors'].append("Dimensional inconsistency detected")
                results['valid'] = False
            
            # 6. Domain-specific rules
            domain_check = self.domain_rules.get(
                domain, 
                self._default_rules
            )(expr, variable_definitions)
            
            results['domain_valid'] = domain_check['valid']
            results['errors'].extend(domain_check['errors'])
            results['warnings'].extend(domain_check.get('warnings', []))
            
            if not domain_check['valid']:
                results['valid'] = False
            
            # 7. Numerical stability analysis
            stability = self._check_numerical_stability(expr)
            results['numerically_stable'] = stability['stable']
            results['warnings'].extend(stability['warnings'])
            
        except Exception as e:
            results['errors'].append(f"Validation error: {str(e)}")
            results['valid'] = False
        
        return self._finalize_results(results)
    
    def _finalize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate score and store in history."""
        results['score'] = self._calculate_score(results)
        self.validation_history.append(results)
        return results
    
    def _safe_parse_latex(self, latex_str: str):
        """Safely parse LaTeX, handling common issues."""
        try:
            # Clean LaTeX string
            latex_str = latex_str.strip()
            latex_str = re.sub(r'\\text\{([^}]+)\}', r'\1', latex_str)
            
            return parse_latex(latex_str)
        except Exception:
            # Try alternative parsing
            try:
                return sympify(latex_str)
            except Exception:
                return None
    
    def _check_dimensions(
        self, 
        expr, 
        variable_definitions: Dict[str, str]
    ) -> bool:
        """
        Dimensional analysis - basic implementation.
        
        This is a simplified check. For production, implement detailed
        dimensional analysis based on variable types.
        """
        # TODO: Implement proper dimensional analysis
        # For now, just check that operations make sense
        
        # Check for operations that mix incompatible types
        # e.g., price * price should not equal return
        
        return True  # Placeholder
    
    def _check_numerical_stability(self, expr) -> Dict[str, Any]:
        """
        Numerical stability analysis.
        
        Checks:
        1. Division by zero risks
        2. Overflow/underflow potential
        3. Precision loss in operations
        4. Subtractive cancellation
        """
        warnings = []
        
        # 1. Find all denominators
        denominators = self._extract_denominators(expr)
        for denom in denominators:
            if self._could_be_zero(denom):
                warnings.append(f"Division by zero risk: {denom}")
        
        # 2. Check for subtractive cancellation
        subtractions = self._find_subtractions(expr)
        if len(subtractions) > 2:
            warnings.append(
                "Multiple subtractions may cause precision loss"
            )
        
        # 3. Check for exponentials (overflow risk)
        if expr.has(sp.exp):
            warnings.append(
                "Exponential functions may overflow - validate input ranges"
            )
        
        # 4. Check for products (overflow risk)
        if expr.has(sp.Mul):
            mul_terms = [arg for arg in expr.args if arg.is_Mul]
            if len(mul_terms) > 3:
                warnings.append(
                    "Multiple multiplications - check for overflow"
                )
        
        # 5. Check sqrt of potentially negative values
        if expr.has(sp.sqrt):
            warnings.append(
                "Square root present - ensure non-negative inputs"
            )
        
        # 6. Check for logarithms (domain issues)
        if expr.has(sp.log):
            warnings.append(
                "Logarithm present - ensure positive inputs"
            )
        
        # 7. Check for trigonometric functions (range issues)
        if any(expr.has(func) for func in [sp.sin, sp.cos, sp.tan]):
            warnings.append(
                "Trigonometric functions - verify input ranges"
            )
        
        return {
            'stable': len(warnings) == 0,
            'warnings': warnings
        }
    
    def _extract_denominators(self, expr) -> List:
        """Extract all denominators from expression."""
        denominators = []
        
        if expr.is_Mul:
            for arg in expr.args:
                if arg.is_Pow and arg.exp.is_negative:
                    denominators.append(arg.base)
        
        if expr.is_Add:
            for arg in expr.args:
                denominators.extend(self._extract_denominators(arg))
        
        if hasattr(expr, 'args'):
            for arg in expr.args:
                denominators.extend(self._extract_denominators(arg))
        
        return denominators
    
    def _could_be_zero(self, expr) -> bool:
        """Check if expression could evaluate to zero."""
        if expr.is_Number:
            return abs(float(expr)) < 1e-10
        
        # Conservative: assume additions could cancel
        if expr.is_Add:
            return True
        
        return False
    
    def _find_subtractions(self, expr) -> List:
        """Find all subtraction operations."""
        subs = []
        
        if expr.is_Add:
            neg_terms = [
                arg for arg in expr.args 
                if arg.could_extract_minus_sign()
            ]
            if len(neg_terms) > 0:
                subs.append(expr)
        
        if hasattr(expr, 'args'):
            for arg in expr.args:
                subs.extend(self._find_subtractions(arg))
        
        return subs
    
    # Domain-specific validation rules
    
    def _defi_rules(
        self, 
        expr, 
        variable_definitions: Dict[str, str]
    ) -> Dict[str, Any]:
        """DeFi-specific validation rules."""
        errors = []
        warnings = []
        
        # Check: Liquidity must be positive
        if 'liquidity' in [str(s) for s in expr.free_symbols]:
            warnings.append("Ensure liquidity is always positive")
        
        # Check: Price impact should be bounded
        if 'price' in str(expr).lower():
            warnings.append("Verify price bounds and slippage limits")
        
        # Check: x*y = k invariant considerations
        if expr.has(sp.Mul) and expr.has(sp.Pow):
            warnings.append(
                "Check AMM constant product invariant preservation"
            )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _finance_rules(
        self, 
        expr, 
        variable_definitions: Dict[str, str]
    ) -> Dict[str, Any]:
        """Finance-specific validation rules."""
        errors = []
        warnings = []
        
        # Check for negative risk metrics
        if 'risk' in str(expr).lower() or 'var' in str(expr).lower():
            warnings.append("Risk metrics should be non-negative")
        
        # Check for return calculations
        if 'return' in str(expr).lower():
            warnings.append("Verify return calculation methodology")
        
        # Check for probability constraints
        if 'prob' in str(expr).lower():
            warnings.append("Ensure probabilities are in [0, 1]")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _esg_rules(
        self, 
        expr, 
        variable_definitions: Dict[str, str]
    ) -> Dict[str, Any]:
        """ESG-specific validation rules."""
        errors = []
        warnings = []
        
        # Check score ranges
        if 'score' in str(expr).lower():
            warnings.append("Verify scores are in valid range (typically 0-100)")
        
        # Check weighting
        if expr.has(sp.Add):
            warnings.append("Ensure component weights sum appropriately")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _risk_rules(
        self, 
        expr, 
        variable_definitions: Dict[str, str]
    ) -> Dict[str, Any]:
        """Risk management validation rules."""
        errors = []
        warnings = []
        
        # Check VaR properties
        if 'var' in str(expr).lower():
            warnings.append("VaR should be positive and bounded")
        
        # Check confidence levels
        if 'confidence' in str(expr).lower():
            warnings.append("Confidence levels must be in (0, 1)")
        
        # Check for unbounded risk
        if expr.has(sp.oo):
            errors.append("Risk metric appears unbounded")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _default_rules(
        self, 
        expr, 
        variable_definitions: Dict[str, str]
    ) -> Dict[str, Any]:
        """Default validation rules."""
        return {
            'valid': True,
            'errors': [],
            'warnings': []
        }
    
    def _calculate_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall validation score (0-100)."""
        score = 0
        
        # Base scores for passing each check
        if results['syntactically_valid']: score += 25
        if results['dimensionally_consistent']: score += 25
        if results['domain_valid']: score += 25
        if results['numerically_stable']: score += 25
        
        # Penalties
        score -= len(results['errors']) * 10
        score -= len(results.get('warnings', [])) * 2
        
        return max(0, min(100, score))
    
    # Utility methods for history management
    
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
    
    def get_statistics(self) -> Dict[str, Any]:
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
    validator = SymbolicValidator()
    
    # Test case 1: Simple valid expression
    result1 = validator.validate(
        expression="2*x + 3",
        variable_definitions={'x': 'Input variable'},
        domain='finance'
    )
    print(f"Test 1 - Valid: {result1['valid']}, Score: {result1['score']}")
    print(f"Canonical form: {result1['canonical_form']}")
    
    # Test case 2: Expression with undefined variable
    result2 = validator.validate(
        expression="2*x + y",
        variable_definitions={'x': 'Input variable'},
        domain='defi'
    )
    print(f"\nTest 2 - Valid: {result2['valid']}, Score: {result2['score']}")
    print(f"Errors: {result2['errors']}")
    
    # Test case 3: Expression with stability issues
    result3 = validator.validate(
        expression="sqrt(x) / (y - z)",
        variable_definitions={'x': 'Value 1', 'y': 'Value 2', 'z': 'Value 3'},
        domain='risk'
    )
    print(f"\nTest 3 - Valid: {result3['valid']}, Score: {result3['score']}")
    print(f"Warnings: {result3['warnings']}")
    
    # Get statistics
    stats = validator.get_statistics()
    print(f"\nValidation statistics: {stats}")
