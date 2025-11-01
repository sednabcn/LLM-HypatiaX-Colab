iimport spacy
from spacy.scorer import Scorer
from spacy.tokens import DocBin
from hypatiax.custom_ner.queries.tableau import custom_tableau_desc_components,custom_tableau_formulas_components, custom_tableau_components

def test_spacy_model(model_path, test_data):
    # Load the trained model
    nlp = spacy.load(model_path)

    # Create a Scorer object
    scorer = Scorer(nlp)

    # Evaluate the model on new data
    for text, ann in test_data:
        doc = nlp(text)  # Predicted document
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

        # Create a reference document using the annotations
        ref_doc = spacy.tokens.Doc(nlp.vocab, words=[t.text for t in doc])
        biluo_tags = spacy.gold.biluo_tags_from_offsets(ref_doc, ann['entities'])
        ref_doc.ents = spacy.gold.spans_from_biluo_tags(ref_doc, biluo_tags)

        # Score the predicted document
        example = spacy.training.Example(predicted=doc, reference=ref_doc)
        scorer.score(example)

    # Obtain overall scores
    scores = scorer.scores
    print("Precision:", scores['ents_p'])
    print("Recall:", scores['ents_r'])
    print("F1-score:", scores['ents_f'])

    return scores
"""
# Example usage:
# Assuming `test_data` is a list of tuples where the first element is the text
# and the second element is a dictionary containing the key 'entities' with entity offsets.
# test_data = [("Some text", {"entities": [(start, end, label)]}), ...]
# model_path = "path_to_your_model"
# scores = test_model(model_path, test_data)
Explanation:
Reference Document Creation: It constructs a reference document (ref_doc) based on the annotations (ann) provided in test_data. This involves setting the correct entity spans according to the BILOU tagging scheme used internally by spaCy.
Scoring: Utilizes spaCy's Scorer object to compute scores for the predicted document against the reference. The Scorer.score() function is used here to update the scorer with the results from the comparison between predicted and reference entities.
Output Metrics: After processing all documents, it outputs the precision, recall, and F1-score, which are crucial for evaluating NER models effectively.
Return Value: The function returns the detailed scores which include precision, recall, and F1-score for entities (ents_p, ents_r, ents_f) among other metrics.
This setup helps you gain a better understanding of your model's performance across multiple dimensions, making it easier to identify areas for improvement.
"""
