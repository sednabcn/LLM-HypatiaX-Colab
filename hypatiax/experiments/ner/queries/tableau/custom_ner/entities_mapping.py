#!/usr/bin/python3
"""
Strategy 1 - Point 2 & 3 Implementation
Point 2: Entities[Desc] → Entities[Formula] (Entity Mapping)
Point 3: Entities[Formula] → Formula String (Formula Generation)
"""

import json
from typing import Dict, List, Optional, Tuple

# ============= POINT 2: ENTITY MAPPING =============


class EntityMapper:
    """
    Maps Description Entities to Formula Entities
    This is the CRITICAL step that learns the transformation
    """

    def __init__(self):
        # Rule-based mapping (can be replaced with ML model)
        self.pattern_database = {}
        self.entity_vocab_map = {
            # Operation mappings
            ("OPER", "calculate"): ("FUNC", "calculate"),
            ("OPER", "compute"): ("FUNC", "calculate"),
            ("OPER", "find"): ("FUNC", "calculate"),
            ("OPER", "sum"): ("FUNC", "SUM"),
            ("OPER", "average"): ("FUNC", "AVG"),
            # Target mappings
            ("TARGET", "area"): ("RESULT", "A"),
            ("TARGET", "volume"): ("RESULT", "V"),
            ("TARGET", "perimeter"): ("RESULT", "P"),
            # Object to formula mappings
            ("OBJECT", "circle"): ("SHAPE", "circle"),
            ("OBJECT", "sphere"): ("SHAPE", "sphere"),
            ("OBJECT", "square"): ("SHAPE", "square"),
        }

        # Pattern-based formula templates
        self.formula_templates = {
            ("area", "circle"): [
                {"type": "VAR", "value": "A"},
                {"type": "OPER", "value": "="},
                {"type": "CONST", "value": "pi"},
                {"type": "OPER", "value": "*"},
                {"type": "VAR", "value": "r"},
                {"type": "OPER", "value": "^"},
                {"type": "CONST", "value": "2"},
            ],
            ("volume", "sphere"): [
                {"type": "VAR", "value": "V"},
                {"type": "OPER", "value": "="},
                {"type": "PAREN", "value": "("},
                {"type": "CONST", "value": "4"},
                {"type": "OPER", "value": "/"},
                {"type": "CONST", "value": "3"},
                {"type": "PAREN", "value": ")"},
                {"type": "OPER", "value": "*"},
                {"type": "CONST", "value": "pi"},
                {"type": "OPER", "value": "*"},
                {"type": "VAR", "value": "r"},
                {"type": "OPER", "value": "^"},
                {"type": "CONST", "value": "3"},
            ],
            ("area", "square"): [
                {"type": "VAR", "value": "A"},
                {"type": "OPER", "value": "="},
                {"type": "VAR", "value": "s"},
                {"type": "OPER", "value": "^"},
                {"type": "CONST", "value": "2"},
            ],
            ("perimeter", "square"): [
                {"type": "VAR", "value": "P"},
                {"type": "OPER", "value": "="},
                {"type": "CONST", "value": "4"},
                {"type": "OPER", "value": "*"},
                {"type": "VAR", "value": "s"},
            ],
        }

    def map_single_entity(self, entity: Dict) -> Dict:
        """Map a single description entity to formula entity"""
        label = entity["label"]
        text = entity["text"]

        key = (label, text)
        if key in self.entity_vocab_map:
            new_label, new_text = self.entity_vocab_map[key]
            return {"label": new_label, "text": new_text}

        # Return unchanged if no mapping found
        return entity

    def map_entities(self, desc_entities: List[Dict]) -> List[Dict]:
        """
        POINT 2 IMPLEMENTATION: Map description entities to formula entities

        Three approaches:
        1. Direct vocab mapping (entity-by-entity)
        2. Pattern matching (find template based on entity combination)
        3. Learned mapping (ML model - placeholder)
        """

        # Approach 1: Try pattern matching first (most accurate)
        formula_entities = self._pattern_based_mapping(desc_entities)
        if formula_entities:
            return formula_entities

        # Approach 2: Fallback to vocab mapping
        formula_entities = self._vocab_based_mapping(desc_entities)
        if formula_entities:
            return formula_entities

        # Approach 3: ML-based mapping (placeholder)
        return self._ml_based_mapping(desc_entities)

    def _pattern_based_mapping(self, desc_entities: List[Dict]) -> Optional[List[Dict]]:
        """
        Use pattern matching to find formula template
        This is the BEST approach for mathematical formulas
        """
        # Extract key components
        target = None
        shape = None

        for entity in desc_entities:
            if entity["label"] == "TARGET":
                target = entity["text"]
            elif entity["label"] == "OBJECT":
                shape = entity["text"]

        # Look up formula template
        if target and shape:
            key = (target, shape)
            if key in self.formula_templates:
                print(f"  ✓ Pattern match found: {key}")
                return self.formula_templates[key]

        return None

    def _vocab_based_mapping(self, desc_entities: List[Dict]) -> List[Dict]:
        """
        Map entities one-by-one using vocabulary mapping
        Good for data aggregation formulas (SUM, AVG, etc.)
        """
        mapped = []
        for entity in desc_entities:
            mapped.append(self.map_single_entity(entity))

        return mapped if mapped else None

    def _ml_based_mapping(self, desc_entities: List[Dict]) -> List[Dict]:
        """
        Placeholder for ML-based entity mapping
        Could use:
        - Sequence-to-sequence model
        - Transformer encoder-decoder
        - Entity pair classifier
        """
        print("  ⚠ ML mapping not implemented, returning empty")
        return []

    def train_from_pairs(self, training_pairs: List[Tuple[List[Dict], List[Dict]]]):
        """
        Learn mappings from (desc_entities, formula_entities) pairs
        This is how you'd train the mapper in production
        """
        print("\n[TRAINING] Learning entity mappings...")

        for desc_ent, formula_ent in training_pairs:
            # Extract pattern
            target = None
            shape = None
            for e in desc_ent:
                if e["label"] == "TARGET":
                    target = e["text"]
                elif e["label"] == "OBJECT":
                    shape = e["text"]

            if target and shape:
                key = (target, shape)
                if key not in self.formula_templates:
                    self.formula_templates[key] = formula_ent
                    print(f"  Learned: {key} → {len(formula_ent)} tokens")


