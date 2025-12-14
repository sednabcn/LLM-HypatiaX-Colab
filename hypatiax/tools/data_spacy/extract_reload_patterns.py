from pathlib import Path

import spacy
import srsly


def extract_patterns_from_old_model(model_path, output_dir):
    """Extract patterns from old model to JSONL files"""
    model_path = Path(model_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Find all ruler components
    for component_dir in model_path.iterdir():
        if component_dir.is_dir() and "ruler" in component_dir.name:
            patterns_file = component_dir / "patterns.jsonl"
            if patterns_file.exists():
                # Copy patterns to output
                output_file = output_dir / f"{component_dir.name}.jsonl"
                shutil.copy(patterns_file, output_file)
                print(f"✓ Extracted: {output_file}")

    return output_dir


# Extract patterns
patterns_dir = extract_patterns_from_old_model(
    "hypatiax/data_spacy/queries/tableau/ner_tableau_v-3.7.2", "hypatiax/data_spacy/queries/tableau/extracted_patterns"
)

# Now rebuild with new spaCy version using the extracted patterns
