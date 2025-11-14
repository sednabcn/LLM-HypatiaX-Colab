#!/usr/bin/env python3
"""
HypatiaX Architecture Migration Script
Extends existing structure with transformers, LLM, agents, and tools
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime


class HypatiaXMigration:
    """Migrates HypatiaX to extended architecture"""
    
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir).resolve()
        self.backup_dir = self.root / "backup_before_extension"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.migration_log = []

    def log(self, message: str, level: str = "INFO"):
        """Log migration message"""
        log_entry = f"[{level}] {message}"
        print(log_entry)
        self.migration_log.append(log_entry)
    
       
    
    def backup_current_structure(self):
        """Create backup of current structure"""
        self.log("=" * 70)
        self.log("CREATING BACKUP OF CURRENT STRUCTURE")
        self.log("=" * 70)
        
        if self.backup_dir.exists():
            self.log(f"⚠️  Backup directory exists: {self.backup_dir}", "WARNING")
            response = input("Remove existing backup? (yes/no): ")
            if response.lower() != 'yes':
                self.log("Migration cancelled by user", "INFO")
                return False
            shutil.rmtree(self.backup_dir)
        
        # Backup critical directories
        critical_dirs = [
            'config', 'core', 'custom_entities', 'custom_ner',
            'datasets', 'data_spacy', 'models', 'mappings',
            'patterns', 'utils', 'scripts_', 'demo', 'docs',
            'examples', 'experiments'
        ]
        
        self.backup_dir.mkdir(exist_ok=True)
        
        for dir_name in critical_dirs:
            src = self.root / dir_name
            if src.exists():
                dst = self.backup_dir / dir_name
                self.log(f"  📦 Backing up {dir_name}...")
                shutil.copytree(src, dst)
        
        self.log(f"✅ Backup created at: {self.backup_dir}\n")
        return True


     
    def create_directory_structure(self):
        """Create new directory structure"""
        self.log("=" * 70)
        self.log("CREATING EXTENDED DIRECTORY STRUCTURE")
        self.log("=" * 70)
        
        # New directories to create
        new_directories = {
            # Tools directory (completely new)
            'tools': [
                'symbolic',
                'numerical',
                'formal',
                'visualization',
                'llm_providers',
                'transformers',
                'validation'
            ],
            
            # Agents directory (completely new)
            'agents': [
                'base',
                'specialists',
                'coordinators',
                'workflows',
                'memory',
                'learning'
            ],

            # Model implementations directory (NEW - separate from models/)
            'model_implementations': [
                 'ner',
                 'transformers',
                 'llm',
                 'agents'
            ],
             
            # Tests directory (completely new)
            'tests': [
                'unit/test_ner',
                'unit/test_transformers',
                'unit/test_llm',
                'unit/test_agents',
                'unit/test_tools',
                'integration',
                'e2e'
            ],
            
            # Requirements directory (completely new)
            'requirements': [],
            
            # Extensions to config/
            'config': [],
            
            # Extensions to core/
            'core/preprocessing': [],
            'core/training': [],
            'core/evaluation': [],
            'core/deployment': [],
            
            # Extensions to custom_ner/
            'custom_ner/queries/tableau': ['transformer', 'hybrid'],
            
            # Extensions to datasets/
            'datasets/queries/tableau': ['transformer', 'llm', 'agent'],
            
            # Extensions to models/ (ONLY for trained artifacts - will be created when saving models)
            'models/queries/tableau/trained_models': ['transformers', 'llm', 'agents'],
            'models/queries/tableau/checkpoints': ['transformers', 'llm', 'agents'],
            'models/queries/tableau/model_configs': [],
        
            
            # Extensions to mappings/
            'mappings': [],
            
            # Extensions to demo/
            'demo': [],
            
            # Extensions to docs/
            'docs': [],
            
            # Extensions to examples/
            'examples': [],
            
            # Extensions to experiments/
            'experiments': ['transformers', 'llm', 'agents', 'hybrid'],
            
            # Extensions to utils/
            'utils': [],
            
            # Extensions to scripts_/
            'scripts_': ['migration'],
        }
        
        for base_dir, subdirs in new_directories.items():
            base_path = self.root / base_dir
            
            # Create base directory if it doesn't exist
            if not base_path.exists():
                base_path.mkdir(parents=True, exist_ok=True)
                self.log(f"  📁 Created {base_dir}/")
            
            # Create subdirectories
            for subdir in subdirs:
                subdir_path = base_path / subdir
                subdir_path.mkdir(parents=True, exist_ok=True)
                self.log(f"  📁 Created {base_dir}/{subdir}/")
                
                # Create __init__.py for Python packages (not for requirements/)
                if base_dir not in ['requirements', 'models/queries/tableau/trained_models',
                                    'models/queries/tableau/checkpoints']:
                    init_file = subdir_path / '__init__.py'
                    if not init_file.exists():
                        init_file.touch()

        for base_dir in ['tools', 'agents', 'tests', 'model_implementations']:
            base_path = self.root / base_dir
            # Extensions to models/if base_path.exists() and base_dir != 'requirements':
            init_file = base_path / '__init__.py'
            if not init_file.exists():
                init_file.touch()
                self.log(f"  ✓ Created {base_dir}/__init__.py")
                    
        self.log("✅ Directory structure created\n")
    
    def create_config_files(self):
        """Create new configuration files"""
        self.log("=" * 70)
        self.log("CREATING CONFIGURATION FILES")
        self.log("=" * 70)
        
        # config/transformer_config.py
        transformer_config = '''"""Transformer model configurations"""
from typing import Dict, Any

class TransformerConfig:
    """Configuration for BERT/T5 models"""
    
    # Model selection
    BERT_MODEL = "bert-base-uncased"
    T5_MODEL = "t5-base"
    
    # Training hyperparameters
    LEARNING_RATE = 5e-5
    BATCH_SIZE = 16
    NUM_EPOCHS = 10
    MAX_LENGTH = 512
    
    # Paths
    TRANSFORMER_MODEL_DIR = "models/queries/tableau/transformers"
    TRANSFORMER_DATA_DIR = "datasets/queries/tableau/transformer"
    
    @classmethod
    def get_config(cls, model_type: str = "bert") -> Dict[str, Any]:
        """Get configuration for specific model type"""
        return {
            "model_name": cls.BERT_MODEL if model_type == "bert" else cls.T5_MODEL,
            "learning_rate": cls.LEARNING_RATE,
            "batch_size": cls.BATCH_SIZE,
            "num_epochs": cls.NUM_EPOCHS,
            "max_length": cls.MAX_LENGTH,
            "model_dir": cls.TRANSFORMER_MODEL_DIR,
            "data_dir": cls.TRANSFORMER_DATA_DIR,
        }
'''
        self._write_file('config/transformer_config.py', transformer_config)
        
        # config/llm_config.py
        llm_config = '''"""LLM provider configurations"""
import os
from typing import Optional

class LLMConfig:
    """Configuration for LLM providers"""
    
    # API Keys (should be in .env)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    
    # Default models
    OPENAI_MODEL = "gpt-4-turbo-preview"
    ANTHROPIC_MODEL = "claude-3-opus-20240229"
    DEEPSEEK_MODEL = "deepseek-math-7b-instruct"
    
    # Generation parameters
    TEMPERATURE = 0.0  # Deterministic for math
    MAX_TOKENS = 2000
    
    # Paths
    LLM_PROMPTS_DIR = "models/queries/tableau/llm/prompt_templates"
    LLM_EXAMPLES_DIR = "models/queries/tableau/llm/few_shot_examples"
    
    @classmethod
    def get_provider_config(cls, provider: str = "openai"):
        """Get configuration for specific provider"""
        configs = {
            "openai": {
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.OPENAI_MODEL,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS,
            },
            "anthropic": {
                "api_key": cls.ANTHROPIC_API_KEY,
                "model": cls.ANTHROPIC_MODEL,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS,
            },
            "deepseek": {
                "api_key": cls.DEEPSEEK_API_KEY,
                "model": cls.DEEPSEEK_MODEL,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS,
            }
        }
        return configs.get(provider, configs["openai"])
'''
        self._write_file('config/llm_config.py', llm_config)
        
        # config/agent_config.py
        agent_config = '''"""Agent system configurations"""

class AgentConfig:
    """Configuration for AI agent system"""
    
    # Agent types
    PARSER_AGENT = "parser_agent"
    GENERATOR_AGENT = "generator_agent"
    VALIDATOR_AGENT = "validator_agent"
    REFINER_AGENT = "refiner_agent"
    EXPLAINER_AGENT = "explainer_agent"
    
    # Workflow settings
    MAX_ITERATIONS = 10
    TIMEOUT_SECONDS = 300
    
    # Memory settings
    WORKING_MEMORY_SIZE = 10
    EPISODIC_MEMORY_SIZE = 100
    
    # Learning settings
    ENABLE_LEARNING = True
    FEEDBACK_STORAGE_PATH = "datasets/queries/tableau/agent/feedback_data.json"
    
    # Paths
    AGENT_MODELS_DIR = "models/queries/tableau/agents"
    AGENT_DATA_DIR = "datasets/queries/tableau/agent"
'''
        self._write_file('config/agent_config.py', agent_config)
        
        # config/tool_config.py
        tool_config = '''"""External tool configurations"""

class ToolConfig:
    """Configuration for external tools"""
    
    # Symbolic computation
    USE_SYMPY = True
    USE_MATHEMATICA = False
    MATHEMATICA_PATH = None
    
    # Numerical computation
    USE_NUMPY = True
    USE_SCIPY = True
    
    # Formal verification
    USE_LEAN = False
    LEAN_PATH = None
    
    # Visualization
    DEFAULT_PLOT_BACKEND = "plotly"  # or "matplotlib"
    
    # Validation
    SYMBOLIC_VALIDATION = True
    NUMERICAL_VALIDATION = True
    DIMENSIONAL_VALIDATION = True
'''
        self._write_file('config/tool_config.py', tool_config)
        
        self.log("✅ Configuration files created\n")
    
    def create_core_extensions(self):
        """Create extensions to core/ directory"""
        self.log("=" * 70)
        self.log("CREATING CORE EXTENSIONS")
        self.log("=" * 70)
        
        # core/preprocessing/transformer_prep.py
        transformer_prep = '''"""Transformer data preprocessing"""
from transformers import AutoTokenizer
from typing import List, Dict, Any
import json

class TransformerPreprocessor:
    """Preprocess data for transformer models"""
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def prepare_seq2seq_data(
        self, 
        input_texts: List[str], 
        target_texts: List[str],
        max_length: int = 512
    ) -> Dict[str, Any]:
        """Prepare data for sequence-to-sequence task"""
        inputs = self.tokenizer(
            input_texts,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        targets = self.tokenizer(
            target_texts,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"],
            "labels": targets["input_ids"]
        }
    
    def save_prepared_data(self, data: Dict, output_path: str):
        """Save prepared data to file"""
        # Save as JSON for now (can be extended to other formats)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
'''
        self._write_file('core/preprocessing/transformer_prep.py', transformer_prep)
        
        # core/preprocessing/llm_prep.py
        llm_prep = '''"""LLM prompt preprocessing"""
from typing import List, Dict, Any

class LLMPreprocessor:
    """Prepare prompts for LLM models"""
    
    def format_few_shot_prompt(
        self,
        query: str,
        examples: List[Dict[str, str]],
        system_message: str = "You are a mathematical expression mapper."
    ) -> str:
        """Format few-shot learning prompt"""
        prompt_parts = [system_message, ""]
        
        # Add examples
        for i, example in enumerate(examples, 1):
            prompt_parts.append(f"Example {i}:")
            prompt_parts.append(f"Query: {example['query']}")
            prompt_parts.append(f"Expression: {example['expression']}")
            prompt_parts.append("")
        
        # Add current query
        prompt_parts.append("Now, for the following query:")
        prompt_parts.append(f"Query: {query}")
        prompt_parts.append("Expression:")
        
        return "\n".join(prompt_parts)
    
    def format_chain_of_thought_prompt(self, query: str) -> str:
        """Format chain-of-thought reasoning prompt"""
        return f"""Let's solve this step by step:

