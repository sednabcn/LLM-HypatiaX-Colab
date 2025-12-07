# HypatiaX Configuration System - Usage Guide

## 📦 Installation

After creating the config files, import them in your code:

```python
from hypatiax.config import config, paths, ModelConfig, EntityLabels
```

---

## 🎯 Basic Usage

### 1. Access Paths

```python
from hypatiax.config import paths

# Get standard paths
datasets_dir = paths.datasets
models_dir = paths.models
output_dir = paths.outputs

# Build custom output path
model_file = paths.get_output_path('models', 'ner_desc', 'model.pkl')
# Result: outputs/models/ner_desc/model.pkl

# Get dataset with standard structure
data_file = paths.get_dataset_path(
    domain='queries',
    sub_domain='tableau',
    action='training',
    filename='formulas_nor.xlsx'
)

# Print all paths
paths.print_paths()
```

### 2. Get Training Configurations

```python
from hypatiax.config import ModelConfig

# Quick training config (for testing)
config = ModelConfig.quick_test()

# Description training
config = ModelConfig.training_desc(niter=50, batchsize=16)

# Formula training
config = ModelConfig.training_formulas(niter=100, batchsize=8)

# Combined training
config = ModelConfig.training_combined(niter=150, sizefile='md')

# Access training parameters
print(config.training.niter)         # 100
print(config.training.batchsize)     # 8
print(config.data.filename)          # 'formulas_nor.xlsx'
print(config.data.dtype)             # 'desc'

# Convert to dictionary (for passing to functions)
config_dict = config.to_dict()
```

### 3. Use Entity Labels

```python
from hypatiax.config import EntityLabels

# Get labels for specific type
desc_labels = EntityLabels.TABLEAU_DESC
formula_labels = EntityLabels.TABLEAU_FORMULAS
all_labels = EntityLabels.get_all_labels()

# Get labels by name
labels = EntityLabels.get_labels_for('desc')
# ['FUNCTION', 'FIELD', 'OPERATOR', 'VALUE', 'AGGREGATION']
```

### 4. Print All Configuration

```python
from hypatiax.config import config

# Print everything
config.print_all()

# Check environment
print(config.environment)  # 'local', 'colab', 'github', etc.

# Save config to file
config.save_to_file('my_config.json')
```

---

## 🔧 Advanced Usage

### Custom Training Configuration

```python
from hypatiax.config import TrainingConfig, DataConfig, ModelConfig

# Create custom training config
training = TrainingConfig(
    niter=200,
    batchsize=16,
    drop=0.3,
    patience=10,
    learn_rate=0.0005,
    output_model_name='my_custom_model'
)

# Create custom data config
data = DataConfig(
    filename='my_data.xlsx',
    dtype='combined',
    test_size=0.25,
    sizefile='lg'
)

# Combine them
model_config = ModelConfig(training=training, data=data)

# Or update existing config
config = ModelConfig.training_desc()
config.training.update(niter=150, batchsize=12)
config.data.update(sizefile='md', test_size=0.3)
```

### Using Presets

```python
from hypatiax.config import TrainingConfig

# Quick training (for testing)
quick_config = TrainingConfig.quick_train()
# niter=10, batchsize=4, patience=3

# Production training (best quality)
prod_config = TrainingConfig.production()
# niter=200, batchsize=16, patience=10
```

### File Format Checking

```python
from hypatiax.config import FileFormats

# Check if file is supported
if FileFormats.is_supported('data.xlsx'):
    file_type = FileFormats.get_type('data.xlsx')
    print(file_type)  # 'excel'
```

---

## 📝 Migration Guide

### Before (Old Way)

```python
# Hard-coded paths everywhere
data_path = 'hypatiax/datasets/queries/tableau/training/formulas_nor.xlsx'
model_path = 'hypatiax/data_spacy/queries/tableau/ner_tableau_desc'

# Hard-coded config dictionaries
config = {
    'modules': 'datasets',
    'domain': 'queries',
    'sub_domain': 'tableau',
    'dtype': 'desc',
    'sizefile': 'sm',
    'niter': 100,
    'batchsize': 8,
    'drop': 0.5
}
```

