# Navigate to experiments directory

cd experiments

# Register your first experiment

python experiment_tracker.py register \
  --name "NER Baseline Test" \
  --tech ner \
  --description "Test existing NER system performance" \
  --author "Your Name" \
  --tags baseline test

# List all experiments

python experiment_tracker.py list

# Generate report

python experiment_tracker.py report

# Benefits of this system

This system gives you:

✅ Centralized experiment tracking
✅ Automatic timestamping
✅ Metrics tracking
✅ Status management
✅ Report generation
✅ Easy CLI interface
✅ Organized results storage