Query: {query}

Step 1: Identify the mathematical operation
Step 2: Extract relevant variables and parameters
Step 3: Construct the mathematical expression
Step 4: Verify the expression is correct

Expression:"""
'''
        self._write_file('core/preprocessing/llm_prep.py', llm_prep)
        
        # core/training/training_transformer.py
        training_transformer = '''"""Transformer model training"""
from transformers import AutoModelForSeq2SeqLM, Trainer, TrainingArguments
from typing import Dict, Any
import torch

class TransformerTrainer:
    """Train transformer models for expression mapping"""
    
    def __init__(self, model_name: str = "t5-base", output_dir: str = "models/queries/tableau/transformers"):
        self.model_name = model_name
        self.output_dir = output_dir
        self.model = None
    
    def initialize_model(self):
        """Initialize model for training"""
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
    
    def train(
        self,
        train_dataset,
        eval_dataset=None,
        num_epochs: int = 10,
        learning_rate: float = 5e-5,
        batch_size: int = 16
    ):
        """Train the transformer model"""
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            evaluation_strategy="epoch" if eval_dataset else "no",
            save_strategy="epoch",
            logging_dir=f"{self.output_dir}/logs",
            load_best_model_at_end=True if eval_dataset else False,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
        )
        
        trainer.train()
        return trainer
    
    def save_model(self, path: str = None):
        """Save trained model"""
        save_path = path or f"{self.output_dir}/final_model"
        self.model.save_pretrained(save_path)
'''
        self._write_file('core/training/training_transformer.py', training_transformer)
        
        self.log("✅ Core extensions created\n")
    
    def create_tools_directory(self):
        """Create tools directory with integrations"""
        self.log("=" * 70)
        self.log("CREATING TOOLS DIRECTORY")
        self.log("=" * 70)
        
        # tools/symbolic/sympy_wrapper.py
        sympy_wrapper = '''"""SymPy integration wrapper"""
import sympy as sp
from typing import Any, Optional

class SymPyWrapper:
    """Wrapper for SymPy symbolic computation"""
    
    def __init__(self):
        self.symbols_cache = {}
    
    def parse_expression(self, expr_string: str) -> Optional[sp.Expr]:
        """Parse string to SymPy expression"""
        try:
            return sp.sympify(expr_string)
        except Exception as e:
            print(f"Failed to parse expression: {e}")
            return None
    
    def simplify(self, expression: Any) -> Any:
        """Simplify expression"""
        if isinstance(expression, str):
            expression = self.parse_expression(expression)
        return sp.simplify(expression)
    
    def differentiate(self, expression: Any, variable: str = 'x') -> Any:
        """Compute derivative"""
        if isinstance(expression, str):
            expression = self.parse_expression(expression)
        var = sp.Symbol(variable)
        return sp.diff(expression, var)
    
    def integrate(self, expression: Any, variable: str = 'x', 
                 lower: Optional[float] = None, upper: Optional[float] = None) -> Any:
        """Compute integral"""
        if isinstance(expression, str):
            expression = self.parse_expression(expression)
        var = sp.Symbol(variable)
        
        if lower is not None and upper is not None:
            return sp.integrate(expression, (var, lower, upper))
        return sp.integrate(expression, var)
    
    def validate_expression(self, expr1: str, expr2: str) -> bool:
        """Check if two expressions are equivalent"""
        try:
            e1 = self.parse_expression(expr1)
            e2 = self.parse_expression(expr2)
            return sp.simplify(e1 - e2) == 0
        except:
            return False
'''
        self._write_file('tools/symbolic/sympy_wrapper.py', sympy_wrapper)
        
        # tools/llm_providers/base_provider.py
        base_provider = '''"""Base LLM provider interface"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate with tool/function calling"""
        pass
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Chat completion"""
        pass
    
    def set_config(self, **kwargs):
        """Update configuration"""
        self.config.update(kwargs)
'''
        self._write_file('tools/llm_providers/base_provider.py', base_provider)
        
        # tools/llm_providers/openai_provider.py
        openai_provider = '''"""OpenAI provider implementation"""
from typing import Dict, List, Any
from .base_provider import BaseLLMProvider

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", **kwargs):
        super().__init__(api_key, **kwargs)
        if OpenAI is None:
            raise ImportError("openai package not installed. Install: pip install openai")
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.0),
            max_tokens=kwargs.get("max_tokens", 2000),
        )
        return response.choices[0].message.content
    
    def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate with tool calling"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
            temperature=kwargs.get("temperature", 0.0),
            max_tokens=kwargs.get("max_tokens", 2000),
        )
        
        message = response.choices[0].message
        return {
            "content": message.content,
            "tool_calls": message.tool_calls if hasattr(message, "tool_calls") else None
        }
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.0),
            max_tokens=kwargs.get("max_tokens", 2000),
        )
        return response.choices[0].message.content
'''
        self._write_file('tools/llm_providers/openai_provider.py', openai_provider)
        
        # tools/validation/symbolic_validator.py
        symbolic_validator = '''"""Symbolic validation using SymPy"""
from tools.symbolic.sympy_wrapper import SymPyWrapper
from typing import Dict, Any

class SymbolicValidator:
    """Validate expressions using symbolic computation"""
    
    def __init__(self):
        self.sympy = SymPyWrapper()
    
    def validate_equivalence(self, expr1: str, expr2: str) -> Dict[str, Any]:
        """Check if two expressions are equivalent"""
        is_valid = self.sympy.validate_expression(expr1, expr2)
        
        return {
            "valid": is_valid,
            "method": "symbolic_equivalence",
            "expr1": expr1,
            "expr2": expr2
        }
    
    def validate_derivative(self, expression: str, variable: str = 'x') -> Dict[str, Any]:
        """Validate if expression can be differentiated"""
        try:
            derivative = self.sympy.differentiate(expression, variable)
            return {
                "valid": True,
                "derivative": str(derivative),
                "original": expression
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "original": expression
            }
'''
        self._write_file('tools/validation/symbolic_validator.py', symbolic_validator)
        
        self.log("✅ Tools directory created\n")
    
    def create_agents_directory(self):
        """Create agents directory"""
        self.log("=" * 70)
        self.log("CREATING AGENTS DIRECTORY")
        self.log("=" * 70)
        
        # agents/base/agent.py
        base_agent = '''"""Base agent class"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, role: str, tools: Optional[List] = None):
        self.name = name
        self.role = role
        self.tools = tools or []
        self.memory = []
        self.created_at = datetime.now()
    
    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Any:
        """Execute agent task"""
        pass
    
    def remember(self, item: Any):
        """Store item in agent memory"""
        self.memory.append({
            'timestamp': datetime.now().isoformat(),
            'content': item
        })
    
    def recall(self, n: int = 10) -> List:
        """Recall last n items from memory"""
        return self.memory[-n:]
    
    def clear_memory(self):
        """Clear agent memory"""
        self.memory = []
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', role='{self.role}')"
'''
        self._write_file('agents/base/agent.py', base_agent)
        
        # agents/specialists/parser_agent.py
        parser_agent = '''"""Parser agent for query understanding"""
