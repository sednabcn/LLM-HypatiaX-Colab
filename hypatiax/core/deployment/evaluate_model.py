import spacy
from spacy.training import Example
from spacy.scorer import Scorer
from hypatiax.custom_ner.queries.tableau import custom_tableau_desc_components,custom_tableau_formulas_components, custom_tableau_components

def evaluate_spacy_model(model_path, validation_data):
    """
    Evaluate a SpaCy model using provided validation data.

    Args:
        nlp (spacy.Language): The SpaCy pipeline (model) to evaluate.
        validation_data (list): A list of tuples where each tuple is (text, annotations)
                                with annotations as a dictionary with a key 'entities'
                                pointing to the list of entities.

    Returns:
        dict: A dictionary of scores including precision, recall, and F1-score for the entities.
    """
    nlp= spacy.load(model_path)
    
    scorer = Scorer(nlp)  # Instantiate Scorer with the NLP object to enable pipeline component scoring
    for text, ann in validation_data:
        doc = nlp.make_doc(text)  # Create a document object from the text
        example = Example.from_dict(doc, ann)  # Create an Example object using the annotations
        pred_value = nlp(text)  # Process the text with the NLP object to generate predictions
        scorer.score(example)  # Score the example using the predictions

    return scorer.scores  # Return all collected scores

# Example usage:
# nlp = spacy.load("en_core_web_sm")  # Load your spaCy model
# validation_data = [
#     ("This is a text.", {"entities": [(0, 4, "LABEL")]}),
#     ("Another example.", {"entities": [(0, 7, "ANOTHER_LABEL")]}),
# ]
# print(evaluate_model(nlp, validation_data))
