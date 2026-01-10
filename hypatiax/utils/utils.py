# Functions to use to get tokens and components
# get_file_hash,rename_files, load_data_from_json,save_data_to_json,save_entity_model,call_main_script,elapsed_run_time,run_script,get_formatted_patterns,get_ner_desc_formulas, get_ner_desc_formulas_simple, auto_migrate_to_new_format, convert_json_to_spacy,dict_list_to_dict_dict, matcher_docs,gather_sym,load_model_from_package,load_spacy_models_from_subdirectory,plot_history_model,make_predictions, evaluate_the_model_in_batches,evaluate_the_model,main_evaluation_function,evaluation_profiler, save_spacy_training_data, upload_spacy_training_data,save_spacy_training_data_to_json, upload_spacy_training_data_from_json,normalize_formula, dataset_normalized, get_pos_,get_patterns,set_entity,create_ruler, preproc_ent,tok_formulas
import cProfile
import datetime
import hashlib
import json
import logging
import os
import platform
import pstats
import re
import shutil
import subprocess
import sys
from datetime import datetime
from importlib import resources
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import nltk
import pandas as pd
import spacy
from nltk.tokenize import sent_tokenize, word_tokenize, wordpunct_tokenize
from spacy import displacy
from spacy.language import Language
from spacy.matcher import Matcher
from spacy.pipeline import EntityRuler
from spacy.tokens import Doc, DocBin
from spacy.training import Example

from hypatiax.utils.tree_id_op import TreeDict, TreeNode, TreeOPDict


def get_file_hash(filepath):
    """Calculate MD5 hash of file to detect if it changed"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def rename_files(directory, in_, out_):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if in_ in filename:
                new_filename = filename.replace(in_, out_)
                old_filepath = os.path.join(root, filename)
                new_filepath = os.path.join(root, new_filename)
                os.rename(old_filepath, new_filepath)
                print(f"Renamed: {old_filepath} -> {new_filepath}")


# Example usage
# directory_path = 'path/to/your/directory'
# rename_queries_to_tableau(directory_path)


def load_data_from_json(file_path):
    # Load the data back into Python
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        print("Data successfully loaded from JSON.")
        return data
    except Exception as e:
        print(f"Failed to load data with error: {e}")
        return None


# loaded_data = load_data_from_json(file_path)
# print(loaded_data)


def save_data_to_json(file_path, data):
    # Convert and save this data to a JSON file
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print("Data successfully saved to JSON.")
    except Exception as e:
        print(f"Failed to save data with error: {e}")


def save_entity_model(path, model, filename):
    # Assuming 'model' is a SpaCy NER model, or similar
    try:
        model_path = os.path.join(path, filename)
        # model.to_disk(model_path)
        print(f"Model saved to {model_path}")
    except Exception as e:
        # logging.error(f"Failed to get NER entity from {model_path} with error: {e}")
        return None, None


def call_main_script(py_function, query_type, python_executable="python3"):
    """Executes a Python script with the given arguments using subprocess."""
    command = [python_executable, py_function, query_type]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running script {py_function}: {e.stderr}") from e

    return result.stdout


def elapsed_run_time(start_time, end_time):
    """Calculates and formats the elapsed time between two datetime instances."""
    elapsed_time = end_time - start_time
    seconds = int(elapsed_time.total_seconds())

    if seconds < 60:
        return f"The function took {seconds} seconds to run."
    elif seconds < 3600:
        minutes, seconds = divmod(seconds, 60)
        return f"The function took {minutes} minutes and {seconds} seconds to run."
    else:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"The function took {hours} hours, {minutes} minutes and {seconds} seconds to run."


def run_script(script_path, python_executable="python3.11"):
    """Runs the specified script using a specified Python version and handles the output."""
    try:
        result = subprocess.run(
            [python_executable, script_path], capture_output=True, text=True, check=True
        )
        print(f"{script_path} completed successfully: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e.stderr}")
        return None
    return result


def get_formatted_patterns(*patterns_list):
    """Converts list of pattern dictionaries into a format compatible with SpaCy's EntityRuler."""
    rules_patterns = []
    for patterns_dict in patterns_list:
        for key, patterns in patterns_dict.items():
            rules_patterns.extend(
                [{"label": key, "pattern": pattern} for pattern in patterns]
            )
    return rules_patterns