from agents.base.agent import BaseAgent
from typing import Dict, Any

class ParserAgent(BaseAgent):
    """Agent specialized in parsing mathematical queries"""
    
    def __init__(self, ner_extractor=None):
        super().__init__(
            name="ParserAgent",
            role="Mathematical Query Parser"
        )
        self.ner_extractor = ner_extractor
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Parse query and extract mathematical intent"""
        query = task.get('query', '')
        
        # Extract entities using NER if available
        entities = []
        if self.ner_extractor:
            entities = self.ner_extractor.extract(query)
        
        # Analyze intent
        intent = self._analyze_intent(query, entities)
        
        # Remember this interaction
        self.remember({
            'query': query,
            'entities': entities,
            'intent': intent
        })
        
        return {
            'query': query,
            'entities': entities,
            'intent': intent,
            'agent': self.name
        }
    
    def _analyze_intent(self, query: str, entities: list) -> Dict[str, Any]:
        """Analyze mathematical intent from query"""
        query_lower = query.lower()
        
        # Simple heuristics
        operations = []
        if 'integral' in query_lower or 'integrate' in query_lower:
            operations.append('integration')
        if 'derivative' in query_lower or 'differentiate' in query_lower:
            operations.append('differentiation')
        if 'solve' in query_lower:
            operations.append('equation_solving')
        if 'simplify' in query_lower:
            operations.append('simplification')
        
        return {
            'operations': operations,
            'entity_count': len(entities),
            'complexity': self._estimate_complexity(query, entities)
        }
    
    def _estimate_complexity(self, query: str, entities: list) -> str:
        """Estimate query complexity"""
        if len(entities) > 5:
            return 'high'
        elif len(entities) > 2:
            return 'medium'
        return 'low'
'''
        self._write_file('agents/specialists/parser_agent.py', parser_agent)
        
        # agents/workflows/hybrid_workflow.py
        hybrid_workflow = '''"""Hybrid workflow combining multiple technologies"""
from typing import Dict, Any, List, Optional

class HybridWorkflow:
    """Workflow that combines NER, Transformers, LLM, and Agents"""
    
    def __init__(self):
        self.agents = []
        self.history = []
    
    def add_agent(self, agent):
        """Add agent to workflow"""
        self.agents.append(agent)
    
    def execute(self, query: str) -> Dict[str, Any]:
        """Execute hybrid workflow"""
        result = {
            'query': query,
            'steps': []
        }
        
        # Execute each agent in sequence
        task = {'query': query}
        for agent in self.agents:
            step_result = agent.execute(task)
            result['steps'].append({
                'agent': agent.name,
                'result': step_result
            })
            # Pass result to next agent
            task.update(step_result)
        
        # Store in history
        self.history.append(result)
        
        return result
    
    def get_history(self, n: int = 10) -> List[Dict]:
        """Get last n executions"""
        return self.history[-n:]
'''
        self._write_file('agents/workflows/hybrid_workflow.py', hybrid_workflow)
        
        self.log("✅ Agents directory created\n")
    
    def create_mappings_extensions(self):
        """Create new mapping strategies"""
        self.log("=" * 70)
        self.log("CREATING MAPPING EXTENSIONS")
        self.log("=" * 70)
        
        # mappings/transformer_mapping.py
        transformer_mapping = '''"""Transformer-based expression mapping"""
from typing import Dict, Any

class TransformerMapper:
    """Map queries using transformer models"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None
        # Initialize transformer model here
    
    def map(self, query: str) -> Dict[str, Any]:
        """Map query to expression using transformer"""
        # TODO: Implement transformer-based mapping
        return {
            'query': query,
            'expression': None,
            'method': 'transformer',
            'confidence': 0.0
        }
