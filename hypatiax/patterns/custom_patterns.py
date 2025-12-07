import os
import subprocess
from importlib import resources

import spacy


class CustomPatterns:
    def __init__(self, domain, sub_domain, query_type):
        self.domain = domain
        self.sub_domain = sub_domain
        self.query_type = query_type
        self.query_types = ["desc", "formulas", "both"]
        self.nlp = spacy.load("en_core_web_sm")  # Load the spaCy model here or specify a different model

    def call_my_script(self, script_path, query_type):
        # Using subprocess to call the script externally
        command = ["python", script_path, query_type]
        subprocess.run(command, check=True)

    def get_custom_patterns(self, option):
        valid_options = ["all", "default"]
        if option not in valid_options:
            logging.error(f"Invalid option '{option}'. Valid options are {valid_options}")

        try:
            if self.domain == "queries" and sub_domain == "tableau":
                path_dir = resources.files("hypatiax.patterns.queries.tableau")
            elif self.domain == "geometry":
                path_dir = resources.files("hypatiax.custom_ner.geometry")
            else:
                raise ValueError(f"No handling defined for domain: {self.sub_domain}")

            # Construct the path to the script
            path_script = path_dir / f"test_create_ruler_{self.sub_domain}.py"

            # Check if the script exists before attempting to run it
            if not os.path.exists(path_script):
                raise FileNotFoundError(f"Script not found: {path_script}")

            # Execute the script based on the specified option
            if option == "all":
                for query_type in self.query_types:
                    self.call_my_script(str(path_script), query_type)
            elif option == "default":
                self.call_my_script(str(path_script), self.query_type)
            else:
                pass
        except Exception as e:
            print(f"Error occurred: {e}")