def integrate_nlp_pipelines(nlp, mlp, ruler_threshold, priority="nlp"):
    """Integrates components from one NLP model into another based on a specified condition."""
    for name, component in mlp.pipeline:
        if name not in nlp.pipe_names:
            print(f"Component {name} isn't in the primary model, adding it.")
            nlp.add_pipe(component, name=name, before=ruler_threshold)
        else:
            print(f"Component {name} already exists in the primary model.")
    return nlp


def auto_migrate_to_new_format(base_name="ruler_tableau_desc", version="version1"):
    """
    Automatically create backup if file changed or version1 doesn't exist.

    Args:
        base_name: Base name of the ruler file (e.g., "ruler_tableau_desc")
        version: Version string (e.g., "version1")

    Returns:
        bool: True if backup was created, False otherwise
    """
    script_dir = Path(__file__).parent

    # Files
    base_file = script_dir / f"{base_name}.jsonl"
    version_file = script_dir / f"{base_name}_{version}.jsonl"
    versions_dir = script_dir / "rules_versions"

    # Create versions directory if it doesn't exist
    versions_dir.mkdir(exist_ok=True)

    # Check if base file exists
    if not base_file.exists():
        print(f"⚠️  Base file not found: {base_file}")
        return False

    # CASE 1: version1 file doesn't exist yet - CREATE IT
    if not version_file.exists():
        try:
            print(f"📄 Creating {version_file.name} from {base_file.name}...")
            shutil.copy2(base_file, version_file)
            print(f"✅ Created {version_file.name}")

            # Create initial backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{base_name}_v1_initial_{timestamp}.jsonl"
            backup_path = versions_dir / backup_name
            shutil.copy2(base_file, backup_path)
            print(f"📦 Initial backup: {backup_name}")

            return True

        except Exception as e:
            print(f"❌ Failed to create version file: {e}")
            return False

    # CASE 2: version1 exists - CHECK IF BASE FILE CHANGED
    else:
        # Compare base file with version1 file
        base_hash = get_file_hash(base_file)
        version_hash = get_file_hash(version_file)

        if base_hash != version_hash:
            # Files are different - base file was modified!
            print(f"🔄 Detected changes in {base_file.name}")

            try:
                # Create backup of OLD version1 before updating
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{base_name}_v1_backup_{timestamp}.jsonl"
                backup_path = versions_dir / backup_name
                shutil.copy2(version_file, backup_path)
                print(f"📦 Backed up old version: {backup_name}")

                # Update version1 file with new content from base
                shutil.copy2(base_file, version_file)
                print(f"✅ Updated {version_file.name} with changes")

                return True

            except Exception as e:
                print(f"❌ Failed to backup changes: {e}")
                return False
        else:
            # Files are identical - no backup needed
            print(f"✓ {base_name}.jsonl unchanged, no backup needed")
            return False


def convert_json_to_spacy(input_file, output_dir, language="en"):
    import subprocess

    try:
        command = [
            "python",
            "-m",
            "spacy",
            "convert",
            input_file,
            output_dir,
            "--converter",
            "json",
            "--lang",
            language,
        ]
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("Output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while converting: {e.stderr}")


def dict_list_to_dict_dict(dictionary):
    new_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, list):
            new_dict[key] = {
                item_key: item_value
                for d in value
                for item_key, item_value in d.items()
            }
    return new_dict


def matcher_docs(nlp):
    matcher = Matcher(nlp.vocab)
    pattern = [{"LOWER": "hello"}, {"IS_PUNCT": True}, {"LOWER": "world"}]
    matcher.add("HelloWorld", [pattern])

    doc = nlp("Hello, world! Hello world!")
    matches = matcher(doc)

    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        print(match_id, string_id, start, end, span.text)