'''
        self._write_file('mappings/transformer_mapping.py', transformer_mapping)
        
        # mappings/llm_mapping.py
        llm_mapping = '''"""LLM-based expression mapping"""
from typing import Dict, Any, Optional
from tools.llm_providers.base_provider import BaseLLMProvider

class LLMMapper:
    """Map queries using LLM providers"""
    
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider
    
    def map(self, query: str, use_few_shot: bool = True) -> Dict[str, Any]:
        """Map query to expression using LLM"""
        if not self.llm_provider:
            return {
                'query': query,
                'expression': None,
                'method': 'llm',
                'error': 'No LLM provider configured'
            }
        
        # Create prompt
        prompt = self._create_prompt(query, use_few_shot)
        
        # Generate expression
        response = self.llm_provider.generate(prompt)
        
        return {
            'query': query,
            'expression': response,
            'method': 'llm',
            'provider': self.llm_provider.__class__.__name__
        }
    
    def _create_prompt(self, query: str, use_few_shot: bool) -> str:
        """Create prompt for LLM"""
        base_prompt = f"Convert the following natural language query to a mathematical expression:\n\nQuery: {query}\nExpression:"
        
        if use_few_shot:
            # Add few-shot examples
            examples = """Here are some examples:

Query: Find the integral of x squared
Expression: ∫x² dx

Query: What is the derivative of sine x?
Expression: d/dx[sin(x)]

Query: Solve x squared equals 4
Expression: x² = 4

"""
            return examples + base_prompt
        
        return base_prompt
