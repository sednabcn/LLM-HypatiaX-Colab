# Pattern 1: Standalone Processing
from demo.engine import HypatiaXEngine

engine = HypatiaXEngine()
result = engine.process("sum of sales")
print(result.formula)  # SUM([Sales])
