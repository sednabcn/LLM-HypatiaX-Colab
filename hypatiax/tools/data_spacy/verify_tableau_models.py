#!/usr/bin/env python3
"""
Verify Tableau NER Models - Check Rules and Test Entities
"""

from pathlib import Path

import spacy


def verify_model(model_path: str, test_texts: list[str] = None):
    """
    Verify a model has rules loaded and test entity recognition.

    Args:
        model_path: Path to the spaCy model
        test_texts: Optional list of test texts
    """
    print(f"\n{'='*70}")
    print(f"VERIFYING: {model_path}")
    print("=" * 70)

    # Load model
    try:
        nlp = spacy.load(model_path)
        print(f"✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    # Show pipeline
    print(f"\n📊 Pipeline components: {nlp.pipe_names}")

    # Check for EntityRuler components
    entity_rulers = [name for name in nlp.pipe_names if "ruler" in name.lower()]

    if not entity_rulers:
        print("\n⚠️  No EntityRuler components found!")
        return

    print(f"\n🔍 EntityRuler components found: {entity_rulers}")

    # Inspect each ruler
    for ruler_name in entity_rulers:
        ruler = nlp.get_pipe(ruler_name)

        # Get patterns/rules
        if hasattr(ruler, "patterns"):
            patterns = ruler.patterns
            print(f"\n📋 {ruler_name}:")
            print(f"   Total patterns: {len(patterns)}")

            # Show pattern distribution by label
            if patterns:
                labels = {}
                for pattern in patterns:
                    label = pattern.get("label", "UNKNOWN")
                    labels[label] = labels.get(label, 0) + 1

                print(f"   Labels found: {len(labels)}")
                print(f"\n   Pattern distribution:")
                for label, count in sorted(labels.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"      {label:30} {count:4} patterns")

                if len(labels) > 10:
                    print(f"      ... and {len(labels) - 10} more labels")

                # Show a few example patterns
                print(f"\n   Example patterns:")
                for i, pattern in enumerate(patterns[:3], 1):
                    label = pattern.get("label", "UNKNOWN")
                    pat = pattern.get("pattern", [])
                    if isinstance(pat, list) and pat:
                        text = " ".join(str(p.get("LOWER", p.get("TEXT", ""))) for p in pat[:5])
                        if len(pat) > 5:
                            text += " ..."
                    else:
                        text = str(pat)[:50]
                    print(f"      {i}. [{label}] {text}")
        else:
            print(f"\n⚠️  {ruler_name} has no 'patterns' attribute")

    # Test with sample texts if provided
    if test_texts:
        print(f"\n{'='*70}")
        print("TESTING ENTITY RECOGNITION")
        print("=" * 70)

        for i, text in enumerate(test_texts, 1):
            print(f"\nTest {i}: {text}")
            doc = nlp(text)

            if doc.ents:
                print(f"   Entities found: {len(doc.ents)}")
                for ent in doc.ents:
                    print(f"      • {ent.text:40} [{ent.label_}]")
            else:
                print("      (No entities detected)")


def verify_all_tableau_models(base_path: str = "hypatiax/data_spacy/queries/tableau"):
    """Verify all three Tableau models."""

    base_path = Path(base_path)

    models = [
        (
            "ner_tableau_formulas",
            [
                "Create a calculated field using SUM([Sales]) and AVG([Profit])",
                "Use IF [Sales] > 1000 THEN 'High' ELSE 'Low' END",
                "Calculate WINDOW_SUM(SUM([Sales])) for running total",
            ],
        ),
        (
            "ner_tableau_desc",
            [
                "Show me the sales dashboard",
                "Create a bar chart of profit by region",
                "Filter the data by date range",
            ],
        ),
        (
            "ner_tableau",
            [
                "Create a calculated field using SUM([Sales])",
                "Show me a bar chart of sales by region",
                "Sort by profit descending",
            ],
        ),
    ]

    print("=" * 70)
    print("VERIFYING ALL TABLEAU NER MODELS")
    print("=" * 70)
    print(f"Base path: {base_path}")
    print(f"SpaCy version: {spacy.__version__}")

    for model_name, test_texts in models:
        model_path = base_path / model_name

        if not model_path.exists():
            print(f"\n⚠️  Model not found: {model_name}")
            print(f"   Path: {model_path}")
            continue

        verify_model(str(model_path), test_texts)

    print(f"\n{'='*70}")
    print("VERIFICATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verify Tableau NER models have rules loaded correctly")

    parser.add_argument("--all", action="store_true", help="Verify all three tableau models")
    parser.add_argument("--model", type=str, help="Path to single model to verify")
    parser.add_argument("--test", type=str, nargs="+", help="Test texts for entity recognition")
    parser.add_argument(
        "--base-path", type=str, default="hypatiax/data_spacy/queries/tableau", help="Base path for models"
    )

    args = parser.parse_args()

    if args.all:
        verify_all_tableau_models(args.base_path)
    elif args.model:
        verify_model(
            args.model,
            args.test
            or [
                "Create a calculated field using SUM([Sales])",
                "Show me a bar chart",
                "Sort by profit descending",
            ],
        )
    else:
        # Default: verify ner_tableau
        print("💡 No arguments provided. Verifying ner_tableau model...\n")
        verify_model(
            f"{args.base_path}/ner_tableau",
            [
                "Create a calculated field using SUM([Sales])",
                "Show me a bar chart of sales by region",
                "Sort by profit descending",
            ],
        )
        print("\n💡 Use --all to verify all models or --model <path> for a specific model")

"""
Now run this to see the rules inside your model:
bashpython verify_tableau_models.py --all
Or for a quick check of just one model:
bashpython verify_tableau_models.py --model hypatiax/data_spacy/queries/tableau/ner_tableau
What to Expect
The ruler_tableau component is an EntityRuler that contains all your patterns. The verification script will show you:

How many patterns are loaded (should be 240 for ner_tableau based on your earlier output)
What entity labels exist (e.g., TABLEAU_FUNCTION, TABLEAU_FIELD, etc.)
Pattern distribution by label
Example patterns from the rules
Live entity recognition on test texts

The rules aren't separate - they're embedded inside the ruler_tableau component as patterns. When you call nlp(text), the EntityRuler applies those 240 patterns to recognize entities.
"""
