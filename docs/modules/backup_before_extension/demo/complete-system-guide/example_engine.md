# Module: `backup_before_extension/demo/complete-system-guide/example_engine.py`

## Description

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

**Last Modified**: 2025-11-10T20:52:17.804608

## Dependencies

- `demo.engine`
