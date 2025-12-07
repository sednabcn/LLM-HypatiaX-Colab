#!/usr/bin/env python3
"""
Unified Custom Tableau Components with Dynamic Auto-Registration

This single module replaces:
- custom_tableau_components.py
- custom_tableau_formulas_components.py
- custom_tableau_desc_components.py

It automatically discovers and registers ALL .jsonl rule files as spaCy components.
Import this module BEFORE loading any trained models.

Usage:
    from hypatiax.custom_ner.queries.tableau import components
    # All components are now registered automatically

    nlp = spacy.load("your_trained_model")  # Will work!
"""

import json
import spacy
from pathlib import Path
from spacy.language import Language
from hypatiax.utils.utils import create_ruler
from hypatiax.auto_migrate import migrate

# Load base model once
try:
    _BASE_NLP = spacy.load("en_core_web_sm")
except OSError:
    print("⚠️  en_core_web_sm not found. Install: python -m spacy download en_core_web_sm")
    _BASE_NLP = None

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent
RULES_DIR = SCRIPT_DIR / "rules"

# Track all registered components globally
_REGISTERED_COMPONENTS = {}
_REGISTRATION_ERRORS = []


def load_rules(rule_type: str) -> list[dict]:
    """
    Load spaCy EntityRuler rules from a JSONL file.

    Args:
        rule_type: Base name of the rule file (without .jsonl extension)

    Returns:
        List of rule dictionaries with 'label' and 'pattern' keys

    Raises:
        FileNotFoundError: If the rule file does not exist
        ValueError: If JSON parsing fails or rules are invalid
    """
    path_to_file = RULES_DIR / f"{rule_type}.jsonl"

    if not path_to_file.exists():
        available = "\n".join(f"  - {f.name}" for f in RULES_DIR.glob("*.jsonl"))
        raise FileNotFoundError(
            f"Rule file not found: {path_to_file}\n"
            f"Available files in {RULES_DIR}:\n{available}"
        )

    rules: list[dict] = []

    with open(path_to_file, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                rule = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"JSON parse error in {path_to_file.name} "
                    f"line {line_number}: {e.msg}"
                )

            # Validate rule structure
            if not isinstance(rule, dict) or "label" not in rule or "pattern" not in rule:
                raise ValueError(
                    f"Invalid rule in {path_to_file.name} "
                    f"line {line_number}: {rule}"
                )

            rules.append(rule)

    return rules


def register_component(component_name: str, rules: list[dict]) -> bool:
    """
    Register a ruler component with spaCy.

    Args:
        component_name: Name for the component
        rules: List of EntityRuler rules

    Returns:
        True if registered successfully, False if already exists
    """
    if component_name in Language.factories:
        return False

    # Create factory function with closure to capture rules
    def make_ruler_factory(rules_list):
        def ruler_factory(nlp, name):
            def ruler_component(doc):
                ruler = create_ruler(rules=rules_list)
                return ruler(doc)
            return ruler_component
        return ruler_factory

    # Register the factory
    Language.factory(component_name)(make_ruler_factory(rules))
    _REGISTERED_COMPONENTS[component_name] = {
        'rules': rules,
        'count': len(rules)
    }

    return True


def discover_and_register_all_rulers(verbose: bool = False):
    """
    Dynamically discover and register all .jsonl rule files.

    Process:
    1. Scan rules/ directory for .jsonl files
    2. Run auto-migration (backup/validation)
    3. Load rules from each file
    4. Register as spaCy component

    Args:
        verbose: Print detailed progress information

    Returns:
        dict: Registered component information
    """
    if not RULES_DIR.exists():
        if verbose:
            print(f"⚠️  Rules directory not found: {RULES_DIR}")
        return {}

    rule_files = sorted(RULES_DIR.glob("*.jsonl"))

    if not rule_files:
        if verbose:
            print(f"⚠️  No .jsonl files found in {RULES_DIR}")
        return {}

    if verbose:
        print(f"\n{'='*80}")
        print(f"🔍 DYNAMIC COMPONENT REGISTRATION")
        print(f"{'='*80}")
        print(f"📂 Rules directory: {RULES_DIR}")
        print(f"📊 Found {len(rule_files)} rule file(s)\n")

    for rule_file in rule_files:
        rule_name = rule_file.stem

        if verbose:
            print(f"🔧 Processing: {rule_file.name}")

        try:
            # Auto-migrate with backup/validation
            migrate(
                filename=rule_file.name,
                style="rules",
                modules="custom_ner",
                domains="queries",
                sub_domains="tableau",
                folder="rules"
            )

            # Load rules
            print(f"📂 Loading rules: {rule_file.name}")
            rules = load_rules(rule_name)
            print(f"✅ Loaded {len(rules)} rules from {rule_file.name}")

            # Register component
            if register_component(rule_name, rules):
                if verbose:
                    print(f"   ✅ Registered: '{rule_name}' ({len(rules)} rules)")
            else:
                if verbose:
                    print(f"   ⏭️  Already registered: '{rule_name}'")

        except Exception as e:
            error_msg = f"Error with {rule_file.name}: {e}"
            _REGISTRATION_ERRORS.append(error_msg)
            if verbose:
                print(f"   ❌ {error_msg}")

    if verbose:
        print(f"\n{'='*80}")
        print(f"✅ Registered {len(_REGISTERED_COMPONENTS)} component(s)")
        if _REGISTRATION_ERRORS:
            print(f"⚠️  {len(_REGISTRATION_ERRORS)} error(s) occurred")
        print(f"{'='*80}\n")

    return _REGISTERED_COMPONENTS


