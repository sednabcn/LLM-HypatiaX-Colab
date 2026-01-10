"""
Strategy 1: Sequential Pipeline for Description → Formula Generation
Input: Natural language description
Output: Mathematical formula

Pipeline Steps:
1. Description → Entities[Desc] (Supervised NER)
2. Formulas → Entities[Formula] (Supervised NER for training data)
3. (Desc, Entities[Desc]) → Mapping → (Formula, Entities[Formula]) (Supervised)
4. Entities[Formula] → Formula Generation (Classification/Rule-based)

Each step is evaluated independently with metrics.
"""

from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


class DescriptionNER:
    """Step 1: Extract entities from natural language descriptions (Supervised)"""

    def __init__(self):
        # In practice, this would be a trained spaCy/BERT model
        self.patterns = {
            "calculate": "OPER",
            "compute": "OPER",
            "find": "OPER",
            "determine": "OPER",
            "area": "TARGET",
            "volume": "TARGET",
            "perimeter": "TARGET",
            "surface": "TARGET",
            "circle": "OBJECT",
            "square": "OBJECT",
            "triangle": "OBJECT",
            "rectangle": "OBJECT",
            "sphere": "OBJECT",
            "cube": "OBJECT",
        }

    def extract_entities(self, description: str) -> List[Dict]:
        """Extract entities from description using supervised model"""
        entities = []
        tokens = description.lower().split()

        for i, token in enumerate(tokens):
            if token in self.patterns:
                entities.append(
                    {"text": token, "label": self.patterns[token], "position": i}
                )

        return entities

    def evaluate(self, test_data: List[Tuple[str, List[Dict]]]) -> Dict:
        """Evaluate NER on descriptions with multiple metrics"""
        all_predicted = []
        all_ground_truth = []
        exact_matches = 0

        for desc, ground_truth in test_data:
            predicted = self.extract_entities(desc)

            # Exact match
            if predicted == ground_truth:
                exact_matches += 1

            # Token-level evaluation
            all_predicted.extend([e["label"] for e in predicted])
            all_ground_truth.extend([e["label"] for e in ground_truth])

        # Calculate metrics
        exact_match_acc = exact_matches / len(test_data) if test_data else 0

        if all_predicted and all_ground_truth:
            token_acc = accuracy_score(all_ground_truth, all_predicted)
            precision, recall, f1, _ = precision_recall_fscore_support(
                all_ground_truth, all_predicted, average="weighted", zero_division=0
            )
        else:
            token_acc = precision = recall = f1 = 0

        return {
            "exact_match_accuracy": exact_match_acc,
            "token_accuracy": token_acc,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }


class FormulaNER:
    """Step 2: Extract entities from mathematical formulas (Supervised)"""

    def __init__(self):
        # In practice, trained on formula corpus
        self.patterns = {
            "A": "VAR",
            "V": "VAR",
            "P": "VAR",
            "r": "VAR",
            "h": "VAR",
            "s": "VAR",
            "l": "VAR",
            "w": "VAR",
            "pi": "CONST",
            "4/3": "CONST",
            "3.14": "CONST",
            "*": "OPER",
            "^": "OPER",
            "+": "OPER",
            "-": "OPER",
            "/": "OPER",
        }

    def extract_entities(self, formula: str) -> List[Dict]:
        """Extract entities from formula using supervised model"""
        entities = []
        # Remove equals sign and tokenize
        formula_clean = formula.replace("=", "").strip()
        tokens = (
            formula_clean.replace("*", " * ")
            .replace("^", " ^ ")
            .replace("+", " + ")
            .replace("-", " - ")
            .replace("/", " / ")
            .split()
        )

        # Filter out numeric tokens that aren't in patterns (like '4', '2')
        for i, token in enumerate(tokens):
            if token in self.patterns:
                entities.append(
                    {"text": token, "label": self.patterns[token], "position": i}
                )
            # Skip numeric literals that aren't constants in our pattern dictionary

        return entities

    def evaluate(self, test_data: List[Tuple[str, List[Dict]]]) -> Dict:
        """Evaluate NER on formulas with multiple metrics"""
        all_predicted = []
        all_ground_truth = []
        exact_matches = 0

        for formula, ground_truth in test_data:
            predicted = self.extract_entities(formula)

            if predicted == ground_truth:
                exact_matches += 1

            all_predicted.extend([e["label"] for e in predicted])
            all_ground_truth.extend([e["label"] for e in ground_truth])

        exact_match_acc = exact_matches / len(test_data) if test_data else 0

        if all_predicted and all_ground_truth:
            token_acc = accuracy_score(all_ground_truth, all_predicted)
            precision, recall, f1, _ = precision_recall_fscore_support(
                all_ground_truth, all_predicted, average="weighted", zero_division=0
            )
        else:
            token_acc = precision = recall = f1 = 0

        return {
            "exact_match_accuracy": exact_match_acc,
            "token_accuracy": token_acc,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }


