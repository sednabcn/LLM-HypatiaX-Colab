#!/usr/bin/python3
"""
Unified Evaluation Framework
Evaluates all models (spaCy, Transformer, RAG, LLM, Ensemble)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics"""
    accuracy: float
    exact_match: float
    partial_match: float
    syntax_correctness: float
    semantic_correctness: float
    total_samples: int
    correct_samples: int


class FormulaEvaluator:
    """Evaluate formula predictions"""
    
    @staticmethod
    def exact_match(predicted: str, ground_truth: str) -> bool:
        """Check exact string match"""
        return predicted.strip() == ground_truth.strip()
    
    @staticmethod
    def normalize_formula(formula: str) -> str:
        """Normalize formula for comparison"""
        # Remove extra spaces
        formula = ' '.join(formula.split())
        # Uppercase operations
        formula = formula.upper()
        return formula
    
    @staticmethod
    def partial_match(predicted: str, ground_truth: str) -> float:
        """Calculate partial match score"""
        pred_norm = FormulaEvaluator.normalize_formula(predicted)
        gt_norm = FormulaEvaluator.normalize_formula(ground_truth)
        
        # Token-level overlap
        pred_tokens = set(pred_norm.split())
        gt_tokens = set(gt_norm.split())
        
        if not gt_tokens:
            return 0.0
        
        overlap = len(pred_tokens.intersection(gt_tokens))
        return overlap / len(gt_tokens)
    
    @staticmethod
    def check_syntax(formula: str) -> bool:
        """Check if formula has valid syntax"""
        # Must have function name
        if not any(op in formula.upper() for op in ['SUM', 'AVG', 'COUNT', 'MAX', 'MIN']):
            return False
        
        # Must have balanced brackets
        if formula.count('[') != formula.count(']'):
            return False
        
        # Must have column reference
        if '[' not in formula or ']' not in formula:
            return False
        
        return True
    
    @staticmethod
    def check_semantic(predicted: str, ground_truth: str, 
                      query: str = "") -> bool:
        """Check semantic correctness"""
        # Extract operation types
        operations = ['SUM', 'AVG', 'COUNT', 'COUNTD', 'MAX', 'MIN', 'MEDIAN']
        
        pred_ops = [op for op in operations if op in predicted.upper()]
        gt_ops = [op for op in operations if op in ground_truth.upper()]
        
        # Operations must match
        if not pred_ops or not gt_ops:
            return False
        
        return pred_ops[0] == gt_ops[0]


class ModelEvaluator:
    """Evaluate different model types"""
    
    def __init__(self):
        self.formula_eval = FormulaEvaluator()
    
    def evaluate_predictions(self, predictions: List[Dict]) -> EvaluationMetrics:
        """Evaluate a list of predictions"""
        
        total = len(predictions)
        exact_matches = 0
        partial_scores = []
        syntax_correct = 0
        semantic_correct = 0
        
        for pred in predictions:
            predicted = pred.get('predicted', '')
            ground_truth = pred.get('true', pred.get('ground_truth', ''))
            query = pred.get('query', pred.get('description', ''))
            
            # Exact match
            if self.formula_eval.exact_match(predicted, ground_truth):
                exact_matches += 1
            
            # Partial match
            partial_score = self.formula_eval.partial_match(predicted, ground_truth)
            partial_scores.append(partial_score)
            
            # Syntax correctness
            if self.formula_eval.check_syntax(predicted):
                syntax_correct += 1
            
            # Semantic correctness
            if self.formula_eval.check_semantic(predicted, ground_truth, query):
                semantic_correct += 1
        
        return EvaluationMetrics(
            accuracy=exact_matches / total if total > 0 else 0,
            exact_match=exact_matches / total if total > 0 else 0,
            partial_match=np.mean(partial_scores) if partial_scores else 0,
            syntax_correctness=syntax_correct / total if total > 0 else 0,
            semantic_correctness=semantic_correct / total if total > 0 else 0,
            total_samples=total,
            correct_samples=exact_matches
        )
    
    def evaluate_spacy_ner(self, model_path: str, test_data: List[Tuple]) -> Dict:
        """Evaluate spaCy NER model"""
        try:
            import spacy
            from spacy.training import Example
            from spacy.scorer import Scorer
            
            nlp = spacy.load(model_path)
            scorer = Scorer(nlp)
            
            for text, annotations in test_data:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                scorer.score([example])
            
            return {
                'precision': scorer.scores.get('ents_p', 0),
                'recall': scorer.scores.get('ents_r', 0),
                'f1': scorer.scores.get('ents_f', 0)
            }
        except Exception as e:
            print(f"Error evaluating spaCy model: {e}")
            return {'precision': 0, 'recall': 0, 'f1': 0}
    
    def evaluate_from_file(self, predictions_file: str) -> EvaluationMetrics:
        """Evaluate predictions from JSON file"""
        with open(predictions_file, 'r') as f:
            predictions = json.load(f)
        
        return self.evaluate_predictions(predictions)


