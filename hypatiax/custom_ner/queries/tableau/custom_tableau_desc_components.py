import os
import json
import spacy
from pathlib import Path
from spacy.language import Language
from hypatiax.utils.utils import create_ruler
from hypatiax.auto_migrate import migrate

nlp = spacy.load("en_core_web_sm")

script_dir = Path(__file__).parent
rules_dir = script_dir / 'rules'

    
def load_rules():
    """Load rules from the canonical JSONL file."""
    script_dir = Path(__file__).parent
    path_to_file = script_dir / 'rules' / 'ruler_tableau_desc.jsonl'
    
    if not path_to_file.exists():
        raise FileNotFoundError(f"Rule file not found: {path_to_file}")
    
    print(f"📂 Loading rules: {path_to_file}")
    
    rules = []
    with open(path_to_file, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            try:
                # Strip whitespace to ignore empty lines
                if line.strip():
                    rules.append(json.loads(line))
            except json.JSONDecodeError as e:
                # Provide a more informative error message
                raise ValueError(f"Error parsing JSON on line {line_number}: {e.msg}")
    return rules


"""Loading the rules from file with auto-migration"""
rules = None
try:
    # Auto-migrate: detects changes, creates backups, auto-restores if broken
    migrate(
        filename="ruler_tableau_desc.jsonl",
        style="rules",
        modules="custom_ner",
        domains="queries",
        sub_domains="tableau",
        folder="rules"
    )
    
    # Load rules (always from canonical name)
    rules = load_rules()
    print(f"✅ Loaded {len(rules)} rules successfully")
    
except FileNotFoundError as e:
    raise FileNotFoundError(f"Failed to load rules: {e}")
except Exception as e:
    raise RuntimeError(f"Error loading rules: {e}")


@Language.component("custom_tableau_desc_ruler")
def custom_tableau_desc_ruler_component(doc):
    custom_tableau_desc_ruler = create_ruler(rules=rules)
    return custom_tableau_desc_ruler(doc)