class EntityMapper:
    """Step 3: Map (Description, Entities[Desc]) → (Formula, Entities[Formula]) (Supervised)"""

    def __init__(self):
        # Training data: (desc, desc_entities) → (formula, formula_entities)
        # This would be learned from paired training data
        self.mapping_rules = {
            ("calculate", "area", "circle"): {
                "formula_type": "circle_area",
                "formula_entities": [
                    {"text": "A", "label": "VAR", "position": 0},
                    {"text": "pi", "label": "CONST", "position": 1},
                    {"text": "r", "label": "VAR", "position": 2},
                    {"text": "^", "label": "OPER", "position": 3},
                ],
            },
            ("calculate", "volume", "sphere"): {
                "formula_type": "sphere_volume",
                "formula_entities": [
                    {"text": "V", "label": "VAR", "position": 0},
                    {"text": "4/3", "label": "CONST", "position": 1},
                    {"text": "pi", "label": "CONST", "position": 2},
                    {"text": "r", "label": "VAR", "position": 3},
                    {"text": "^", "label": "OPER", "position": 4},
                ],
            },
            ("find", "perimeter", "square"): {
                "formula_type": "square_perimeter",
                "formula_entities": [
                    {"text": "P", "label": "VAR", "position": 0},
                    {"text": "s", "label": "VAR", "position": 1},
                    {"text": "*", "label": "OPER", "position": 2},
                ],
            },
        }

    def map_entities(self, description: str, desc_entities: List[Dict]) -> Dict:
        """Map description entities to formula entities (supervised learning)"""
        # Create key from description entities
        key = tuple([e["text"] for e in desc_entities])

        if key in self.mapping_rules:
            return self.mapping_rules[key]

        return {"formula_type": "unknown", "formula_entities": []}

    def evaluate(self, test_data: List[Tuple[Tuple[str, List[Dict]], Dict]]) -> Dict:
        """Evaluate mapping accuracy"""
        correct_mappings = 0
        correct_entity_sequences = 0
        total = len(test_data)

        all_predicted_types = []
        all_ground_truth_types = []

        for (desc, desc_entities), ground_truth in test_data:
            predicted = self.map_entities(desc, desc_entities)

            # Check formula type classification
            pred_type = predicted["formula_type"]
            gt_type = ground_truth["formula_type"]
            all_predicted_types.append(pred_type)
            all_ground_truth_types.append(gt_type)

            if pred_type == gt_type:
                correct_mappings += 1

                # Check if entity sequence also matches
                if predicted["formula_entities"] == ground_truth["formula_entities"]:
                    correct_entity_sequences += 1

        mapping_accuracy = correct_mappings / total if total > 0 else 0
        entity_sequence_accuracy = correct_entity_sequences / total if total > 0 else 0

        return {
            "formula_type_accuracy": mapping_accuracy,
            "entity_sequence_accuracy": entity_sequence_accuracy,
            "total_samples": total,
        }


