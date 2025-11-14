# HypatiaX Demo

Interactive demonstrations of HypatiaX Named Entity Recognition capabilities for Tableau query processing.

## 📁 Directory Structure

```
demo/
├── README.md                       # This file
├── demo_interactive.py             # Command-line interactive demo
├── demo_examples.py                # Curated example queries
├── demo_web_app.py                 # Web-based demo (Flask)
├── demo_quick_start.py             # Quick 5-minute demo
└── utils/
    └── demo_helpers.py             # Helper functions
```

## 🚀 Quick Start

### 1. Command-Line Demo (Recommended)

The easiest way to see HypatiaX in action:

```bash
python demo/demo_interactive.py
```

This launches an interactive menu with multiple demo options:
- **Description NER Demo** - Extract entities from natural language
- **Formula NER Demo** - Parse Tableau formula syntax
- **Combined NER Demo** - Process description + formula pairs
- **Model Comparison** - Compare all three model types
- **Interactive Mode** - Type your own queries

### 2. Web Demo (Visual)

For a visual, browser-based experience:

```bash
pip install flask
python demo/demo_web_app.py
```

Then open http://localhost:5000 in your browser.

## 📋 Demo Options

### Interactive Demo

```python
from demo.demo_interactive import HypatiaXDemo

# Initialize with model type
demo = HypatiaXDemo(model_type='desc')

# Process a single query
result = demo.run_example("calculate the sum of sales by region")

# Or run multiple examples
examples = [
    "calculate sum of sales",
    "find average profit",
    "show total revenue"
]
results = demo.run_examples(examples)

# Interactive mode
demo.interactive_mode()
```

### Programmatic Usage

```python
from demo.demo_interactive import HypatiaXDemo

# Create demo instance
demo = HypatiaXDemo(model_type='both')

# Process text
result = demo.process_text("calculate the sum of sales : SUM([Sales])")

# Access extracted entities
for entity in result['entities']:
    print(f"{entity['text']} → {entity['label']}")
```

## 🎯 Demo Scenarios

### 1. Description NER

Extract entities from natural language queries:

```python
demo = HypatiaXDemo(model_type='desc')

examples = [
    "calculate the sum of sales by region",
    "find the average profit per category",
    "show me total revenue for each date"
]

demo.run_examples(examples)
```

**Expected Output:**
```
Entity: "calculate" → OPERATION
Entity: "sum" → FUNCTION
Entity: "sales" → FIELD
Entity: "region" → DIMENSION
```

### 2. Formula NER

Parse Tableau formula syntax:

```python
demo = HypatiaXDemo(model_type='formulas')

examples = [
    "SUM([Sales])",
    "AVG([Profit])",
    "IF [Sales] > 1000 THEN 'High' ELSE 'Low'"
]

demo.run_examples(examples)
```

**Expected Output:**
```
Entity: "SUM" → FUNCTION
Entity: "[Sales]" → FIELD
```

### 3. Combined NER

Process description + formula pairs:

```python
demo = HypatiaXDemo(model_type='both')

examples = [
    "calculate sum of sales : SUM([Sales])",
    "find average profit : AVG([Profit])"
]

demo.run_examples(examples)
```

### 4. Model Comparison

Compare how different models process the same text:

```python
from demo.demo_interactive import run_comparison_demo

run_comparison_demo()
```

## 📚 Example Categories

Use curated examples from `demo_examples.py`:

```python
from demo.demo_examples import get_examples, get_all_categories

# See all available categories
categories = get_all_categories()

# Get specific examples
basic_examples = get_examples('description', 'basic_calculations')
formula_examples = get_examples('formula', 'basic_aggregations')
combined_examples = get_examples('combined', 'simple_mappings')
```

**Available Categories:**

**Description Examples:**
- `basic_calculations` - Simple aggregations
- `aggregations_with_dimensions` - Group by operations
- `time_based` - Time-series queries
- `complex_queries` - Advanced queries

