"""
2. ui.py - Reusable UI Components
Purpose: Rich console output, visualizations, and interactive components
Key Classes:

UIComponents: Static UI building blocks
InteractiveDemo: Full interactive demo runner
Colors: ANSI color codes

UI Components Available:

📊 Headers, subheaders, dividers
📦 Text boxes and tables
📈 Progress bars
🎨 Entity visualization with colors
📝 Formula display with confidence
📊 Metric cards
🔄 Comparison tables
✅ Status messages (success/error/warning/info)

"""

from demo.engine import HypatiaXEngine
from demo.ui import InteractiveDemo, UIComponents

ui = UIComponents()

# Create beautiful headers
print(ui.header("HypatiaX Demo", width=60))

# Display entities with colors
entities = [
    {"text": "sum", "label": "OPER", "start": 0, "end": 3},
    {"text": "sales", "label": "ARG", "start": 7, "end": 12},
]
print(ui.entity_visualization("sum of sales", entities))

# Show formula with confidence
print(ui.formula_display("SUM([Sales])", 0.95))

# Create comparison table
results = [
    {"method": "vocab", "formula": "SUM([Sales])", "confidence": 0.95, "processing_time": 12},
    {"method": "regex", "formula": "SUM([Sales])", "confidence": 0.88, "processing_time": 8},
]
print(ui.comparison_table(results))

# Run full interactive demo
engine = HypatiaXEngine()
demo = InteractiveDemo(engine)
demo.run()  # Interactive menu-driven interface
