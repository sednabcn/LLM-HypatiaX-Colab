# HypatiaX Experiments

This directory contains all experiments across different technologies.

## Directory Structure

```
experiments/
├── ner/          # Named Entity Recognition experiments
├── transformers/ # BERT/T5 transformer experiments
├── llm/          # Large Language Model experiments
├── agents/       # AI Agent system experiments
└── hybrid/       # Multi-technology ensemble experiments
```

## Usage

### Register a New Experiment

```bash
python experiment_tracker.py register \
  --name "BERT Fine-tuning v1" \
  --tech transformers \
  --description "Fine-tune BERT on formula mapping" \
  --author "Your Name" \
  --tags bert fine-tuning baseline
```

### List Experiments

```bash
# List all experiments
python experiment_tracker.py list

# List by technology
python experiment_tracker.py list --tech ner

# List by status
python experiment_tracker.py list --status completed
```

### Update Experiment

```bash
python experiment_tracker.py update \
  --id transformers_20250112_143022 \
  --status completed \
  --notes "Achieved 92% accuracy"
```

### Generate Report

```bash
python experiment_tracker.py report
```

## Experiment Workflow

1. **Register** experiment before starting
2. **Update** status to "running" when you start
3. Save **results** in the designated results/ directory
4. **Update** with metrics and status when complete
5. **Generate report** to document progress

## Example Experiment Script

```python
from experiments.experiment_tracker import ExperimentTracker, TechnologyType, ExperimentStatus

# Initialize tracker
tracker = ExperimentTracker()

# Register experiment
exp_id = tracker.register_experiment(
    name="LLM Prompt Engineering v1",
    technology=TechnologyType.LLM,
    description="Test different prompt strategies",
    author="Your Name",
    config={"model": "gpt-4", "temperature": 0.0},
    tags=["prompt-engineering", "gpt-4"]
)

# Start experiment
tracker.update_experiment(exp_id, status=ExperimentStatus.RUNNING)

# Run your experiment
# ... your code ...

# Update with results
tracker.update_experiment(
    exp_id,
    status=ExperimentStatus.COMPLETED,
    metrics={
        "accuracy": 0.95,
        "avg_time": 1.2,
        "cost": 0.05
    },
    notes="Few-shot prompting worked best"
)
```

## Best Practices

1. Always register experiments before running
2. Use descriptive names and tags
3. Save all results in the designated directory
4. Update metrics as soon as available
5. Document important findings in notes
6. Generate reports regularly
