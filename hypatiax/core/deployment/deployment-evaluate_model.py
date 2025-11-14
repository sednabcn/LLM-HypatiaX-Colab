#!/usr/bin/python3
"""
Updated Model Evaluation for Deployment
Evaluates formula accuracy, not just NER entities
"""

import json
import spacy
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np


class FormulaAccuracyEvaluator:
    """Evaluate formula prediction accuracy"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.nlp = None
        
        if model_path and Path(model_path).exists():
            try:
                self.nlp = spacy.load(model_path)
                print(f"✅ Loaded spaCy model from {model_path}")
            except Exception as e:
                print(f"⚠️  Failed to load spaCy model: {e}")
    
    def exact_match(self, predicted: str, ground_truth: str) -> bool:
        """Check exact string match"""
        return predicted.strip().upper() == ground_truth.strip().upper()
    
    def partial_match(self, predicted: str, ground_truth: str) -> float:
        """Calculate token-level overlap"""
        pred_tokens = set(predicted.upper().split())
        gt_tokens = set(ground_truth.upper().split())
        
        if not gt_tokens:
            return 0.0
        
        overlap = len(pred_tokens.intersection(gt_tokens))
        return overlap / len(gt_tokens)
    
    def syntax_correctness(self, formula: str) -> bool:
        """Check if formula has valid syntax"""
        # Must have operation
        operations = ['SUM', 'AVG', 'COUNT', 'COUNTD', 'MAX', 'MIN', 'MEDIAN']
        if not any(op in formula.upper() for op in operations):
            return False
        
        # Must have balanced brackets
        if formula.count('[') != formula.count(']'):
            return False
        
        return True
    
    def semantic_correctness(self, predicted: str, ground_truth: str) -> bool:
        """Check if operations match semantically"""
        operations = ['SUM', 'AVG', 'COUNT', 'COUNTD', 'MAX', 'MIN', 'MEDIAN']
        
        pred_ops = [op for op in operations if op in predicted.upper()]
        gt_ops = [op for op in operations if op in ground_truth.upper()]
        
        if not pred_ops or not gt_ops:
            return False
        
        return pred_ops[0] == gt_ops[0]
    
    def evaluate_predictions(self, predictions: List[Dict]) -> Dict:
        """Evaluate list of predictions"""
        total = len(predictions)
        exact_matches = 0
        partial_scores = []
        syntax_correct = 0
        semantic_correct = 0
        
        for pred in predictions:
            predicted = pred.get('predicted', '')
            ground_truth = pred.get('ground_truth', pred.get('true', ''))
            
            # Exact match
            if self.exact_match(predicted, ground_truth):
                exact_matches += 1
            
            # Partial match
            partial_scores.append(self.partial_match(predicted, ground_truth))
            
            # Syntax
            if self.syntax_correctness(predicted):
                syntax_correct += 1
            
            # Semantic
            if self.semantic_correctness(predicted, ground_truth):
                semantic_correct += 1
        
        return {
            'total_samples': total,
            'exact_match_count': exact_matches,
            'exact_match_accuracy': exact_matches / total if total > 0 else 0,
            'partial_match_avg': np.mean(partial_scores) if partial_scores else 0,
            'syntax_correctness': syntax_correct / total if total > 0 else 0,
            'semantic_correctness': semantic_correct / total if total > 0 else 0
        }
    
    def evaluate_from_file(self, predictions_file: str) -> Dict:
        """Load predictions from file and evaluate"""
        with open(predictions_file, 'r') as f:
            predictions = json.load(f)
        
        return self.evaluate_predictions(predictions)
    
    def evaluate_ner_model(self, test_file: str) -> Dict:
        """Evaluate spaCy NER model (backward compatibility)"""
        if not self.nlp:
            return {'error': 'No spaCy model loaded'}
        
        from spacy.training import Example
        from spacy.scorer import Scorer
        
        # Load test data
        with open(test_file, 'r') as f:
            test_data = json.load(f)
        
        examples = []
        for item in test_data:
            text = item['text']
            annotations = item['annotations']
            
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        
        # Score
        scorer = Scorer(self.nlp)
        scores = scorer.score(examples)
        
        return {
            'precision': scores.get('ents_p', 0),
            'recall': scores.get('ents_r', 0),
            'f1': scores.get('ents_f', 0)
        }
    
    def generate_report(self, metrics: Dict, output_file: str):
        """Generate evaluation report"""
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("FORMULA EVALUATION REPORT\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Total Samples: {metrics.get('total_samples', 0)}\n\n")
            
            f.write("ACCURACY METRICS:\n")
            f.write(f"  Exact Match: {metrics.get('exact_match_accuracy', 0):.4f}\n")
            f.write(f"  Partial Match: {metrics.get('partial_match_avg', 0):.4f}\n")
            f.write(f"  Syntax Correct: {metrics.get('syntax_correctness', 0):.4f}\n")
            f.write(f"  Semantic Correct: {metrics.get('semantic_correctness', 0):.4f}\n")
            
            f.write("\n" + "="*70 + "\n")
        
        print(f"✅ Report saved to {output_file}")


def main():
    """Example usage"""
    print("="*70)
    print("FORMULA EVALUATION")
    print("="*70)
    
    evaluator = FormulaAccuracyEvaluator()
    
    # Sample predictions
    test_predictions = [
        {
            'description': 'average of Sales',
            'predicted': 'AVG([Sales])',
            'ground_truth': 'AVG([Sales])'
        },
        {
            'description': 'sum of Revenue by Region',
            'predicted': 'SUM([Revenue]) GROUP BY [Region]',
            'ground_truth': 'SUM([Revenue]) GROUP BY [Region]'
        },
        {
            'description': 'count unique customers',
            'predicted': 'COUNTD([Customer])',
            'ground_truth': 'COUNT(DISTINCT [Customer])'
        }
    ]
    
    # Evaluate
    metrics = evaluator.evaluate_predictions(test_predictions)
    
    # Print results
    print(f"\nTotal Samples: {metrics['total_samples']}")
    print(f"Exact Match Accuracy: {metrics['exact_match_accuracy']:.4f}")
    print(f"Partial Match Average: {metrics['partial_match_avg']:.4f}")
    print(f"Syntax Correctness: {metrics['syntax_correctness']:.4f}")
    print(f"Semantic Correctness: {metrics['semantic_correctness']:.4f}")
    
    # Generate report
    evaluator.generate_report(metrics, "evaluation_report.txt")


if __name__ == "__main__":
    main()
