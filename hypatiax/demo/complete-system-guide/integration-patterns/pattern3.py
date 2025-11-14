# Pattern 3: With Example Management

from demo.engine import HypatiaXEngine
from demo.examples import ExampleManager

engine = HypatiaXEngine()
manager = ExampleManager()

# Test all basic examples
basic_examples = manager.filter_by_category('basic')
results = []

for example in basic_examples:
    result = engine.process(example.description)
    accuracy = 1.0 if result.formula == example.expected_formula else 0.0
    results.append({
        'example': example.id,
        'expected': example.expected_formula,
        'got': result.formula,
        'match': accuracy
    })

# Calculate accuracy
total_accuracy = sum(r['match'] for r in results) / len(results)
print(f"Accuracy on basic examples: {total_accuracy:.2%}")
