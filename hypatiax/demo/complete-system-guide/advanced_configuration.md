🛠️ Advanced Configuration
Custom Model Paths

engine = HypatiaXEngine(
    desc_model_path='path/to/custom/desc/model',
    formula_model_path='path/to/custom/formula/model',
    use_gpu=True  # Enable GPU acceleration
)
engine.load_models()

Custom Vocabulary Mappings

engine = HypatiaXEngine()
engine.vocab_map.update({
    'summation': 'SUM',
    'aggregate': 'SUM',
    'total_sales': 'Total Sales',
    'customer_count': 'Customer Count'
})

Custom Example Categories

from demo.examples import ExampleManager, Example

manager = ExampleManager()

# Add domain-specific examples
manager.add_example(Example(
    id="healthcare_01",
    description="average patient wait time by department",
    expected_formula="AVG([Wait Time])",
    category="healthcare",
    difficulty=2,
    tags=["healthcare", "average", "time"]
))


🎓 Next Steps

1.Test the System: Run interactive demo

   python demo/ui.py

2.Customize Examples: Edit examples.py for your domain
3.Train Models: Use examples.py to export training data
4.Deploy Backend: Use Flask API for web integration
5.Extend: Add new mapping methods in engine.py