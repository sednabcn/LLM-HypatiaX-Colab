class AnalyticalExpressionGenerator:
    """
    COMPLETE SYSTEM
    This is what you've been asking for!
    """
    
    def __init__(self, anthropic_api_key):
        self.generator = FormulaGenerator(anthropic_api_key)
        self.validator = FormulaValidator()
        self.backtester = None  # Set with historical data
    
    def generate_and_validate(self, requirements, domain="finance", n_candidates=5):
        """
        Generate multiple formulas, validate, return best
        """
        
        candidates = []
        
        # Generate multiple candidates
        for i in range(n_candidates):
            print(f"Generating candidate {i+1}/{n_candidates}...")
            
            formula = self.generator.generate_novel_formula(
                requirements, 
                domain
            )
            
            # Validate
            validation = self.validator.validate(
                formula['formula_latex'],
                domain
            )
            
            formula['validation'] = validation
            formula['score'] = self._score_formula(formula, validation)
            
            candidates.append(formula)
        
        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return candidates
    
    def _score_formula(self, formula, validation):
        """
        Score formula quality
        """
        score = 0
        
        # Validity checks
        if validation['syntactically_valid']: score += 25
        if validation['dimensionally_consistent']: score += 25
        if validation['domain_valid']: score += 25
        if validation['numerically_stable']: score += 25
        
        # Novelty bonus
        novelty = formula.get('novelty_score', 5)
        score += novelty * 2
        
        # Penalty for errors
        score -= len(validation['errors']) * 5
        
        return max(0, min(100, score))
    
    def refine_formula(self, formula, feedback):
        """
        Iteratively improve based on user feedback
        """
        refinement_prompt = f"""
Original formula: {formula['formula_latex']}
User feedback: {feedback}

Generate an improved version addressing the feedback.
Maintain mathematical validity.
"""
        
        refined = self.generator.generate_novel_formula(refinement_prompt)
        validation = self.validator.validate(refined['formula_latex'])
        
        refined['validation'] = validation
        refined['score'] = self._score_formula(refined, validation)
        
        return refined
