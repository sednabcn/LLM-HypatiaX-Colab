# Pattern 2: With UI Components

from demo.engine import HypatiaXEngine
from demo.ui import UIComponents

engine = HypatiaXEngine()
ui = UIComponents()

result = engine.process("average profit per region")

# Beautiful output
print(ui.header("Processing Result"))
print(
    ui.entity_visualization(
        result.query, [{"text": e.text, "label": e.label, "start": e.start, "end": e.end} for e in result.entities]
    )
)
print(ui.formula_display(result.formula, result.confidence))
