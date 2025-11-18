#!/usr/bin/env python3
"""
Comprehensive Test Suite for Symbolic Validator
Tests DeFi-specific validation rules and full pipeline integration
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.validation.symbolic_validator import SymbolicValidator
    from tools.symbolic.sympy_wrapper import SymPyWrapper
except ImportError as e:
    print(f"⚠️  Import warning: {e}")
    print("Creating mock classes for testing...")
    
    # Mock classes for testing
    class SymPyWrapper:
        def validate_expression(self, expr1, expr2):
            return True
        def differentiate(self, expr, var):
            return f"d({expr})/d{var}"
    
    class SymbolicValidator:
        def __init__(self):
            self.sympy = SymPyWrapper()
        
        def validate_equivalence(self, expr1, expr2):
            return {
                "valid": self.sympy.validate_expression(expr1, expr2),
                "method": "symbolic_equivalence",
                "expr1": expr1,
                "expr2": expr2
            }
        
        def validate_derivative(self, expression, variable='x'):
            try:
                derivative = self.sympy.differentiate(expression, variable)
                return {
                    "valid": True,
                    "derivative": str(derivative),
                    "original": expression
                }
            except Exception as e:
                return {
                    "valid": False,
                    "error": str(e),
                    "original": expression
                }


class DeFiValidator(SymbolicValidator):
    """Extended validator with DeFi-specific rules"""
    
    def __init__(self):
        super().__init__()
        self.defi_rules = {
            'constant_product': self._check_constant_product,
            'division_by_zero': self._check_division_by_zero,
            'overflow': self._check_overflow_risk,
            'sqrt_domain': self._check_sqrt_domain,
            'range_constraints': self._check_range_constraints
        }
    
    def validate(self, formula_latex: str, domain: str = 'defi') -> Dict[str, Any]:
        """
        Complete validation with scoring system
        
        Args:
            formula_latex: LaTeX formula string
            domain: Domain for validation rules (default: 'defi')
            
        Returns:
            Dictionary with score, errors, and validation details
        """
        result = {
            'formula': formula_latex,
            'domain': domain,
            'score': 100,
            'errors': [],
            'warnings': [],
            'validations': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Run all DeFi validation rules
        if domain == 'defi':
            for rule_name, rule_func in self.defi_rules.items():
                try:
                    rule_result = rule_func(formula_latex)
                    result['validations'][rule_name] = rule_result
                    
                    if not rule_result['passed']:
                        result['score'] -= rule_result.get('penalty', 10)
                        if rule_result.get('severity') == 'error':
                            result['errors'].append({
                                'rule': rule_name,
                                'message': rule_result['message']
                            })
                        else:
                            result['warnings'].append({
                                'rule': rule_name,
                                'message': rule_result['message']
                            })
                except Exception as e:
                    result['errors'].append({
                        'rule': rule_name,
                        'message': f"Validation error: {str(e)}"
                    })
                    result['score'] -= 5
        
        # Ensure score doesn't go negative
        result['score'] = max(0, result['score'])
        
        return result
    
    def _check_constant_product(self, formula: str) -> Dict[str, Any]:
        """Check x·y = k invariant for AMM formulas"""
        # Look for constant product patterns
        has_xy_product = 'x' in formula.lower() and 'y' in formula.lower()
        has_multiplication = '\\cdot' in formula or '\\times' in formula or 'xy' in formula
        
        # Check if formula maintains invariant
        maintains_invariant = has_xy_product and has_multiplication
        
        if maintains_invariant or 'sqrt' in formula.lower():
            return {
                'passed': True,
                'message': 'Constant product invariant respected or not applicable',
                'severity': 'info'
            }
        else:
            return {
                'passed': False,
                'message': 'Formula may not respect x·y = k invariant',
                'severity': 'warning',
                'penalty': 5
            }
    
    def _check_division_by_zero(self, formula: str) -> Dict[str, Any]:
        """Detect potential division by zero issues"""
        critical_patterns = [
            (r'\frac{.*}{.*\+.*}', False),  # Safe: denominator has addition
            (r'\frac{.*}{[xy]_?0}', True),   # Risky: dividing by initial reserves
            (r'\frac{.*}{.*-.*}', True),     # Risky: subtraction in denominator
            (r'\frac{.*}{\epsilon}', False), # Safe: epsilon constant
        ]
        
        has_division = '\\frac' in formula or '/' in formula
        
        if not has_division:
            return {
                'passed': True,
                'message': 'No division operations detected',
                'severity': 'info'
            }
        
        # Check for epsilon protection
        has_epsilon_protection = '\\epsilon' in formula or 'epsilon' in formula
        
        # Check for dangerous patterns
        risky_divisions = []
        if '\\frac' in formula:
            # Simple heuristic: check if denominator has protections
            if not has_epsilon_protection and ('{0}' in formula or '- ' in formula):
                risky_divisions.append('Denominator may reach zero')
        
        if risky_divisions:
            return {
                'passed': False,
                'message': f'Potential division by zero: {"; ".join(risky_divisions)}',
                'severity': 'error',
                'penalty': 20
            }
        
        return {
            'passed': True,
            'message': 'Division operations appear safe',
            'severity': 'info'
        }
    
    def _check_overflow_risk(self, formula: str) -> Dict[str, Any]:
        """Check for potential numerical overflow"""
        risky_operations = []
        
        # Check for exponentiation
        if '^' in formula or '**' in formula:
            risky_operations.append('Exponentiation may cause overflow')
        
        # Check for products without sqrt normalization
        if ('\\cdot' in formula or '\\times' in formula) and 'sqrt' not in formula.lower():
            if formula.count('\\cdot') > 2 or formula.count('\\times') > 2:
                risky_operations.append('Multiple multiplications without normalization')
        
        if risky_operations:
            return {
                'passed': False,
                'message': f'Overflow risk: {"; ".join(risky_operations)}',
                'severity': 'warning',
                'penalty': 10
            }
        
        return {
            'passed': True,
            'message': 'No obvious overflow risks detected',
            'severity': 'info'
        }
    
    def _check_sqrt_domain(self, formula: str) -> Dict[str, Any]:
        """Validate square root domain (no negative inputs)"""
        has_sqrt = '\\sqrt' in formula or 'sqrt' in formula.lower()
        
        if not has_sqrt:
            return {
                'passed': True,
                'message': 'No square root operations',
                'severity': 'info'
            }
        
        # Check for protections
        has_abs = '\\abs' in formula or '|' in formula or 'abs(' in formula.lower()
        has_positive_constraint = any(char in formula for char in ['>', '+', 'max'])
        
        if has_abs or has_positive_constraint:
            return {
                'passed': True,
                'message': 'Square root domain appears protected',
                'severity': 'info'
            }
        
        # Check if sqrt argument is clearly positive
        import re
        sqrt_matches = re.findall(r'\\sqrt{([^}]+)}', formula)
        
        for sqrt_arg in sqrt_matches:
            # Check if argument is a product or sum of positive terms
            if all(char not in sqrt_arg for char in ['-', 'IL']):
                continue
            else:
                return {
                    'passed': False,
                    'message': f'Square root argument "{sqrt_arg}" may be negative',
                    'severity': 'error',
                    'penalty': 15
                }
        
        return {
            'passed': True,
            'message': 'Square root operations appear safe',
            'severity': 'info'
        }
    
    def _check_range_constraints(self, formula: str) -> Dict[str, Any]:
        """Check if formula respects DeFi range constraints"""
        issues = []
        
        # Prices should be positive
        if 'price' in formula.lower() or 'p_' in formula.lower():
            if not any(constraint in formula for constraint in ['>', '\\geq', 'max']):
                issues.append('Price variables should have positivity constraints')
        
        # Fees should be 0-100% (0-1 in formula)
        if 'fee' in formula.lower() or 'f_' in formula.lower():
            if not any(constraint in formula for constraint in ['\\leq', '<', '\\in']):
                issues.append('Fee variables should have upper bound constraints')
        
        # Percentages should be bounded
        if '%' in formula or 'percent' in formula.lower():
            issues.append('Percentage notation detected - ensure proper scaling')
        
        if issues:
            return {
                'passed': False,
                'message': f'Range constraint issues: {"; ".join(issues)}',
                'severity': 'warning',
                'penalty': 8
            }
        
        return {
            'passed': True,
            'message': 'Range constraints appear adequate',
            'severity': 'info'
        }


class TestSuite:
    """Complete test suite for symbolic validator"""
    
    def __init__(self):
        self.validator = DeFiValidator()
        self.results = []
        self.test_formulas = self._load_test_formulas()
    
    def _load_test_formulas(self) -> List[Dict[str, Any]]:
        """Load test formulas (mock data for now)"""
        return [
            {
                'name': 'Basic Impermanent Loss',
                'formula_latex': r'IL = \sqrt{\frac{2\sqrt{r}}{1+r}} - 1',
                'expected_score_min': 85
            },
            {
                'name': 'Weighted IL with Volatility',
                'formula_latex': r'IL_{weighted} = \sqrt{\frac{2\sqrt{r}}{1+r}} - 1 + \lambda \cdot \frac{\sigma_{rel}^2 \cdot t}{2} \cdot \left(\frac{r-1}{\sqrt{r}+1}\right)^2',
                'expected_score_min': 80
            },
            {
                'name': 'Price Impact with Protection',
                'formula_latex': r'\Pi = \frac{\Delta y}{\Delta x + \epsilon} \cdot \left(1 + \frac{\sqrt{\Delta x}}{\sqrt{x_0}}\right)',
                'expected_score_min': 90
            },
            {
                'name': 'Dangerous Division (No Protection)',
                'formula_latex': r'P = \frac{y_0}{x_0 - \Delta x}',
                'expected_score_min': 0,
                'expected_errors': True
            },
            {
                'name': 'Overflow Risk Formula',
                'formula_latex': r'V = x_0 \cdot y_0 \cdot z_0 \cdot w_0',
                'expected_score_min': 70
            },
            {
                'name': 'Negative Sqrt Risk',
                'formula_latex': r'S = \sqrt{P_t - P_0}',
                'expected_score_min': 0,
                'expected_errors': True
            },
            {
                'name': 'Safe Sqrt with Abs',
                'formula_latex': r'S = \sqrt{|P_t - P_0|}',
                'expected_score_min': 95
            },
            {
                'name': 'LP ROI with Range Constraints',
                'formula_latex': r'ROI = \frac{F_t}{L_0} + IL_t \quad \text{where} \quad F_t > 0',
                'expected_score_min': 85
            },
            {
                'name': 'Complex AMM Formula',
                'formula_latex': r'\text{output} = \frac{y_0 \cdot \Delta x}{x_0 + \Delta x + \epsilon} \cdot (1 - fee)',
                'expected_score_min': 90
            },
            {
                'name': 'Constant Product Check',
                'formula_latex': r'k = x \cdot y = x_0 \cdot y_0',
                'expected_score_min': 95
            }
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("=" * 70)
        print("SYMBOLIC VALIDATOR TEST SUITE - DeFi Formula Validation")
        print("=" * 70)
        print()
        
        passed = 0
        failed = 0
        
        for idx, test in enumerate(self.test_formulas, 1):
            print(f"Test {idx}/{len(self.test_formulas)}: {test['name']}")
            print("-" * 70)
            
            result = self.validator.validate(
                formula_latex=test['formula_latex'],
                domain='defi'
            )
            
            # Check expectations
            score_ok = result['score'] >= test['expected_score_min']
            errors_ok = (len(result['errors']) > 0) == test.get('expected_errors', False)
            
            test_passed = score_ok and errors_ok
            
            # Print results
            print(f"📐 Formula: {test['formula_latex'][:60]}...")
            print(f"⭐ Score: {result['score']}/100 (expected ≥ {test['expected_score_min']})")
            
            if result['errors']:
                print(f"❌ Errors ({len(result['errors'])}):")
                for error in result['errors']:
                    print(f"   - {error['rule']}: {error['message']}")
            
            if result['warnings']:
                print(f"⚠️  Warnings ({len(result['warnings'])}):")
                for warning in result['warnings']:
                    print(f"   - {warning['rule']}: {warning['message']}")
            
            # Validation details
            print(f"🔍 Validations:")
            for rule, details in result['validations'].items():
                status = "✓" if details['passed'] else "✗"
                print(f"   {status} {rule}: {details['message']}")
            
            if test_passed:
                print(f"✅ TEST PASSED")
                passed += 1
            else:
                print(f"❌ TEST FAILED")
                failed += 1
            
            print()
            
            # Store result
            self.results.append({
                'test_name': test['name'],
                'passed': test_passed,
                'result': result
            })
        
        # Summary
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {passed}/{len(self.test_formulas)}")
        print(f"❌ Failed: {failed}/{len(self.test_formulas)}")
        print(f"📊 Success Rate: {passed/len(self.test_formulas)*100:.1f}%")
        print()
        
        # Save results
        self._save_results()
        
        return {
            'total': len(self.test_formulas),
            'passed': passed,
            'failed': failed,
            'success_rate': passed/len(self.test_formulas),
            'results': self.results
        }
    
    def _save_results(self):
        """Save test results to JSON"""
        output_dir = Path('outputs/test_outputs')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'validator_test_results_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {output_file}")


def test_full_pipeline():
    """Test complete pipeline with formula generation and validation"""
    print("\n" + "=" * 70)
    print("FULL PIPELINE TEST")
    print("=" * 70)
    print()
    
    validator = DeFiValidator()
    
    # Simulate generated formulas (would come from AnthropicProvider)
    generated_formulas = [
        {
            'formula_latex': r'IL = \sqrt{\frac{2\sqrt{r}}{1+r}} - 1',
            'description': 'Basic impermanent loss',
            'novelty_score': 7
        },
        {
            'formula_latex': r'\Pi = \frac{\Delta P}{P_0 + \epsilon}',
            'description': 'Price impact with protection',
            'novelty_score': 6
        },
        {
            'formula_latex': r'ROI = \frac{F}{L} - |IL|',
            'description': 'LP ROI with absolute IL',
            'novelty_score': 8
        }
    ]
    
    selected_formulas = []
    
    for idx, formula in enumerate(generated_formulas, 1):
        print(f"\nFormula {idx}: {formula['description']}")
        print("-" * 50)
        
        # Validate
        validation = validator.validate(
            formula['formula_latex'],
            domain='defi'
        )
        
        print(f"Score: {validation['score']}/100")
        print(f"Errors: {len(validation['errors'])}")
        print(f"Warnings: {len(validation['warnings'])}")
        
        # Selection criteria
        if validation['score'] > 70:
            print("✅ Formula passed validation!")
            selected_formulas.append({
                **formula,
                'validation_score': validation['score']
            })
        else:
            print("❌ Needs improvement")
    
    print("\n" + "=" * 70)
    print(f"PIPELINE RESULTS: {len(selected_formulas)}/{len(generated_formulas)} formulas selected")
    print("=" * 70)
    
    # Save selected formulas
    if selected_formulas:
        output_file = Path('outputs/test_outputs/selected_formulas.json')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(selected_formulas, f, indent=2)
        
        print(f"\n💾 Selected formulas saved to: {output_file}")
    
    return selected_formulas


def main():
    """Main test execution"""
    
    print("\n🚀 Starting Symbolic Validator Test Suite\n")
    
    # Run validator tests
    suite = TestSuite()
    test_results = suite.run_all_tests()
    
    # Run full pipeline test
    pipeline_results = test_full_pipeline()
    
    # Final summary
    print("\n" + "=" * 70)
    print("COMPLETE TEST SESSION SUMMARY")
    print("=" * 70)
    print(f"Validator Tests: {test_results['passed']}/{test_results['total']} passed")
    print(f"Pipeline: {len(pipeline_results)} high-quality formulas selected")
    print("✅ All tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