'''
        self._write_file('mappings/llm_mapping.py', llm_mapping)
        
        # mappings/agent_mapping.py
        agent_mapping = '''"""Agent-based expression mapping"""
from typing import Dict, Any, List
from agents.base.agent import BaseAgent

class AgentMapper:
    """Map queries using AI agents"""
    
    def __init__(self, agents: List[BaseAgent] = None):
        self.agents = agents or []
    
    def add_agent(self, agent: BaseAgent):
        """Add agent to mapper"""
        self.agents.append(agent)
    
    def map(self, query: str) -> Dict[str, Any]:
        """Map query using agent workflow"""
        results = []
        current_task = {'query': query}
        
        for agent in self.agents:
            result = agent.execute(current_task)
            results.append({
                'agent': agent.name,
                'output': result
            })
            current_task.update(result)
        
        return {
            'query': query,
            'expression': current_task.get('expression'),
            'method': 'agent',
            'workflow': results
        }
'''
        self._write_file('mappings/agent_mapping.py', agent_mapping)
        
        # mappings/hybrid_mapping.py
        hybrid_mapping = '''"""Hybrid mapping combining all methods"""
from typing import Dict, Any, Optional, List

class HybridMapper:
    """Ensemble mapper using multiple strategies"""
    
    def __init__(
        self,
        ner_mapper=None,
        transformer_mapper=None,
        llm_mapper=None,
        agent_mapper=None
    ):
        self.ner_mapper = ner_mapper
        self.transformer_mapper = transformer_mapper
        self.llm_mapper = llm_mapper
        self.agent_mapper = agent_mapper
    
    def map(
        self,
        query: str,
        use_ner: bool = True,
        use_transformer: bool = True,
        use_llm: bool = True,
        use_agents: bool = False
    ) -> Dict[str, Any]:
        """Map using multiple strategies and combine results"""
        results = {
            'query': query,
            'methods': {}
        }
        
        # Try NER-based mapping
        if use_ner and self.ner_mapper:
            try:
                results['methods']['ner'] = self.ner_mapper.map(query)
            except Exception as e:
                results['methods']['ner'] = {'error': str(e)}
        
        # Try transformer-based mapping
        if use_transformer and self.transformer_mapper:
            try:
                results['methods']['transformer'] = self.transformer_mapper.map(query)
            except Exception as e:
                results['methods']['transformer'] = {'error': str(e)}
        
        # Try LLM-based mapping
        if use_llm and self.llm_mapper:
            try:
                results['methods']['llm'] = self.llm_mapper.map(query)
            except Exception as e:
                results['methods']['llm'] = {'error': str(e)}
        
        # Try agent-based mapping
        if use_agents and self.agent_mapper:
            try:
                results['methods']['agent'] = self.agent_mapper.map(query)
            except Exception as e:
                results['methods']['agent'] = {'error': str(e)}
        
        # Select best result (simple strategy: prefer LLM > Transformer > NER)
        results['best_expression'] = self._select_best(results['methods'])
        
        return results
    
    def _select_best(self, methods: Dict) -> Optional[str]:
        """Select best expression from multiple methods"""
        # Priority: agent > llm > transformer > ner
        for method in ['agent', 'llm', 'transformer', 'ner']:
            if method in methods and 'expression' in methods[method]:
                expr = methods[method]['expression']
                if expr:
                    return expr
        return None