# ============= POINT 3: FORMULA GENERATION =============


class FormulaGenerator:
    """
    Generate formula string from formula entities
    This is the final step that produces human-readable output
    """

    def __init__(self):
        self.formatting_rules = {
            "space_before": ["OPER", "CONST", "VAR"],  # Add space before these
            "space_after": ["OPER", "CONST"],  # Add space after these
            "no_space": ["PAREN", "^"],  # No spaces around these
        }

    def generate(self, formula_entities: List[Dict]) -> str:
        """
        POINT 3 IMPLEMENTATION: Generate formula string from entities

        Handles:
        - Proper spacing
        - Operator precedence
        - Parentheses
        - Special symbols (pi, ^)
        """
        if not formula_entities:
            return ""

        formula_parts = []

        for i, entity in enumerate(formula_entities):
            entity_type = entity.get("type") or entity.get("label")
            value = entity.get("value") or entity.get("text")

            # Add space before (if not first element)
            if i > 0 and self._needs_space_before(entity_type, value):
                formula_parts.append(" ")

            # Add the token
            formula_parts.append(value)

            # Add space after (if not last element)
            if i < len(formula_entities) - 1 and self._needs_space_after(entity_type, value):
                formula_parts.append(" ")

        return "".join(formula_parts)

    def _needs_space_before(self, entity_type: str, value: str) -> bool:
        """Determine if space is needed before this token"""
        if entity_type == "OPER" and value == "=":
            return True
        if entity_type in ["VAR", "CONST"] and value not in ["(", ")"]:
            return True
        return False

    def _needs_space_after(self, entity_type: str, value: str) -> bool:
        """Determine if space is needed after this token"""
        if entity_type == "OPER" and value in ["=", "*", "+", "-", "/"]:
            return True
        if value == ")":
            return True
        return False

    def generate_with_validation(self, formula_entities: List[Dict]) -> Tuple[str, bool, str]:
        """
        Generate formula with validation
        Returns: (formula, is_valid, error_message)
        """
        formula = self.generate(formula_entities)

        # Basic validation
        if not formula:
            return "", False, "Empty formula"

        if "=" not in formula:
            return formula, False, "Missing assignment operator"

        # Check balanced parentheses
        if formula.count("(") != formula.count(")"):
            return formula, False, "Unbalanced parentheses"

        return formula, True, "Valid"


# ============= COMPLETE PIPELINE =============


