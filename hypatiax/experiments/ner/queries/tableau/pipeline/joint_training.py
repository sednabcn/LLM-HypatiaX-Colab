"""
Strategy 2: Joint Training on (Description, Formula) Pairs
End-to-end training with realistic error propagation
"""

from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np


class JointEntityExtractor:
    """Extract entities from both description and formula simultaneously"""

    def __init__(self):
        # Combined entity vocabulary
        self.desc_patterns = {
            "calculate": "OPER",
            "compute": "OPER",
            "find": "OPER",
            "area": "TARGET",
            "volume": "TARGET",
            "perimeter": "TARGET",
            "circle": "OBJECT",
            "square": "OBJECT",
            "sphere": "OBJECT",
        }

        self.formula_patterns = {
            "A": "VAR",
            "V": "VAR",
            "P": "VAR",
            "r": "VAR",
            "pi": "CONST",
            "*": "OPER",
            "^": "OPER",
        }

    def extract_pair_entities(self, description: str, formula: str) -> Dict:
        """Extract entities from both description and formula"""
        desc_entities = []
        tokens = description.lower().split()

        for token in tokens:
            if token in self.desc_patterns:
                desc_entities.append(
                    {"text": token, "label": self.desc_patterns[token]}
                )

        formula_entities = []
        formula_tokens = (
            formula.replace("=", " ").replace("*", " * ").replace("^", " ^ ").split()
        )

        for token in formula_tokens:
            if token in self.formula_patterns:
                formula_entities.append(
                    {"text": token, "label": self.formula_patterns[token]}
                )

        return {"desc_entities": desc_entities, "formula_entities": formula_entities}


class JointMappingModel:
    """Learn end-to-end mapping from (description, formula) pairs"""

    def __init__(self):
        self.training_pairs = []
        self.entity_pair_patterns = defaultdict(list)

    def train(self, training_data: List[Tuple[str, str]]):
        """Train on (description, formula) pairs"""
        extractor = JointEntityExtractor()

        print("\n[TRAINING] Processing training pairs...")
        for i, (desc, formula) in enumerate(training_data):
            entities = extractor.extract_pair_entities(desc, formula)
            self.training_pairs.append(
                {
                    "description": desc,
                    "formula": formula,
                    "desc_entities": entities["desc_entities"],
                    "formula_entities": entities["formula_entities"],
                }
            )

            # Create pattern key for similarity matching
            pattern_key = self._create_pattern_key(entities["desc_entities"])
            self.entity_pair_patterns[pattern_key].append(
                {"formula": formula, "formula_entities": entities["formula_entities"]}
            )

            print(f"  Pair {i+1}: '{desc}' → '{formula}'")

        print(f"\nTrained on {len(training_data)} pairs")
        print(f"Learned {len(self.entity_pair_patterns)} unique patterns")

    def _create_pattern_key(self, desc_entities: List[Dict]) -> str:
        """Create pattern key from description entities"""
        return "|".join([f"{e['label']}:{e['text']}" for e in desc_entities])

    def predict(self, description: str) -> str:
        """Predict formula from description"""
        extractor = JointEntityExtractor()

        # Extract entities from input
        dummy_formula = ""  # We don't have the formula yet
        entities = extractor.extract_pair_entities(description, dummy_formula)
        desc_entities = entities["desc_entities"]

        # Create pattern and find match
        pattern_key = self._create_pattern_key(desc_entities)

        if pattern_key in self.entity_pair_patterns:
            # Return the first matching formula
            return self.entity_pair_patterns[pattern_key][0]["formula"]

        return "Unknown pattern"

    def evaluate(self, test_data: List[Tuple[str, str]]) -> Dict:
        """Evaluate on test data with error propagation"""
        results = {
            "exact_match": 0,
            "partial_match": 0,
            "total": len(test_data),
            "predictions": [],
        }

        print("\n[EVALUATION] Testing on held-out data...")
        for i, (desc, expected_formula) in enumerate(test_data):
            predicted_formula = self.predict(desc)

            # Normalize for comparison
            expected_norm = expected_formula.replace(" ", "")
            predicted_norm = predicted_formula.replace(" ", "")

            exact_match = expected_norm == predicted_norm
            partial_match = any(
                token in predicted_norm for token in expected_norm.split("*")
            )

            if exact_match:
                results["exact_match"] += 1
                results["partial_match"] += 1
                match_type = "✓ EXACT"
            elif partial_match:
                results["partial_match"] += 1
                match_type = "~ PARTIAL"
            else:
                match_type = "✗ FAIL"

            results["predictions"].append(
                {
                    "description": desc,
                    "expected": expected_formula,
                    "predicted": predicted_formula,
                    "match": match_type,
                }
            )

            print(f"  Test {i+1} [{match_type}]:")
            print(f"    Input:    '{desc}'")
            print(f"    Expected: '{expected_formula}'")
            print(f"    Predicted: '{predicted_formula}'")

        # Calculate metrics
        results["exact_match_rate"] = results["exact_match"] / results["total"]
        results["partial_match_rate"] = results["partial_match"] / results["total"]

        return results


