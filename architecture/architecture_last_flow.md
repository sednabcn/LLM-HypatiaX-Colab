──(py312)(agagora㉿localhost)-[~/Downloads/LLM-HypatiaX-OLD/hypatiax]
└─$ tree -d -L 2
.
├── agents
│   ├── base
│   ├── coordinators
│   ├── learning
│   ├── memory
│   ├── specialists
│   └── workflows
├── backup_before_extension
│   ├── config
│   ├── core
│   ├── custom_entities
│   ├── custom_ner
│   ├── datasets
│   ├── data_spacy
│   ├── demo
│   ├── docs
│   ├── examples
│   ├── experiments
│   ├── mappings
│   ├── models
│   ├── patterns
│   ├── scripts_
│   └── utils
├── config
│   ├── docs
│   └── __pycache__
├── core
│   ├── deployment
│   ├── evaluation
│   ├── preprocessing
│   └── training
├── custom_entities
│   └── __pycache__
├── custom_ner
│   ├── __pycache__
│   └── queries
├── datasets
│   ├── __pycache__
│   └── queries
├── data_spacy
│   ├── corpus
│   ├── embedding
│   ├── pipelines
│   ├── pre_trained_models
│   ├── __pycache__
│   └── queries
├── demo
│   ├── complete-system-guide
│   ├── templates
│   ├── update
│   └── utils
├── docs
│   ├── llm_history
│   └── run_ner_training
├── examples
│   └── ner
├── experiments
│   ├── agents
│   ├── docs
│   ├── hybrid
│   ├── llm
│   ├── ner
│   └── transformers
├── mappings
├── model_implementations
│   ├── agents
│   ├── llm
│   ├── ner
│   └── transformers
├── models
│   ├── __pycache__
│   └── queries
├── patterns
│   ├── __pycache__
│   └── queries
├── __pycache__
├── requirements
├── scripts_
│   └── migration
├── tests
│   ├── e2e
│   ├── integration
│   └── unit
├── tools
│   ├── formal
│   ├── llm_providers
│   ├── numerical
│   ├── symbolic
│   ├── transformers
│   ├── validation
│   └── visualization
└── utils
    └── __pycache__

94 directories

