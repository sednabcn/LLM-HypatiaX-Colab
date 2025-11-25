# Should I Extract from core/? - Decision Guide

## TL;DR: **Not right now. Only when you touch that code anyway.**

---

## Current State Assessment

### ✅ What's Working (Don't Touch)
```
core/
├── training/
│   ├── training_spacy.py          # Working, leave it
│   ├── training_transformer.py    # Working, leave it
│   └── baseline_neural_network.py # Working, leave it
├── generation/
│   └── baseline_pure_llm.py       # Working, leave it
└── preprocessing/
    └── preprocessing_pipeline.py  # Working, leave it
```

**Reason:** These files work. Extracting adds risk with no immediate benefit.

---

## When to Extract (Decision Matrix)

| Situation | Extract? | Why |
|-----------|----------|-----|
| Adding new BERT model | ❌ No | Put in `model_implementations/bert_ner.py` directly |
| Fixing bug in `training_spacy.py` | ❌ No | Just fix the bug |
| `training_spacy.py` is 800 lines | ✅ Yes | Too big, hard to maintain |
| Need to reuse spaCy model elsewhere | ✅ Yes | Extract for reusability |
| Adding 2nd spaCy variant | ✅ Yes | Extract base class first |
| File works fine, not touching it | ❌ No | Leave it alone |

---

## Extraction Triggers

### 🔴 **Don't Extract If:**
- File is < 200 lines
- Code works fine
- You're not currently editing it
- It's only used in one place
- You're busy with other features

### 🟢 **Do Extract If:**
- File is > 500 lines (too complex)
- You're already editing it anyway
- You need to reuse the model
- You're adding a variant
- The model/training logic is tangled

---

## Example Scenarios

### Scenario 1: Adding GPT-4 Integration
**Question:** Should I extract existing LLM code first?

**Answer:** ❌ NO
```python
# Just add new file
# model_implementations/llm/gpt4_wrapper.py
class GPT4Wrapper:
    pass
```

### Scenario 2: `training_spacy.py` has a bug
**Question:** Should I extract while fixing?

**Answer:** ❌ NO (unless file is huge)
```python
# Just fix the bug in place
# core/training/training_spacy.py
def train_spacy_model():
    # Fix the bug here
    pass
```

### Scenario 3: Need 3 different spaCy model variants
**Question:** Should I extract now?

**Answer:** ✅ YES
```python
# Extract base class
# model_implementations/ner/base_spacy_ner.py
class BaseSpacyNER:
    pass

# Create variants
# model_implementations/ner/spacy_ner_v1.py
class SpacyNERV1(BaseSpacyNER):
    pass

# model_implementations/ner/spacy_ner_v2.py
class SpacyNERV2(BaseSpacyNER):
    pass
```

### Scenario 4: `training_transformer.py` is 800 lines
**Question:** Should I extract?

**Answer:** ✅ YES (file is too large)
```python
# Extract model architecture
# model_implementations/transformers/bert_classifier.py
class BertClassifier:
    # Model definition only
    pass

# Keep training workflow
# core/training/training_transformer.py
from hypatiax.model_implementations.transformers import BertClassifier

def train_transformer():
    model = BertClassifier()
    # Training logic
    pass
```

---

## Your Action Plan

### **Week 1-4: Coexistence Phase** ✅ (You are here)
```
Status: Add new models to model_implementations/, leave core/ alone
```

**Do:**
- Add new architectures to `model_implementations/`
- Keep using existing `core/` files as-is
- Document what's in each new file

**Don't:**
- Don't refactor working code
- Don't extract from `core/` yet
- Don't worry about the mess

### **Month 2+: Opportunistic Extraction** (Future)
```
Status: Extract only when already editing that file
```

**Rules:**
1. Editing `training_spacy.py` for a new feature?
   - → Consider extracting while you're there
2. File works fine and you're not touching it?
   - → Leave it alone
3. File is getting too complex (>500 lines)?
   - → Extract architecture to `model_implementations/`

---

## Code Smells That Indicate "Time to Extract"

### 🚨 Extract When You See:
```python
# core/training/training_spacy.py

class CustomNER:           # ← Model definition
    pass

class AnotherNER:          # ← Another model
    pass

def train_model_v1():      # ← Training logic
    pass

def train_model_v2():      # ← More training logic
    pass

def preprocess():          # ← Preprocessing
    pass

def evaluate():            # ← Evaluation
    pass

# 600 lines later...
```

**This file does TOO MUCH** → Time to extract

### ✅ OK to Keep:
```python
# core/training/training_spacy.py

def train_spacy_model():   # ← Just training workflow
    model = spacy.load()
    # Training logic
    pass

# 100-200 lines total
```

**This file has ONE JOB** → Keep as-is

---

## Practical Example: Real Decision

**You want to add BERT-based NER:**

### ❌ Bad Approach (Premature Refactoring)
```
1. Extract all models from core/training/
2. Reorganize everything
3. Update all imports
4. Test everything
5. Then add BERT model
6. Time wasted: 2 days
```

### ✅ Good Approach (Your Strategy)
```
1. Create model_implementations/ner/bert_ner.py
2. Add BERT model directly there
3. Done!
4. Time wasted: 0 minutes
```

---

## Summary

### Your Question: "Should I extract from core/ now?"

**Answer: NO** ❌

**Better Question:** "When should I extract?"

**Answer:** When you're already editing that code AND it's complex/messy

---

## One-Line Rule

> **"If you're not currently opening the file, don't refactor it."**

---

## Checklist Before Extracting

Before extracting anything from `core/`, ask:

- [ ] Am I already editing this file?
- [ ] Is the file > 500 lines?
- [ ] Do I need to reuse this model?
- [ ] Am I adding a variant of this model?
- [ ] Will this make my current work easier?

**If less than 3 checkmarks:** Don't extract yet.

---

## Final Recommendation

**Do this:**
```python
# Add new models to model_implementations/
model_implementations/llm/claude_wrapper.py     # NEW
model_implementations/transformers/t5_model.py  # NEW
```

**Don't do this (yet):**
```python
# Extract from existing core/ files
core/training/training_spacy.py → model_implementations/ner/spacy_ner.py
```

**Do this later (when needed):**
```python
# Only when you're already editing training_spacy.py for other reasons
```