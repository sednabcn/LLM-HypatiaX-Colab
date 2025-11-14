#!/usr/bin/env python3
"""
HypatiaX Demo Configuration
Centralized configuration for all demo components
Easy to update and maintain
"""

from pathlib import Path
from typing import Dict, List

# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DEMO_DIR = Path(__file__).parent

# Model paths
MODELS_DIR = PROJECT_ROOT / "models" / "queries" / "tableau"
DATA_SPACY_DIR = PROJECT_ROOT / "data_spacy" / "queries" / "tableau"

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

MODEL_CONFIG = {
    'desc': {
        'name': 'Description NER',
        'path': DATA_SPACY_DIR / "ner_tableau_desc",
        'description': 'Extracts entities from natural language descriptions',
        'entity_types': ['NOUN', 'VERB', 'ADJ', 'ADP', 'CONJ'],
    },
    'formulas': {
        'name': 'Formula NER',
        'path': DATA_SPACY_DIR / "ner_tableau_formulas",
        'description': 'Parses Tableau formula syntax',
        'entity_types': ['OPER', 'ARG', 'ARGN', 'NUM', 'ADP', 'ADV'],
    },
    'both': {
        'name': 'Combined NER',
        'path': DATA_SPACY_DIR / "ner_tableau",
        'description': 'Processes both descriptions and formulas',
        'entity_types': ['NOUN', 'VERB', 'OPER', 'ARG', 'NUM'],
    }
}

# ============================================================================
# EXAMPLE QUERIES
# ============================================================================

DEMO_EXAMPLES = {
    'basic': [
        {
            'category': 'Aggregations',
            'description': 'calculate the sum of sales',
            'expected_formula': 'SUM([Sales])',
            'difficulty': 'easy',
        },
        {
            'category': 'Aggregations',
            'description': 'find the average profit',
            'expected_formula': 'AVG([Profit])',
            'difficulty': 'easy',
        },
        {
            'category': 'Counting',
            'description': 'count total orders',
            'expected_formula': 'COUNT([Orders])',
            'difficulty': 'easy',
        },
    ],
    
    'intermediate': [
        {
            'category': 'Grouped Aggregations',
            'description': 'sum of sales by region',
            'expected_formula': 'SUM([Sales])',
            'note': 'GROUP BY [Region]',
            'difficulty': 'medium',
        },
        {
            'category': 'Grouped Aggregations',
            'description': 'average profit per category',
            'expected_formula': 'AVG([Profit])',
            'note': 'GROUP BY [Category]',
            'difficulty': 'medium',
        },
        {
            'category': 'Calculated Fields',
            'description': 'calculate profit margin',
            'expected_formula': 'SUM([Profit]) / SUM([Sales])',
            'difficulty': 'medium',
        },
    ],
    
    'advanced': [
        {
            'category': 'Conditional Logic',
            'description': 'if sales greater than 1000 then high else low',
            'expected_formula': 'IF [Sales] > 1000 THEN "High" ELSE "Low"',
            'difficulty': 'hard',
        },
        {
            'category': 'Complex Calculations',
            'description': 'year over year growth rate',
            'expected_formula': '(SUM([Sales]) - LOOKUP(SUM([Sales]), -1)) / LOOKUP(SUM([Sales]), -1)',
            'difficulty': 'hard',
        },
    ],
    
    'real_world': [
        {
            'category': 'Retail Analytics',
            'description': 'Sum of sales by year',
            'expected_formula': 'SUM([Sales])',
            'note': 'GROUP BY YEAR([Order Date])',
            'use_case': 'Yearly sales trends dashboard',
        },
        {
            'category': 'Data Science',
            'description': 'Average of Petal Length across all flowers',
            'expected_formula': 'AVG([Petal Length])',
            'use_case': 'Iris dataset analysis',
        },
        {
            'category': 'Customer Analytics',
            'description': 'Total number of unique customers',
            'expected_formula': 'COUNT DISTINCT([Customer ID])',
            'use_case': 'Customer segmentation',
        },
    ]
}

# ============================================================================
# ENTITY LABELS & COLORS
# ============================================================================

ENTITY_STYLES = {
    # Description entities
    'NOUN': {'color': '#1e40af', 'bg': '#dbeafe', 'name': 'Noun'},
    'VERB': {'color': '#166534', 'bg': '#dcfce7', 'name': 'Verb'},
    'ADJ': {'color': '#92400e', 'bg': '#fef3c7', 'name': 'Adjective'},
    'ADP': {'color': '#831843', 'bg': '#fbcfe8', 'name': 'Preposition'},
    'CONJ': {'color': '#7c2d12', 'bg': '#fed7aa', 'name': 'Conjunction'},
    
    # Formula entities
    'OPER': {'color': '#6b21a8', 'bg': '#e9d5ff', 'name': 'Operator'},
    'ARG': {'color': '#991b1b', 'bg': '#fecaca', 'name': 'Argument'},
    'ARGN': {'color': '#9a3412', 'bg': '#fed7aa', 'name': 'Named Arg'},
    'NUM': {'color': '#3730a3', 'bg': '#e0e7ff', 'name': 'Number'},
    'ADV': {'color': '#065f46', 'bg': '#d1fae5', 'name': 'Adverb'},
}

