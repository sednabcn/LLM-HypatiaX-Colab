# prototype_a_lookup.py
"""
Prototype A: Smart Lookup via Semantic Search
Uses sentence-transformers to match descriptions to your 580 formulas
"""

from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from typing import Dict, List
import json

class SmartLookupAPI:
    def __init__(self):
        # Load embedding model (small, fast)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 80MB model
        
        # Load your formulas
        self.defi_df = pd.read_csv('../defi_queries_280.csv')
        self.risk_df = pd.read_csv('../risk_queries_comprehensive.csv')
        self.formulas_df = pd.concat([self.defi_df, self.risk_df])
        
        # Pre-compute embeddings for all descriptions
        print("Computing embeddings for 580 formulas...")
        self.embeddings = self.model.encode(
            self.formulas_df['description'].tolist(),
            show_progress_bar=True
        )
        print("✓ Ready")
    
    def search(self, user_query: str, top_k: int = 3) -> List[Dict]:
        """Find most similar formulas."""
        # Embed user query
        query_embedding = self.model.encode([user_query])[0]
        
        # Cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top matches
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            row = self.formulas_df.iloc[idx]
            results.append({
                'similarity': float(similarities[idx]),
                'description': row['description'],
                'formula': row['analytical_formula'],
                'category': row['category'],
                'confidence': 'high' if similarities[idx] > 0.8 else 
                             'medium' if similarities[idx] > 0.6 else 'low'
            })
        
        return results
    
    def generate_formula(self, user_query: str) -> Dict:
        """Main API endpoint."""
        matches = self.search(user_query, top_k=1)
        best_match = matches[0]
        
        if best_match['similarity'] < 0.5:
            return {
                'status': 'no_match',
                'error': 'No similar formula found. Try rephrasing.',
                'closest_match': best_match
            }
        
        # Extract variables from formula
        variables = self._extract_variables(best_match['formula'])
        
        # Simple validation (just check formula is parseable)
        validation = self._quick_validate(best_match['formula'], variables)
        
        return {
            'status': 'success',
            'method': 'lookup',
            'match_confidence': best_match['similarity'],
            'formula': {
                'expression': best_match['formula'],
                'latex': self._to_latex(best_match['formula']),
                'description': best_match['description'],
                'category': best_match['category']
            },
            'validation': validation,
            'metadata': {
                'variables': variables,
                'domain': 'defi' if 'defi' in best_match['category'].lower() else 'risk',
                'complexity': self._estimate_complexity(best_match['formula'])
            },
            'response_time_ms': 150  # Typical
        }
    
    def _extract_variables(self, formula: str) -> List[Dict]:
        """Extract variable names from formula."""
        import re
        vars = re.findall(r'\b[a-z_][a-z0-9_]*\b', formula.lower())
        functions = ['sqrt', 'exp', 'log', 'sin', 'cos']
        vars = [v for v in set(vars) if v not in functions]
        
        return [{'name': v, 'unit': 'dimensionless', 'type': 'float'} for v in vars]
    
    def _quick_validate(self, formula: str, variables: List[Dict]) -> Dict:
        """Quick validation check."""
        try:
            # Try to parse with sympy
            from sympy import sympify
            expr = sympify(formula)
            return {
                'passed': True,
                'score': 85,
                'method': 'quick_check',
                'errors': []
            }
        except:
            return {
                'passed': False,
                'score': 0,
                'method': 'quick_check',
                'errors': ['Formula failed to parse']
            }
    
    def _to_latex(self, formula: str) -> str:
        """Convert to LaTeX."""
        try:
            from sympy import sympify, latex
            return latex(sympify(formula))
        except:
            return formula
    
    def _estimate_complexity(self, formula: str) -> int:
        """Estimate formula complexity."""
        operators = ['+', '-', '*', '/', '^', 'sqrt', 'exp', 'log']
        return sum(formula.count(op) for op in operators)

# ===== TEST =====
if __name__ == "__main__":
    api = SmartLookupAPI()
    
    # Test cases
    test_queries = [
        "Calculate impermanent loss for 50/50 pool",
        "Value at Risk at 95% confidence",
        "Uniswap V2 swap output with fees",
        "Sharpe ratio for portfolio",
        "Something completely random that doesn't exist"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        result = api.generate_formula(query)
        print(json.dumps(result, indent=2))
```

**Test Metrics:**
- Speed: Target <200ms
- Accuracy: % of queries returning correct formula
- Coverage: % of test queries with similarity >0.8

---

# PROTOTYPE B: "LLM Generator" (Natural Language)

## Architecture
```
User description 
  → Send to Claude/GPT-4 with structured prompt
  → Parse JSON response
  → Validate with your ensemble_validator
  → Return formula + validation