def gather_sym(data, column_name):
    dp = data[column_name]
    dp_text = []
    dp_sym = []

    for row in dp:
        drow_text = []
        drow_sym = []

        for item in row:
            if re.match(r"\w+", item):
                drow_text.append(item)
            else:
                drow_sym.append(item)
        dp_text.append(drow_text)
        dp_sym.append(drow_sym)
    return dp_text, dp_sym


def load_model_from_package(package_name, model_dir):
    from importlib import resources

    import spacy

    with resources.path(package_name, model_dir) as path:
        nlp = spacy.load(str(path))
        return nlp


def load_spacy_models_from_subdirectory(package, subdirname):
    import os
    from importlib import resources

    import spacy

    models = {}

    with resources.path(package, subdirname) as base_path:
        for model_dir in os.listdir(base_path):
            model_path = os.path.join(base_path, model_dir)
            if os.path.isdir(model_path):
                nlp = spacy.load(model_path)
                models[model_dir] = nlp
    return models


def plot_history_model(history, title_plot, figname):
    if isinstance(history, pd.DataFrame):
        x_l, y_l = history.columns
        plt.plot(history[x_l], history[y_l])
        plt.xlabel(x_l)
        plt.ylabel(y_l)
        plt.grid()
        plt.title(title_plot)
        plt.savefig(figname + ".png")
        plt.show()
    else:
        print("Error: history isn't in a DataFrame format")


def make_predictions(model_path, texts, option=1, custom_labels=None):
    """
    Make predictions using a saved spaCy model.

    Args:
        model_path (str or Path): Path to the trained spaCy model.
        texts (str or list[str]): One or more texts to analyze.
        option (int): 1 = print entities, 2 = render via displacy.
        custom_labels (list[str], optional): Custom labels to ensure are displayed.
    """
    nlp = spacy.load(model_path)
    print(f"Pipeline components: {nlp.pipe_names}")

    if not isinstance(texts, list):
        texts = [texts]

    for doc in nlp.pipe(texts):
        # Optionally print recognized entities
        if option == 1:
            if doc.ents:
                for ent in doc.ents:
                    label = ent.label_
                    # Show custom labels even if not in built-in spaCy labels
                    if custom_labels and label not in custom_labels:
                        print(f"⚠ Unregistered label detected: {label}")
                    print(f"{ent.text:40} -> {label}")
            else:
                print("  (No entities detected)")
        # Optionally render via displacy
        elif option == 2:
            displacy.render(doc, style="ent")


# from spacy.training import Example
# from spacy.scorer import Scorer

# Default scoring pipeline
# scorer = Scorer()

# Provided scoring pipeline
# nlp = spacy.load("en_core_web_sm")
# scorer = Scorer(nlp)
# scores = scorer.score(examples)
# NAME	DESCRIPTION
# examples	The Example objects holding both the predictions and the correct gold-standard annotations.
"""
nlp = spacy.load(path_to_model)
examples = []
scorer = Scorer()
for text, annotations in TEST_REVISION_DATA:
    doc = nlp.make_doc(text)
    example = Example.from_dict(doc, annotations)
    example.predicted = nlp(str(example.predicted))
    examples.append(example)
scorer.score(examples)
"""


def aggregate_scores(leaves_scores):
    """
    Aggregates batch scores safely, handling nested dicts like ents_per_type.
    """
    total_scores = {}

    for key, scores_list in leaves_scores.items():
        # Remove None
        valid_scores = [s for s in scores_list if s is not None]

        if not valid_scores:
            total_scores[key] = 0
            continue

        # Handle dicts (e.g., ents_per_type)
        if isinstance(valid_scores[0], dict):
            # Aggregate per subkey
            agg_dict = {}
            for d in valid_scores:
                for subkey, metrics in d.items():
                    if subkey not in agg_dict:
                        agg_dict[subkey] = {}
                    for metric, value in metrics.items():
                        agg_dict[subkey].setdefault(metric, []).append(value)
            # Compute average per metric
            for subkey, metrics in agg_dict.items():
                for metric, values in metrics.items():
                    metrics[metric] = sum(values) / len(values)
            total_scores[key] = agg_dict
        else:
            # Normal float values
            total_scores[key] = sum(valid_scores) / len(valid_scores)

    return total_scores


