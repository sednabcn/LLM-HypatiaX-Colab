"""
1. engine.py - Core Processing Engine
Purpose: Handles NER model integration, entity extraction, and formula generation
Key Classes:

HypatiaXEngine: Main processing engine
Entity: Represents extracted entities
ProcessingResult: Container for results

Features:

✅ Multiple mapping methods (vocab, sentence, regex, NER)
✅ GPU acceleration support
✅ Fallback to rule-based when models unavailable
✅ Batch processing with statistics
✅ Export to CSV/JSON/Excel

"""

from demo.engine import HypatiaXEngine

# Initialize with custom models
engine = HypatiaXEngine(
    desc_model_path='data_spacy/queries/tableau/ner_tableau_desc',
    formula_model_path='data_spacy/queries/tableau/ner_tableau_formulas',
    use_gpu=False
)

# Load models (optional, falls back to rule-based)
engine.load_models()

# Process single query
result = engine.process(
    query="average profit per product",
    method='vocab',  # or 'sentence', 'regex', 'ner'
    use_model=True
)

# Batch process
queries = ["sum of sales", "count customers", "max revenue"]
results = engine.batch_process(queries, method='vocab')

# Export results
engine.export_results(results, 'output.csv', format='csv')

# View statistics
stats = engine.get_stats()
print(f"Success rate: {stats['successful_mappings'] / stats['total_queries']:.2%}")
