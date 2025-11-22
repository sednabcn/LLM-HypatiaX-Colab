"""
NER Service for Mathematical Formula Extraction
File: backend/services/ner_service.py
"""

import re
from typing import Dict, List, Any, Tuple
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application


class NERService:
    """Service for Named Entity Recognition in mathematical formulas"""
    
    # Domain-specific keywords
    DOMAIN_KEYWORDS = {
        'defi': [
            'impermanent loss', 'liquidity', 'pool', 'swap', 'fee', 
            'price ratio', 'tvl', 'volume', 'slippage', 'amm',
            'constant product', 'reserve', 'token', 'yield'
        ],
        'finance': [
            'interest', 'rate', 'return', 'investment', 'profit',
            'dividend', 'bond', 'equity', 'valuation', 'npv',
            'discount', 'cash flow', 'yield', 'duration'
        ],
        'physics': [
            'velocity', 'acceleration', 'force', 'mass', 'energy',
            'momentum', 'power', 'work', 'frequency', 'wavelength'
        ],
        'statistics': [
            'mean', 'median', 'variance', 'deviation', 'probability',
            'distribution', 'correlation', 'regression', 'hypothesis'
        ]
    }
    
    # Mathematical operators and functions
    OPERATORS = ['+', '-', '*', '/', '^', '**', '=', '<', '>', '≤', '≥', '≠']
    FUNCTIONS = ['sqrt', 'log', 'ln', 'exp', 'sin', 'cos', 'tan', 'abs', 'max', 'min']
    
    def __init__(self):
        """Initialize NER service"""
        self.formula_patterns = [
            # Pattern for equations: var = expression
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^,;.]+)',
            # Pattern for expressions in parentheses
            r'\(([^()]+)\)',
            # Pattern for mathematical expressions
            r'([a-zA-Z_][a-zA-Z0-9_]*(?:\s*[+\-*/^]\s*[a-zA-Z0-9_]+)+)',
        ]
    
    def extract_formulas(
        self, 
        text: str, 
        domain: str = 'general',
        extract_variables: bool = True
    ) -> Dict[str, Any]:
        """
        Extract mathematical formulas from text
        
        Args:
            text: Input text containing formulas
            domain: Mathematical domain (defi, finance, physics, etc.)
            extract_variables: Whether to extract variables
            
        Returns:
            Dictionary with extracted formulas and metadata
        """
        formulas = []
        variables = set()
        constants = set()
        operators = set()
        
        # Extract formulas using patterns
        for pattern in self.formula_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                formula = match.group(0).strip()
                if formula and len(formula) > 2:
                    formulas.append(formula)
                    
                    # Extract variables if requested
                    if extract_variables:
                        vars_in_formula = self._extract_variables(formula)
                        variables.update(vars_in_formula)
        
        # Remove duplicates
        formulas = list(set(formulas))
        
        # Extract operators
        for op in self.OPERATORS:
            if op in text:
                operators.add(op)
        
        # Identify constants (numbers)
        constant_matches = re.findall(r'\b\d+\.?\d*\b', text)
        constants.update(constant_matches)
        
        # Convert to LaTeX (simplified)
        latex_formulas = []
        for formula in formulas:
            try:
                latex = self._to_latex_simple(formula)
                latex_formulas.append(latex)
            except:
                latex_formulas.append(formula)
        
        return {
            'formulas': formulas,
            'variables': sorted(list(variables)),
            'constants': sorted(list(constants)),
            'operators': sorted(list(operators)),
            'latex': latex_formulas,
            'domain': domain,
            'count': len(formulas)
        }
    
    def recognize_entities(
        self,
        text: str,
        entity_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Recognize mathematical entities in text
        
        Args:
            text: Input text
            entity_types: Types of entities to recognize
            
        Returns:
            Dictionary with recognized entities
        """
        if entity_types is None:
            entity_types = ['variable', 'constant', 'operator', 'function']
        
        entities = []
        
        # Recognize variables (single letters or words followed by numbers)
        if 'variable' in entity_types:
            var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
            for match in re.finditer(var_pattern, text):
                # Skip if it's a function name
                if match.group(1) not in self.FUNCTIONS:
                    entities.append({
                        'text': match.group(1),
                        'type': 'variable',
                        'position': [match.start(), match.end()],
                        'confidence': 0.9
                    })
        
        # Recognize constants (numbers)
        if 'constant' in entity_types:
            const_pattern = r'\b(\d+\.?\d*)\b'
            for match in re.finditer(const_pattern, text):
                entities.append({
                    'text': match.group(1),
                    'type': 'constant',
                    'position': [match.start(), match.end()],
                    'confidence': 1.0
                })
        
        # Recognize operators
        if 'operator' in entity_types:
            for op in self.OPERATORS:
                for match in re.finditer(re.escape(op), text):
                    entities.append({
                        'text': op,
                        'type': 'operator',
                        'position': [match.start(), match.end()],
                        'confidence': 1.0
                    })
        
        # Recognize functions
        if 'function' in entity_types:
            for func in self.FUNCTIONS:
                pattern = rf'\b{func}\b'
                for match in re.finditer(pattern, text):
                    entities.append({
                        'text': func,
                        'type': 'function',
                        'position': [match.start(), match.end()],
                        'confidence': 1.0
                    })
        
        return {
            'entities': entities,
            'total_count': len(entities)
        }
    
    def parse_expression(
        self,
        expression: str,
        output_format: str = 'tree'
    ) -> Dict[str, Any]:
        """
        Parse mathematical expression into structured format
        
        Args:
            expression: Mathematical expression
            output_format: Output format (tree, list, graph)
            
        Returns:
            Parsed expression structure
        """
        try:
            # Parse using sympy
            transformations = standard_transformations + (implicit_multiplication_application,)
            expr = parse_expr(expression, transformations=transformations)
            
            # Extract components
            variables = [str(s) for s in expr.free_symbols]
            
            # Get operators and functions
            operators = []
            functions = []
            
            for atom in sp.preorder_traversal(expr):
                if isinstance(atom, sp.Function):
                    functions.append(atom.func.__name__)
                elif atom.is_Mul or atom.is_Add or atom.is_Pow:
                    op = type(atom).__name__
                    operators.append(op)
            
            return {
                'parsed': str(expr),
                'variables': sorted(list(set(variables))),
                'operators': sorted(list(set(operators))),
                'functions': sorted(list(set(functions))),
                'complexity': len(list(sp.preorder_traversal(expr))),
                'sympy_repr': repr(expr)
            }
        
        except Exception as e:
            return {
                'error': f'Failed to parse expression: {str(e)}',
                'expression': expression
            }
    
    def convert_to_latex(
        self,
        expression: str,
        style: str = 'inline'
    ) -> Dict[str, Any]:
        """
        Convert mathematical expression to LaTeX
        
        Args:
            expression: Mathematical expression
            style: LaTeX style (inline, display, equation)
            
        Returns:
            LaTeX formatted expression
        """
        try:
            # Parse using sympy
            transformations = standard_transformations + (implicit_multiplication_application,)
            expr = parse_expr(expression, transformations=transformations)
            
            # Convert to LaTeX
            latex = sp.latex(expr)
            
            # Apply style
            if style == 'display':
                latex = f'\\[{latex}\\]'
            elif style == 'equation':
                latex = f'\\begin{{equation}}\n{latex}\n\\end{{equation}}'
            else:  # inline
                latex = f'${latex}$'
            
            return {
                'latex': latex,
                'style': style,
                'original': expression
            }
        
        except Exception as e:
            # Fallback to simple conversion
            latex = self._to_latex_simple(expression)
            return {
                'latex': f'${latex}$' if style == 'inline' else f'\\[{latex}\\]',
                'style': style,
                'original': expression,
                'warning': 'Used simplified LaTeX conversion'
            }
    
    def identify_domain(self, text: str) -> Dict[str, Any]:
        """
        Identify mathematical domain from text
        
        Args:
            text: Input text
            
        Returns:
            Identified domain with confidence and keywords
        """
        text_lower = text.lower()
        domain_scores = {}
        found_keywords = {}
        
        # Calculate scores for each domain
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = 0
            found = []
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
                    found.append(keyword)
            domain_scores[domain] = score
            found_keywords[domain] = found
        
        # Find best match
        if max(domain_scores.values()) > 0:
            best_domain = max(domain_scores, key=domain_scores.get)
            confidence = domain_scores[best_domain] / len(self.DOMAIN_KEYWORDS[best_domain])
            
            return {
                'domain': best_domain,
                'confidence': round(confidence, 2),
                'keywords': found_keywords[best_domain],
                'alternative_domains': [
                    {'domain': d, 'score': s} 
                    for d, s in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)[1:3]
                    if s > 0
                ]
            }
        else:
            return {
                'domain': 'general',
                'confidence': 0.0,
                'keywords': [],
                'alternative_domains': []
            }
    
    def validate_syntax(
        self,
        expression: str,
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Validate mathematical expression syntax
        
        Args:
            expression: Mathematical expression
            strict: Strict validation mode
            
        Returns:
            Validation result with errors and suggestions
        """
        errors = []
        warnings = []
        suggestions = []
        
        # Check for balanced parentheses
        if expression.count('(') != expression.count(')'):
            errors.append('Unmatched parentheses')
            suggestions.append('Check opening and closing parentheses')
        
        # Check for balanced brackets
        if expression.count('[') != expression.count(']'):
            errors.append('Unmatched brackets')
        
        # Check for consecutive operators
        if re.search(r'[+\-*/^]{2,}', expression):
            warnings.append('Consecutive operators found')
            suggestions.append('Review operator usage')
        
        # Check for empty parentheses
        if '()' in expression:
            errors.append('Empty parentheses found')
        
        # Try to parse with sympy
        try:
            transformations = standard_transformations + (implicit_multiplication_application,)
            parse_expr(expression, transformations=transformations)
            valid = len(errors) == 0
        except Exception as e:
            valid = False
            errors.append(f'Parse error: {str(e)}')
        
        return {
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions,
            'expression': expression
        }
    
    # Helper methods
    
    def _extract_variables(self, formula: str) -> List[str]:
        """Extract variable names from formula"""
        # Match variable names (letters followed by optional numbers/underscores)
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        variables = re.findall(var_pattern, formula)
        
        # Filter out function names
        variables = [v for v in variables if v not in self.FUNCTIONS]
        
        return list(set(variables))
    
    def _to_latex_simple(self, formula: str) -> str:
        """Simple LaTeX conversion without sympy"""
        latex = formula
        
        # Replace common patterns
        latex = re.sub(r'\*\*', '^', latex)
        latex = re.sub(r'sqrt\(([^)]+)\)', r'\\sqrt{\1}', latex)
        latex = re.sub(r'(\w+)/(\w+)', r'\\frac{\1}{\2}', latex)
        
        return latex
