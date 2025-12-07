📊 Experiment Tracking Structure
Create this structure in your experiments/ directory:
experiments/
├── __init__.py
├── experiment_registry.json          # 🆕 Central registry
├── experiment_tracker.py             # 🆕 Tracking utility
├── README.md                         # 🆕 Experiment documentation
│
├── ner/                              # ✅ Existing
│   ├── __init__.py
│   ├── experiment_config.json        # 🆕 NER experiment metadata
│   ├── queries/tableau/...
│   ├── docs/
│   └── html/
│
├── transformers/                     # 🆕 New
│   ├── __init__.py
│   ├── experiment_config.json
│   ├── bert_seq2seq/
│   │   ├── __init__.py
│   │   ├── train_bert.py
│   │   └── results/
│   └── t5_formula_mapper/
│       ├── __init__.py
│       ├── train_t5.py
│       └── results/
│
├── llm/                              # 🆕 New
│   ├── __init__.py
│   ├── experiment_config.json
│   ├── prompt_engineering/
│   │   ├── __init__.py
│   │   ├── few_shot_experiments.py
│   │   └── results/
│   ├── model_comparison/
│   │   ├── __init__.py
│   │   ├── compare_providers.py
│   │   └── results/
│   └── chain_of_thought/
│       ├── __init__.py
│       ├── cot_experiments.py
│       └── results/
│
├── agents/                           # 🆕 New
│   ├── __init__.py
│   ├── experiment_config.json
│   ├── workflow_optimization/
│   │   ├── __init__.py
│   │   ├── optimize_workflows.py
│   │   └── results/
│   ├── multi_agent_performance/
│   │   ├── __init__.py
│   │   ├── benchmark_agents.py
│   │   └── results/
│   └── learning_experiments/
│       ├── __init__.py
│       ├── test_learning.py
│       └── results/
│
└── hybrid/                           # 🆕 New
    ├── __init__.py
    ├── experiment_config.json
    ├── ensemble_strategies/
    │   ├── __init__.py
    │   ├── test_ensemble.py
    │   └── results/
    └── comparative_analysis/
        ├── __init__.py
        ├── compare_all_methods.py
        └── results/
