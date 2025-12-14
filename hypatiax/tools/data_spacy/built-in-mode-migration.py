import spacy
from spacy.cli import package

# Load the old model with compatibility mode
try:
    nlp = spacy.load("path/to/ner_tableau_v", exclude=["vectors"])

    # Save it in the new format
    nlp.to_disk("path/to/ner_tableau_v-3.8.0")
    print("Migration successful!")
except Exception as e:
    print(f"Migration failed: {e}")
