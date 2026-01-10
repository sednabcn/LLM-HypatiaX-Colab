#!/usr/bin/env python3
"""
HypatiaX Interactive Demo
Demonstrates NER capabilities for Tableau query processing

Main command-line demo

Interactive menu system
Multiple demo modes (desc, formulas, both)
Batch processing
Model comparison
Works with OR without trained models

"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class HypatiaXDemo:
    """
    Interactive demo for HypatiaX NER system
    Showcases description and formula entity extraction
    """

    def __init__(self, model_type: str = "desc"):
        """
        Initialize demo with a model type

        Args:
            model_type: 'desc', 'formulas', or 'both'
        """
        self.model_type = model_type
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the trained spaCy model"""
        try:
            from hypatiax.utils.model_loader import load_model

            self.model = load_model("queries", "tableau", self.model_type)
            print(f"✓ Loaded {self.model_type} model successfully")
        except Exception as e:
            print(f"⚠ Could not load model: {e}")
            print("  Running in demo mode with mock entities")
            self.model = None

    def process_text(self, text: str) -> Dict:
        """
        Process text and extract entities

        Args:
            text: Input text to process

        Returns:
            Dictionary with entities and metadata
        """
        if self.model:
            # Use actual model
            doc = self.model(text)
            entities = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                }
                for ent in doc.ents
            ]
        else:
            # Mock entities for demo
            entities = self._mock_entities(text)

        return {
            "text": text,
            "entities": entities,
            "model_type": self.model_type,
            "entity_count": len(entities),
        }

    def _mock_entities(self, text: str) -> List[Dict]:
        """Generate mock entities for demo mode"""
        mock_patterns = {
            "desc": {
                "calculate": "OPERATION",
                "compute": "OPERATION",
                "find": "OPERATION",
                "sum": "FUNCTION",
                "average": "FUNCTION",
                "count": "FUNCTION",
                "sales": "FIELD",
                "profit": "FIELD",
                "revenue": "FIELD",
                "region": "DIMENSION",
                "category": "DIMENSION",
                "date": "DIMENSION",
            },
            "formulas": {
                "SUM": "FUNCTION",
                "AVG": "FUNCTION",
                "COUNT": "FUNCTION",
                "IF": "LOGIC",
                "THEN": "LOGIC",
                "ELSE": "LOGIC",
                "[": "BRACKET",
                "]": "BRACKET",
                "Sales": "FIELD",
                "Profit": "FIELD",
            },
        }

        entities = []
        patterns = mock_patterns.get(self.model_type, mock_patterns["desc"])

        text_lower = text.lower()
        for pattern, label in patterns.items():
            if pattern.lower() in text_lower:
                start = text_lower.index(pattern.lower())
                entities.append(
                    {
                        "text": pattern,
                        "label": label,
                        "start": start,
                        "end": start + len(pattern),
                    }
                )

        return entities

    def display_result(self, result: Dict):
        """Display processing result in a formatted way"""
        print("\n" + "=" * 70)
        print("📊 HYPATIAX NER RESULTS")
        print("=" * 70)
        print(f"Input Text: {result['text']}")
        print(f"Model Type: {result['model_type']}")
        print(f"Entities Found: {result['entity_count']}")
        print("\n🏷️  Extracted Entities:")

        if result["entities"]:
            for i, ent in enumerate(result["entities"], 1):
                print(f"  {i}. '{ent['text']}' → {ent['label']}")
                print(f"     Position: {ent['start']}-{ent['end']}")
        else:
            print("  (No entities found)")

        print("=" * 70)

    def run_example(self, example_text: str):
        """Run a single example"""
        print(f"\n🔍 Processing: '{example_text}'")
        result = self.process_text(example_text)
        self.display_result(result)
        return result

    def run_examples(self, examples: List[str]):
        """Run multiple examples"""
        print(f"\n{'=' * 70}")
        print(f"Running {len(examples)} examples...")
        print(f"{'=' * 70}")

        results = []
        for i, example in enumerate(examples, 1):
            print(f"\n[Example {i}/{len(examples)}]")
            result = self.run_example(example)
            results.append(result)

        return results

    def interactive_mode(self):
        """Run in interactive mode"""
        print("\n" + "=" * 70)
        print("🎯 HYPATIAX INTERACTIVE DEMO")
        print("=" * 70)
        print("Enter text to extract entities, or 'quit' to exit")
        print("Model type:", self.model_type)
        print("-" * 70)

        while True:
            try:
                user_input = input("\n> ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Thanks for trying HypatiaX!")
                    break

                if not user_input:
                    continue

                result = self.process_text(user_input)
                self.display_result(result)

            except KeyboardInterrupt:
                print("\n\n👋 Thanks for trying HypatiaX!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def run_description_demo():
    """Demo for description entity extraction"""
    print("\n" + "🔹" * 35)
    print("DESCRIPTION NER DEMO")
    print("🔹" * 35)

    demo = HypatiaXDemo(model_type="desc")

    examples = [
        "calculate the sum of sales by region",
        "find the average profit per category",
        "show me total revenue for each date",
        "compute the count of orders by customer",
    ]

    demo.run_examples(examples)


def run_formula_demo():
    """Demo for formula entity extraction"""
    print("\n" + "🔸" * 35)
    print("FORMULA NER DEMO")
    print("🔸" * 35)

    demo = HypatiaXDemo(model_type="formulas")

    examples = [
        "SUM([Sales])",
        "AVG([Profit])",
        "IF [Sales] > 1000 THEN 'High' ELSE 'Low'",
        "COUNT([Orders])",
    ]

    demo.run_examples(examples)


def run_combined_demo():
    """Demo for combined description + formula"""
    print("\n" + "🔶" * 35)
    print("COMBINED NER DEMO")
    print("🔶" * 35)

    demo = HypatiaXDemo(model_type="both")

    examples = [
        "calculate sum of sales : SUM([Sales])",
        "find average profit : AVG([Profit])",
        "compute total revenue : SUM([Revenue])",
    ]

    demo.run_examples(examples)


def run_comparison_demo():
    """Compare all three model types on the same text"""
    print("\n" + "⚖️ " * 35)
    print("MODEL COMPARISON DEMO")
    print("⚖️ " * 35)

    test_text = "calculate the sum of sales"

    print(f"\nTest Text: '{test_text}'")
    print("\nComparing all model types...\n")

    for model_type in ["desc", "formulas", "both"]:
        print(f"\n{'─' * 70}")
        print(f"Model: {model_type}")
        print("─" * 70)

        demo = HypatiaXDemo(model_type=model_type)
        result = demo.process_text(test_text)

        if result["entities"]:
            for ent in result["entities"]:
                print(f"  • {ent['text']} → {ent['label']}")
        else:
            print("  (No entities found)")


def main():
    """Main demo menu"""
    print("\n" + "=" * 70)
    print(" " * 20 + "🚀 HYPATIAX DEMO")
    print("=" * 70)
    print("\nSelect a demo to run:")
    print("  1. Description NER Demo")
    print("  2. Formula NER Demo")
    print("  3. Combined NER Demo")
    print("  4. Model Comparison Demo")
    print("  5. Interactive Mode")
    print("  6. Run All Demos")
    print("  q. Quit")

    choice = input("\nEnter your choice (1-6, q): ").strip()

    if choice == "1":
        run_description_demo()
    elif choice == "2":
        run_formula_demo()
    elif choice == "3":
        run_combined_demo()
    elif choice == "4":
        run_comparison_demo()
    elif choice == "5":
        model_choice = (
            input("Choose model (desc/formulas/both) [desc]: ").strip() or "desc"
        )
        demo = HypatiaXDemo(model_type=model_choice)
        demo.interactive_mode()
    elif choice == "6":
        run_description_demo()
        run_formula_demo()
        run_combined_demo()
        run_comparison_demo()
    elif choice.lower() == "q":
        print("\n👋 Goodbye!")
        return
    else:
        print("\n❌ Invalid choice")
        return

    # Ask if user wants to continue
    print("\n" + "=" * 70)
    again = input("\nRun another demo? (y/n) [n]: ").strip().lower()
    if again == "y":
        main()
    else:
        print("\n👋 Thanks for trying HypatiaX!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for trying HypatiaX!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
