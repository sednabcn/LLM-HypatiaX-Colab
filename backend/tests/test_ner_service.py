"""
Unit tests for NER Service
File: backend/tests/test_ner_service.py

Run with: pytest test_ner_service.py
or: python -m pytest test_ner_service.py -v
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from services.ner_service import NERService


class TestNERService(unittest.TestCase):
    """Test cases for NER Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ner_service = NERService()
    
    # ========================================================================
    # Formula Extraction Tests
    # ========================================================================
    
    def test_extract_simple_formula(self):
        """Test extracting a simple formula"""
        text = "The impermanent loss is IL = 2*sqrt(r)/(r+1) - 1"
        result = self.ner_service.extract_formulas(text, domain='defi')
        
        self.assertGreater(len(result['formulas']), 0)
        self.assertIn('IL', result['variables'])
        self.assertIn('r', result['variables'])
        self.assertEqual(result['domain'], 'defi')
    
    def test_extract_multiple_formulas(self):
        """Test extracting multiple formulas from text"""
        text = """
        First, calculate IL = 2*sqrt(r)/(r+1) - 1.
        Then compute fees = volume * rate.
        Finally, net = fees - IL.
        """
        result = self.ner_service.extract_formulas(text)
        
        self.assertGreaterEqual(len(result['formulas']), 2)
        self.assertGreater(len(result['variables']), 0)
    
    def test_extract_no_formulas(self):
        """Test text with no formulas"""
        text = "This is just plain text with no mathematical formulas."
        result = self.ner_service.extract_formulas(text)
        
        self.assertEqual(result['count'], 0)
    
    def test_extract_defi_formulas(self):
        """Test DeFi specific formula extraction"""
        text = "Calculate quality_score = daily_fees / daily_il_rate"
        result = self.ner_service.extract_formulas(text, domain='defi')
        
        self.assertIn('quality_score', result['variables'])
        self.assertIn('daily_fees', result['variables'])
        self.assertIn('daily_il_rate', result['variables'])
    
    # ========================================================================
    # Entity Recognition Tests
    # ========================================================================
    
    def test_recognize_variables(self):
        """Test recognizing variables"""
        text = "Calculate x + y = z"
        result = self.ner_service.recognize_entities(text, entity_types=['variable'])
        
        variables = [e for e in result['entities'] if e['type'] == 'variable']
        variable_names = [e['text'] for e in variables]
        
        self.assertIn('x', variable_names)
        self.assertIn('y', variable_names)
        self.assertIn('z', variable_names)
    
    def test_recognize_constants(self):
        """Test recognizing numeric constants"""
        text = "The formula is 2 * pi * 3.14"
        result = self.ner_service.recognize_entities(text, entity_types=['constant'])
        
        constants = [e for e in result['entities'] if e['type'] == 'constant']
        constant_values = [e['text'] for e in constants]
        
        self.assertIn('2', constant_values)
        self.assertIn('3.14', constant_values)
    
    def test_recognize_operators(self):
        """Test recognizing operators"""
        text = "x + y - z * w / 2"
        result = self.ner_service.recognize_entities(text, entity_types=['operator'])
        
        operators = [e for e in result['entities'] if e['type'] == 'operator']
        operator_symbols = [e['text'] for e in operators]
        
        self.assertIn('+', operator_symbols)
        self.assertIn('-', operator_symbols)
        self.assertIn('*', operator_symbols)
        self.assertIn('/', operator_symbols)
    
    def test_recognize_functions(self):
        """Test recognizing mathematical functions"""
        text = "Calculate sqrt(x) + log(y) + exp(z)"
        result = self.ner_service.recognize_entities(text, entity_types=['function'])
        
        functions = [e for e in result['entities'] if e['type'] == 'function']
        function_names = [e['text'] for e in functions]
        
        self.assertIn('sqrt', function_names)
        self.assertIn('log', function_names)
        self.assertIn('exp', function_names)
    
    def test_entity_positions(self):
        """Test that entity positions are correct"""
        text = "x + y"
        result = self.ner_service.recognize_entities(text, entity_types=['variable', 'operator'])
        
        self.assertGreater(len(result['entities']), 0)
        for entity in result['entities']:
            self.assertIn('position', entity)
            self.assertEqual(len(entity['position']), 2)
    
    # ========================================================================
    # Expression Parsing Tests
    # ========================================================================
    
    def test_parse_simple_expression(self):
        """Test parsing a simple expression"""
        expression = "x + y"
        result = self.ner_service.parse_expression(expression)
        
        self.assertIn('variables', result)
        self.assertIn('operators', result)
        self.assertIn('x', result['variables'])
        self.assertIn('y', result['variables'])
    
    def test_parse_complex_expression(self):
        """Test parsing a complex expression"""
        expression = "2*sqrt(x)/(x+1) - 1"
        result = self.ner_service.parse_expression(expression)
        
        self.assertIn('variables', result)
        self.assertIn('functions', result)
        self.assertIn('x', result['variables'])
        self.assertGreater(result['complexity'], 0)
    
    def test_parse_invalid_expression(self):
        """Test parsing an invalid expression"""
        expression = "x + + y"  # Invalid: consecutive operators
        result = self.ner_service.parse_expression(expression)
        
        # Should return error information
        self.assertTrue('error' in result or 'parsed' in result)
    
    # ========================================================================
    # LaTeX Conversion Tests
    # ========================================================================
    
    def test_convert_to_latex_inline(self):
        """Test converting to inline LaTeX"""
        expression = "x + y"
        result = self.ner_service.convert_to_latex(expression, style='inline')
        
        self.assertIn('latex', result)
        self.assertIn('$', result['latex'])
        self.assertEqual(result['style'], 'inline')
    
    def test_convert_to_latex_display(self):
        """Test converting to display LaTeX"""
        expression = "x + y"
        result = self.ner_service.convert_to_latex(expression, style='display')
        
        self.assertIn('latex', result)
        self.assertTrue('\\[' in result['latex'] or '\\]' in result['latex'])
    
    def test_convert_complex_to_latex(self):
        """Test converting complex expression to LaTeX"""
        expression = "sqrt(x) / (x + 1)"
        result = self.ner_service.convert_to_latex(expression)
        
        self.assertIn('latex', result)
        self.assertIn('sqrt', result['latex'].lower())
    
    # ========================================================================
    # Domain Identification Tests
    # ========================================================================
    
    def test_identify_defi_domain(self):
        """Test identifying DeFi domain"""
        text = "Calculate impermanent loss in the liquidity pool"
        result = self.ner_service.identify_domain(text)
        
        self.assertEqual(result['domain'], 'defi')
        self.assertGreater(result['confidence'], 0)
        self.assertIn('impermanent loss', result['keywords'])
    
    def test_identify_finance_domain(self):
        """Test identifying finance domain"""
        text = "Calculate the net present value and discount rate"
        result = self.ner_service.identify_domain(text)
        
        self.assertEqual(result['domain'], 'finance')
        self.assertGreater(result['confidence'], 0)
    
    def test_identify_physics_domain(self):
        """Test identifying physics domain"""
        text = "Calculate velocity and acceleration using force and mass"
        result = self.ner_service.identify_domain(text)
        
        self.assertEqual(result['domain'], 'physics')
        self.assertGreater(result['confidence'], 0)
    
    def test_identify_general_domain(self):
        """Test identifying general domain (no specific keywords)"""
        text = "This is just general text with no specific domain"
        result = self.ner_service.identify_domain(text)
        
        self.assertEqual(result['domain'], 'general')
        self.assertEqual(result['confidence'], 0.0)
    
    # ========================================================================
    # Syntax Validation Tests
    # ========================================================================
    
    def test_validate_correct_syntax(self):
        """Test validating correct syntax"""
        expression = "x + y * z"
        result = self.ner_service.validate_syntax(expression)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_unmatched_parentheses(self):
        """Test detecting unmatched parentheses"""
        expression = "(x + y"
        result = self.ner_service.validate_syntax(expression)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertTrue(any('parenthes' in e.lower() for e in result['errors']))
    
    def test_validate_consecutive_operators(self):
        """Test detecting consecutive operators"""
        expression = "x ++ y"
        result = self.ner_service.validate_syntax(expression)
        
        # Should have warnings or errors
        self.assertTrue(len(result['warnings']) > 0 or len(result['errors']) > 0)
    
    def test_validate_empty_parentheses(self):
        """Test detecting empty parentheses"""
        expression = "x + ()"
        result = self.ner_service.validate_syntax(expression)
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('empty' in e.lower() for e in result['errors']))
    
    # ========================================================================
    # Helper Method Tests
    # ========================================================================
    
    def test_extract_variables_helper(self):
        """Test _extract_variables helper method"""
        formula = "x + y * z - abc"
        variables = self.ner_service._extract_variables(formula)
        
        self.assertIn('x', variables)
        self.assertIn('y', variables)
        self.assertIn('z', variables)
        self.assertIn('abc', variables)
    
    def test_simple_latex_conversion(self):
        """Test _to_latex_simple helper method"""
        formula = "x**2 + sqrt(y)"
        latex = self.ner_service._to_latex_simple(formula)
        
        self.assertIn('^', latex)  # Power converted
        self.assertIn('sqrt', latex)  # Sqrt preserved
    
    # ========================================================================
    # Integration Tests
    # ========================================================================
    
    def test_full_workflow(self):
        """Test complete workflow: extract -> parse -> convert"""
        text = "The formula is IL = 2*sqrt(r)/(r+1) - 1"
        
        # Step 1: Extract
        extract_result = self.ner_service.extract_formulas(text, domain='defi')
        self.assertGreater(len(extract_result['formulas']), 0)
        
        # Step 2: Parse
        formula = extract_result['formulas'][0]
        parse_result = self.ner_service.parse_expression(formula)
        self.assertIn('variables', parse_result)
        
        # Step 3: Convert
        latex_result = self.ner_service.convert_to_latex(formula)
        self.assertIn('latex', latex_result)
    
    def test_batch_processing(self):
        """Test processing multiple texts"""
        texts = [
            "IL = 2*sqrt(r)/(r+1) - 1",
            "fees = volume * rate",
            "net = fees - IL"
        ]
        
        results = []
        for text in texts:
            result = self.ner_service.extract_formulas(text)
            results.append(result)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertGreaterEqual(result['count'], 0)


# ============================================================================
# Test Runner
# ============================================================================

def run_tests():
    """Run all tests with detailed output"""
    print("="*80)
    print("Running NER Service Tests")
    print("="*80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNERService)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*80)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
