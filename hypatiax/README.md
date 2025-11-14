# HypatiaX - AI-Powered Analytical Expression Mapper

## 🚀 Multi-Technology AI System

HypatiaX maps natural language queries to mathematical expressions using:
- **NER**: Named Entity Recognition with spaCy (existing)
- **Transformers**: BERT/T5 for sequence-to-sequence mapping
- **LLM**: OpenAI GPT-4, Anthropic Claude, DeepSeek-Math
- **Agents**: Multi-agent AI system for complex reasoning

## 📁 Architecture
```
hypatiax/
├── config/          # Configurations for all technologies
├── core/            # Training, evaluation, deployment
├── custom_ner/      # Existing NER system
├── mappings/        # Mapping strategies (NER, Transformer, LLM, Agent, Hybrid)
├── tools/           # External integrations (SymPy, LLMs, validators)
├── agents/          # AI agent system
├── models/          # Trained models for all technologies
├── datasets/        # Training data
├── examples/        # Usage examples
└── requirements/    # Modular dependencies
```

## 🔧 Installation

### 1. Clone and setup
```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax
```

### 2. Install dependencies (choose what you need)
```bash
# For existing NER only
pip install -r requirements/ner.txt

# For transformers
pip install -r requirements/transformers.txt

# For LLM integration
pip install -r requirements/llm.txt

# For agents
pip install -r requirements/agents.txt

# For all tools
pip install -r requirements/tools.txt

# For development (includes everything)
pip install -r requirements/dev.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

## 📚 Quick Start

### Using Existing NER
```python
from custom_ner.queries.tableau import TableauNER
from mappings.mapping import BasicMapping

ner = TableauNER()
mapper = BasicMapping()
result = mapper.map("integrate x squared")
```

### Using LLM
```python
from tools.llm_providers.openai_provider import OpenAIProvider
from mappings.llm_mapping import LLMMapper

llm = OpenAIProvider(api_key="your-key")
mapper = LLMMapper(llm_provider=llm)
result = mapper.map("solve differential equation dy/dx = 2x")
```

### Using Agents
```python
from agents.workflows.hybrid_workflow import HybridWorkflow
from agents.specialists.parser_agent import ParserAgent

workflow = HybridWorkflow()
workflow.add_agent(ParserAgent())
result = workflow.execute("find integral of cos(x)")
```

### Using Hybrid (All Methods)
```python
from mappings.hybrid_mapping import HybridMapper

mapper = HybridMapper(
    use_ner=True,
    use_transformer=True,
    use_llm=True,
    use_agents=True
)
result = mapper.map("complex mathematical query")
```

## 📖 Examples

See `examples/` directory:
- `basic_usage.py` - Existing NER usage
- `transformer_example.py` - BERT/T5 usage
- `llm_example.py` - LLM usage
- `agent_example.py` - Agent workflow
- `hybrid_example.py` - Combined approach

## 🧪 Testing
```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/test_ner/
pytest tests/unit/test_llm/
pytest tests/integration/

# Run with coverage
pytest --cov=hypatiax tests/
```

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [Tools Reference](docs/tools_reference.md)

## 🔄 Migration

This structure extends the original HypatiaX architecture.
All existing NER functionality is preserved and enhanced.

## ✅ Features

- ✅ Original NER system preserved
- ✅ Transformer-based mapping (BERT/T5)
- ✅ LLM integration (GPT-4, Claude, DeepSeek)
- ✅ Multi-agent AI system
- ✅ Symbolic validation (SymPy)
- ✅ Hybrid ensemble mapping
- ✅ Modular dependencies
- ✅ Comprehensive examples

## 📝 License

[Your License]

## 🤝 Contributing

Contributions welcome! Please follow the modular architecture.
