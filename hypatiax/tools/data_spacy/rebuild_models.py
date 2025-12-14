import spacy

from hypatiax.utils.files import FilesManager


def rebuild_models():
    """Rebuild all models with current spaCy version"""
    F = FilesManager("data_spacy", "queries", "tableau", "")

    # Start fresh with current spaCy
    nlp_base = spacy.load("en_core_web_sm")

    # Rebuild formulas model
    nlp_formulas = nlp_base.copy()
    nlp_formulas.add_pipe("span_ruler", name="ruler_tableau_formulas")
    ruler_formulas = nlp_formulas.get_pipe("ruler_tableau_formulas")
    # Load your formula rules
    ruler_formulas.from_disk("hypatiax/custom_ner/queries/tableau/rules/ruler_tableau_formulas.jsonl")
    nlp_formulas.to_disk("hypatiax/data_spacy/queries/tableau/ner_tableau_formulas")

    # Rebuild desc model
    nlp_desc = nlp_base.copy()
    nlp_desc.add_pipe("span_ruler", name="ruler_tableau_desc")
    ruler_desc = nlp_desc.get_pipe("ruler_tableau_desc")
    # Load your desc rules
    ruler_desc.from_disk("hypatiax/custom_ner/queries/tableau/rules/ruler_tableau_desc.jsonl")
    nlp_desc.to_disk("hypatiax/data_spacy/queries/tableau/ner_tableau_desc")

    # Combine them
    from hypatiax.utils.utils import get_ner_desc_formulas

    nlp_combined = get_ner_desc_formulas(nlp_formulas, nlp_desc, "ruler_arg")
    nlp_combined.to_disk("hypatiax/data_spacy/queries/tableau/ner_tableau")

    print("✅ All models rebuilt successfully")


rebuild_models()
