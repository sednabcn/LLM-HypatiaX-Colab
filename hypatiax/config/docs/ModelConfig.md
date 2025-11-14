──(py312)(agagora㉿localhost)-[~/Downloads/LLM-HypatiaX-OLD/hypatiax/config]
└─$ python -c "from hypatiax.config import config; config.print_all()"                                               
======================================================================
HypatiaX Configuration
======================================================================
Environment: local
Debug Mode:  False

======================================================================
Path Configuration
======================================================================
Environment:      local
Root:             /home/agagora/Downloads/LLM-HypatiaX-OLD
HypatiaX:         /home/agagora/Downloads/LLM-HypatiaX-OLD/hypatiax
Datasets:         /home/agagora/Downloads/LLM-HypatiaX-OLD/hypatiax/datasets
Data Spacy:       /home/agagora/Downloads/LLM-HypatiaX-OLD/hypatiax/data_spacy
Custom NER:       /home/agagora/Downloads/LLM-HypatiaX-OLD/hypatiax/custom_ner
Outputs:          /home/agagora/Downloads/LLM-HypatiaX-OLD/outputs

Dataset Subdirectories:
  Training:       /home/agagora/Downloads/LLM-HypatiaX-OLD/hypatiax/datasets/queries/tableau/training
  Testing:        /home/agagora/Downloads/LLM-HypatiaX-OLD/hypatiax/datasets/queries/tableau/testing
  Training Spacy: /home/agagora/Downloads/LLM-HypatiaX-OLD/hypatiax/datasets/queries/tableau/training_spacy
  Testing Spacy:  /home/agagora/Downloads/LLM-HypatiaX-OLD/hypatiax/datasets/queries/tableau/testing_spacy

Model Directories:
  Models:         /home/agagora/Downloads/LLM-HypatiaX-OLD/hypatiax/data_spacy/queries/tableau
  Custom Rules:   /home/agagora/Downloads/LLM-HypatiaX-OLD/hypatiax/custom_ner/queries/tableau/rules
======================================================================

Model Configurations Available:
  - ModelConfig.training_desc()
  - ModelConfig.training_formulas()
  - ModelConfig.training_combined()
======================================================================

🎯 Immediate Next Steps
1. Replace Hard-Coded Paths (Most Important!)
Go through your existing scripts and replace hard-coded paths:
Before:
pythondata_path = 'hypatiax/datasets/queries/tableau/training/formulas_nor.xlsx'
output_path = 'outputs/models/ner_desc'
After:
pythonfrom hypatiax.config import paths

data_path = paths.training_data / 'formulas_nor.xlsx'
output_path = paths.get_output_path('models', 'ner_desc')
2. Update Your Training Scripts
Replace any config dictionaries:
Before:
pythonconfig = {'niter': 100, 'batchsize': 8, 'drop': 0.5}
After:
pythonfrom hypatiax.config import ModelConfig

config = ModelConfig.training_desc(niter=100, batchsize=8)
3. Verify It Works
bash# Test that imports work from anywhere
cd ~/Downloads/LLM-HypatiaX-OLD
python -c "from hypatiax.config import paths; print(paths.training_data)"

# Run a script that uses the config
python hypatiax/your_training_script.py

🔍 Quick Audit
Find all hard-coded paths to replace:
bashcd ~/Downloads/LLM-HypatiaX-OLD
grep -r "hypatiax/datasets" --include="*.py"
grep -r "outputs/" --include="*.py"

from hypatiax.config import ModelConfig

config = ModelConfig.training_desc(niter=100, batchsize=8)