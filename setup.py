import tomllib
import setuptools_scm, platform
from setuptools import setup, find_packages

def read_pyproject(file_path):
    with open(file_path, 'rb') as file:
        data = tomllib.load(file)
    return data

# Determine architecture
architecture = platform.architecture()[0]

# Read dependencies from pyproject.toml
config = read_pyproject('pyproject.toml')
requirements = config['build-system']['requires']

# Conditional requirements based on architecture
if architecture == '64bit':
    requirements.append('transformers==4.40.0','spacy-transformers==1.3.4')
else:
    requirements.append('')  # Alternative package for 32-bit systems
    
def readme():
    with open('README.rst') as f:
        return f.read()

setup(
      name='hypatiax',
      use_scm_version={"fallback_version": "0.1.0",
                       "write_to": "_version.py"},
      setup_requires=['setuptools_scm'],
      description="LLM-HypatiaX: AI-Driven Formula Discovery with LLM",
      long_description=readme(),
      long_description_content_type='text/markdown',
      python_requires='>=3.6, <4.0',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      url='http://github.com/sednabcn/LLM-HypatiaX',
      author="Ruperto Pedro Bonet Chaple",
      author_email="ruperto.bonet@modelphysmat.com",
      license="MIT",
      packages=find_packages(where="."),  # Search in the root directory
      package_dir={'': '.'},
      install_requires=requirements,
      entry_points = {
        'console_scripts': [
            'pattern_gen=hypatiax.scripts_.script_custom_patterns:pattern_gen',
            'get_ner_component=hypatiax.scripts_.script_custom_ner:get_ner_component',
            'get_ner_entity=hypatiax.scripts_.script_custom_entities:get_ner_entity',
            'make_combined_data=hypatiax.scripts_.script_combined_data:make_combined_data'
        ]},

      package_data={"": ["*.xlsx","*.json","*.spacy","*.cfg","*.txt","*.bin"],
         "data_spacy.queries.tableau.ner_tableau_desc":["*"],
         "data_spacy.queries.tableau.ner_tableau_formulas":["*"],
         "data_spacy.queries.tableau.ner_tableau":["*"],
         "data_spacy.queries.tableau.ner_tableau_desc.lemmatizer.lookups":["*"],
         "data_spacy.queries.tableau.ner_tableau_formulas.parser":["*"],
         "data_spacy.queries.tableau.ner_tableau_formulas.vocab":["*"],
         "data_spacy.queries.tableau.ner_tableau_formulas.tagger":["*"],
         "data_spacy.queries.tableau.ner_tableau_formulas.tok2vec":["*"],
         "data_spacy.queries.tableau.ner_tableau.lemmatizer.lookups":["*"],
         "data_spacy.queries.tableau.ner_tableau.parser":["*"],
         "data_spacy.queries.tableau.ner_tableau.vocab":["*"],
         "data_spacy.queries.tableau.ner_tableau.tagger":["*"],
         "data_spacy.queries.tableau.ner_tableau.tok2vec":["*"],
         "data_spacy.queries.tableau.ner_versions":["*"],
         "data_spacy.queries.tableau.testing_spacy":["*"],
         "data_spacy.queries.tableau.training_spacy":["*"],
         "data_spacy.queries.tableau.vocab":["*"],
         "datasets.queries":["*"],
         "datasets.queries.tableau":["*"],
         "datasets.queries.data":["*"],
         "datasets.queries.tableau.training":["*"],
         "datasets.queries.tableau.validation":["*"],
         "datasets.queries.tableau.testing":["*"],
         "datasets.queries.tableau.testing_spacy":["*"],
         "datasets.queries.tableau.training_spacy":["*"]
         
      },
      exclude_package_data={'hypatiax':['__pycache__']},
      
      test_suite='pytest.collector',
      tests_require=['pytest'],
      scripts=[
        "hypatiax/scripts_/script_custom_entities.py",
        "hypatiax/scripts_/script_custom_ner.py",
        "hypatiax/scripts_/script_custom_patterns.py",
        "hypatiax/scripts_/script_combined_data.py"],
      
      include_package_data=True,
      zip_safe=False
)

