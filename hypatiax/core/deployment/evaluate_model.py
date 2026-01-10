import spacy
from spacy.scorer import Scorer
from spacy.training import Example

from hypatiax.custom_ner.queries.tableau import (
    custom_tableau_components,
    custom_tableau_desc_components,
    custom_tableau_formulas_components,
)


def evaluate_spacy_model(model_path, validation_data):
    """
    Evaluate a SpaCy model using provided validation data.

    Args:
        model_path (str): Path to the trained SpaCy model.
        validation_data (list): A list of tuples where each tuple is (text, annotations)
                                with annotations as a dictionary with a key 'entities'
                                pointing to the list of entities in format (start, end, label).

    Returns:
        dict: A dictionary of scores including precision, recall, and F1-score for the entities.

    Example:
        validation_data = [
            ("Apple Inc. was founded in California",
             {"entities": [(0, 10, "ORG"), (27, 37, "GPE")]}),
            ("Steve Jobs worked at Apple",
             {"entities": [(0, 10, "PERSON"), (21, 26, "ORG")]}),
        ]
        scores = evaluate_spacy_model("path/to/model", validation_data)
    """
    # Load the trained model
    nlp = spacy.load(model_path)

    # Collect all examples
    examples = []

    for text, annotations in validation_data:
        try:
            # Create reference document with gold annotations
            doc = nlp.make_doc(text)

            # Create Example object with reference annotations
            example = Example.from_dict(doc, annotations)

            # Apply the model's pipeline to get predictions
            example.predicted = nlp(text)

            examples.append(example)

        except Exception as e:
            print(f"Error processing text: '{text}'")
            print(f"Error details: {e}")
            continue

    if not examples:
        print("Warning: No valid examples to evaluate!")
        return {}

    # Evaluate all examples at once using nlp.evaluate()
    scores = nlp.evaluate(examples)

    # Print evaluation results
    print("=" * 60)
    print("MODEL EVALUATION RESULTS")
    print("=" * 60)
    print(f"Total examples evaluated: {len(examples)}")
    print(f"\nEntity Recognition Metrics:")
    print(f"  Precision: {scores.get('ents_p', 0.0):.4f}")
    print(f"  Recall:    {scores.get('ents_r', 0.0):.4f}")
    print(f"  F1-score:  {scores.get('ents_f', 0.0):.4f}")

    # Print per-entity type scores if available
    if "ents_per_type" in scores:
        print(f"\nPer-Entity Type Metrics:")
        for entity_type, type_scores in scores["ents_per_type"].items():
            print(f"\n  {entity_type}:")
            print(f"    Precision: {type_scores.get('p', 0.0):.4f}")
            print(f"    Recall:    {type_scores.get('r', 0.0):.4f}")
            print(f"    F1-score:  {type_scores.get('f', 0.0):.4f}")

    # Print token accuracy if available
    if "token_acc" in scores:
        print(f"\nToken Accuracy: {scores.get('token_acc', 0.0):.4f}")

    print("=" * 60)

    return scores


def evaluate_spacy_model_with_scorer(model_path, validation_data):
    """
    Alternative implementation using Scorer object directly.
    Provides more control over the scoring process.

    Args:
        model_path (str): Path to the trained SpaCy model.
        validation_data (list): A list of tuples (text, annotations).

    Returns:
        dict: A dictionary of evaluation scores.
    """
    # Load the trained model
    nlp = spacy.load(model_path)

    # Create a Scorer object (no need to pass nlp in spaCy v3+)
    scorer = Scorer()

    # Process validation data
    examples = []
    for text, annotations in validation_data:
        try:
            # Create reference document
            doc = nlp.make_doc(text)

            # Create Example with annotations
            example = Example.from_dict(doc, annotations)

            # Get predictions from the model
            example.predicted = nlp(text)

            examples.append(example)

        except Exception as e:
            print(f"Error processing text: '{text}'")
            print(f"Error: {e}")
            continue

    if not examples:
        print("Warning: No valid examples to score!")
        return {}

    # Score all examples
    scores = scorer.score(examples)

    print(f"\nEvaluation Results:")
    print(f"  Precision: {scores.get('ents_p', 0.0):.4f}")
    print(f"  Recall:    {scores.get('ents_r', 0.0):.4f}")
    print(f"  F1-score:  {scores.get('ents_f', 0.0):.4f}")

    return scores


def evaluate_model_on_docbin(model_path, docbin_path):
    """
    Evaluate a model on data stored in DocBin format.

    Args:
        model_path (str): Path to the trained SpaCy model.
        docbin_path (str): Path to the DocBin file containing validation data.

    Returns:
        dict: Evaluation scores.
    """
    from spacy.tokens import DocBin

    # Load model
    nlp = spacy.load(model_path)

    # Load DocBin
    doc_bin = DocBin().from_disk(docbin_path)
    docs = list(doc_bin.get_docs(nlp.vocab))

    # Create examples
    examples = []
    for gold_doc in docs:
        pred_doc = nlp(gold_doc.text)
        example = Example(predicted=pred_doc, reference=gold_doc)
        examples.append(example)

    # Evaluate
    scores = nlp.evaluate(examples)

    print(f"\nDocBin Evaluation Results:")
    print(f"  Examples: {len(examples)}")
    print(f"  Precision: {scores.get('ents_p', 0.0):.4f}")
    print(f"  Recall:    {scores.get('ents_r', 0.0):.4f}")
    print(f"  F1-score:  {scores.get('ents_f', 0.0):.4f}")

    return scores


# Example usage
if __name__ == "__main__":
    # Example validation data
    validation_data = [
        (
            "Apple Inc. was founded by Steve Jobs in Cupertino",
            {"entities": [(0, 10, "ORG"), (28, 38, "PERSON"), (42, 51, "GPE")]},
        ),
        (
            "Google acquired YouTube in 2006 for $1.65 billion",
            {
                "entities": [
                    (0, 6, "ORG"),
                    (16, 23, "PRODUCT"),
                    (27, 31, "DATE"),
                    (36, 50, "MONEY"),
                ]
            },
        ),
        (
            "Microsoft CEO Satya Nadella announced new products",
            {"entities": [(0, 9, "ORG"), (14, 27, "PERSON")]},
        ),
    ]

    # Evaluate the model
    model_path = "path/to/your/model"
    # scores = evaluate_spacy_model(model_path, validation_data)

    print("\n# To use this script:")
    print("# scores = evaluate_spacy_model('path/to/model', validation_data)")
    print("# print(f\"F1-Score: {scores['ents_f']:.4f}\")")