# Register special utility components
@Language.component("ruler_sort_command")
def ruler_sort_command_component(doc):
    """Handle sort commands in Tableau queries."""
    for sent in doc.sents:
        text = sent.text.lower()
        if "sort by" in text:
            try:
                idx = text.index("sort by") + len("sort by")
                criteria = text[idx:].strip()
                # Add custom logic here if needed
            except (ValueError, IndexError):
                pass
    return doc


# API Functions
def get_registered_components():
    """Get list of all registered ruler component names."""
    return list(_REGISTERED_COMPONENTS.keys())


def get_component_info(component_name: str = None):
    """
    Get information about registered components.

    Args:
        component_name: Specific component to query, or None for all

    Returns:
        dict: Component information
    """
    if component_name:
        return _REGISTERED_COMPONENTS.get(component_name)
    return _REGISTERED_COMPONENTS


def get_registration_errors():
    """Get list of registration errors that occurred."""
    return _REGISTRATION_ERRORS.copy()


def add_all_rulers_to_pipeline(nlp_instance, skip_existing=True):
    """
    Add all registered rulers to a spaCy pipeline.

    Args:
        nlp_instance: spaCy Language object
        skip_existing: Skip components already in pipeline

    Returns:
        Modified spaCy Language object
    """
    added = []
    skipped = []

    for comp_name in _REGISTERED_COMPONENTS.keys():
        if skip_existing and comp_name in nlp_instance.pipe_names:
            skipped.append(comp_name)
            continue

        try:
            nlp_instance.add_pipe(comp_name, last=True)
            added.append(comp_name)
        except Exception as e:
            print(f"⚠️  Failed to add '{comp_name}': {e}")

    if added:
        print(f"✅ Added {len(added)} components: {', '.join(added[:3])}" +
              (f" and {len(added)-3} more" if len(added) > 3 else ""))
    if skipped:
        print(f"⏭️  Skipped {len(skipped)} existing components")

    return nlp_instance


def print_registration_summary():
    """Print detailed summary of all registered components."""
    print("\n" + "="*80)
    print("TABLEAU NER COMPONENTS - REGISTRATION SUMMARY")
    print("="*80)

    if not _REGISTERED_COMPONENTS:
        print("⚠️  No components registered")
    else:
        print(f"\n📊 Total components: {len(_REGISTERED_COMPONENTS)}\n")

        for comp_name, info in sorted(_REGISTERED_COMPONENTS.items()):
            print(f"  • {comp_name:40} ({info['count']:>4} rules)")

    if _REGISTRATION_ERRORS:
        print(f"\n⚠️  Errors ({len(_REGISTRATION_ERRORS)}):")
        for err in _REGISTRATION_ERRORS:
            print(f"  • {err}")

    print("="*80 + "\n")


# AUTO-REGISTER ON MODULE IMPORT
# This ensures all components are available when loading trained models
print(f"🔄 Auto-registering Tableau components from: {RULES_DIR}")
discover_and_register_all_rulers(verbose=False)

if _REGISTERED_COMPONENTS:
    print(f"✅ Registered {len(_REGISTERED_COMPONENTS)} Tableau components")
else:
    print("⚠️  No components were registered - check rules directory")


# Test function
def test_components():
    """Run component tests."""
    if _BASE_NLP is None:
        print("❌ Cannot test - en_core_web_sm not available")
        return False

    print("\n" + "="*80)
    print("TESTING TABLEAU COMPONENTS")
    print("="*80 + "\n")

    print_registration_summary()

    # Create test pipeline
    nlp = spacy.load("en_core_web_sm")
    nlp = add_all_rulers_to_pipeline(nlp)

    if "ruler_sort_command" not in nlp.pipe_names:
        nlp.add_pipe("ruler_sort_command", last=True)

    print(f"\n📊 Test pipeline: {nlp.pipe_names}\n")
    print("-"*80)

    # Test texts
    test_texts = [
        "Create a calculated field using SUM([Sales]) and AVG([Profit])",
        "Use IF [Sales] > 1000 THEN 'High' ELSE 'Low' END",
        "Calculate WINDOW_SUM(SUM([Sales]))",
        "Sort by sales descending",
        "Filter where CONTAINS([Product Name], 'Chair')"
    ]

    print("\n🧪 Testing entity recognition:\n")

    for i, text in enumerate(test_texts, 1):
        print(f"Test {i}: {text}")
        doc = nlp(text)

        if doc.ents:
            print("   Entities:")
            for ent in doc.ents:
                print(f"     • {ent.text:40} -> {ent.label_}")
        else:
            print("     (No entities detected)")
        print()

    print("-"*80)
    print("\n✅ Component test complete!\n")
    return True


if __name__ == "__main__":
    test_components()

    print("💡 Backups managed in .versions/ directory")
    print("   • List: python -m hypatiax.auto_migrate list <file> rules")
    print("   • Restore: python -m hypatiax.auto_migrate restore <file> rules --index 0\n")
