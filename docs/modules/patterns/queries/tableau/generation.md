# Module: `patterns/queries/tableau/generation.py`

**Last Modified**: 2025-11-08T21:51:33.838522

## Dependencies

- `hypatiax.utils.utils`
- `importlib`
- `matplotlib.pyplot`
- `nltk`
- `nltk.tokenize`
- `os`
- `pandas`
- `re`
- `spacy`
- `spacy.language`
- `spacy.matcher`
- `spacy.pipeline`
- `spacy.tokens`

## Classes

### `Generation_custom_tableau_patterns`

**Methods**:

- `__init__(self, path_data, stopwords, train)`
- `gen_patterns_tableau_desc(self)`
- `gen_patterns_tableau_formulas(self)`
- `get_rules_tableau_desc(self)`
- `get_rules_tableau_formulas(self)`
- `create_ruler_tableau(self, nlp, type)`