# ============================================================================
# DEMO SETTINGS
# ============================================================================

DEMO_CONFIG = {
    'title': 'HypatiaX NER Demo',
    'subtitle': 'Named Entity Recognition for Tableau Queries',
    'version': '1.0.0',
    'author': 'HypatiaX Team',
    
    'features': {
        'live_processing': True,
        'batch_mode': True,
        'comparison_mode': True,
        'export_results': True,
    },
    
    'ui': {
        'theme': 'gradient',  # 'gradient', 'dark', 'light'
        'animation_speed': 'normal',  # 'fast', 'normal', 'slow'
        'show_confidence': True,
        'show_metrics': True,
    },
    
    'performance': {
        'max_batch_size': 100,
        'timeout_seconds': 30,
        'cache_enabled': True,
    }
}

# ============================================================================
# LINKEDIN DEMO SETTINGS
# ============================================================================

LINKEDIN_CONFIG = {
    'title': '🚀 HypatiaX: AI-Powered Tableau Query Understanding',
    'tagline': 'Transform natural language into Tableau formulas instantly',
    
    'showcase_examples': [
        {
            'input': 'calculate the sum of sales by region',
            'highlight': 'Business Intelligence',
            'icon': '📊',
        },
        {
            'input': 'average profit margin per product',
            'highlight': 'Financial Analytics',
            'icon': '💰',
        },
        {
            'input': 'year over year revenue growth',
            'highlight': 'Trend Analysis',
            'icon': '📈',
        },
    ],
    
    'metrics_to_display': [
        'Processing Speed',
        'Entity Accuracy',
        'Formula Generation Rate',
    ],
    
    'call_to_action': {
        'text': 'Try it yourself!',
        'link': 'https://github.com/yourusername/hypatiax',
    }
}

# ============================================================================
# MOCK DATA (for demo mode when models not available)
# ============================================================================

MOCK_PATTERNS = {
    'desc': {
        'calculate': 'VERB',
        'compute': 'VERB',
        'find': 'VERB',
        'show': 'VERB',
        'sum': 'NOUN',
        'average': 'NOUN',
        'total': 'NOUN',
        'count': 'NOUN',
        'sales': 'NOUN',
        'profit': 'NOUN',
        'revenue': 'NOUN',
        'cost': 'NOUN',
        'of': 'ADP',
        'by': 'ADP',
        'per': 'ADP',
        'across': 'ADP',
    },
    
    'formulas': {
        'SUM': 'OPER',
        'AVG': 'OPER',
        'COUNT': 'OPER',
        'MAX': 'OPER',
        'MIN': 'OPER',
        'IF': 'OPER',
        'THEN': 'OPER',
        'ELSE': 'OPER',
        '[': 'ARG',
        ']': 'ARG',
        '(': 'NUM',
        ')': 'NUM',
        '>': 'ADP',
        '<': 'ADP',
        '=': 'ADP',
    }
}

FORMULA_TEMPLATES = {
    'sum': 'SUM([{field}])',
    'average': 'AVG([{field}])',
    'avg': 'AVG([{field}])',
    'count': 'COUNT([{field}])',
    'total': 'SUM([{field}])',
    'max': 'MAX([{field}])',
    'maximum': 'MAX([{field}])',
    'min': 'MIN([{field}])',
    'minimum': 'MIN([{field}])',
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_examples() -> List[Dict]:
    """Get all demo examples flattened"""
    all_examples = []
    for category, examples in DEMO_EXAMPLES.items():
        for ex in examples:
            ex['example_category'] = category
            all_examples.append(ex)
    return all_examples

def get_examples_by_difficulty(difficulty: str) -> List[Dict]:
    """Get examples filtered by difficulty"""
    all_examples = get_all_examples()
    return [ex for ex in all_examples if ex.get('difficulty') == difficulty]

def get_examples_by_category(category: str) -> List[Dict]:
    """Get examples filtered by category"""
    all_examples = get_all_examples()
    return [ex for ex in all_examples if ex.get('category') == category]

def get_entity_style(label: str) -> Dict:
    """Get style configuration for an entity label"""
    return ENTITY_STYLES.get(label, {
        'color': '#666',
        'bg': '#f3f4f6',
        'name': label
    })

def get_model_path(model_type: str) -> Path:
    """Get path to trained model"""
    return MODEL_CONFIG.get(model_type, {}).get('path')

# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    print("HypatiaX Demo Configuration")
    print("=" * 60)
    print(f"Demo Dir: {DEMO_DIR}")
    print(f"Models Dir: {MODELS_DIR}")
    print(f"\nAvailable Models:")
    for model_type, config in MODEL_CONFIG.items():
        print(f"  - {config['name']}: {config['path']}")
    print(f"\nTotal Examples: {len(get_all_examples())}")
    print(f"Entity Types: {len(ENTITY_STYLES)}")