class ErrorPropagationAnalyzer:
    """Analyze how errors propagate through the pipeline"""

    @staticmethod
    def analyze(model: JointMappingModel, test_case: Tuple[str, str]):
        """Detailed analysis of a single prediction"""
        description, expected_formula = test_case

        print("\n[ERROR ANALYSIS]")
        print(f"Input: '{description}'")

        # Extract entities
        extractor = JointEntityExtractor()
        entities = extractor.extract_pair_entities(description, expected_formula)

        print("\nExtracted Description Entities:")
        for ent in entities["desc_entities"]:
            print(f"  - {ent['text']} ({ent['label']})")

        print("\nExpected Formula Entities:")
        for ent in entities["formula_entities"]:
            print(f"  - {ent['text']} ({ent['label']})")

        # Predict
        predicted_formula = model.predict(description)

        print(f"\nExpected:  '{expected_formula}'")
        print(f"Predicted: '{predicted_formula}'")

        # Analyze errors
        if predicted_formula != expected_formula:
            print("\n⚠ Mismatch detected!")
            print("Possible error sources:")
            print("  1. Entity extraction error (missing/wrong entities)")
            print("  2. Pattern matching failure (unseen pattern)")
            print("  3. Formula generation error")


# ============= MAIN EXECUTION =============


def main():
    print("=" * 60)
    print("STRATEGY 2: Joint Training on (Description, Formula) Pairs")
    print("=" * 60)

    # Training data: (description, formula) pairs
    training_data = [
        ("calculate area of circle", "A=pi*r^2"),
        ("compute area of circle", "A=pi*r^2"),
        ("find area of square", "A=a^2"),
        ("calculate volume of sphere", "V=4/3*pi*r^3"),
        ("find perimeter of square", "P=4*a"),
    ]

    # Test data
    test_data = [
        ("calculate area of circle", "A=pi*r^2"),  # Seen pattern
        ("compute area of square", "A=a^2"),  # Partially seen
    ]

    # Initialize and train model
    model = JointMappingModel()
    model.train(training_data)

    # Evaluate on test data
    results = model.evaluate(test_data)

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY:")
    print("=" * 60)
    print(f"Total test cases:      {results['total']}")
    print(
        f"Exact matches:         {results['exact_match']} ({results['exact_match_rate']:.1%})"
    )
    print(
        f"Partial matches:       {results['partial_match']} ({results['partial_match_rate']:.1%})"
    )
    print(f"Exact match accuracy:  {results['exact_match_rate']:.1%}")

    # Detailed error analysis on first test case
    print("\n" + "=" * 60)
    ErrorPropagationAnalyzer.analyze(model, test_data[0])

    # Main example from prompt
    print("\n" + "=" * 60)
    print("ORIGINAL EXAMPLE:")
    print("=" * 60)
    input_text = "calculate area of circle"
    output = model.predict(input_text)
    print(f"Input:  '{input_text}'")
    print(f"Output: '{output}'")
    print(f"Expected: 'A=pi*r^2'")
    print(f"Match: {output.replace(' ', '') == 'A=pi*r^2'.replace(' ', '')}")


if __name__ == "__main__":
    main()
