# 4.-test_model_loading.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

# Test 1: Load spaCy model
try:
    import spacy

    nlp = spacy.load("en_core_web_sm")
    print("✅ Standard spaCy model loads")
except Exception as e:
    print(f"❌ spaCy model failed: {e}")

# Test 2: Try custom models
try:
    from hypatiax.utils.files import F

    nlp = F.load("ner_tableau", "ner")
    print("✅ Custom HypatiaX model loads")
except Exception as e:
    print(f"❌ Custom model failed: {e}")

# Test 3: Check custom components
try:
    import hypatiax.custom_ner.queries.tableau.custom_tableau_desc_components

    print("✅ Custom desc components import")
except Exception as e:
    print(f"❌ Desc components failed: {e}")

try:
    import hypatiax.custom_ner.queries.tableau.custom_tableau_formulas_components

    print("✅ Custom formulas components import")
except Exception as e:
    print(f"❌ Formulas components failed: {e}")
