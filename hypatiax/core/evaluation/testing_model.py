import spacy
from spacy.scorer import Scorer
from spacy.tokens import Doc, DocBin
from spacy.training import Example, biluo_tags_to_spans, offsets_to_biluo_tags

from hypatiax.custom_ner.queries.tableau import (
    custom_tableau_components,
    custom_tableau_desc_components,
    custom_tableau_formulas_components,
)


def test_spacy_model(model_path, test_data):
    """
    Test a trained spaCy NER model and compute evaluation metrics.

    Parameters:
        model_path (str): Path to the trained spaCy model.
        test_data (list): List of tuples (text, annotations) where annotations
                         is a dict with 'entities' key containing (start, end, label) tuples.

    Returns:
        dict: Dictionary containing precision, recall, and F1-score metrics.

    Example:
        test_data = [
            ("Apple Inc. was founded by Steve Jobs",
             {"entities": [(0, 10, "ORG"), (28, 38, "PERSON")]}),
        ]
        scores = test_spacy_model("path/to/model", test_data)
    """
    # Load the trained model
    nlp = spacy.load(model_path)

    # Create examples list for scoring
    examples = []

    # Evaluate the model on test data
    for text, annotations in test_data:
        # Create predicted document
        doc = nlp(text)

        print("=" * 50)
        print(f"Text: {text}")
        print("Predicted Entities:", [(ent.text, ent.label_) for ent in doc.ents])
        print("Token Details:", [(t.text, t.ent_type_, t.ent_iob_) for t in doc])

        # Create reference document with gold-standard annotations
        try:
            # Method 1: Using make_doc to create reference
            ref_doc = nlp.make_doc(text)

            # Convert entity offsets to BILUO tags
            entities = annotations.get("entities", [])
            biluo_tags = offsets_to_biluo_tags(ref_doc, entities)

            # Convert BILUO tags to spans and set as entities
            ref_spans = biluo_tags_to_spans(ref_doc, biluo_tags)
            ref_doc.ents = ref_spans

            # Create Example object for scoring
            example = Example(predicted=doc, reference=ref_doc)
            examples.append(example)

            print("Reference Entities:", [(ent.text, ent.label_) for ent in ref_doc.ents])

        except Exception as e:
            print(f"Error processing example: {text}")
            print(f"Error details: {e}")
            continue

    # Score all examples
    if not examples:
        print("No valid examples to score!")
        return {}

    scores = nlp.evaluate(examples)

    # Print overall scores
    print("\n" + "=" * 50)
    print("OVERALL EVALUATION METRICS")
    print("=" * 50)
    print(f"Precision: {scores.get('ents_p', 0.0):.4f}")
    print(f"Recall:    {scores.get('ents_r', 0.0):.4f}")
    print(f"F1-score:  {scores.get('ents_f', 0.0):.4f}")

    # Print per-entity type scores if available
    if "ents_per_type" in scores:
        print("\nPer-Entity Type Scores:")
        for entity_type, type_scores in scores["ents_per_type"].items():
            print(f"\n{entity_type}:")
            print(f"  Precision: {type_scores.get('p', 0.0):.4f}")
            print(f"  Recall:    {type_scores.get('r', 0.0):.4f}")
            print(f"  F1-score:  {type_scores.get('f', 0.0):.4f}")

    return scores


def test_spacy_model_with_scorer(model_path, test_data):
    """
    Alternative implementation using Scorer object directly.
    This provides more granular control over the scoring process.

    Parameters:
        model_path (str): Path to the trained spaCy model.
        test_data (list): List of tuples (text, annotations).

    Returns:
        dict: Dictionary containing evaluation metrics.
    """
    # Load the trained model
    nlp = spacy.load(model_path)

    # Create a Scorer object
    scorer = Scorer()

    # Process each test example
    for text, annotations in test_data:
        try:
            # Create predicted document
            doc = nlp(text)

            # Create reference document
            ref_doc = nlp.make_doc(text)
            entities = annotations.get("entities", [])
            biluo_tags = offsets_to_biluo_tags(ref_doc, entities)
            ref_spans = biluo_tags_to_spans(ref_doc, biluo_tags)
            ref_doc.ents = ref_spans

            # Create Example and score it
            example = Example(predicted=doc, reference=ref_doc)
            scorer.score([example])

        except Exception as e:
            print(f"Error processing: {text}")
            print(f"Error: {e}")
            continue

    # Get scores
    scores = scorer.scores

    print("\n" + "=" * 50)
    print("EVALUATION METRICS")
    print("=" * 50)
    print(f"Precision: {scores.get('ents_p', 0.0):.4f}")
    print(f"Recall:    {scores.get('ents_r', 0.0):.4f}")
    print(f"F1-score:  {scores.get('ents_f', 0.0):.4f}")

    return scores


def load_test_data_from_docbin(docbin_path, nlp):
    """
    Load test data from a DocBin file.

    Parameters:
        docbin_path (str): Path to the DocBin file.
        nlp: spaCy language model for vocabulary.

    Returns:
        list: List of Example objects.
    """
    doc_bin = DocBin().from_disk(docbin_path)
    docs = list(doc_bin.get_docs(nlp.vocab))

    examples = []
    for doc in docs:
        # Create a predicted version by running through the pipeline
        pred_doc = nlp(doc.text)
        example = Example(predicted=pred_doc, reference=doc)
        examples.append(example)

    return examples


# Example usage
if __name__ == "__main__":
    # Example test data format
    test_data = [
        (
            "Apple Inc. was founded by Steve Jobs in Cupertino",
            {"entities": [(0, 10, "ORG"), (28, 38, "PERSON"), (42, 51, "GPE")]},
        ),
        ("Google acquired YouTube in 2006", {"entities": [(0, 6, "ORG"), (16, 23, "PRODUCT"), (27, 31, "DATE")]}),
    ]

    # Test the model
    model_path = "path/to/your/model"
    # scores = test_spacy_model(model_path, test_data)

    print("\n# Usage with DocBin:")
    print("# docbin_path = 'path/to/test.spacy'")
    print("# nlp = spacy.load(model_path)")
    print("# examples = load_test_data_from_docbin(docbin_path, nlp)")
    print("# scores = nlp.evaluate(examples)")
