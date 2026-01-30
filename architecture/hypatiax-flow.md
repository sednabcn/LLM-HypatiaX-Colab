hypatiax/
│
├── 📂 core/
│   ├── preprocessing/
│   │   ├── preparation_data.py          # spaCy format preparation
│   │   └── preprocessing_pipeline.py    # Multi-format preprocessing
│   │
│   ├── training/
│   │   ├── training_spacy.py           # spaCy NER training
│   │   ├── training_transformer.py     # BERT/T5 training
│   │   ├── training_rag.py             # RAG vector index
│   │   └── training_llm.py             # LLM integration
│   │
│   ├── evaluation/
│   │   ├── testing_model.py            # Basic testing
│   │   └── evaluation_unified.py       # Unified evaluation
│   │
│   ├── deployment/
│   │   ├── deployment_pipeline.py      # REST API server
│   │   ├── deployment_batch.py         # Batch processing
│   │   └── evaluate_model.py           # Model evaluation
│   │
│   └── run_complete_pipeline.py        # 🎯 MASTER SCRIPT
│
├── 📂 mappings/
│   ├── mapping.py                      # Basic strategies
│   ├── mapping_plus.py                 # Enhanced strategies
│   ├── mapping_transformer.py          # Transformer-based
│   ├── mapping_rag.py                  # RAG-based
│   ├── mapping_llm.py                  # LLM-based
│   └── mapping_hybrid.py               # Ensemble of all
│
├── 📂 data/
│   ├── training_data.json              # Raw training data
│   ├── test_data.json                  # Test dataset
│   └── sample_batch_input.json         # Batch processing samples
│
├── 📂 preprocessed_data/
│   ├── spacy/                          # .spacy format
│   ├── transformer/                    # JSON for seq2seq
│   ├── mapping/                        # Desc-Formula pairs
│   └── rag/                            # Vector embeddings
│
├── 📂 models/
│   ├── spacy_ner/                      # Trained spaCy model
│   ├── transformer_formula_mapper/     # Trained T5/BERT
│   ├── rag_formula_mapper/             # Vector index + examples
│   └── llm_formula_mapper/             # Few-shot examples
│
├── 📂 results/
│   ├── evaluation_report.txt           # Evaluation results
│   ├── evaluation_plot.png             # Comparison chart
│   ├── deployment_info.json            # Deployment config
│   └── pipeline_results_*.json         # Pipeline execution logs
│
├── 📂 logs/
│   └── pipeline_*.log                  # Execution logs
│
├── 📂 tests/
│   ├── integration/                    # Integration tests
│   └── benchmark/                      # Performance tests
│
├── 📂 .github/workflows/
│   └── ml-pipeline.yml                 # CI/CD workflow
│
├── requirements.txt                    # Python dependencies
├── README.md                           # Project documentation
└── .gitignore                          # Git ignore rules
