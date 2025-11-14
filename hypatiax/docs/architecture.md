# HypatiaX Architecture

## Overview
HypatiaX is a multi-technology AI system for mapping natural language queries to mathematical expressions.

## Architecture Layers

### 1. Core Layer (`core/`)
- **Preprocessing**: Data preparation for all models
- **Training**: Model training scripts
- **Evaluation**: Testing and metrics
- **Deployment**: Model serving

### 2. Technology Implementations
- **NER** (`custom_ner/`, `data_spacy/`): Named Entity Recognition with spaCy
- **Transformers** (`models/.../transformers/`): BERT/T5 for seq2seq
- **LLM** (`tools/llm_providers/`): OpenAI, Anthropic, DeepSeek
- **Agents** (`agents/`): Multi-agent AI system

### 3. Tools Layer (`tools/`)
External integrations:
- Symbolic computation (SymPy, Mathematica)
- Numerical computation (NumPy, SciPy)
- Validation tools

### 4. Mapping Layer (`mappings/`)
Different mapping strategies that can be combined.

## Technology Coexistence
All technologies work together through the hybrid mapper.
