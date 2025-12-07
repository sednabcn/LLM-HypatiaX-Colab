# 📊 Benchmarking & Evaluation
# Run Comprehensive Benchmark

from demo.engine import HypatiaXEngine
from demo.examples import ExampleManager
from demo.ui import UIComponents

engine = HypatiaXEngine()
manager = ExampleManager()
ui = UIComponents()

# Get all test examples
test_examples = manager.filter_by_category("test")

# Test all methods
methods = ["vocab", "sentence", "regex", "ner"]
results = {}

print(ui.header("Benchmark Results"))

for method in methods:
    correct = 0
    total = len(test_examples)

    for example in test_examples:
        result = engine.process(example.description, method=method)
        if result.formula == example.expected_formula:
            correct += 1

    accuracy = correct / total
    results[method] = accuracy
    print(f"{method.capitalize()}: {accuracy:.2%} ({correct}/{total})")

# Show best method
best_method = max(results, key=results.get)
print(f"\nBest method: {best_method} ({results[best_method]:.2%})")
