─(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/models]
└─$ tree
.
├── finance
│   ├── defi
│   │   └── __init__.py
│   └── __init__.py
├── __init__.py
└── queries
    ├── __init__.py
    └── tableau
        ├── checkpoints
        │   ├── agents
        │   ├── __init__.py
        │   ├── llm
        │   └── transformers
        ├── generated_models
        ├── __init__.py
        ├── model_configs
        │   └── __init__.py
        ├── trained_models
        │   ├── agent_policies
        │   ├── bert_classifier
        │   ├── __init__.py
        │   ├── llm_models
        │   ├── ner_models
        │   │   ├── Combined_multi_task_200_0.5_8_data
        │   │   │   ├── attribute_ruler
        │   │   │   │   └── patterns
        │   │   │   ├── config.cfg
        │   │   │   ├── lemmatizer
        │   │   │   │   └── lookups
        │   │   │   │       └── lookups.bin
        │   │   │   ├── meta.json
        │   │   │   ├── ner
        │   │   │   │   ├── cfg
        │   │   │   │   ├── model
        │   │   │   │   └── moves
        │   │   │   ├── parser
        │   │   │   │   ├── cfg
        │   │   │   │   ├── model
        │   │   │   │   └── moves
        │   │   │   ├── senter
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tagger
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tok2vec
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tokenizer
        │   │   │   └── vocab
        │   │   │       ├── key2row
        │   │   │       ├── lookups.bin
        │   │   │       ├── strings.json
        │   │   │       ├── vectors
        │   │   │       └── vectors.cfg
        │   │   ├── Combined_multi_task_400_0.5_8_data
        │   │   │   ├── attribute_ruler
        │   │   │   │   └── patterns
        │   │   │   ├── config.cfg
        │   │   │   ├── lemmatizer
        │   │   │   │   └── lookups
        │   │   │   │       └── lookups.bin
        │   │   │   ├── meta.json
        │   │   │   ├── ner
        │   │   │   │   ├── cfg
        │   │   │   │   ├── model
        │   │   │   │   └── moves
        │   │   │   ├── parser
        │   │   │   │   ├── cfg
        │   │   │   │   ├── model
        │   │   │   │   └── moves
        │   │   │   ├── senter
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tagger
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tok2vec
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tokenizer
        │   │   │   └── vocab
        │   │   │       ├── key2row
        │   │   │       ├── lookups.bin
        │   │   │       ├── strings.json
        │   │   │       ├── vectors
        │   │   │       └── vectors.cfg
        │   │   ├── Combined_multi_task_data_200.0.5.8
        │   │   │   ├── attribute_ruler
        │   │   │   │   └── patterns
        │   │   │   ├── config.cfg
        │   │   │   ├── lemmatizer
        │   │   │   │   └── lookups
        │   │   │   │       └── lookups.bin
        │   │   │   ├── meta.json
        │   │   │   ├── ner
        │   │   │   │   ├── cfg
        │   │   │   │   ├── model
        │   │   │   │   └── moves
        │   │   │   ├── parser
        │   │   │   │   ├── cfg
        │   │   │   │   ├── model
        │   │   │   │   └── moves
        │   │   │   ├── senter
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tagger
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tok2vec
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tokenizer
        │   │   │   └── vocab
        │   │   │       ├── key2row
        │   │   │       ├── lookups.bin
        │   │   │       ├── strings.json
        │   │   │       ├── vectors
        │   │   │       └── vectors.cfg
        │   │   ├── Description_sm_tableau_400_0.5_8_data
        │   │   │   ├── attribute_ruler
        │   │   │   │   └── patterns
        │   │   │   ├── config.cfg
        │   │   │   ├── lemmatizer
        │   │   │   │   └── lookups
        │   │   │   │       └── lookups.bin
        │   │   │   ├── meta.json
        │   │   │   ├── ner
        │   │   │   │   ├── cfg
        │   │   │   │   ├── model
        │   │   │   │   └── moves
        │   │   │   ├── parser
        │   │   │   │   ├── cfg
        │   │   │   │   ├── model
        │   │   │   │   └── moves
        │   │   │   ├── senter
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tagger
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tok2vec
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tokenizer
        │   │   │   └── vocab
        │   │   │       ├── key2row
        │   │   │       ├── lookups.bin
        │   │   │       ├── strings.json
        │   │   │       ├── vectors
        │   │   │       └── vectors.cfg
        │   │   ├── Formulas_sm_tableau_400_0.5_8_data
        │   │   │   ├── attribute_ruler
        │   │   │   │   └── patterns
        │   │   │   ├── config.cfg
        │   │   │   ├── lemmatizer
        │   │   │   │   └── lookups
        │   │   │   │       └── lookups.bin
        │   │   │   ├── meta.json
        │   │   │   ├── ner
        │   │   │   │   ├── cfg
        │   │   │   │   ├── model
        │   │   │   │   └── moves
        │   │   │   ├── parser
        │   │   │   │   ├── cfg
        │   │   │   │   ├── model
        │   │   │   │   └── moves
        │   │   │   ├── senter
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tagger
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tok2vec
        │   │   │   │   ├── cfg
        │   │   │   │   └── model
        │   │   │   ├── tokenizer
        │   │   │   └── vocab
        │   │   │       ├── key2row
        │   │   │       ├── lookups.bin
        │   │   │       ├── strings.json
        │   │   │       ├── vectors
        │   │   │       └── vectors.cfg
        │   │   ├── test_description_model.txt
        │   │   ├── test_formulas_model_old.txt
        │   │   ├── test_formulas_model.txt
        │   │   └── test_multi_task_400_model.txt
        │   ├── t5_mapper
        │   ├── test_comb_multi_task_model.py
        │   ├── test_description_model.py
        │   ├── test_formulas_model.py
        │   ├── trained_models_versions
        │   │   └── __init__.py
        │   └── tranformers_models
        └── training_history
            ├── __init__.py
            └── training_history_versions
                └── __init__.py

71 directories, 128 files