class FormulaGenerator:
    """Step 4: Generate formula string from entities (Classification + Rules)"""

    def __init__(self):
        # Formula templates based on entity patterns (learned or rule-based)
        self.templates = {
            "circle_area": lambda e: f"A = pi * r^2",
            "sphere_volume": lambda e: f"V = 4/3 * pi * r^3",
            "square_perimeter": lambda e: f"P = 4 * s",
            "rectangle_area": lambda e: f"A = l * w",
        }

    def generate(self, formula_type: str, formula_entities: List[Dict]) -> str:
        """Generate formula from entities using classification/rules"""
        if formula_type in self.templates:

            return self.templates[formula_type](formula_entities)

        # Fallback: construct from entities
        return self._construct_from_entities(formula_entities)

    def _construct_from_entities(self, entities: List[Dict]) -> str:
        """Fallback construction from entities"""
        if not entities:
            return ""

        formula_parts = []
        for i, entity in enumerate(entities):
            if i == 0:
                formula_parts.append(entity["text"] + " = ")
            elif entity["label"] == "OPER" and entity["text"] == "^":
                formula_parts.append("^2")
            else:
                formula_parts.append(entity["text"])
                if i < len(entities) - 1 and entity["label"] != "OPER":
                    formula_parts.append(" * ")

        return "".join(formula_parts)

    def evaluate(self, test_data: List[Tuple[Tuple[str, List[Dict]], str]]) -> Dict:
        """Evaluate formula generation"""
        exact_matches = 0
        syntactic_matches = 0
        total = len(test_data)

        for (formula_type, entities), ground_truth in test_data:
            predicted = self.generate(formula_type, entities)

            # Exact match
            if predicted == ground_truth:
                exact_matches += 1

            # Syntactic match (ignoring spaces)
            if predicted.replace(" ", "") == ground_truth.replace(" ", ""):
                syntactic_matches += 1

        return {
            "exact_match_accuracy": exact_matches / total if total > 0 else 0,
            "syntactic_accuracy": syntactic_matches / total if total > 0 else 0,
            "total_samples": total,
        }


# ============= MAIN EXECUTION =============