┌──(py312)(agagora㉿localhost)-[~/Downloads/LLM-HypatiaX-OLD/hypatiax]
└─$ tree -d -L 4
.
├── agents
│   ├── base
│   ├── coordinators
│   ├── learning
│   ├── memory
│   ├── specialists
│   └── workflows
├── backup_before_extension
│   ├── config
│   │   ├── docs
│   │   └── __pycache__
│   ├── core
│   │   ├── deployment
│   │   │   └── docs
│   │   ├── evaluation
│   │   │   └── docs
│   │   ├── preprocessing
│   │   └── training
│   │       └── docs
│   ├── custom_entities
│   │   └── __pycache__
│   ├── custom_ner
│   │   ├── __pycache__
│   │   └── queries
│   │       ├── __pycache__
│   │       └── tableau
│   ├── datasets
│   │   ├── __pycache__
│   │   └── queries
│   │       ├── combined
│   │       ├── normalize
│   │       ├── __pycache__
│   │       └── tableau
│   ├── data_spacy
│   │   ├── corpus
│   │   ├── embedding
│   │   ├── pipelines
│   │   ├── pre_trained_models
│   │   │   ├── en_core_web_sm
│   │   │   └── en_core_web_sm-3.8.0.dist-info
│   │   ├── __pycache__
│   │   └── queries
│   │       ├── __pycache__
│   │       └── tableau
│   ├── demo
│   │   ├── complete-system-guide
│   │   │   ├── benchmark
│   │   │   ├── custom_demos
│   │   │   └── integration-patterns
│   │   ├── templates
│   │   ├── update
│   │   └── utils
│   ├── docs
│   │   ├── llm_history
│   │   └── run_ner_training
│   ├── examples
│   │   └── ner
│   ├── experiments
│   │   ├── docs
│   │   │   └── experiment_config_by_tech
│   │   └── ner
│   │       ├── docs
│   │       ├── html
│   │       └── queries
│   ├── mappings
│   ├── models
│   │   ├── __pycache__
│   │   └── queries
│   │       ├── __pycache__
│   │       └── tableau
│   ├── patterns
│   │   ├── __pycache__
│   │   └── queries
│   │       ├── __pycache__
│   │       └── tableau
│   ├── scripts_
│   └── utils
│       └── __pycache__
├── config
│   ├── docs
│   └── __pycache__
├── core
│   ├── deployment
│   │   └── docs
│   ├── evaluation
│   │   └── docs
│   ├── preprocessing
│   └── training
│       └── docs
├── custom_entities
│   └── __pycache__
├── custom_ner
│   ├── __pycache__
│   └── queries
│       ├── __pycache__
│       └── tableau
│           ├── components
│           ├── hybrid
│           ├── __pycache__
│           ├── rules
│           └── transformer
├── datasets
│   ├── __pycache__
│   └── queries
│       ├── agent
│       │   └── __pycache__
│       ├── analytics
│       │   └── __pycache__
│       ├── combined
│       │   └── __pycache__
│       ├── llm
│       │   └── __pycache__
│       ├── normalize
│       ├── __pycache__
│       ├── tableau
│       │   ├── agent
│       │   ├── data
│       │   ├── llm
│       │   ├── __pycache__
│       │   ├── testing
│       │   ├── testing_spacy
│       │   ├── training
│       │   ├── training_spacy
│       │   ├── transformer
│       │   ├── validation
│       │   └── validation_spacy
│       └── transformer
│           └── __pycache__
├── data_spacy
│   ├── corpus
│   ├── embedding
│   ├── pipelines
│   ├── pre_trained_models
│   │   ├── en_core_web_sm
│   │   │   ├── en_core_web_sm-3.7.1
│   │   │   ├── en_core_web_sm-3.8.0
│   │   │   └── __pycache__
│   │   └── en_core_web_sm-3.8.0.dist-info
│   ├── __pycache__
│   └── queries
│       ├── __pycache__
│       └── tableau
│           ├── ner_tableau
│           ├── ner_tableau_desc
│           ├── ner_tableau_formulas
│           ├── __pycache__
│           ├── testing_spacy
│           ├── training_spacy
│           └── vocab
├── demo
│   ├── complete-system-guide
│   │   ├── benchmark
│   │   ├── custom_demos
│   │   └── integration-patterns
│   ├── templates
│   ├── update
│   └── utils
├── docs
│   ├── llm_history
│   └── run_ner_training
├── examples
│   └── ner
├── experiments
│   ├── agents
│   ├── docs
│   │   └── experiment_config_by_tech
│   │       ├── agents
│   │       ├── hybrid
│   │       ├── llm
│   │       ├── ner
│   │       └── transformers
│   ├── hybrid
│   ├── llm
│   ├── ner
│   │   ├── docs
│   │   ├── html
│   │   └── queries
│   │       └── tableau
│   └── transformers
├── mappings
├── model_implementations
│   ├── agents
│   ├── llm
│   ├── ner
│   └── transformers
├── models
│   ├── __pycache__
│   └── queries
│       ├── __pycache__
│       └── tableau
│           ├── checkpoints
│           ├── model_configs
│           ├── __pycache__
│           ├── trained_models
│           └── training_history
├── patterns
│   ├── __pycache__
│   └── queries
│       ├── __pycache__
│       └── tableau
│           └── __pycache__
├── __pycache__
├── requirements
├── scripts_
│   └── migration
├── tests
│   ├── e2e
│   ├── integration
│   └── unit
│       ├── test_agents
│       ├── test_llm
│       ├── test_ner
│       ├── test_tools
│       └── test_transformers
├── tools
│   ├── formal
│   ├── llm_providers
│   ├── numerical
│   ├── symbolic
│   ├── transformers
│   ├── validation
│   └── visualization
└── utils
    └── __pycache__

225 directories
