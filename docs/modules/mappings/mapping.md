# Module: `mappings/mapping.py`

**Last Modified**: 2025-11-04T16:01:29.777753

## Dependencies

- `re`

## Classes

### `map_description_to_formula`

**Methods**:

- `__init__(self, description, rules, ner_entity)`
- `extract_column_name(description)`
- `map_vocab_to_vocab(self)`
- `map_sentence_to_sentence(self)`
- `map_vocab_to_vocab_regex(self)`
- `__call__(self, description, option)`
  - "vocab": use nlp to map desc_vocab to formula_vocab