**Formula Examples:**
- `basic_aggregations` - SUM, AVG, COUNT, etc.
- `calculated_fields` - Complex calculations
- `conditional_logic` - IF/CASE statements
- `string_operations` - Text functions
- `date_operations` - Date functions

**Combined Examples:**
- `simple_mappings` - Basic description → formula
- `aggregations_with_dimensions` - Group by mappings
- `calculated_metrics` - Complex metric calculations

## 🌐 Web Demo

The web demo provides a visual interface with:

- **Model Selection** - Choose between desc/formulas/both
- **Real-time Processing** - See entities as you type
- **Example Buttons** - Quick-load sample queries
- **Visual Entity Display** - Color-coded entity labels
- **Confidence Scores** - See model confidence

**Running the Web Demo:**

```bash
# Install Flask if needed
pip install flask

# Start server
python demo/demo_web_app.py

# Open browser
# http://localhost:5000
```

## 🔧 Demo Modes

The demo can run in two modes:

### 1. Mock Mode (No Models Required)

If trained models aren't available, the demo uses pattern matching to simulate entity extraction. Great for:
- Testing the demo infrastructure
- Showcasing the UI/UX
- Demonstrations without model files

### 2. Full Mode (With Trained Models)

When models are available, uses actual spaCy models for entity extraction:

```python
demo = HypatiaXDemo(model_type='desc')
# Automatically loads: hypatiax/models/queries/tableau/ner_tableau_desc
```

## 📊 Understanding Results

Each result contains:

```python
{
    'text': 'calculate the sum of sales',
    'entities': [
        {
            'text': 'calculate',
            'label': 'OPERATION',
            'start': 0,
            'end': 9
        },
        {
            'text': 'sum',
            'label': 'FUNCTION',
            'start': 14,
            'end': 17
        }
    ],
    'model_type': 'desc',
    'entity_count': 2
}
```

## 🎓 Educational Demos

The demo also includes educational examples comparing different NER strategies:

```bash
# Sequential pipeline approach
python demo/sequential_pipeline_demo.py

# Joint training approach
python demo/joint_training_demo.py
```

These demonstrate:
- How entity extraction pipelines work
- Error propagation in sequential vs joint models
- Training data requirements
- Accuracy metrics

## 💡 Tips

1. **Start Simple** - Begin with basic examples before trying complex queries
2. **Try Different Models** - See how 'desc', 'formulas', and 'both' differ
3. **Check Confidence** - Lower confidence scores may indicate edge cases
4. **Use Examples** - Load pre-made examples to understand capabilities
5. **Interactive Mode** - Best for exploring and experimenting

## 🐛 Troubleshooting

**"Could not load model" warning:**
- Demo runs in mock mode automatically
- Install models or use mock mode for testing

**Web demo not starting:**
```bash
pip install flask
```

**Port already in use:**
```bash
# Use a different port
python demo/demo_web_app.py --port 5001
```

## 📈 Performance

Demo performance varies by mode:
- **Mock Mode**: Instant (pattern matching)
- **Full Mode**: ~10-50ms per query (spaCy model inference)

## 🔗 Integration

Use the demo components in your own applications:

```python
from demo.demo_interactive import HypatiaXDemo
from demo.demo_examples import get_examples

# Create your custom demo
class MyCustomDemo:
    def __init__(self):
        self.demo = HypatiaXDemo(model_type='both')
    
    def process_batch(self, queries):
        return [self.demo.process_text(q) for q in queries]
```

## 📝 Next Steps

After exploring the demo:

1. **Review Documentation** - See `/docs` for detailed guides
2. **Check Examples** - Look at `/examples` for usage patterns
3. **Run Tests** - See `/tests` for validation scripts
4. **Train Models** - Use `/scripts` to train your own models

## 🤝 Contributing

To add new demo examples:

1. Edit `demo_examples.py`
2. Add to appropriate category
3. Test with `demo_interactive.py`
4. Submit a PR

## 📄 License

Same as main HypatiaX project.

---

**Need Help?** Check the main project README or open an issue.