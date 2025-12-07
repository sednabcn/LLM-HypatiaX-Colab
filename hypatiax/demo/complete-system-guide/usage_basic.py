# 2. Basic Usage
from demo.engine import HypatiaXEngine
from demo.examples import ExampleManager
from demo.ui import InteractiveDemo, UIComponents

# Initialize engine
engine = HypatiaXEngine()

# Process a query
result = engine.process("calculate sum of sales by region")

print(f"Formula: {result.formula}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Entities: {len(result.entities)}")
