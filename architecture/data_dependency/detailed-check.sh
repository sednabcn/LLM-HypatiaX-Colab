# 2. Detailed Check (Python)
cd ~/Downloads/LLM-HypatiaX-OLD

# Activate your environment
source py312/bin/activate

# Run comprehensive check
python check_data_and_models.py

# Or specify project path
python check_data_and_models.py /path/to/project

# View the JSON report
cat data_model_check_report.json | jq
