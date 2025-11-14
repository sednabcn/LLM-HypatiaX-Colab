#!/usr/bin/python3
"""
Improved Description-to-Formula Mapping System
Supports multiple strategies: vocab mapping, sentence mapping, regex, NER-based, and ML models
"""

import re
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod


class MappingStrategy(ABC):
    """Abstract base class for mapping strategies"""
    
    @abstractmethod
    def map(self, description: str, ner_entities: Optional[List] = None) -> str:
        """Map description to formula"""
        pass


class VocabToVocabStrategy(MappingStrategy):
    """Map vocabulary terms directly (e.g., 'average' -> 'AVG')"""
    
    def __init__(self):
        self.vocab_map = {
            "total": "SUM",
            "sum": "SUM",
            "average": "AVG",
            "mean": "AVG",
            "median": "MEDIAN",
            "count": "COUNT",
            "number of": "COUNT",
            "unique": "COUNTD",
            "distinct": "COUNTD",
            "maximum": "MAX",
            "max": "MAX",
            "minimum": "MIN",
            "min": "MIN",
            "standard deviation": "STDEV",
            "variance": "VAR"
        }
    
    def map(self, description: str, ner_entities: Optional[List] = None) -> str:
        desc_lower = description.lower()
        
        # Extract column name
        column_name = self._extract_column_name(description)
        if not column_name:
            return "Error: Column name not found"
        
        # Find matching operation
        for keyword, formula_func in self.vocab_map.items():
            if keyword in desc_lower:
                return f"{formula_func}([{column_name}])"
        
        return "Error: Operation not recognized"
    
    def _extract_column_name(self, description: str) -> Optional[str]:
        """Extract column name from description"""
        # Pattern 1: "of [Column Name]"
        match = re.search(r"of ([A-Z][a-z]+(?: [A-Z][a-z]+)*)", description)
        if match:
            return match.group(1)
        
        # Pattern 2: "for [Column Name]"
        match = re.search(r"for ([A-Z][a-z]+(?: [A-Z][a-z]+)*)", description)
        if match:
            return match.group(1)
        
        # Pattern 3: Last capitalized words
        words = description.split()
        capitalized = [w for w in words if w[0].isupper() and len(w) > 1]
        if capitalized:
            return ' '.join(capitalized[-2:]) if len(capitalized) >= 2 else capitalized[-1]
        
        return None


class SentenceToSentenceStrategy(MappingStrategy):
    """Map complete sentences using pattern matching"""
    
    def __init__(self):
        self.mapping_rules = {
            "sum of sales by year": "SUM([Sales]) GROUP BY [Year]",
            "average cost per item": "AVG([Cost]) / COUNT([Item])",
            "total revenue by region": "SUM([Revenue]) GROUP BY [Region]",
            "count of unique customers": "COUNTD([Customer ID])",
            "average of petal length": "AVG([Petal Length])",
            "calculate area of circle": "A = pi * r^2",
            "compute volume of sphere": "V = (4/3) * pi * r^3"
        }
    
    def map(self, description: str, ner_entities: Optional[List] = None) -> str:
        desc_lower = description.lower()
        
        # Exact match
        if desc_lower in self.mapping_rules:
            return self.mapping_rules[desc_lower]
        
        # Fuzzy match (contains pattern)
        for pattern, formula in self.mapping_rules.items():
            if pattern in desc_lower:
                return formula
        
        return "Error: No matching sentence pattern found"


class RegexStrategy(MappingStrategy):
    """Use regex patterns to extract components and build formulas"""
    
    def __init__(self):
        self.operation_patterns = {
            r"(total|sum)\s+of\s+(\w+(?:\s+\w+)*)": ("SUM", 1),
            r"(average|mean)\s+of\s+(\w+(?:\s+\w+)*)": ("AVG", 1),
            r"(count|number)\s+of\s+(\w+(?:\s+\w+)*)": ("COUNT", 1),
            r"(max|maximum)\s+of\s+(\w+(?:\s+\w+)*)": ("MAX", 1),
            r"(min|minimum)\s+of\s+(\w+(?:\s+\w+)*)": ("MIN", 1),
        }
        
        self.groupby_pattern = r"by\s+(\w+(?:\s+\w+)*)"
    
    def map(self, description: str, ner_entities: Optional[List] = None) -> str:
        desc_lower = description.lower()
        
        # Find operation and column
        operation = None
        column = None
        
        for pattern, (op, group_idx) in self.operation_patterns.items():
            match = re.search(pattern, desc_lower)
            if match:
                operation = op
                column = match.group(2)
                break
        
        if not operation or not column:
            return "Error: Could not parse operation or column"
        
        # Format column name (capitalize each word)
        column_formatted = ' '.join(word.capitalize() for word in column.split())
        formula = f"{operation}([{column_formatted}])"
        
        # Check for GROUP BY
        groupby_match = re.search(self.groupby_pattern, desc_lower)
        if groupby_match:
            groupby_col = groupby_match.group(1)
            groupby_formatted = ' '.join(word.capitalize() for word in groupby_col.split())
            formula += f" GROUP BY [{groupby_formatted}]"
        
        return formula