### After (New Way)

```python
from hypatiax.config import paths, ModelConfig

# Use path manager
data_path = paths.get_dataset_path(
    domain='queries',
    sub_domain='tableau',
    action='training',
    filename='formulas_nor.xlsx'
)

model_path = paths.get_model_path(
    domain='queries',
    sub_domain='tableau',
    model_name='ner_tableau_desc'
)

# Use config objects
config = ModelConfig.training_desc(niter=100, batchsize=8)
config_dict = config.to_dict()
```

---

## 🎨 Real-World Examples

### Example 1: Training Script

```python
from hypatiax.config import paths, ModelConfig

def train_model(model_type='desc'):
    # Get configuration
    config = ModelConfig.training_desc() if model_type == 'desc' else ModelConfig.training_formulas()

    # Get paths
    data_file = paths.get_dataset_path(
        action='training',
        filename=config.data.filename
    )

    output_dir = paths.get_output_path('models', config.training.output_model_name)

    # Your training code here
    print(f"Training with config: {config.to_dict()}")
    print(f"Data from: {data_file}")
    print(f"Saving to: {output_dir}")

# Use it
train_model('desc')
```

### Example 2: Data Processing

```python
from hypatiax.config import paths, EntityLabels, DEFAULT_STOPWORDS

def process_data(dtype='desc'):
    # Get entity labels
    labels = EntityLabels.get_labels_for(dtype)

    # Get data path
    data_path = paths.get_dataset_path(
        action='training',
        filename='formulas_nor.xlsx'
    )

    # Load and process
    import pandas as pd
    df = pd.read_excel(data_path)

    # Filter stopwords
    filtered = [word for word in df['text'] if word not in DEFAULT_STOPWORDS]

    return filtered, labels

# Use it
data, labels = process_data('desc')
```

### Example 3: Model Evaluation

```python
from hypatiax.config import paths, EvaluationConfig

def evaluate_model(model_name):
    # Get evaluation config
    eval_config = EvaluationConfig(batch_size=27, save_results=True)

    # Get model path
    model_path = paths.get_model_path(model_name=model_name)

    # Get output path for results
    results_file = paths.get_output_path(
        'evaluation',
        f'{model_name}_results.json'
    )

    # Your evaluation code
    print(f"Evaluating: {model_path}")
    print(f"Saving results to: {results_file}")

# Use it
evaluate_model('ner_tableau_desc')
```

---

## ⚙️ Environment Variables

You can override paths using environment variables:

```bash
# Set custom project root
export HYPATIAX_ROOT=/path/to/project

# Enable debug mode
export HYPATIAX_DEBUG=True
```

Then in Python:

```python
from hypatiax.config import config

print(config.environment)  # Shows detected environment
print(config.debug_mode)   # True if HYPATIAX_DEBUG=True
```

---

## ✅ Benefits of New System

| Old Way | New Way |
|---------|---------|
| âŒ Hard-coded paths everywhere | âœ… Centralized path management |
| âŒ Config dictionaries scattered | âœ… Type-safe config objects |
| âŒ No validation | âœ… Automatic validation |
| âŒ Hard to maintain | âœ… Easy to update |
| âŒ Environment-specific code | âœ… Auto-detects environment |
| âŒ No IDE autocomplete | âœ… Full IDE support |

---

## 🚀 Quick Reference

```python
# Import everything you need
from hypatiax.config import (
    config,              # Main config instance
    paths,               # Path manager
    ModelConfig,         # Model configurations
    TrainingConfig,      # Training settings
    DataConfig,          # Data settings
    EntityLabels,        # NER labels
    FileFormats,         # File format utilities
    DEFAULT_STOPWORDS    # Default stopwords list
)

# Common operations
data_path = paths.get_dataset_path('queries', 'tableau', 'training', 'file.xlsx')
model_config = ModelConfig.training_desc(niter=100)
labels = EntityLabels.TABLEAU_DESC
config.print_all()
```
