# Module: `utils/files.py`

**Last Modified**: 2025-11-09T08:38:49.771691

## Dependencies

- `hypatiax.auto_migrate`
- `hypatiax.custom_ner.queries.tableau`
- `hypatiax.utils.utils`
- `importlib`
- `json`
- `os`
- `pandas`
- `spacy`

## Classes

### `FilesManager`

**Methods**:

- `__init__(self, modules, domains, sub_domains, actions, package)`
- `load(self, filename, style)`
- `_load_csv(self, filename)`
- `_load_excel(self, filename)`
- `_load_text(self, filename)`
- `_load_ner(self, filename)`
- `_load_entity(self, filename)`
- `_load_entity_json(self, filename)`
- `_load_rules(self, filename)`
- `_load_models(self, filename)`
