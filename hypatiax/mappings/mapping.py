# /usr/bin/python3


class map_description_to_formula:
    def __init__(self, description, rules={}, ner_entity=None):
        self.description = description
        self.mapping_rules = rules
        self.ner_entity = ner_entity

    def extract_column_name(description):
        # A simple regex pattern to find "of [Column Name]"
        # This pattern might need to be adjusted based on actual descriptions
        match = re.search(r"of (\w+ \w+)", description)
        if match:
            return match.group(1)  # Return the column name
        return None

    def map_vocab_to_vocab(self):
        pass

    def map_sentence_to_sentence(self):

        # Normalize the description
        normalized_description = description.lower()

        # Mapping rules
        mapping_rules = {
            "sum of sales by year": "SUM(Sales) GROUP BY Year",
            "average cost per item": "AVG(Cost) / COUNT(Item)",
        }

        # Apply rules
        for pattern, formula in mapping_rules.items():
            if pattern in normalized_description:
                return formula

            # Fallback if no rule matched
            return "Formula not recognized. Please provide more details."

        # Example usage
        description = "Sum of sales by year"
        print(map_description_to_formula(description))

    def map_vocab_to_vocab_regex(self):

        import re  # Regular expressions for pattern matching

        # def generate_tableau_formula(description):
        vocab_map = {
            "total": "SUM",
            "average": "AVG",
            "median": "MEDIAN",
            "number of entries": "COUNT",
            "unique count": "COUNT DISTINCT",
        }

        column_name = extract_column_name(description)
        if column_name is None:
            return "Column name not found"

        for key, value in vocab_map.items():
            if key in description.lower():
                return f"{value}({column_name})"

        return "Formula not found"

    # Example usage
    description = "Average of Petal Length across all flowers"
    # print(generate_tableau_formula(description))

    def __call__(self, description, option):
        """
        "vocab": use nlp to map desc_vocab to formula_vocab
        "sentence": map_sentence_to_formula_sentence
        "regex" : use regex to map desc_vocab to formula_vocab
        "logistic regression": use external training mappaing
        "core-trf": pre-trained transformer en-core-web-trf
        "core-sm": pre-trained en-core-web-sm
        "Bert" : Bert-transformer
        "Bert_ner": Bert-Transformer with ner_entities
        "Spacy_c200a": Combined_multitask_models
        "Spacy_200b"
        "Spacy_c400"
        "Description_Tableau_data"
        "Formulas Tableau_data"
        """
        # Normalize the description
        normalized_description = description.lower()

        self.mapping_rules = self.map_vocab_to_vocab()

        self.mapping_rules = self.map_sentence_to_sentence()
        # Apply rules
        for pattern, formula in self.mapping_rules.items():
            if pattern in normalized_description:
                return formula
        # Fallback if no rule matched
        return "Formula not recognized. Please provide more details."