'''
        self._write_file('mappings/hybrid_mapping.py', hybrid_mapping)
        
        self.log("✅ Mapping extensions created\n")
    
    def create_requirements_files(self):
        """Create requirements files"""
        self.log("=" * 70)
        self.log("CREATING REQUIREMENTS FILES")
        self.log("=" * 70)
        
        # requirements/base.txt
        base_req = '''# Core dependencies
numpy>=1.24.0
pandas>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
'''
        self._write_file('requirements/base.txt', base_req)
        
        # requirements/ner.txt
        ner_req = '''-r base.txt

# NER dependencies (existing)
spacy>=3.7.0
spacy-transformers>=1.3.0
'''
        self._write_file('requirements/ner.txt', ner_req)
        
        # requirements/transformers.txt
        transformer_req = '''-r base.txt

# Transformer dependencies
transformers>=4.35.0
torch>=2.1.0
tokenizers>=0.15.0
sentencepiece>=0.1.99
accelerate>=0.25.0
datasets>=2.15.0
'''
        self._write_file('requirements/transformers.txt', transformer_req)
        
        # requirements/llm.txt
        llm_req = '''-r base.txt

# LLM provider SDKs
openai>=1.3.0
anthropic>=0.8.0
langchain>=0.1.0
langchain-openai>=0.0.2
langchain-anthropic>=0.0.2
tiktoken>=0.5.0
'''
        self._write_file('requirements/llm.txt', llm_req)
        
        # requirements/agents.txt
        agent_req = '''-r llm.txt

# Agent frameworks
langgraph>=0.0.20
crewai>=0.1.0
'''
        self._write_file('requirements/agents.txt', agent_req)
        
        # requirements/tools.txt
        tools_req = '''-r base.txt

# Symbolic computation
sympy>=1.12

