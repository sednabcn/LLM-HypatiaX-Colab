#!/usr/bin/env python3
"""
HypatiaX Example Usage
======================
Basic example showing how to use HypatiaX for NER on Tableau queries.
"""

from pathlib import Path

import spacy


def main():
    """Run basic NER example."""
    print("🚀 HypatiaX Example Usage\n")

    # Load base spaCy model
    print("Loading spaCy model...")
    nlp = spacy.load("en_core_web_sm")

    # Example Tableau query
    query = "SELECT SUM(Sales) FROM Orders WHERE Region = 'West'"

    # Process with spaCy
    doc = nlp(query)

    print(f"\nQuery: {query}")
    print(f"\nTokens:")
    for token in doc:
        print(f"  - {token.text:15} {token.pos_:10} {token.tag_:10}")

    print("\n✅ Example complete!")
    print("\n💡 Next steps:")
    print("  1. Load custom Tableau NER model")
    print("  2. Try with your own Tableau queries")
    print("  3. Train custom models on your data")


if __name__ == "__main__":
    main()
