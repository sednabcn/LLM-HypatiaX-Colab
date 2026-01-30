# HypatiaX Workflow Profiles Comparison

## Overview

HypatiaX supports multiple workflow profiles optimized for different use cases. Each profile determines the execution order of modules and which components are included.

## Available Profiles

### 1. NER Profile (Named Entity Recognition)

**Execution Order:**
```
config → datasets → patterns → custom_entities → custom_ner →
data_spacy → mappings → models → model_implementations → core →
tools → agents → utils → scripts_ → experiments → tests
```

**Focus:** Traditional NER pipeline with spaCy
**Use Cases:**
- Entity extraction from text
- Pattern matching
- Custom NER model training
- SpaCy pipeline development

**Key Components:**
- ✅ patterns - Pattern definitions
- ✅ custom_entities - Custom entity definitions
- ✅ custom_ner - Custom NER components
- ✅ data_spacy - SpaCy data processing

**Trigger:** Changes to `patterns/`, `custom_entities/`, `custom_ner/`, `data_spacy/`

---

### 2. LLM Profile (Large Language Models)

**Execution Order:**
```
config → datasets → utils → tools → mappings → models →
model_implementations → agents → core → experiments → scripts_ → tests
```

**Focus:** Language models and prompt engineering
**Use Cases:**
- Text generation
- Reasoning tasks
- LLM fine-tuning
- Prompt engineering experiments
- Agent-based LLM orchestration

**Key Components:**
- ✅ tools (early) - LLM providers, validation
- ✅ utils (early) - Preprocessing helpers
- ✅ agents - LLM coordination
- ❌ Skips: patterns, custom_entities, custom_ner, data_spacy

**Trigger:** Changes to `tools/`, `agents/`, `model_implementations/llm/`, `experiments/llm/`

---

### 3. Agents Profile (Multi-Agent Systems)

**Execution Order:**
```
config → datasets → tools → utils → models → model_implementations →
agents → core → experiments → scripts_ → tests
```

**Focus:** Multi-agent coordination and communication
**Use Cases:**
- Coordinator agents
- Specialist agents
- Agent workflows
- Multi-agent orchestration

**Key Components:**
- ✅ agents (priority) - base, coordinators, specialists, workflows
- ✅ tools (early) - Agent communication tools
- ✅ model_implementations/agents - Agent model implementations

**Trigger:** Changes to `agents/`, `model_implementations/agents/`, `experiments/agents/`

---

### 4. Transformers Profile

**Execution Order:**
```
config → datasets → utils → mappings → tools → models →
model_implementations → core → experiments → scripts_ → tests
```

**Focus:** Transformer model architectures
**Use Cases:**
- BERT implementations
- GPT implementations
- T5 implementations
- Custom transformer architectures

**Key Components:**
- ✅ tools/transformers - Transformer utilities
- ✅ model_implementations/transformers - Transformer models
- ✅ experiments/transformers - Transformer experiments

---

### 5. Hybrid Profile (NER + LLM)

**Execution Order:**
```
config → datasets → patterns → custom_entities → utils → tools →
mappings → models → model_implementations → custom_ner →
data_spacy → agents → core → experiments → scripts_ → tests
```

**Focus:** Combined NER and LLM capabilities
**Use Cases:**
- Entity-aware language models
- NER with LLM enhancement
- Hybrid extraction and generation

**Key Components:**
- ✅ All NER components
- ✅ All LLM components
- ✅ Integrated workflow

---

### 6. Evaluation Profile (Testing Only)

**Execution Order:**
```
config → datasets → utils → models → model_implementations →
core → tests
```

**Focus:** Model evaluation without training
**Use Cases:**
- Quick validation
- Benchmarking
- Model comparison
- CI/CD testing

**Key Components:**
- ✅ Minimal set for evaluation
- ❌ Skips: training, experiments, scripts

---

## Comparison Matrix

| Component | NER | LLM | Agents | Transformers | Hybrid | Evaluation |
|-----------|-----|-----|--------|--------------|--------|------------|
| config | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| datasets | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| patterns | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| custom_entities | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| custom_ner | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| data_spacy | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| utils | ✅ | ✅ (early) | ✅ (early) | ✅ (early) | ✅ | ✅ |
| tools | ✅ | ✅ (early) | ✅ (early) | ✅ | ✅ | ❌ |
| mappings | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| models | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| model_implementations | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| agents | ✅ | ✅ | ✅ (priority) | ❌ | ✅ | ❌ |
| core | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| experiments | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| scripts_ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| tests | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Usage

### Command Line
```bash
# Run NER profile
python .github/scripts/workflow_runner.py --profile ner

# Run LLM profile
python .github/scripts/workflow_runner.py --profile llm

# Run Agents profile
python .github/scripts/workflow_runner.py --profile agents

# Run Transformers profile
python .github/scripts/workflow_runner.py --profile transformers

# Run Hybrid profile
python .github/scripts/workflow_runner.py --profile hybrid

# Run Evaluation profile
python .github/scripts/workflow_runner.py --profile evaluation

# Run custom modules
python .github/scripts/workflow_runner.py --modules config datasets tools models
```

### GitHub Actions

1. Go to **Actions** tab in your repository
2. Select the workflow:
   - **HypatiaX NER Workflow** - for NER tasks
   - **HypatiaX LLM Workflow** - for LLM tasks
   - **HypatiaX Agents Workflow** - for agent tasks
   - **Test Specific Profile** - to test any profile
3. Click **Run workflow**
4. Select options and run

### Automated Triggers

- **NER Workflow**: Triggers on changes to `patterns/`, `custom_entities/`, `custom_ner/`, `data_spacy/`
- **LLM Workflow**: Triggers on changes to `tools/`, `agents/`, `model_implementations/llm/`
- **Agents Workflow**: Triggers on changes to `agents/`, `model_implementations/agents/`

---

## Architecture Notes

- **agents/**: Multi-agent system (base, coordinators, learning, memory, specialists, workflows)
- **tools/**: Utilities (formal, llm_providers, numerical, symbolic, transformers, validation, visualization)
- **model_implementations/**: Implementations (agents, llm, ner, transformers)
- **tests/**: Testing (unit, integration, e2e)

---

## Choosing the Right Profile

| If you want to... | Use this profile |
|-------------------|------------------|
| Extract entities from text | **NER** |
| Generate or analyze text with LLMs | **LLM** |
| Build multi-agent systems | **Agents** |
| Work with transformer architectures | **Transformers** |
| Combine NER and LLM | **Hybrid** |
| Just evaluate existing models | **Evaluation** |

---

## Version

Document version: 1.0
Last updated: 2024-11-15
Compatible with: HypatiaX v0.1.1+