def main():
    print("=" * 70)
    print("SEQUENTIAL PIPELINE: Description → Formula Generation")
    print("=" * 70)
    print("\nPipeline Architecture:")
    print("1. Description → Entities[Desc] (Supervised NER)")
    print("2. Formulas → Entities[Formula] (Supervised NER, for training)")
    print("3. (Desc, Entities[Desc]) → Mapping → (Formula, Entities[Formula])")
    print("4. Entities[Formula] → Formula Generation (Classification)")
    print("=" * 70)

    # Initialize components
    desc_ner = DescriptionNER()
    formula_ner = FormulaNER()
    mapper = EntityMapper()
    generator = FormulaGenerator()

    # Test input
    input_description = "calculate area of circle"
    expected_output = "A = pi * r^2"

    print(f"\n{'='*70}")
    print(f"INPUT: '{input_description}'")
    print(f"EXPECTED OUTPUT: '{expected_output}'")
    print(f"{'='*70}")

    # ========== STEP 1: Description → Entities[Desc] ==========
    print(f"\n{'─'*70}")
    print("[STEP 1] Description → Entities[Desc] (Supervised NER)")
    print(f"{'─'*70}")

    desc_entities = desc_ner.extract_entities(input_description)
    print(f"Extracted entities: {desc_entities}")

    # Evaluate Step 1
    desc_test_data = [
        (
            "calculate area of circle",
            [
                {"text": "calculate", "label": "OPER", "position": 0},
                {"text": "area", "label": "TARGET", "position": 1},
                {"text": "circle", "label": "OBJECT", "position": 3},
            ],
        ),
        (
            "find perimeter of square",
            [
                {"text": "find", "label": "OPER", "position": 0},
                {"text": "perimeter", "label": "TARGET", "position": 1},
                {"text": "square", "label": "OBJECT", "position": 3},
            ],
        ),
    ]

    desc_metrics = desc_ner.evaluate(desc_test_data)
    print(f"\n📊 STEP 1 METRICS:")
    print(f"   • Exact Match Accuracy: {desc_metrics['exact_match_accuracy']:.2%}")
    print(f"   • Token Accuracy: {desc_metrics['token_accuracy']:.2%}")
    print(f"   • Precision: {desc_metrics['precision']:.3f}")
    print(f"   • Recall: {desc_metrics['recall']:.3f}")
    print(f"   • F1-Score: {desc_metrics['f1_score']:.3f}")

    # ========== STEP 2: Formulas → Entities[Formula] ==========
    print(f"\n{'─'*70}")
    print("[STEP 2] Formulas → Entities[Formula] (Supervised NER)")
    print(f"{'─'*70}")
    print("(Training step - extracting entities from ground-truth formulas)")

    # Evaluate Step 2 on formula corpus
    formula_test_data = [
        (
            "A = pi * r^2",
            [
                {"text": "A", "label": "VAR", "position": 0},
                {"text": "pi", "label": "CONST", "position": 1},
                {"text": "*", "label": "OPER", "position": 2},
                {"text": "r", "label": "VAR", "position": 3},
                {"text": "^", "label": "OPER", "position": 4},
            ],
        ),
        (
            "P = 4 * s",
            [
                {"text": "P", "label": "VAR", "position": 0},
                {"text": "*", "label": "OPER", "position": 1},
                {"text": "s", "label": "VAR", "position": 2},
            ],
        ),
    ]
    formula_metrics = formula_ner.evaluate(formula_test_data)
    print(f"\n📊 STEP 2 METRICS:")
    print(f"   • Exact Match Accuracy: {formula_metrics['exact_match_accuracy']:.2%}")
    print(f"   • Token Accuracy: {formula_metrics['token_accuracy']:.2%}")
    print(f"   • Precision: {formula_metrics['precision']:.3f}")
    print(f"   • Recall: {formula_metrics['recall']:.3f}")
    print(f"   • F1-Score: {formula_metrics['f1_score']:.3f}")

    # ========== STEP 3: Mapping ==========
    print(f"\n{'─'*70}")
    print(
        "[STEP 3] (Desc, Entities[Desc]) → Mapping → (Formula Type, Entities[Formula])"
    )
    print(f"{'─'*70}")

    mapping_result = mapper.map_entities(input_description, desc_entities)
    formula_type = mapping_result["formula_type"]
    mapped_formula_entities = mapping_result["formula_entities"]

    print(f"Formula Type: {formula_type}")
    print(f"Mapped formula entities: {mapped_formula_entities}")

    # Evaluate Step 3
    mapping_test_data = [
        (
            ("calculate area of circle", desc_entities),
            {
                "formula_type": "circle_area",
                "formula_entities": [
                    {"text": "A", "label": "VAR", "position": 0},
                    {"text": "pi", "label": "CONST", "position": 1},
                    {"text": "r", "label": "VAR", "position": 2},
                    {"text": "^", "label": "OPER", "position": 3},
                ],
            },
        )
    ]

    mapping_metrics = mapper.evaluate(mapping_test_data)
    print(f"\n📊 STEP 3 METRICS:")
    print(
        f"   • Formula Type Classification Accuracy: {mapping_metrics['formula_type_accuracy']:.2%}"
    )
    print(
        f"   • Entity Sequence Accuracy: {mapping_metrics['entity_sequence_accuracy']:.2%}"
    )

    # ========== STEP 4: Formula Generation ==========
    print(f"\n{'─'*70}")
    print("[STEP 4] Entities[Formula] → Formula Generation")
    print(f"{'─'*70}")

    generated_formula = generator.generate(formula_type, mapped_formula_entities)
    print(f"Generated formula: '{generated_formula}'")

    # Evaluate Step 4
    generation_test_data = [
        (("circle_area", mapped_formula_entities), "A = pi * r^2"),
        (("square_perimeter", []), "P = 4 * s"),
    ]

    generation_metrics = generator.evaluate(generation_test_data)
    print(f"\n📊 STEP 4 METRICS:")
    print(
        f"   • Exact Match Accuracy: {generation_metrics['exact_match_accuracy']:.2%}"
    )
    print(f"   • Syntactic Accuracy: {generation_metrics['syntactic_accuracy']:.2%}")

    # ========== FINAL RESULTS ==========
    print(f"\n{'='*70}")
    print("FINAL RESULTS")
    print(f"{'='*70}")
    print(f"Input Description:  '{input_description}'")
    print(f"Generated Formula:  '{generated_formula}'")
    print(f"Expected Formula:   '{expected_output}'")
    print(f"✓ Match: {generated_formula == expected_output}")

    print(f"\n{'='*70}")
    print("PIPELINE PERFORMANCE SUMMARY")
    print(f"{'='*70}")
    print(f"Step 1 - Description NER:      {desc_metrics['f1_score']:.2%} (F1)")
    print(f"Step 2 - Formula NER:          {formula_metrics['f1_score']:.2%} (F1)")
    print(
        f"Step 3 - Entity Mapping:       {mapping_metrics['formula_type_accuracy']:.2%} (Type Acc)"
    )
    print(
        f"Step 4 - Formula Generation:   {generation_metrics['syntactic_accuracy']:.2%} (Syn Acc)"
    )
    print(f"{'='*70}")

    # Error propagation analysis
    print(f"\n💡 ERROR PROPAGATION ANALYSIS:")
    print(
        f"   Pipeline accuracy ≈ {desc_metrics['f1_score'] * mapping_metrics['formula_type_accuracy'] * generation_metrics['syntactic_accuracy']:.2%}"
    )
    print(f"   (Product of component accuracies)")


if __name__ == "__main__":
    main()