class ComparisonReport:
    """Generate comparison reports across models"""
    
    def __init__(self):
        self.results = {}
    
    def add_model_results(self, model_name: str, metrics: EvaluationMetrics):
        """Add results for a model"""
        self.results[model_name] = metrics
    
    def generate_table(self) -> pd.DataFrame:
        """Generate comparison table"""
        data = []
        
        for model_name, metrics in self.results.items():
            data.append({
                'Model': model_name,
                'Accuracy': f"{metrics.accuracy:.3f}",
                'Exact Match': f"{metrics.exact_match:.3f}",
                'Partial Match': f"{metrics.partial_match:.3f}",
                'Syntax Correct': f"{metrics.syntax_correctness:.3f}",
                'Semantic Correct': f"{metrics.semantic_correctness:.3f}",
                'Total Samples': metrics.total_samples
            })
        
        return pd.DataFrame(data)
    
    def plot_comparison(self, save_path: str = None):
        """Plot comparison chart"""
        if not self.results:
            print("No results to plot")
            return
        
        metrics_names = ['Accuracy', 'Exact Match', 'Partial Match', 
                        'Syntax Correct', 'Semantic Correct']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(metrics_names))
        width = 0.15
        
        for i, (model_name, metrics) in enumerate(self.results.items()):
            values = [
                metrics.accuracy,
                metrics.exact_match,
                metrics.partial_match,
                metrics.syntax_correctness,
                metrics.semantic_correctness
            ]
            
            offset = width * (i - len(self.results)/2)
            ax.bar(x + offset, values, width, label=model_name)
        
        ax.set_xlabel('Metrics')
        ax.set_ylabel('Score')
        ax.set_title('Model Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        
        plt.show()
    
    def save_report(self, output_path: str):
        """Save detailed report"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Generate table
        df = self.generate_table()
        
        # Save as CSV
        csv_path = output_path.replace('.txt', '.csv')
        df.to_csv(csv_path, index=False)
        
        # Save as text report
        with open(output_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("MODEL EVALUATION REPORT\n")
            f.write("="*70 + "\n\n")
            
            f.write(df.to_string(index=False))
            f.write("\n\n")
            
            f.write("="*70 + "\n")
            f.write("DETAILED METRICS\n")
            f.write("="*70 + "\n\n")
            
            for model_name, metrics in self.results.items():
                f.write(f"\n{model_name}:\n")
                f.write(f"  Accuracy: {metrics.accuracy:.4f}\n")
                f.write(f"  Exact Match: {metrics.exact_match:.4f}\n")
                f.write(f"  Partial Match: {metrics.partial_match:.4f}\n")
                f.write(f"  Syntax Correctness: {metrics.syntax_correctness:.4f}\n")
                f.write(f"  Semantic Correctness: {metrics.semantic_correctness:.4f}\n")
                f.write(f"  Correct: {metrics.correct_samples}/{metrics.total_samples}\n")
        
        print(f"✅ Report saved to {output_path}")


def main():
    """Example usage"""
    print("="*70)
    print("UNIFIED MODEL EVALUATION")
    print("="*70)
    
    evaluator = ModelEvaluator()
    report = ComparisonReport()
    
    # Example: Load test data
    test_data = [
        {
            'query': 'average of Sales',
            'predicted': 'AVG([Sales])',
            'true': 'AVG([Sales])'
        },
        {
            'query': 'sum of Revenue by Region',
            'predicted': 'SUM([Revenue]) GROUP BY [Region]',
            'true': 'SUM([Revenue]) GROUP BY [Region]'
        },
        {
            'query': 'count unique customers',
            'predicted': 'COUNTD([Customer])',
            'true': 'COUNT(DISTINCT [Customer])'
        }
    ]
    
    # Evaluate
    print("\nEvaluating predictions...")
    metrics = evaluator.evaluate_predictions(test_data)
    
    print(f"\nResults:")
    print(f"  Accuracy: {metrics.accuracy:.3f}")
    print(f"  Exact Match: {metrics.exact_match:.3f}")
    print(f"  Partial Match: {metrics.partial_match:.3f}")
    print(f"  Syntax Correctness: {metrics.syntax_correctness:.3f}")
    print(f"  Semantic Correctness: {metrics.semantic_correctness:.3f}")
    
    # Add to report
    report.add_model_results("Example Model", metrics)
    
    # Generate report
    print("\n" + "="*70)
    print("COMPARISON TABLE")
    print("="*70)
    print(report.generate_table())
    
    # Save report
    report.save_report("./evaluation/comparison_report.txt")
    report.plot_comparison("./evaluation/comparison_plot.png")


if __name__ == "__main__":
    main()