class NERBasedStrategy(MappingStrategy):
    """Use NER entities to construct formulas"""
    
    def __init__(self):
        self.entity_to_function = {
            "OPER": {"sum": "SUM", "average": "AVG", "count": "COUNT", 
                     "max": "MAX", "min": "MIN", "total": "SUM"},
            "TARGET": {},  # Extracted from NER
            "OBJECT": {},  # Context for formula selection
        }
    
    def map(self, description: str, ner_entities: Optional[List] = None) -> str:
        if not ner_entities:
            return "Error: NER entities required for this strategy"
        
        # Extract entity values
        operation = None
        target = None
        object_name = None
        
        for entity in ner_entities:
            label = entity.get('label', '')
            text = entity.get('text', '').lower()
            
            if label == 'OPER':
                operation = self.entity_to_function['OPER'].get(text, text.upper())
            elif label == 'TARGET':
                target = text
            elif label == 'OBJECT':
                object_name = text
        
        # Build formula based on entities
        if operation and target:
            if target == 'area' and object_name == 'circle':
                return "A = pi * r^2"
            elif target == 'volume' and object_name == 'sphere':
                return "V = (4/3) * pi * r^3"
            else:
                return f"{operation}([{target.title()}])"
        
        return "Error: Insufficient entities to construct formula"


class MLModelStrategy(MappingStrategy):
    """Use machine learning model for mapping (placeholder for trained models)"""
    
    def __init__(self, model_type: str = "spacy"):
        self.model_type = model_type
        self.trained = False
    
    def map(self, description: str, ner_entities: Optional[List] = None) -> str:
        """
        Placeholder for ML-based mapping
        In production, this would use:
        - Trained spaCy model
        - BERT/Transformer model
        - Logistic regression on entity pairs
        """
        if not self.trained:
            return f"Error: {self.model_type} model not trained yet"
        
        # TODO: Implement actual model prediction
        return "ML prediction placeholder"


class MapDescriptionToFormula:
    """Main class for mapping descriptions to formulas"""
    
    def __init__(self, description: str = "", rules: Dict = None, ner_entities: Optional[List] = None):
        self.description = description
        self.custom_rules = rules or {}
        self.ner_entities = ner_entities
        
        # Initialize available strategies
        self.strategies = {
            "vocab": VocabToVocabStrategy(),
            "sentence": SentenceToSentenceStrategy(),
            "regex": RegexStrategy(),
            "ner": NERBasedStrategy(),
            "ml": MLModelStrategy()
        }
    
    def map(self, description: str = None, strategy: str = "vocab", 
            ner_entities: Optional[List] = None) -> str:
        """
        Map description to formula using specified strategy
        
        Args:
            description: Natural language description
            strategy: Mapping strategy to use
            ner_entities: Optional NER entities for entity-based strategies
        
        Returns:
            Generated formula string
        """
        desc = description or self.description
        entities = ner_entities or self.ner_entities
        
        if strategy not in self.strategies:
            return f"Error: Unknown strategy '{strategy}'. Available: {list(self.strategies.keys())}"
        
        try:
            result = self.strategies[strategy].map(desc, entities)
            return result
        except Exception as e:
            return f"Error in {strategy} strategy: {str(e)}"
    
    def map_with_fallback(self, description: str, 
                          strategies: List[str] = ["sentence", "regex", "vocab"]) -> Tuple[str, str]:
        """
        Try multiple strategies in order until one succeeds
        
        Returns:
            (formula, strategy_used)
        """
        for strategy in strategies:
            result = self.map(description, strategy)
            if not result.startswith("Error:"):
                return result, strategy
        
        return "Error: All strategies failed", "none"
    
    def __call__(self, description: str, option: str = "vocab") -> str:
        """Backward compatibility with original interface"""
        return self.map(description, strategy=option)


# ============= EXAMPLE USAGE =============

def main():
    print("="*70)
    print("IMPROVED MAPPING SYSTEM - DEMONSTRATION")
    print("="*70)
    
    # Test cases
    test_cases = [
        ("Average of Petal Length", "vocab"),
        ("Sum of sales by year", "sentence"),
        ("total of Revenue by Region", "regex"),
        ("calculate area of circle", "sentence"),
    ]
    
    mapper = MapDescriptionToFormula()
    
    for description, strategy in test_cases:
        print(f"\nInput: '{description}'")
        print(f"Strategy: {strategy}")
        result = mapper.map(description, strategy)
        print(f"Output: {result}")
        print("-"*70)
    
    # Test with NER entities
    print("\n" + "="*70)
    print("NER-BASED STRATEGY TEST")
    print("="*70)
    
    ner_entities = [
        {'text': 'calculate', 'label': 'OPER'},
        {'text': 'area', 'label': 'TARGET'},
        {'text': 'circle', 'label': 'OBJECT'}
    ]
    
    description = "calculate area of circle"
    result = mapper.map(description, strategy="ner", ner_entities=ner_entities)
    print(f"Input: '{description}'")
    print(f"NER Entities: {ner_entities}")
    print(f"Output: {result}")
    
    # Test fallback mechanism
    print("\n" + "="*70)
    print("FALLBACK STRATEGY TEST")
    print("="*70)
    
    description = "average of Petal Width"
    result, strategy_used = mapper.map_with_fallback(description)
    print(f"Input: '{description}'")
    print(f"Output: {result}")
    print(f"Strategy Used: {strategy_used}")


if __name__ == "__main__":
    main()
