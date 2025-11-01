# Functions to use to get tokens and components
#rename_files,load_data_from_json,save_data_to_json,save_entity_model,call_main_script,elapsed_run_time,run_script,get_formatted_patterns,get_ner_desc_formulas, convert_json_to_spacy,dict_list_to_dict_dict, matcher_docs,gather_sym,load_model_from_package,load_spacy_models_from_subdirectory,plot_history_model,make_predictions, evaluate_the_model_in_batches,evaluate_the_model,main_evaluation_function,evaluation_profiler, save_spacy_training_data, upload_spacy_training_data,save_spacy_training_data_to_json, upload_spacy_training_data_from_json,normalize_formula, dataset_normalized, get_pos_,get_patterns,set_entity,create_ruler, preproc_ent,tok_formulas
import os
import re
import platform
import nltk
import spacy
import pandas as pd
import subprocess
import datetime
import cProfile
import pstats
import json

import matplotlib.pyplot as plt
from spacy import displacy
from spacy.matcher import Matcher
from spacy.training import Example
from spacy.tokens import DocBin
from spacy.pipeline import EntityRuler

from nltk.tokenize import word_tokenize, sent_tokenize, wordpunct_tokenize
from spacy.pipeline import EntityRuler
from importlib import resources
from hypatiax.utils.tree_id_op import TreeNode, TreeDict, TreeOPDict

def rename_files(directory,in_,out_):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if in_ in filename:
                new_filename = filename.replace(in_,out_)
                old_filepath = os.path.join(root, filename)
                new_filepath = os.path.join(root, new_filename)
                os.rename(old_filepath, new_filepath)
                print(f'Renamed: {old_filepath} -> {new_filepath}')

# Example usage
#directory_path = 'path/to/your/directory'
#rename_queries_to_tableau(directory_path)

def load_data_from_json(file_path):
    # Load the data back into Python
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print("Data successfully loaded from JSON.")
        return data
    except Exception as e:
        print(f"Failed to load data with error: {e}")
        return None


#loaded_data = load_data_from_json(file_path)
#print(loaded_data)

def save_data_to_json(file_path, data):
    # Convert and save this data to a JSON file
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
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
        result = subprocess.run([python_executable, script_path], capture_output=True, text=True, check=True)
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
            rules_patterns.extend([{"label": key, "pattern": pattern} for pattern in patterns])
    return rules_patterns


def integrate_nlp_pipelines(nlp, mlp, ruler_threshold, priority='nlp'):
    """Integrates components from one NLP model into another based on a specified condition."""
    for name, component in mlp.pipeline:
        if name not in nlp.pipe_names:
            print(f"Component {name} isn't in the primary model, adding it.")
            nlp.add_pipe(component, name=name, before=ruler_threshold)
        else:
            print(f"Component {name} already exists in the primary model.")
    return nlp

def convert_json_to_spacy(input_file, output_dir, language='en'):
    import subprocess
    try:
        command = [
            'python', '-m', 'spacy', 'convert',
            input_file, output_dir,
            '--converter', 'json',
            '--lang', language
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
            new_dict[key] = {item_key: item_value for d in value for item_key, item_value in d.items()}
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
            if re.match(r'\w+', item):
                drow_text.append(item)
            else:
                drow_sym.append(item)
        dp_text.append(drow_text)
        dp_sym.append(drow_sym)
    return dp_text, dp_sym

def load_model_from_package(package_name, model_dir):
    import spacy
    from importlib import resources
    with resources.path(package_name, model_dir) as path:
        nlp = spacy.load(str(path))
        return nlp

def load_spacy_models_from_subdirectory(package, subdirname):
    import os
    import spacy
    from importlib import resources
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
        plt.savefig(figname + '.png')
        plt.show()
    else:
        print("Error: history isn't in a DataFrame format")

def make_predictions(model_path, texts, option=1):
    nlp = spacy.load(model_path)
    print(nlp.pipe_names)

    if not isinstance(texts, list):
        texts = [texts]  # Convert single text to list for uniform processing

    for doc in nlp.pipe(texts):
        if option == 1:
            print([(ent.text, ent.label_) for ent in doc.ents])
        else:
            displacy.render(doc, style="ent")

#from spacy.training import Example
#from spacy.scorer import Scorer

# Default scoring pipeline
#scorer = Scorer()

# Provided scoring pipeline
#nlp = spacy.load("en_core_web_sm")
#scorer = Scorer(nlp)
#scores = scorer.score(examples)
#NAME	DESCRIPTION
#examples	The Example objects holding both the predictions and the correct gold-standard annotations.
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
def evaluate_the_model_in_batches(nlp, TEST_DATA, batch_size=27):
    total_scores = {}
    leaves_scores = {}

    for i in range(0, len(TEST_DATA), batch_size):
        batch = TEST_DATA[i:i + batch_size]
        examples = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in batch]
        try:
            batch_scores = nlp.evaluate(examples).scores
        except:
            batch_scores = nlp.evaluate(examples)
            
        for key, value in batch_scores.items():
            if key not in leaves_scores:
                leaves_scores[key] = []
            leaves_scores[key].append(value)

    for key, scores in leaves_scores.items():
        try:
            # Removing None and ensuring the list isn't empty
            valid_scores = [score for score in scores if score is not None]
            total_scores[key] = sum(valid_scores) / len(valid_scores) if valid_scores else 0  # Default to 0 if no valid scores
        except Exception as e:
            print(f"Error processing scores for {key}: {e}")
            total_scores[key] = 0  # or some error indicator

    return total_scores