def demonstrate_point2_and_point3():
    """Complete demonstration of Point 2 and Point 3"""

    print("=" * 70)
    print("STRATEGY 1 - POINT 2 & 3 IMPLEMENTATION")
    print("=" * 70)

    # Initialize components
    mapper = EntityMapper()
    generator = FormulaGenerator()

    # Test Case: "calculate area of circle"
    print("\n[TEST CASE] 'calculate area of circle'")
    print("-" * 70)

    # Input: Description entities (from Point 1 - NER)
    desc_entities = [
        {"label": "OPER", "text": "calculate"},
        {"label": "TARGET", "text": "area"},
        {"label": "OBJECT", "text": "circle"},
    ]

    print("\n[INPUT] Description Entities:")
    for ent in desc_entities:
        print(f"  {ent['label']:10} : {ent['text']}")

    # POINT 2: Map to formula entities
    print("\n[POINT 2] Mapping Description Entities → Formula Entities...")
    formula_entities = mapper.map_entities(desc_entities)

    print("\n[OUTPUT] Formula Entities:")
    for ent in formula_entities:
        entity_type = ent.get("type") or ent.get("label")
        value = ent.get("value") or ent.get("text")
        print(f"  {entity_type:10} : {value}")

    # POINT 3: Generate formula string
    print("\n[POINT 3] Generating Formula String...")
    formula = generator.generate(formula_entities)

    print("\n[OUTPUT] Generated Formula:")
    print(f"  {formula}")

    # Validate
    formula_valid, is_valid, message = generator.generate_with_validation(formula_entities)
    print(f"\n[VALIDATION] {message}")

    # Test more examples
    print("\n" + "=" * 70)
    print("ADDITIONAL TEST CASES")
    print("=" * 70)

    test_cases = [
        ("volume of sphere", [{"label": "TARGET", "text": "volume"}, {"label": "OBJECT", "text": "sphere"}]),
        ("area of square", [{"label": "TARGET", "text": "area"}, {"label": "OBJECT", "text": "square"}]),
        ("perimeter of square", [{"label": "TARGET", "text": "perimeter"}, {"label": "OBJECT", "text": "square"}]),
    ]

    for description, entities in test_cases:
        print(f"\n[TEST] '{description}'")
        formula_entities = mapper.map_entities(entities)
        if formula_entities:
            formula = generator.generate(formula_entities)
            print(f"  Result: {formula}")
        else:
            print("  Result: No mapping found")


# ============= TRAINING DEMONSTRATION =============


def demonstrate_training():
    """Show how to train the mapper from examples"""

    print("\n" + "=" * 70)
    print("TRAINING THE MAPPER")
    print("=" * 70)

    mapper = EntityMapper()

    # Training pairs: (description_entities, formula_entities)
    training_data = [
        (
            [{"label": "TARGET", "text": "circumference"}, {"label": "OBJECT", "text": "circle"}],
            [
                {"type": "VAR", "value": "C"},
                {"type": "OPER", "value": "="},
                {"type": "CONST", "value": "2"},
                {"type": "OPER", "value": "*"},
                {"type": "CONST", "value": "pi"},
                {"type": "OPER", "value": "*"},
                {"type": "VAR", "value": "r"},
            ],
        )
    ]

    mapper.train_from_pairs(training_data)

    # Test the trained mapping
    print("\n[TESTING] Using newly learned pattern...")
    test_entities = [{"label": "TARGET", "text": "circumference"}, {"label": "OBJECT", "text": "circle"}]

    formula_entities = mapper.map_entities(test_entities)
    generator = FormulaGenerator()
    formula = generator.generate(formula_entities)

    print(f"Input:  circumference of circle")
    print(f"Output: {formula}")


# ============= MAIN =============

if __name__ == "__main__":
    demonstrate_point2_and_point3()
    demonstrate_training()

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print(
        """
POINT 2 - Entity Mapping (Entities[Desc] → Entities[Formula]):
  • Pattern-based: Best for math formulas (area, volume, etc.)
  • Vocab-based: Good for data operations (SUM, AVG, etc.)
  • ML-based: For complex, learned transformations

POINT 3 - Formula Generation (Entities[Formula] → String):
  • Handle spacing rules
  • Format operators correctly
  • Validate output
  • Support multiple notation styles

Critical Success Factors:
  ✓ Test each component separately (Strategy 1 approach)
  ✓ Use ground truth for entity mapping accuracy
  ✓ Build template library for common patterns
  ✓ Train on (desc_entities, formula_entities) pairs
    """
    )
