import os
import spacy
import subprocess
from importlib import resources

class CustomNerComponent:
    def __init__(self, domain,sub_domain, type, python_version, path_entity_name=None, ner_base_model=None):
        self.domain = domain
        self.sub_domain=sub_domain
        self.type = type
        self.entity_name = path_entity_name
        self.ner_base_model = ner_base_model if ner_base_model else "en_core_web_sm"
        self.py_version = python_version

    def get_entity_ruler(self):
        nlp = spacy.load(self.ner_base_model)
        
        # Using resources to safely access package resources
        try:
            if self.domain == "queries":
                path_dir = resources.files(f"hypatiax.custom_ner.queries.{self.sub_donain}.components")
                
                if self.type == 'desc':
                    path_entity = path_dir / f"ruler_{self.sub_domain}_desc.py"
                elif self.type == "formulas":
                    path_entity = path_dir / f"ruler_{self.sub_domain}_formulas.py"
                elif self.type == "both":
                    path_entity = path_dir / f"ruler_{self.sub_domain}.py"
                else:
                    raise ValueError(f"Invalid type specified for domain {sub_domain}")
            
            elif self.domain == "geometry":
                # Assuming similar path structures and script naming conventions for geometry
                path_dir = resources.files("hypatiax.custom_ner.geometry.components")
                path_entity = path_dir / f"ruler_{self.domain}_{self.type}.py"
            
            else:
                raise ValueError(f"No handling defined for domain: {self.domain}")
            
            # Run the Python script for the specified entity ruler
            result = subprocess.run([self.py_version, str(path_entity)], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Error running script {path_entity}: {result.stderr}")
            return result.stdout

        except Exception as e:
            print(f"Error: {e}")