def main_evaluation_function(model_path, TEST_DATA):
    nlp = spacy.load(model_path)
    scores = evaluate_the_model(nlp, TEST_DATA)
    print(scores)


def evaluation_profiler(function, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.runcall(function, *args, **kwargs)
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(10)

def evaluate_the_model(nlp, TEST_DATA):
    examples = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in TEST_DATA]
    return nlp.evaluate(examples).scores

def save_spacy_training_data(output_dir, training_data, filename, model):
    nlp = spacy.load(model)
    os.makedirs(output_dir, exist_ok=True)
    doc_bin = DocBin()
    for text, annotations in training_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        doc_bin.add(example.reference)
    doc_bin.to_disk(os.path.join(output_dir, filename + ".spacy"))

def upload_spacy_training_data(input_dir, filename, nlp):
    file_path = os.path.join(input_dir, filename + ".spacy")
    doc_bin = DocBin().from_disk(file_path)
    docs = list(doc_bin.get_docs(nlp.vocab))
    return [(doc.text, {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}) for doc in docs]

def save_spacy_training_data_to_json(output_dir, training_data, filename):
    file_path = os.path.join(output_dir, filename + ".json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=4)

def upload_spacy_training_data_from_json(input_dir, filename):
    file_path = os.path.join(input_dir, filename + ".json")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

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

import pandas as pd
import re

def dataset_normalized(path_data, col_name):
    # Validate parameters
    if not isinstance(path_data, str):
        raise ValueError("path_data must be a string representing the file path.")
    if not isinstance(col_name, str):
        raise ValueError("col_name must be a string representing the column name.")

    # Attempt to load the dataset
    try:
        if path_data.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(path_data)
        elif path_data.endswith('.csv'):
            df = pd.read_csv(path_data)
        else:
            raise ValueError("Unsupported file format. Only Excel and CSV files are supported.")
        
        if col_name not in df.columns:
            raise ValueError(f"Column {col_name} not found in the data.")
        
        # Normalize data
        df[col_name] = df[col_name].apply(normalize_formula)
        return df
    except Exception as e:
        raise IOError(f"An error occurred while loading the data: {e}")
 
# Function to get the position of each token
def get_pos_(data,col_name,nlp):
  dd=[]
  gg=[]

  for tok in data[col_name]:

          for ent in nlp(str(list(str(tok).split()))):
              # checking text between punct
              dd.append({ent.text:ent.pos_})
              gg.append({ent.pos_:ent.text})
  return dd,gg

# Function to get patterns based on the tokenization
def get_patterns(data,col_name,nlp):
     dt,dp=get_pos_(data,col_name,nlp)

     pos_=[list(item.keys())[0] for item in dp]
     pos_=list(set(pos_))
     #print(dt)
     #print(col_name,":",pos_)
     patterns={}
     patterns_head=[]
     for key in pos_:
         patterns.update({key:list(set([d[key] for d in dp if  key==list(d.keys())[0] and d[key] not in data["stopwords"]]))})
     return patterns

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
            dt_e["entities"].append((int(ent.start_char), int(ent.end_char), ent.label_))
        dt.append((text, dt_e))
        dd.append(dp)
    return dd, dt

 
# Function to create and return an EntityRuler with specified patterns
def create_ruler(rules,nlp=None,ner_base_model=None):
       if ner_base_model==None:             
            nlp=spacy.load("en_core_web_sm")
       else:
            nlp=spacy.load(ner_base_model) 
       ruler = EntityRuler(nlp, overwrite_ents=True)
       if isinstance(rules,list)==True:
               formatted_patterns=rules
       elif isinstance(rules,dict)==True and isinstance(*rules.values(),list)==True:
               formatted_patterns = [{"label":label, "pattern": pattern} for (label,patterns) in rules.items() for  pattern in patterns]
       elif isinstance(rules,dict)==True and isinstance(*rules.values(),list)==False:
               formatted_patterns=[{"label":label, "pattern":pattern} for (label,pattern) in rules.items()]
       else:
           pass
       ruler.add_patterns(formatted_patterns)
       return ruler


# Function to transform data 
def preproc_ent(path_data, stopwords, train=True):
    # Validate parameters

    if not isinstance(str(path_data), str):
        raise ValueError("path_data must be a string representing the file path.")
    # Load data
    file_data=str(path_data).split('/')[-1]
    try:
        if file_data.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(path_data)
        elif file_data.endswith('.csv'):
            df = pd.read_csv(path_data)
        else:
            raise ValueError("Unsupported file format. Only Excel and CSV files are supported.")
    except Exception as e:
        raise IOError(f"An error occurred while loading the data: {e}")

    df[df.columns[1]] = df[df.columns[1]].apply(lambda x: normalize_formula(x))
    
    if train:          
        out_d = {"stopwords": stopwords[0], "text": [], "vocab": []}
        out_f = {"stopwords": stopwords[1], "text": [], "vocab": []}
        
        # Tokenize data
        dg_tok = df.apply(lambda x: [wordpunct_tokenize(y) for y in x])
        for col in df.columns[:2]:  # Assumes the relevant columns are the first two
            out = out_d if col == df.columns[0] else out_f
            out['text'] = [sentence for sentence in df[col]]
            out['vocab'] = list(set(word for sentence in dg_tok[col] for word in sentence if word not in out['stopwords']))
        
        return out_d, out_f
    else:
        return df

# Functions to tokenize "FORMULAS" with symbols and get the operators

def tok_formulas(path_data, not_oper):
    # Validate input parameters
    if not isinstance(str(path_data), str):
        raise ValueError("path_data must be a string representing the file path.")
    if not isinstance(not_oper, list):
        raise ValueError("not_oper must be a list of strings representing non-operator tokens.")

    # Check the file format and read the file accordingly
    file_data=str(path_data).split('/')[-1]
    if file_data.endswith('.xlsx') or file_data.endswith('.xls'):
        try:
            df = pd.read_excel(path_data)
        except Exception as e:
            raise IOError(f"Failed to load Excel file: {e}")
    elif path_data.endswith('.csv'):
        try:
            df = pd.read_csv(path_data)
        except Exception as e:
            raise IOError(f"Failed to load CSV file: {e}")
    else:
        raise ValueError("Unsupported file format. Only Excel and CSV files are supported.")
    
    # Define regex pattern for splitting
    patterns = r'\(| = | >= | > | \[ | \) | \{ | \]'
    tr_0 = []

    # Process each row in the specified column
    for tr in df[df.columns[1]]:
        try:
            items = re.split(patterns, tr)
            if len(items) >= 2:
                it0, it1 = items[0:2]
            else:
                it0 = items[0]

            it01 = it0.split()
            if len(it01) == 1:
                iten = it01[0]
            elif len(it01) == 2:
                iten = it01[0] + ' ' + it01[1]
            else:
                iten = ''
                for item in it01:
                    if item not in tr_0 and item not in not_oper:
                        iten += item + ' '
                iten = iten.rstrip()

            if iten not in tr_0 and iten not in not_oper:
                tr_0.append(iten)

        except Exception as e:
            raise ValueError(f"Error processing formula '{tr}': {e}")
    
    return tr_0
