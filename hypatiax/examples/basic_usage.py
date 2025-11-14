# examples/basic_usage.py
"""Show users how to use your trained models"""
from hypatiax import load_model, process_query

model = load_model('tableau_desc')
result = model.process("calculate area of circle")
print(result)