# Numerical computation
scipy>=1.11.0

# Visualization
plotly>=5.17.0
matplotlib>=3.8.0
'''
        self._write_file('requirements/tools.txt', tools_req)
        
        # requirements/dev.txt
        dev_req = '''-r base.txt
-r ner.txt
-r transformers.txt
-r llm.txt
-r agents.txt
-r tools.txt

# Development tools
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.9.0
ruff>=0.1.0
mypy>=1.5.0
ipython>=8.17.0
jupyter>=1.0.0
'''
        self._write_file('requirements/dev.txt', dev_req)
        
        self.log("✅ Requirements files created\n")
    
    def create_examples(self):
        """Create example usage scripts"""
        self.log("=" * 70)
        self.log("CREATING EXAMPLE SCRIPTS")
        self.log("=" * 70)
        
        # examples/transformer_example.py
        transformer_example = '''"""Example: Using Transformer-based mapping"""
from mappings.transformer_mapping import TransformerMapper

def main():
    """Demonstrate transformer mapping"""
    print("Transformer-based Expression Mapping Example\n")
    
    # Initialize mapper
    mapper = TransformerMapper()
    
    # Example queries
    queries = [
        "Find the integral of x squared",
        "What is the derivative of sine x?",
        "Solve the equation x squared equals 4"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        result = mapper.map(query)
        print(f"Expression: {result.get('expression', 'N/A')}")
        print(f"Method: {result['method']}")
        print()

if __name__ == "__main__":
    main()
'''
        self._write_file('examples/transformer_example.py', transformer_example)
        
        # examples/llm_example.py
        llm_example = '''"""Example: Using LLM-based mapping"""
from tools.llm_providers.openai_provider import OpenAIProvider
from mappings.llm_mapping import LLMMapper
import os

def main():
    """Demonstrate LLM mapping"""
    print("LLM-based Expression Mapping Example\n")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return
    
    # Initialize LLM provider
    llm = OpenAIProvider(api_key=api_key)
    
    # Initialize mapper
    mapper = LLMMapper(llm_provider=llm)
    
    # Example queries
    queries = [
        "Find the integral of x squared from 0 to 1",
        "What is the derivative of cos(x)?",
        "Solve dy/dx = 2x"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        result = mapper.map(query, use_few_shot=True)
        print(f"Expression: {result.get('expression', 'N/A')}")
        print(f"Provider: {result.get('provider', 'N/A')}")
        print()

if __name__ == "__main__":
    main()
'''
        self._write_file('examples/llm_example.py', llm_example)
        
        # examples/agent_example.py
        agent_example = '''"""Example: Using Agent-based mapping"""
from agents.specialists.parser_agent import ParserAgent
from agents.workflows.hybrid_workflow import HybridWorkflow

def main():
    """Demonstrate agent workflow"""
    print("Agent-based Expression Mapping Example\n")
    
    # Create workflow
    workflow = HybridWorkflow()
    
    # Add parser agent
    parser = ParserAgent()
    workflow.add_agent(parser)
    
    # Example query
    query = "Find the integral of x squared from 0 to 1"
    
    print(f"Query: {query}\n")
    
    # Execute workflow
    result = workflow.execute(query)
    
    print("Workflow Results:")
    for step in result['steps']:
        print(f"  Agent: {step['agent']}")
        print(f"  Output: {step['result']}")
        print()

if __name__ == "__main__":
    main()
'''
        self._write_file('examples/agent_example.py', agent_example)
        
        # examples/hybrid_example.py
        hybrid_example = '''"""Example: Using Hybrid mapping (all methods)"""
from mappings.hybrid_mapping import HybridMapper
from tools.llm_providers.openai_provider import OpenAIProvider
from mappings.llm_mapping import LLMMapper
import os

def main():
    """Demonstrate hybrid mapping combining all methods"""
    print("Hybrid Expression Mapping Example\n")
    print("This combines NER + Transformer + LLM + Agents\n")
    
    # Initialize LLM mapper (if API key available)
    llm_mapper = None
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm = OpenAIProvider(api_key=api_key)
        llm_mapper = LLMMapper(llm_provider=llm)
    else:
        print("⚠️  OPENAI_API_KEY not set, LLM mapping will be skipped\n")
    
    # Initialize hybrid mapper
    hybrid = HybridMapper(llm_mapper=llm_mapper)
    
    # Example query
    query = "Find the derivative of sin(x) * cos(x)"
    
    print(f"Query: {query}\n")
    
    # Map using all available methods
    result = hybrid.map(
        query,
        use_ner=True,
        use_transformer=True,
        use_llm=bool(llm_mapper),
        use_agents=False
    )
    
    print("Results from each method:")
    for method, output in result['methods'].items():
        print(f"  {method.upper()}:")
        if 'error' in output:
            print(f"    Error: {output['error']}")
        else:
            print(f"    Expression: {output.get('expression', 'N/A')}")
    
    print(f"\nBest Expression: {result['best_expression']}")

if __name__ == "__main__":
    main()
'''
        self._write_file('examples/hybrid_example.py', hybrid_example)
        
        self.log("✅ Example scripts created\n")
    
    def create_env_example(self):
        """Create .env.example file"""
        self.log("=" * 70)
        self.log("CREATING ENVIRONMENT TEMPLATE")
        self.log("=" * 70)
        
        env_content = '''# HypatiaX Configuration

# Environment
ENVIRONMENT=development
DEBUG=true

# NER Configuration (existing)
NER_MODEL_PATH=models/queries/tableau/trained_models/Combined_multi_task_data_400.0.5.8

# LLM API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here

# LLM Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=2000

# Transformer Configuration
TRANSFORMER_MODEL_PATH=models/queries/tableau/transformers/t5_formula_mapper
USE_GPU=false

# Agent Configuration
AGENT_MAX_ITERATIONS=10
AGENT_TIMEOUT=300
ENABLE_AGENT_LEARNING=true

# Tool Configuration
USE_SYMPY=true
USE_MATHEMATICA=false
USE_LEAN=false

# Database
DATABASE_URL=sqlite:///data/hypatiax.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/hypatiax.log

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
'''
        self._write_file('.env.example', env_content)
        
        self.log("✅ Environment template created\n")
    
    def create_documentation(self):
        """Create documentation files"""
        self.log("=" * 70)
        self.log("CREATING DOCUMENTATION")
        self.log("=" * 70)
        
        # docs/architecture.md
        architecture_doc = '''# HypatiaX Architecture

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
'''
        self._write_file('docs/architecture.md', architecture_doc)
        
        self.log("✅ Documentation created\n")
    
    def create_readme_update(self):
        """Create updated README"""
        self.log("=" * 70)
        self.log("CREATING UPDATED README")
        self.log("=" * 70)
    
        readme_content = '''# HypatiaX - AI-Powered Analytical Expression Mapper

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
'''
        self._write_file('README.md', readme_content)
    
        self.log("✅ README updated\n")

        
    def update_gitignore(self):
        """Update .gitignore with new patterns"""
        self.log("=" * 70)
        self.log("UPDATING .GITIGNORE")
        self.log("=" * 70)
        
        gitignore_additions = '''
# Extended HypatiaX patterns
__pycache__/
*.py[cod]
.env
.env.local
logs/
*.log
*.bin
*.pt
*.pth
models/queries/tableau/transformers/*/checkpoint-*/
backup_*/
*.bak
.vscode/
.idea/
.DS_Store
.coverage
htmlcov/
.pytest_cache/
'''
        
        gitignore_path = self.root / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'a') as f:
                f.write(gitignore_additions)
            self.log("  ✓ Updated existing .gitignore")
        else:
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_additions.strip())
            self.log("  ✓ Created new .gitignore")
        
        self.log("✅ .gitignore updated\n")
    
    def save_migration_log(self):
        """Save migration log"""
        log_path = self.root / f"migration_log_{self.timestamp}.txt"
        with open(log_path, 'w') as f:
            f.write("\n".join(self.migration_log))
        self.log(f"✅ Migration log saved to: {log_path}")
    
    def _write_file(self, relative_path: str, content: str):
        """Helper to write file with logging"""
        file_path = self.root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        self.log(f"  ✓ Created {relative_path}")
    
    def run_migration(self):
        """Execute full migration"""
        self.log("=" * 70)
        self.log("HYPATIAX ARCHITECTURE EXTENSION MIGRATION")
        self.log("=" * 70)
        self.log("")
        
        # Execute all migration steps
        if not self.backup_current_structure():
            return False
        
        self.create_directory_structure()
        self.create_config_files()
        self.create_core_extensions()
        self.create_tools_directory()
        self.create_agents_directory()
        self.create_mappings_extensions()
        self.create_requirements_files()
        self.create_examples()
        self.create_env_example()
        self.create_documentation()
        self.create_readme_update() 
        self.update_gitignore()
        self.save_migration_log()
        
        # Final summary
        self.log("")
        self.log("=" * 70)
        self.log("✅ MIGRATION COMPLETE!")
        self.log("=" * 70)
        self.log("")
        self.log("Next steps:")
        self.log("1. Review the created structure")
        self.log("2. Install dependencies:")
        self.log("   pip install -r requirements/ner.txt")
        self.log("   pip install -r requirements/llm.txt")
        self.log("   pip install -r requirements/agents.txt")
        self.log("3. Copy .env.example to .env and configure")
        self.log("4. Test examples:")
        self.log("   python examples/basic_usage.py")
        self.log("   python examples/llm_example.py")
        self.log("   python examples/agent_example.py")
        self.log("")
        self.log(f"Backup: {self.backup_dir}")
        self.log(f"Log: migration_log_{self.timestamp}.txt")
        self.log("")
        
        return True


def main():
    """Main migration entry point"""
    import sys
    
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    migration = HypatiaXMigration(root_dir)
    success = migration.run_migration()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
