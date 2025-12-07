# HypatiaX Workflow Profiles Comparison

## NER Profile (Named Entity Recognition)
```
config → datasets → patterns → custom_entities → custom_ner →
data_spacy → mappings → models → model_implementations → core →
tools → agents → utils → scripts_ → experiments → tests
```
**Focus:** Traditional NER pipeline with spaCy
**Use Case:** Entity extraction, pattern matching, custom NER training

## LLM Profile (Large Language Models)
```
config → datasets → utils → tools → mappings → models →
model_implementations → agents → core → experiments → scripts_ → tests
```
**Focus:** Language models and prompt engineering
**Use Case:** Text generation, reasoning, LLM fine-tuning
**Skips:** patterns, custom_entities, custom_ner, data_spacy

## Agents Profile (Multi-Agent Systems)
```
config → datasets → tools → utils → models → model_implementations →
agents → core → experiments → scripts_ → tests
```
**Focus:** Coordinators, specialists, workflows
**Use Case:** Multi-agent orchestration, agent communication

## Transformers Profile
```
config → datasets → utils → mappings → tools → models →
model_implementations → core → experiments → scripts_ → tests
```
**Focus:** Transformer architectures
**Use Case:** BERT, GPT, T5 implementations

## Hybrid Profile (NER + LLM)
```
config → datasets → patterns → custom_entities → utils → tools →
mappings → models → model_implementations → custom_ner →
data_spacy → agents → core → experiments → scripts_ → tests
```
**Focus:** Combined NER and LLM capabilities
**Use Case:** Entity-aware language models

## Evaluation Profile (Testing Only)
```
config → datasets → utils → models → model_implementations →
core → tests
```
**Focus:** Model evaluation without training
**Use Case:** Quick validation, benchmarking