def evaluate_the_model_in_batches(nlp, TEST_DATA, batch_size):
    leaves_scores = {}

    for i in range(0, len(TEST_DATA), batch_size):
        print("batch_nmuber:", i + 1)
        batch = TEST_DATA[i : i + batch_size]
        examples = [Example.from_dict(nlp.make_doc(text), ann) for text, ann in batch]
        batch_scores = nlp.evaluate(examples)  # <- returns dict directly

        for key, value in batch_scores.items():
            leaves_scores.setdefault(key, []).append(value)

    total_scores = aggregate_scores(leaves_scores)
    return total_scores


def main_evaluation_function(model_path, TEST_DATA):
    nlp = spacy.load(model_path)
    scores = evaluate_the_model(nlp, TEST_DATA)
    print(scores)


def evaluation_profiler(function, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.runcall(function, *args, **kwargs)
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative").print_stats(10)


def evaluate_the_model(nlp, TEST_DATA):
    examples = [
        Example.from_dict(nlp.make_doc(text), annotations)
        for text, annotations in TEST_DATA
    ]
    return nlp.evaluate(examples).scores


def save_spacy_training_data(output_dir, training_data, filename, model):
    """Save training data to .spacy format."""
    try:
        nlp = spacy.load(model)
    except OSError:
        # Fallback to blank model if specific model not available
        print(f"⚠️  Model '{model}' not found, using blank 'en' model")
        nlp = spacy.blank("en")

    os.makedirs(output_dir, exist_ok=True)
    doc_bin = DocBin()

    for text, annotations in training_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        doc_bin.add(example.reference)

    output_path = os.path.join(output_dir, filename + ".spacy")
    doc_bin.to_disk(output_path)
    print(f"✓ Saved {len(training_data)} examples to {output_path}")


def upload_spacy_training_data(input_dir, filename, nlp):
    """Load training data from .spacy format."""
    file_path = os.path.join(input_dir, filename + ".spacy")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Training data not found: {file_path}")

    doc_bin = DocBin().from_disk(file_path)
    docs = list(doc_bin.get_docs(nlp.vocab))

    training_data = [
        (
            doc.text,
            {
                "entities": [
                    (ent.start_char, ent.end_char, ent.label_) for ent in doc.ents
                ]
            },
        )
        for doc in docs
    ]

    print(f"✓ Loaded {len(training_data)} examples from {file_path}")
    return training_data


def save_spacy_training_data_to_json(output_dir, training_data, filename):
    """Save training data to JSON format."""
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename + ".json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=4)

    print(f"✓ Saved {len(training_data)} examples to {file_path}")


def upload_spacy_training_data_from_json(input_dir, filename):
    """Load training data from JSON format."""
    file_path = os.path.join(input_dir, filename + ".json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Training data not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        training_data = json.load(f)

    print(f"✓ Loaded {len(training_data)} examples from {file_path}")
    return training_data


# Funtion to normalize data to allow get the token more easily
def normalize_formula(text):

    # Add space after function names if missing
    text = re.sub(r"(\w)\(", r"\1 (", text)
    # Ensure there's a space before and after parentheses
    text = re.sub(r"\s*\(\s*", " ( ", text)
    text = re.sub(r"\s*\)\s*", " ) ", text)
    # Ensure there's a space before and after square brackets
    text = re.sub(r"\s*\[\s*", " [ ", text)
    text = re.sub(r"\s*\]\s*", " ] ", text)
    # Ensure there's a space before and after curly brackets
    text = re.sub(r"\s*\{\s*", " { ", text)
    text = re.sub(r"\s*\}\s*", " } ", text)
    # Ensure there's a space before and after comparison symbols
    text = re.sub(r"\s*\==\s*", " == ", text)
    text = re.sub(r"(?<!\=)\s*\=\s*(?!=)", " = ", text)
    text = re.sub(r"\s*\>=\s*", " >= ", text)
    text = re.sub(r"\s*\<=\s*", " <= ", text)
    text = re.sub(r"\s*\>\s*", " > ", text)
    text = re.sub(r"\s*\<\s*", " < ", text)
    # Ensure there's a space before and after interrogative/exclamative symbols
    text = re.sub(r"\s*\?\s*", " ? ", text)
    text = re.sub(r"\s*\!\s*", " ! ", text)

    return text


import re

import pandas as pd


def dataset_normalized(path_data, col_name):
    # Validate parameters
    if not isinstance(path_data, str):
        raise ValueError("path_data must be a string representing the file path.")
    if not isinstance(col_name, str):
        raise ValueError("col_name must be a string representing the column name.")

    # Attempt to load the dataset
    try:
        if path_data.endswith((".xlsx", ".xls")):
            df = pd.read_excel(path_data)
        elif path_data.endswith(".csv"):
            df = pd.read_csv(path_data)
        else:
            raise ValueError(
                "Unsupported file format. Only Excel and CSV files are supported."
            )

        if col_name not in df.columns:
            raise ValueError(f"Column {col_name} not found in the data.")

        # Normalize data
        df[col_name] = df[col_name].apply(normalize_formula)
        return df
    except Exception as e:
        raise IOError(f"An error occurred while loading the data: {e}")


# Function to get the position of each token
def get_pos_(data, col_name, nlp):
    dd = []
    gg = []

    for tok in data[col_name]:

        for ent in nlp(str(list(str(tok).split()))):
            # checking text between punct
            dd.append({ent.text: ent.pos_})
            gg.append({ent.pos_: ent.text})
    return dd, gg


# Function to get patterns based on the tokenization
def get_patterns(data, col_name, nlp):
    dt, dp = get_pos_(data, col_name, nlp)

    pos_ = [list(item.keys())[0] for item in dp]
    pos_ = list(set(pos_))
    # print(dt)
    # print(col_name,":",pos_)
    patterns = {}
    patterns_head = []
    for key in pos_:
        patterns.update(
            {
                key: list(
                    set(
                        [
                            d[key]
                            for d in dp
                            if key == list(d.keys())[0]
                            and d[key] not in data["stopwords"]
                        ]
                    )
                )
            }
        )
    return patterns


def get_ner_desc_formulas(nlp_formulas, nlp_desc, ruler_name="ruler_arg"):
    """
    Merge two spaCy NLP pipelines (formulas and descriptions) into one.

    Args:
        nlp_formulas: spaCy nlp object with formulas NER pipeline
        nlp_desc: spaCy nlp object with descriptions NER pipeline
        ruler_name: Name of the ruler component to merge (default: 'ruler_arg')

    Returns:
        Merged spaCy nlp object containing components from both pipelines
    """
    # Start with a copy of the desc pipeline as base
    nlp = nlp_desc

    # Get the ruler component from formulas pipeline if it exists
    if ruler_name in nlp_formulas.pipe_names:
        formulas_ruler = nlp_formulas.get_pipe(ruler_name)

        # Check if ruler already exists in desc pipeline
        if ruler_name in nlp.pipe_names:
            # Get existing ruler from desc pipeline
            desc_ruler = nlp.get_pipe(ruler_name)

            # Merge patterns from both rulers
            if isinstance(formulas_ruler, EntityRuler) and isinstance(
                desc_ruler, EntityRuler
            ):
                # Get patterns from both rulers
                formulas_patterns = formulas_ruler.patterns
                desc_patterns = desc_ruler.patterns

                # Combine patterns (avoiding duplicates)
                combined_patterns = desc_patterns + [
                    p for p in formulas_patterns if p not in desc_patterns
                ]

                # Remove old ruler and add new one with combined patterns
                nlp.remove_pipe(ruler_name)
                ruler = nlp.add_pipe("entity_ruler", name=ruler_name, before="ner")
                ruler.add_patterns(combined_patterns)

                print(
                    f"✅ Merged {len(desc_patterns)} desc patterns + {len(formulas_patterns)} formulas patterns"
                )
                print(f"   Total unique patterns: {len(combined_patterns)}")
        else:
            # Add formulas ruler to desc pipeline if it doesn't exist
            nlp.add_pipe(ruler_name, source=nlp_formulas, before="ner")
            print(f"✅ Added '{ruler_name}' component from formulas pipeline")

    # Optionally merge other custom components from formulas pipeline
    for pipe_name in nlp_formulas.pipe_names:
        if pipe_name.startswith("custom_") and pipe_name not in nlp.pipe_names:
            nlp.add_pipe(pipe_name, source=nlp_formulas, last=True)
            print(f"✅ Added custom component '{pipe_name}' from formulas pipeline")

    print(f"\n📋 Final pipeline: {nlp.pipe_names}")

    return nlp


# Alternative simpler version if you just want to combine NER entities
def get_ner_desc_formulas_simple(nlp_formulas, nlp_desc, ruler_name="ruler_arg"):
    """
    Simple version: Use desc pipeline and add formulas ruler patterns.

    Args:
        nlp_formulas: spaCy nlp object with formulas NER pipeline
        nlp_desc: spaCy nlp object with descriptions NER pipeline
        ruler_name: Name of the ruler component to extract patterns from

    Returns:
        Combined spaCy nlp object
    """
    nlp = nlp_desc

    # Extract patterns from both pipelines
    patterns = []

    if ruler_name in nlp_desc.pipe_names:
        desc_ruler = nlp_desc.get_pipe(ruler_name)
        if isinstance(desc_ruler, EntityRuler):
            patterns.extend(desc_ruler.patterns)

    if ruler_name in nlp_formulas.pipe_names:
        formulas_ruler = nlp_formulas.get_pipe(ruler_name)
        if isinstance(formulas_ruler, EntityRuler):
            patterns.extend(formulas_ruler.patterns)

    # Remove duplicates while preserving order
    seen = set()
    unique_patterns = []
    for p in patterns:
        p_str = str(p)
        if p_str not in seen:
            seen.add(p_str)
            unique_patterns.append(p)

    # Replace ruler with combined patterns
    if ruler_name in nlp.pipe_names:
        nlp.remove_pipe(ruler_name)

    ruler = nlp.add_pipe("entity_ruler", name=ruler_name, before="ner")
    ruler.add_patterns(unique_patterns)

    print(f"✅ Combined {len(unique_patterns)} unique patterns")
    print(f"📋 Pipeline: {nlp.pipe_names}")

    return nlp


# Usage example:
# if __name__ == "__main__":
#    from hypatiax.utils.files import FilesManager

#    F = FilesManager('data_spacy', 'queries', 'tableau', '')

#    # Load both models
#    nlp_formulas = F.load('ner_tableau_formulas', 'ner')
#    nlp_desc = F.load('ner_tableau_desc', 'ner')

#    # Merge them
#    nlp = get_ner_desc_formulas(nlp_formulas, nlp_desc, 'ruler_arg')

#    # Test
#    text = "Sum of Sales and Average Profit across all entries"
#    doc = nlp(text)

#    print(f"\nTest: {text}")
#    for ent in doc.ents:
#        print(f"  {ent.text:30} -> {ent.label_}")

# Function to get entities in the format (text, ent.start_char, ent.end_char, ent.label_)


def set_entity(data, col_name, ner_base_entity=None):
    if not isinstance(col_name, str):
        raise ValueError("col_name must be a string representing the column name.")

    if col_name not in data.columns:
        raise ValueError(f"Column {col_name} not found in the data.")

    # Load spaCy model only once and reuse
    try:
        if ner_base_entity is None:
            nlp = spacy.load("en_core_web_sm")
        else:
            nlp = spacy.load(ner_base_entity)
    except Exception as e:
        raise ValueError(f"Failed to load spaCy model: {e}")

    dd = []
    dt = []
    for text in data[col_name]:
        doc = nlp(text)
        dp = [text]
        dt_e = {"entities": []}
        for ent in doc.ents:
            dp.append([ent.text, ent.label_])
            dt_e["entities"].append(
                (int(ent.start_char), int(ent.end_char), ent.label_)
            )
        dt.append((text, dt_e))
        dd.append(dp)
    return dd, dt


# Function to create and return an EntityRuler with specified patterns
def create_ruler(rules, nlp=None, ner_base_model=None):
    if ner_base_model == None:
        nlp = spacy.load("en_core_web_sm")
    else:
        nlp = spacy.load(ner_base_model)
    ruler = EntityRuler(nlp, overwrite_ents=True)
    if isinstance(rules, list) == True:
        formatted_patterns = rules
    elif isinstance(rules, dict) == True and isinstance(*rules.values(), list) == True:
        formatted_patterns = [
            {"label": label, "pattern": pattern}
            for (label, patterns) in rules.items()
            for pattern in patterns
        ]
    elif isinstance(rules, dict) == True and isinstance(*rules.values(), list) == False:
        formatted_patterns = [
            {"label": label, "pattern": pattern} for (label, pattern) in rules.items()
        ]
    else:
        pass
    ruler.add_patterns(formatted_patterns)
    return ruler


# Function to transform data


def preproc_ent(path_data, stopwords, train=True):
    """
    Process entity data from file path or DataFrame.

    Args:
        path_data: Either a file path (str/Path) or a pandas DataFrame
        stopwords: List of stopwords for filtering
        train: Boolean indicating training mode

    Returns:
        If train=True: tuple of (out_d, out_f) dictionaries
        If train=False: DataFrame
    """
    # Check if input is already a DataFrame
    if isinstance(path_data, pd.DataFrame):
        df = path_data
    else:
        # Validate path parameter
        if not isinstance(path_data, (str, Path)):
            raise ValueError(
                "path_data must be a string/Path representing the file path or a DataFrame."
            )

        # Load data from file
        path_str = str(path_data)
        file_data = path_str.split("/")[-1]

        try:
            if file_data.endswith((".xlsx", ".xls")):
                df = pd.read_excel(path_data)
            elif file_data.endswith(".csv"):
                df = pd.read_csv(path_data)
            else:
                raise ValueError(
                    "Unsupported file format. Only Excel and CSV files are supported."
                )
        except Exception as e:
            raise IOError(f"An error occurred while loading the data: {e}")

    # Normalize formulas in the second column (index 1)
    if len(df.columns) > 1:
        df[df.columns[1]] = df[df.columns[1]].apply(lambda x: normalize_formula(x))

    if train:
        # Ensure stopwords is a list or tuple with at least 2 elements
        if isinstance(stopwords, list) and not isinstance(stopwords[0], list):
            # Single list provided, use same stopwords for both
            stopwords = [stopwords, stopwords]

        out_d = {"stopwords": stopwords[0], "text": [], "vocab": []}
        out_f = {"stopwords": stopwords[1], "text": [], "vocab": []}

        # Tokenize data
        dg_tok = df.apply(lambda x: [wordpunct_tokenize(str(y)) for y in x])

        # Process first two columns
        for idx, col in enumerate(df.columns[:2]):
            out = out_d if idx == 0 else out_f
            out["text"] = [str(sentence) for sentence in df[col]]
            out["vocab"] = list(
                set(
                    word
                    for sentence in dg_tok[col]
                    for word in sentence
                    if word not in out["stopwords"]
                )
            )

        return out_d, out_f
    else:
        return df


# Functions to tokenize "FORMULAS" with symbols and get the operators
# Function to transform data
def preproc_ent(path_data, stopwords, train=True):
    """
    Process entity data from file path or DataFrame.

    Args:
        path_data: Either a file path (str/Path) or a pandas DataFrame
        stopwords: List of stopwords for filtering
        train: Boolean indicating training mode

    Returns:
        If train=True: tuple of (out_d, out_f) dictionaries
        If train=False: DataFrame
    """
    # Check if input is already a DataFrame
    if isinstance(path_data, pd.DataFrame):
        df = path_data
    else:
        # Validate path parameter
        if not isinstance(path_data, (str, Path)):
            raise ValueError(
                "path_data must be a string/Path representing the file path or a DataFrame."
            )

        # Load data from file
        path_str = str(path_data)
        file_data = path_str.split("/")[-1]

        try:
            if file_data.endswith((".xlsx", ".xls")):
                df = pd.read_excel(path_data)
            elif file_data.endswith(".csv"):
                df = pd.read_csv(path_data)
            else:
                raise ValueError(
                    "Unsupported file format. Only Excel and CSV files are supported."
                )
        except Exception as e:
            raise IOError(f"An error occurred while loading the data: {e}")

    # Normalize formulas in the second column (index 1)
    if len(df.columns) > 1:
        df[df.columns[1]] = df[df.columns[1]].apply(lambda x: normalize_formula(x))

    if train:
        # Ensure stopwords is a list or tuple with at least 2 elements
        if isinstance(stopwords, list) and not isinstance(stopwords[0], list):
            # Single list provided, use same stopwords for both
            stopwords = [stopwords, stopwords]

        out_d = {"stopwords": stopwords[0], "text": [], "vocab": []}
        out_f = {"stopwords": stopwords[1], "text": [], "vocab": []}

        # Tokenize data
        dg_tok = df.apply(lambda x: [wordpunct_tokenize(str(y)) for y in x])

        # Process first two columns
        for idx, col in enumerate(df.columns[:2]):
            out = out_d if idx == 0 else out_f
            out["text"] = [str(sentence) for sentence in df[col]]
            out["vocab"] = list(
                set(
                    word
                    for sentence in dg_tok[col]
                    for word in sentence
                    if word not in out["stopwords"]
                )
            )

        return out_d, out_f
    else:
        return df


# Functions to tokenize "FORMULAS" with symbols and get the operators


def tok_formulas(path_data, not_oper):
    """
    Tokenize formulas and extract operators.

    Args:
        path_data: Either a file path (str/Path) or a pandas DataFrame
        not_oper: List of strings representing non-operator tokens

    Returns:
        List of extracted operators
    """
    # Validate not_oper parameter
    if not isinstance(not_oper, list):
        raise ValueError(
            "not_oper must be a list of strings representing non-operator tokens."
        )

    # Check if input is already a DataFrame
    if isinstance(path_data, pd.DataFrame):
        df = path_data
    else:
        # Validate path parameter
        if not isinstance(path_data, (str, Path)):
            raise ValueError(
                "path_data must be a string/Path representing the file path or a DataFrame."
            )

        # Check the file format and read the file accordingly
        path_str = str(path_data)
        file_data = path_str.split("/")[-1]

        if file_data.endswith((".xlsx", ".xls")):
            try:
                df = pd.read_excel(path_data)
            except Exception as e:
                raise IOError(f"Failed to load Excel file: {e}")
        elif file_data.endswith(".csv"):
            try:
                df = pd.read_csv(path_data)
            except Exception as e:
                raise IOError(f"Failed to load CSV file: {e}")
        else:
            raise ValueError(
                "Unsupported file format. Only Excel and CSV files are supported."
            )

    # Define regex pattern for splitting
    patterns = r"\(| = | >= | > | \[ | \) | \{ | \]"
    tr_0 = []

    # Process each row in the specified column (formulas column is index 1)
    for tr in df[df.columns[1]]:
        try:
            items = re.split(patterns, str(tr))
            if len(items) >= 2:
                it0, it1 = items[0:2]
            else:
                it0 = items[0]

            it01 = it0.split()
            if len(it01) == 1:
                iten = it01[0]
            elif len(it01) == 2:
                iten = it01[0] + " " + it01[1]
            else:
                iten = ""
                for item in it01:
                    if item not in tr_0 and item not in not_oper:
                        iten += item + " "
                iten = iten.rstrip()

            if iten not in tr_0 and iten not in not_oper:
                tr_0.append(iten)

        except Exception as e:
            raise ValueError(f"Error processing formula '{tr}': {e}")

    return tr_0
