"""
HypatiaX Ensemble Validator (UPDATED - Week 2, Day 3)
tools/validation/ensemble_validator.py

Combines multiple validators for comprehensive validation.

CRITICAL FIXES:
- Recalibrated scoring thresholds (94.0 → 85.0 alignment)
- Adjusted domain validator weights for dimensional issues
- Enhanced penalty system for edge cases
- Documented clear acceptance criteria
"""

from hypatiax.tools.validation.symbolic_validator import SymbolicValidator
from hypatiax.tools.validation.dimensional_validator import DimensionalValidator
from hypatiax.tools.validation.domain_validator import DomainValidator
from typing import Dict, List, Optional
from collections import deque
import numpy as np


class EnsembleValidator:
    """
    Ensemble validator that combines multiple validation layers:
    1. Symbolic validation (mathematical correctness)
    2. Dimensional validation (unit consistency)
    3. Domain validation (domain-specific rules)
    4. Numerical validation (stability with test data)
    
    ACCEPTANCE CRITERIA (Updated Week 2):
    - Overall score >= 85.0 (was 70.0)
    - All critical validators must pass (symbolic, dimensional)
    - Domain-specific rules must be satisfied
    - No critical edge cases (division by zero, overflow, NaN)
    """
    
    # UPDATED: Clear threshold documentation
    VALIDATION_THRESHOLDS = {
        'minimum_total_score': 85.0,  # Aligned with test expectations
        'minimum_layer_score': 70.0,  # Individual layer minimum
        'critical_failure_threshold': 50.0,  # Below this = automatic failure
        'edge_case_penalty': 15.0,  # Penalty for each edge case violation
        'dimensional_inconsistency_penalty': 20.0,  # Increased from 10.0
    }
    
    def __init__(
        self, 
        domain: str = 'defi',
        max_history: Optional[int] = 1000,
        weights: Optional[Dict[str, float]] = None,
        strict_mode: bool = False
    ):
        """
        Initialize the ensemble validator.
        
        Args:
            domain: Domain context ('defi', 'risk', 'finance', 'esg')
            max_history: Maximum number of validation results to keep
            weights: Custom weights for each validation layer
            strict_mode: If True, apply stricter validation criteria
        """
        self.domain = domain
        self.strict_mode = strict_mode
        
        # Initialize validators
        self.symbolic_validator = SymbolicValidator(max_history=max_history)
        self.dimensional_validator = DimensionalValidator(max_history=max_history)
        self.domain_validator = DomainValidator(domain, max_history=max_history)
        
        # UPDATED: Recalibrated validation weights
        # Increased domain weight to better catch domain-specific issues
        self.weights = weights or {
            'symbolic': 0.30,      # Decreased from 0.35
            'dimensional': 0.30,   # Increased from 0.25 (dimensional issues critical)
            'domain': 0.30,        # Same as 0.30 (domain rules critical)
            'numerical': 0.10      # Same as 0.10 (supplementary check)
        }
        
        # Validate weights
        weight_sum = sum(self.weights.values())
        if not np.isclose(weight_sum, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")
        
        # Bounded validation history
        if max_history is not None:
            self.validation_history = deque(maxlen=max_history)
        else:
            self.validation_history = []
    
    def validate_complete(
        self, 
        expression_str: str,
        variable_definitions: Dict[str, str],
        variable_units: Dict[str, str],
        test_data: Optional[Dict[str, np.ndarray]] = None,
        from_latex: bool = False
    ) -> Dict:
        """
        Perform comprehensive validation across all layers.
        
        UPDATED: Now applies recalibrated thresholds and enhanced penalties.
        
        Args:
            expression_str: The mathematical expression
            variable_definitions: Variable name to description mapping
            variable_units: Variable name to unit string mapping
            test_data: Optional test data for numerical validation
            from_latex: Whether expression is in LaTeX format
            
        Returns:
            {
                'valid': bool,
                'total_score': float (0-100, >= 85.0 to pass),
                'layer_scores': Dict[str, float],
                'layer_results': Dict[str, Dict],
                'errors': List[str],
                'warnings': List[str],
                'recommendations': List[str],
                'edge_cases_detected': List[str],
                'acceptance_criteria': Dict
            }
        """
        # 1. Symbolic validation
        symbolic_result = self.symbolic_validator.validate(
            expression=expression_str,
            variable_definitions=variable_definitions,
            domain=self.domain,
            from_latex=from_latex
        )
        
        # 2. Dimensional validation
        dimensional_result = self.dimensional_validator.validate(
            expression_str=expression_str,
            variable_units=variable_units
        )
        
        # 3. Domain validation
        domain_result = self.domain_validator.validate(
            expression_str=expression_str,
            variable_definitions=variable_definitions,
            test_data=test_data
        )
        
        # 4. Numerical validation (if test data provided)
        numerical_result = self._numerical_validation(
            expression_str, test_data, symbolic_result.get('sympy_expr')
        ) if test_data else {'score': 100.0, 'errors': [], 'warnings': []}
        
        # UPDATED: Apply edge case penalties
        edge_cases = self._detect_edge_cases(
            symbolic_result, dimensional_result, domain_result, numerical_result
        )
        
        # Calculate base weighted score
        base_score = (
            self.weights['symbolic'] * symbolic_result['score'] +
            self.weights['dimensional'] * dimensional_result['score'] +
            self.weights['domain'] * domain_result['score'] +
            self.weights['numerical'] * numerical_result['score']
        )
        
        # UPDATED: Apply penalties for edge cases and dimensional issues
        total_score = self._apply_penalties(
            base_score, edge_cases, dimensional_result
        )
        
        # Aggregate all errors and warnings
        all_errors = (
            symbolic_result.get('errors', []) + 
            dimensional_result.get('errors', []) + 
            domain_result.get('errors', []) +
            numerical_result.get('errors', [])
        )
        
        all_warnings = (
            symbolic_result.get('warnings', []) + 
            dimensional_result.get('warnings', []) + 
            domain_result.get('warnings', []) +
            numerical_result.get('warnings', [])
        )
        
        # UPDATED: Determine overall validity with new criteria
        overall_valid = self._check_acceptance_criteria(
            total_score,
            symbolic_result,
            dimensional_result,
            domain_result,
            edge_cases
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            symbolic_result, dimensional_result, domain_result, numerical_result,
            edge_cases
        )
        
        # UPDATED: Document acceptance criteria evaluation
        acceptance_criteria = {
            'minimum_score_met': total_score >= self.VALIDATION_THRESHOLDS['minimum_total_score'],
            'symbolic_valid': symbolic_result['valid'],
            'dimensional_valid': dimensional_result['valid'],
            'domain_valid': domain_result['valid'],
            'no_critical_edge_cases': len([e for e in edge_cases if 'CRITICAL' in e]) == 0,
            'threshold_used': self.VALIDATION_THRESHOLDS['minimum_total_score']
        }
        
        # Compile complete result
        complete_result = {
            'valid': overall_valid,
            'total_score': total_score,
            'base_score': base_score,  # Score before penalties
            'layer_scores': {
                'symbolic': symbolic_result['score'],
                'dimensional': dimensional_result['score'],
                'domain': domain_result['score'],
                'numerical': numerical_result['score']
            },
            'layer_results': {
                'symbolic': symbolic_result,
                'dimensional': dimensional_result,
                'domain': domain_result,
                'numerical': numerical_result
            },
            'errors': all_errors,
            'warnings': all_warnings,
            'recommendations': recommendations,
            'edge_cases_detected': edge_cases,
            'acceptance_criteria': acceptance_criteria,
            'expression': expression_str,
            'canonical_form': symbolic_result.get('canonical_form'),
            'domain': self.domain,
            'strict_mode': self.strict_mode
        }
        
        # Store in history
        self.validation_history.append(complete_result)
        
        return complete_result
    
    def _detect_edge_cases(
        self,
        symbolic: Dict,
        dimensional: Dict,
        domain: Dict,
        numerical: Dict
    ) -> List[str]:
        """
        UPDATED: Enhanced edge case detection.
        
        Detects:
        - Division by zero risks
        - Numerical overflow/underflow
        - Empty expressions
        - Invalid mathematical operations
        - Dimensional inconsistencies
        """
        edge_cases = []
        
        # Check for critical symbolic issues
        if 'division by zero' in str(symbolic.get('errors', [])).lower():
            edge_cases.append('CRITICAL: Division by zero detected')
        
        if 'empty' in str(symbolic.get('errors', [])).lower():
            edge_cases.append('CRITICAL: Empty expression')
        
        # Check for numerical issues
        if 'nan' in str(numerical.get('errors', [])).lower():
            edge_cases.append('CRITICAL: Expression produces NaN values')
        
        if 'inf' in str(numerical.get('errors', [])).lower():
            edge_cases.append('CRITICAL: Expression produces infinite values')
        
        if 'overflow' in str(numerical.get('warnings', [])).lower():
            edge_cases.append('WARNING: Potential numerical overflow')
        
        # UPDATED: Enhanced dimensional inconsistency detection
        if dimensional.get('errors'):
            for error in dimensional.get('errors', []):
                if 'inconsistent' in error.lower() or 'mismatch' in error.lower():
                    edge_cases.append(f'DIMENSIONAL: {error}')
        
        # Check domain-specific edge cases
        if 'constraint violation' in str(domain.get('errors', [])).lower():
            edge_cases.append('DOMAIN: Constraint violation detected')
        
        return edge_cases
    
    def _apply_penalties(
        self,
        base_score: float,
        edge_cases: List[str],
        dimensional_result: Dict
    ) -> float:
        """
        UPDATED: Apply penalties for edge cases and dimensional issues.
        
        Penalty structure:
        - Each CRITICAL edge case: -15 points
        - Each WARNING edge case: -5 points
        - Each dimensional inconsistency: -20 points (increased)
        """
        score = base_score
        
        for edge_case in edge_cases:
            if 'CRITICAL' in edge_case:
                score -= self.VALIDATION_THRESHOLDS['edge_case_penalty']
            elif 'WARNING' in edge_case:
                score -= 5.0
            elif 'DIMENSIONAL' in edge_case:
                score -= self.VALIDATION_THRESHOLDS['dimensional_inconsistency_penalty']
            elif 'DOMAIN' in edge_case:
                score -= 10.0
        
        # Ensure score doesn't go below 0
        return max(0.0, score)
    
    def _check_acceptance_criteria(
        self,
        total_score: float,
        symbolic: Dict,
        dimensional: Dict,
        domain: Dict,
        edge_cases: List[str]
    ) -> bool:
        """
        UPDATED: Check if expression meets acceptance criteria.
        
        Requirements (all must be met):
        1. Total score >= 85.0 (updated threshold)
        2. Symbolic validation must pass
        3. Dimensional validation must pass
        4. No critical edge cases
        5. In strict mode: domain validation must also pass
        """
        # Check minimum score threshold
        if total_score < self.VALIDATION_THRESHOLDS['minimum_total_score']:
            return False
        
        # Critical validators must pass
        if not symbolic['valid'] or not dimensional['valid']:
            return False
        
        # No critical edge cases allowed
        critical_edge_cases = [e for e in edge_cases if 'CRITICAL' in e]
        if critical_edge_cases:
            return False
        
        # In strict mode, domain validation must also pass
        if self.strict_mode and not domain['valid']:
            return False
        
        # Check for critical failure in any layer
        for score in [symbolic['score'], dimensional['score'], domain['score']]:
            if score < self.VALIDATION_THRESHOLDS['critical_failure_threshold']:
                return False
        
        return True
    
    def _numerical_validation(
        self,
        expression_str: str,
        test_data: Dict[str, np.ndarray],
        sympy_expr
    ) -> Dict:
        """
        Validate numerical stability using test data.
        
        Checks:
        - No NaN or Inf in outputs
        - Reasonable output ranges
        - Numerical stability
        """
        result = {
            'score': 100.0,
            'errors': [],
            'warnings': []
        }
        
        if not test_data or sympy_expr is None:
            return result
        
        try:
            import sympy as sp
            
            # Convert test data to evaluation
            free_vars = list(sympy_expr.free_symbols)
            
            # Check if we have all required variables
            missing_vars = [str(v) for v in free_vars if str(v) not in test_data]
            if missing_vars:
                result['warnings'].append(
                    f"Missing test data for variables: {missing_vars}"
                )
                result['score'] -= 10
                return result
            
            # Evaluate expression with test data
            n_samples = len(next(iter(test_data.values())))
            outputs = []
            
            for i in range(n_samples):
                substitutions = {
                    str(var): float(test_data[str(var)][i])
                    for var in free_vars
                    if str(var) in test_data
                }
                
                try:
                    value = float(sympy_expr.subs(substitutions))
                    outputs.append(value)
                except Exception as e:
                    result['errors'].append(
                        f"Evaluation error at sample {i}: {str(e)}"
                    )
                    result['score'] -= 10
            
            if outputs:
                outputs = np.array(outputs)
                
                # Check for NaN
                if np.any(np.isnan(outputs)):
                    result['errors'].append(
                        f"Expression produces NaN values "
                        f"({np.sum(np.isnan(outputs))}/{len(outputs)} samples)"
                    )
                    result['score'] -= 30
                
                # Check for Inf
                if np.any(np.isinf(outputs)):
                    result['errors'].append(
                        f"Expression produces infinite values "
                        f"({np.sum(np.isinf(outputs))}/{len(outputs)} samples)"
                    )
                    result['score'] -= 30
                
                # Check for extreme values (potential overflow)
                valid_outputs = outputs[np.isfinite(outputs)]
                if len(valid_outputs) > 0:
                    max_abs = np.max(np.abs(valid_outputs))
                    if max_abs > 1e10:
                        result['warnings'].append(
                            f"Very large output values detected (max: {max_abs:.2e})"
                        )
                        result['score'] -= 10
                    
                    # Check for very small values (potential underflow)
                    min_abs = np.min(np.abs(valid_outputs[valid_outputs != 0]))
                    if min_abs < 1e-10:
                        result['warnings'].append(
                            f"Very small output values detected (min: {min_abs:.2e})"
                        )
                        result['score'] -= 5
        
        except Exception as e:
            result['warnings'].append(f"Numerical validation error: {str(e)}")
            result['score'] -= 15
        
        return result
    
    def _generate_recommendations(
        self,
        symbolic: Dict,
        dimensional: Dict,
        domain: Dict,
        numerical: Dict,
        edge_cases: List[str]
    ) -> List[str]:
        """
        UPDATED: Generate actionable recommendations including edge case fixes.
        """
        recommendations = []
        
        # Edge case recommendations (highest priority)
        if edge_cases:
            critical_cases = [e for e in edge_cases if 'CRITICAL' in e]
            if critical_cases:
                recommendations.append(
                    f"🔴 FIX CRITICAL: Resolve {len(critical_cases)} edge case(s) immediately"
                )
                for case in critical_cases[:3]:  # Show first 3
                    recommendations.append(f"  - {case}")
        
        # Symbolic recommendations
        if not symbolic['valid']:
            recommendations.append(
                "🔴 FIX CRITICAL: Resolve symbolic/mathematical errors first"
            )
        elif symbolic['score'] < 90:
            if symbolic.get('canonical_form'):
                recommendations.append(
                    f"🟡 IMPROVE: Simplify expression to: {symbolic['canonical_form']}"
                )
        
        # Dimensional recommendations
        if not dimensional['valid']:
            recommendations.append(
                "🔴 FIX CRITICAL: Resolve dimensional inconsistencies"
            )
        elif dimensional['warnings']:
            recommendations.append(
                "🟡 VERIFY: Check dimensional analysis warnings carefully"
            )
        
        # Domain recommendations
        if not domain['valid']:
            recommendations.append(
                f"🔴 FIX CRITICAL: Violates {self.domain} domain constraints"
            )
        elif domain['warnings']:
            recommendations.append(
                f"🟡 REVIEW: Address domain-specific warnings for {self.domain}"
            )
        
        # Numerical recommendations
        if numerical['errors']:
            recommendations.append(
                "🔴 FIX: Resolve numerical stability issues"
            )
        elif numerical['warnings']:
            recommendations.append(
                "🟡 OPTIMIZE: Improve numerical stability"
            )
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ Expression passes all validation checks")
        
        return recommendations
    
    # History management methods
    
    def clear_history(self):
        """Clear all validation history."""
        if isinstance(self.validation_history, deque):
            self.validation_history.clear()
        else:
            self.validation_history = []
        
        # Also clear sub-validator histories
        self.symbolic_validator.clear_history()
        self.dimensional_validator.clear_history()
        self.domain_validator.clear_history()
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get validation history."""
        history_list = list(self.validation_history)
        if limit is not None:
            return history_list[-limit:]
        return history_list
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about validation history."""
        if not self.validation_history:
            return {
                'total_validations': 0,
                'success_rate': 0.0,
                'average_total_score': 0.0,
                'average_layer_scores': {},
                'threshold_used': self.VALIDATION_THRESHOLDS['minimum_total_score']
            }
        
        total = len(self.validation_history)
        valid_count = sum(1 for v in self.validation_history if v['valid'])
        
        avg_total_score = sum(
            v['total_score'] for v in self.validation_history
        ) / total
        
        # Calculate average scores per layer
        avg_layer_scores = {}
        for layer in ['symbolic', 'dimensional', 'domain', 'numerical']:
            scores = [
                v['layer_scores'][layer] 
                for v in self.validation_history
            ]
            avg_layer_scores[layer] = sum(scores) / len(scores)
        
        return {
            'total_validations': total,
            'success_rate': valid_count / total,
            'average_total_score': avg_total_score,
            'average_layer_scores': avg_layer_scores,
            'valid_count': valid_count,
            'invalid_count': total - valid_count,
            'domain': self.domain,
            'threshold_used': self.VALIDATION_THRESHOLDS['minimum_total_score']
        }
    
    def get_weakest_layer(self) -> str:
        """Identify which validation layer has the lowest average score."""
        stats = self.get_statistics()
        if not stats['average_layer_scores']:
            return None
        
        return min(
            stats['average_layer_scores'].items(),
            key=lambda x: x[1]
        )[0]


# Example usage
if __name__ == "__main__":
    # Initialize ensemble validator
    validator = EnsembleValidator(domain='defi')
    
    # Test expression
    result = validator.validate_complete(
        expression_str="sqrt(reserve0 * reserve1) / liquidity",
        variable_definitions={
            'reserve0': 'Token 0 reserves',
            'reserve1': 'Token 1 reserves',
            'liquidity': 'Total pool liquidity'
        },
        variable_units={
            'reserve0': 'USD',
            'reserve1': 'USD',
            'liquidity': 'USD'
        },
        test_data={
            'reserve0': np.array([100, 200, 300]),
            'reserve1': np.array([50, 100, 150]),
            'liquidity': np.array([1000, 2000, 3000])
        }
    )
    
    print(f"Overall Valid: {result['valid']}")
    print(f"Total Score: {result['total_score']:.2f}")
    print(f"Base Score: {result['base_score']:.2f}")
    print(f"\nAcceptance Criteria:")
    for key, value in result['acceptance_criteria'].items():
        print(f"  {key}: {value}")
    
    print(f"\nLayer Scores:")
    for layer, score in result['layer_scores'].items():
        print(f"  {layer}: {score:.2f}")
    
    print(f"\nEdge Cases: {result['edge_cases_detected']}")
    
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  {rec}")
    
    # Get statistics
    stats = validator.get_statistics()
    print(f"\nStatistics: {stats}")
    print(f"Weakest layer: {validator.get_weakest_layer()}")
