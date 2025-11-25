# Gradual Migration Strategy for model_implementations/

## Strategy: Incremental Adoption
**Don't touch existing code. Use `model_implementations/` ONLY for new architectures.**

---

## Current State
```
✅ Keep as-is:
├── custom_ner/              # Leave existing NER code here
├── core/training/           # Keep current training scripts
├── core/preprocessing/      # Keep current preprocessing
└── models/trained_models/   # Keep current saved models

🆕 Use for new work:
└── model_implementations/   # Add NEW architectures only
    ├── ner/                # Future: new NER models
    ├── llm/                # Future: LLM wrappers
    ├── transformers/       # Future: transformer models
    └── agents/             # Future: RL agents
```

---

## Rules for Gradual Migration

### ✅ DO: Add New Architectures Here
When building **new** model architectures, put them in `model_implementations/`:

```python
# Example: Adding a new BERT-based NER model
# model_implementations/ner/bert_ner.py

from transformers import BertForTokenClassification

class BertNERModel:
    """New BERT-based NER model - separate from existing spaCy models"""
    def __init__(self, model_name="bert-base-uncased"):
        self.model = BertForTokenClassification.from_pretrained(model_name)
    
    def predict(self, text):
        # Inference logic
        pass
```

```python
# core/training/training_bert_ner.py (NEW training script)
from hypatiax.model_implementations.ner import BertNERModel

def train_bert_ner():
    model = BertNERModel()
    # Training logic...
```

### ✅ DO: New LLM Integrations
```python
# model_implementations/llm/openai_wrapper.py
class OpenAIWrapper:
    """Wrapper for OpenAI API calls"""
    def __init__(self, api_key, model="gpt-4"):
        self.api_key = api_key
        self.model = model
    
    def generate(self, prompt):
        # API call logic
        pass
```

### ✅ DO: New Transformer Models
```python
# model_implementations/transformers/t5_model.py
class T5ForQueryGeneration:
    """T5 model for SQL/Tableau query generation"""
    def __init__(self):
        # Model architecture
        pass
```

### ❌ DON'T: Touch Existing Code
- **Don't refactor** `custom_ner/` → Leave it alone
- **Don't move** existing training scripts
- **Don't modify** working code paths

---

## When to Use Each Directory

| Scenario | Use This Directory | Reason |
|----------|-------------------|---------|
| Adding BERT/RoBERTa NER | `model_implementations/ner/` | New architecture |
| Modifying existing spaCy NER | `custom_ner/` | Existing code |
| Adding OpenAI/Claude LLM wrapper | `model_implementations/llm/` | New functionality |
| Adding T5/BART for generation | `model_implementations/transformers/` | New architecture |
| Adding RL agent for optimization | `model_implementations/agents/` | New architecture |
| Training existing models | `core/training/` | Existing workflow |
| New training pipeline | `core/training/` or new file | Workflow logic |

---

## Example: Adding a New Model (Step-by-Step)

### Scenario: You want to add GPT-based entity extraction

**Step 1: Create model architecture**
```python
# model_implementations/llm/gpt_entity_extractor.py

import openai

class GPTEntityExtractor:
    """GPT-based entity extraction for Tableau queries"""
    
    def __init__(self, model="gpt-4", api_key=None):
        self.model = model
        self.api_key = api_key
        openai.api_key = api_key
    
    def extract_entities(self, text):
        """Extract entities using GPT"""
        prompt = f"""
        Extract Tableau-related entities from: {text}
        Return as JSON with keys: formulas, fields, calculations
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

**Step 2: Create training/usage script**
```python
# core/generation/llm_entity_extraction.py

from hypatiax.model_implementations.llm import GPTEntityExtractor

def run_gpt_extraction(query_text):
    """Use GPT for entity extraction"""
    extractor = GPTEntityExtractor(api_key="your-key")
    entities = extractor.extract_entities(query_text)
    return entities
```

**Step 3: Use it**
```python
# Your main script or notebook
from hypatiax.core.generation import run_gpt_extraction

result = run_gpt_extraction("SUM([Sales]) / COUNT([Orders])")
print(result)
```

---

## Migration Timeline (Optional - As Needed)

### Phase 1: NOW - Coexistence ✅
- Keep all existing code as-is
- Add new models only to `model_implementations/`
- Both systems work in parallel

### Phase 2: LATER - When you have time
- Gradually extract reusable model classes from `custom_ner/`
- Move them to `model_implementations/ner/`
- Update imports (one file at a time)

### Phase 3: FUTURE - Full migration (optional)
- All model architectures in `model_implementations/`
- All workflows in `core/`
- Clean separation

---

## Benefits of This Approach

✅ **No immediate work** - Existing code keeps working  
✅ **Clear separation** - New code goes in new place  
✅ **Gradual improvement** - Refactor when you have time  
✅ **Easy to understand** - Clear rule: "New architectures → model_implementations"  
✅ **Low risk** - No breaking changes to existing system

---

## Quick Reference

### Adding New Model Checklist
- [ ] Is this a NEW model architecture? → `model_implementations/`
- [ ] Does it already exist in `custom_ner/`? → Keep it there
- [ ] Is it a workflow/pipeline? → `core/`
- [ ] Is it saved model weights? → `models/trained_models/`

### File Naming Convention
```
model_implementations/
├── ner/
│   ├── bert_ner.py          # BERT-based NER
│   ├── roberta_ner.py       # RoBERTa-based NER
│   └── custom_spacy_v2.py   # New spaCy variant
├── llm/
│   ├── openai_wrapper.py    # OpenAI integration
│   ├── claude_wrapper.py    # Claude integration
│   └── local_llm.py         # Local LLM (Ollama/vLLM)
├── transformers/
│   ├── t5_generator.py      # T5 for generation
│   └── bart_summarizer.py   # BART for summarization
└── agents/
    └── rl_optimizer.py      # RL agent for query optimization
```

---

## Summary

🎯 **Strategy:** "New goes in `model_implementations/`, existing stays put"

💡 **Philosophy:** Gradual improvement without disruption

⏰ **Timeline:** At your own pace

🔄 **Flexibility:** Refactor old code only when beneficial