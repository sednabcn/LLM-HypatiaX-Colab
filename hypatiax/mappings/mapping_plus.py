#!/usr/bin/python3
"""
Enhanced Description-to-Formula Mapping System
Includes: Confidence scoring, fuzzy matching, template learning,
context-awareness, semantic similarity, and ensemble methods
"""

import json
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from difflib import get_close_matches
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

# ============= BASE CLASSES =============

class MappingStrategy(ABC):
    """Abstract base class for mapping strategies"""

    @abstractmethod
    def map(self, description: str, context: 'MappingContext' = None,
            ner_entities: Optional[List] = None) -> Tuple[str, float]:
        """Map description to formula with confidence score"""
        pass


class MappingContext:
    """Context information for mapping"""

    def __init__(self, available_columns: List[str] = None,
                 data_types: Dict[str, str] = None,
                 sample_data: Dict[str, List] = None):
        self.available_columns = available_columns or []
        self.data_types = data_types or {}
        self.sample_data = sample_data or {}

    def is_numeric_column(self, column: str) -> bool:
        """Check if column contains numeric data"""
        return self.data_types.get(column, "").lower() in ["int", "float", "numeric", "number"]

    def column_exists(self, column: str) -> bool:
        """Check if column exists in schema"""
        return column in self.available_columns


# ============= UTILITY FUNCTIONS =============

class FuzzyMatcher:
    """Fuzzy string matching utilities"""

    @staticmethod
    def fuzzy_column_match(text: str, known_columns: List[str],
                          cutoff: float = 0.6) -> Optional[str]:
        """Find closest matching column name"""
        # Try exact match first
        if text in known_columns:
            return text

        # Try case-insensitive match
        text_lower = text.lower()
        for col in known_columns:
            if col.lower() == text_lower:
                return col

        # Try fuzzy match
        matches = get_close_matches(text, known_columns, n=1, cutoff=cutoff)
        return matches[0] if matches else None

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison"""
        return re.sub(r'\s+', ' ', text.lower().strip())


class ConfidenceScorer:
    """Calculate confidence scores for mappings"""

    @staticmethod
    def calculate_confidence(formula: str, description: str,
                           context: MappingContext = None,
                           strategy_name: str = "") -> float:
        """Calculate confidence score (0-1)"""
        score = 0.5  # Base score

        # Bonus for not being an error
        if not formula.startswith("Error:"):
            score += 0.2
        else:
            return 0.0

        # Bonus for valid column references
        if context and context.available_columns:
            columns_in_formula = re.findall(r'\[([^\]]+)\]', formula)
            valid_columns = sum(1 for col in columns_in_formula
                              if context.column_exists(col))
            if columns_in_formula:
                score += 0.2 * (valid_columns / len(columns_in_formula))

        # Bonus for appropriate operations on numeric columns
        if context:
            if any(op in formula for op in ["SUM", "AVG", "MIN", "MAX"]):
                columns = re.findall(r'\[([^\]]+)\]', formula)
                if columns and all(context.is_numeric_column(col) for col in columns):
                    score += 0.1

        # Strategy-specific bonuses
        if strategy_name == "sentence":
            score += 0.1  # Sentence matching is usually high precision
        elif strategy_name == "ner":
            score += 0.15  # NER-based is sophisticated

        return min(score, 1.0)


# ============= ENHANCED STRATEGIES =============

class EnhancedVocabStrategy(MappingStrategy):
    """Enhanced vocabulary mapping with fuzzy matching"""

    def __init__(self):
        self.vocab_map = {
            "total": "SUM",
            "sum": "SUM",
            "add": "SUM",
            "average": "AVG",
            "mean": "AVG",
            "avg": "AVG",
            "median": "MEDIAN",
            "count": "COUNT",
            "number of": "COUNT",
            "how many": "COUNT",
            "unique": "COUNTD",
            "distinct": "COUNTD",
            "maximum": "MAX",
            "max": "MAX",
            "highest": "MAX",
            "minimum": "MIN",
            "min": "MIN",
            "lowest": "MIN",
            "standard deviation": "STDEV",
            "std dev": "STDEV",
            "variance": "VAR",
            "var": "VAR"
        }

    def map(self, description: str, context: MappingContext = None,
            ner_entities: Optional[List] = None) -> Tuple[str, float]:
        desc_lower = description.lower()

        # Extract column name
        column_name = self._extract_column_name(description, context)
        if not column_name:
            return "Error: Column name not found", 0.0

        # Validate column exists in context
        if context and context.available_columns:
            matched_column = FuzzyMatcher.fuzzy_column_match(
                column_name, context.available_columns
            )
            if matched_column:
                column_name = matched_column
            else:
                confidence = 0.3  # Lower confidence for unknown columns
        else:
            confidence = 0.5

        # Find matching operation
        for keyword, formula_func in self.vocab_map.items():
            if keyword in desc_lower:
                formula = f"{formula_func}([{column_name}])"

                # Validate operation for data type
                if context and not self._validate_operation(formula_func, column_name, context):
                    confidence *= 0.5  # Reduce confidence for type mismatch

                return formula, confidence + 0.3

        return "Error: Operation not recognized", 0.0

    def _extract_column_name(self, description: str,
                            context: MappingContext = None) -> Optional[str]:
        """Extract column name with multiple strategies"""
        # Pattern 1: "of [Column Name]"
        match = re.search(r"of ([A-Z][a-z]+(?: [A-Z][a-z]+)*)", description)
        if match:
            return match.group(1)

        # Pattern 2: "for [Column Name]"
        match = re.search(r"for ([A-Z][a-z]+(?: [A-Z][a-z]+)*)", description)
        if match:
            return match.group(1)

        # Pattern 3: Quoted column "[Column]"
        match = re.search(r'\[([^\]]+)\]', description)
        if match:
            return match.group(1)

        # Pattern 4: Last capitalized words
        words = description.split()
        capitalized = [w for w in words if w and w[0].isupper() and len(w) > 1]
        if capitalized:
            return ' '.join(capitalized[-2:]) if len(capitalized) >= 2 else capitalized[-1]

        # Pattern 5: Use context columns if available
        if context and context.available_columns:
            for col in context.available_columns:
                if col.lower() in description.lower():
                    return col

        return None

    def _validate_operation(self, operation: str, column: str,
                           context: MappingContext) -> bool:
        """Validate that operation is appropriate for column type"""
        numeric_ops = {"SUM", "AVG", "MIN", "MAX", "MEDIAN", "STDEV", "VAR"}

        if operation in numeric_ops:
            return context.is_numeric_column(column)

        return True  # COUNT, COUNTD work on any type


class EnhancedSentenceStrategy(MappingStrategy):
    """Enhanced sentence mapping with pattern generalization"""

    def __init__(self):
        self.exact_mappings = {
            "sum of sales by year": "SUM([Sales]) GROUP BY [Year]",
            "average cost per item": "AVG([Cost]) / COUNT([Item])",
            "total revenue by region": "SUM([Revenue]) GROUP BY [Region]",
            "count of unique customers": "COUNTD([Customer ID])",
            "average of petal length": "AVG([Petal Length])",
            "calculate area of circle": "A = pi * r^2",
            "compute volume of sphere": "V = (4/3) * pi * r^3"
        }

        # Learned patterns from corrections
        self.learned_patterns = {}

    def map(self, description: str, context: MappingContext = None,
            ner_entities: Optional[List] = None) -> Tuple[str, float]:
        desc_lower = FuzzyMatcher.normalize_text(description)

        # Exact match
        if desc_lower in self.exact_mappings:
            return self.exact_mappings[desc_lower], 0.95

        # Check learned patterns
        if desc_lower in self.learned_patterns:
            return self.learned_patterns[desc_lower], 0.9

        # Fuzzy match (contains pattern)
        for pattern, formula in self.exact_mappings.items():
            if pattern in desc_lower or desc_lower in pattern:
                # Attempt to adapt formula with context
                adapted = self._adapt_formula(formula, description, context)
                return adapted, 0.7

        return "Error: No matching sentence pattern found", 0.0

    def _adapt_formula(self, template: str, description: str,
                      context: MappingContext) -> str:
        """Adapt formula template to current description"""
        # Extract columns from description
        if context and context.available_columns:
            for col in context.available_columns:
                if col.lower() in description.lower():
                    # Replace placeholder with actual column
                    template = re.sub(r'\[([^\]]+)\]', f'[{col}]', template, count=1)

        return template

    def add_learned_pattern(self, description: str, formula: str):
        """Learn from user corrections"""
        normalized = FuzzyMatcher.normalize_text(description)
        self.learned_patterns[normalized] = formula


class EnhancedRegexStrategy(MappingStrategy):
    """Enhanced regex with GROUP BY and multiple aggregations"""

    def __init__(self):
        self.operation_patterns = {
            r"(total|sum)\s+(?:of\s+)?(\w+(?:\s+\w+)*)": ("SUM", 2),
            r"(average|mean|avg)\s+(?:of\s+)?(\w+(?:\s+\w+)*)": ("AVG", 2),
            r"(count|number)\s+of\s+(\w+(?:\s+\w+)*)": ("COUNT", 2),
            r"(max|maximum|highest)\s+(?:of\s+)?(\w+(?:\s+\w+)*)": ("MAX", 2),
            r"(min|minimum|lowest)\s+(?:of\s+)?(\w+(?:\s+\w+)*)": ("MIN", 2),
            r"(median)\s+(?:of\s+)?(\w+(?:\s+\w+)*)": ("MEDIAN", 2),
            r"(unique|distinct)\s+(\w+(?:\s+\w+)*)": ("COUNTD", 2),
        }

        self.groupby_pattern = r"(?:by|per|for each)\s+(\w+(?:\s+\w+)*)"
        self.filter_pattern = r"where\s+(.+?)(?:\s+(?:by|per|$))"

    def map(self, description: str, context: MappingContext = None,
            ner_entities: Optional[List] = None) -> Tuple[str, float]:
        desc_lower = description.lower()

        # Find operation and column
        operation = None
        column = None
        confidence = 0.6

        for pattern, (op, group_idx) in self.operation_patterns.items():
            match = re.search(pattern, desc_lower)
            if match:
                operation = op
                column = match.group(group_idx)
                break

        if not operation or not column:
            return "Error: Could not parse operation or column", 0.0

        # Format column name with context
        if context and context.available_columns:
            matched_col = FuzzyMatcher.fuzzy_column_match(column, context.available_columns)
            if matched_col:
                column = matched_col
                confidence += 0.2
            else:
                column = ' '.join(word.capitalize() for word in column.split())
        else:
            column = ' '.join(word.capitalize() for word in column.split())

        formula = f"{operation}([{column}])"

        # Check for GROUP BY
        groupby_match = re.search(self.groupby_pattern, desc_lower)
        if groupby_match:
            groupby_col = groupby_match.group(1)
            if context and context.available_columns:
                matched_gb = FuzzyMatcher.fuzzy_column_match(groupby_col, context.available_columns)
                if matched_gb:
                    groupby_col = matched_gb
                else:
                    groupby_col = ' '.join(word.capitalize() for word in groupby_col.split())
            else:
                groupby_col = ' '.join(word.capitalize() for word in groupby_col.split())

            formula += f" GROUP BY [{groupby_col}]"
            confidence += 0.1

        # Check for WHERE clause
        filter_match = re.search(self.filter_pattern, desc_lower)
        if filter_match:
            filter_condition = filter_match.group(1).strip()
            formula += f" WHERE {filter_condition}"
            confidence += 0.05

        return formula, min(confidence, 1.0)


class EnhancedNERStrategy(MappingStrategy):
    """Enhanced NER-based mapping with multi-entity support"""

    def __init__(self):
        self.entity_to_function = {
            "OPER": {
                "sum": "SUM", "total": "SUM", "add": "SUM",
                "average": "AVG", "mean": "AVG", "avg": "AVG",
                "count": "COUNT", "number": "COUNT",
                "max": "MAX", "maximum": "MAX", "highest": "MAX",
                "min": "MIN", "minimum": "MIN", "lowest": "MIN",
                "median": "MEDIAN",
                "unique": "COUNTD", "distinct": "COUNTD"
            }
        }

        # Multi-entity formula templates
        self.templates = {
            ("OPER", "TARGET"): lambda op, tgt: f"{op}([{tgt}])",
            ("OPER", "TARGET", "GROUPBY"): lambda op, tgt, grp: f"{op}([{tgt}]) GROUP BY [{grp}]",
            ("OPER", "TARGET", "OBJECT"): self._handle_geometric,
        }

    def map(self, description: str, context: MappingContext = None,
            ner_entities: Optional[List] = None) -> Tuple[str, float]:
        if not ner_entities:
            return "Error: NER entities required for this strategy", 0.0

        # Extract entity values
        entities_dict = defaultdict(list)

        for entity in ner_entities:
            label = entity.get('label', '')
            text = entity.get('text', '').lower()

            if label == 'OPER':
                operation = self.entity_to_function['OPER'].get(text, text.upper())
                entities_dict['OPER'].append(operation)
            elif label in ['TARGET', 'ARG']:
                # Validate against context
                if context and context.available_columns:
                    matched = FuzzyMatcher.fuzzy_column_match(text, context.available_columns)
                    entities_dict['TARGET'].append(matched or text.title())
                else:
                    entities_dict['TARGET'].append(text.title())
            elif label == 'OBJECT':
                entities_dict['OBJECT'].append(text)
            elif label in ['GROUPBY', 'BY']:
                entities_dict['GROUPBY'].append(text.title())

        # Build formula based on entity pattern
        pattern_key = tuple(sorted(entities_dict.keys()))

        if pattern_key in self.templates:
            try:
                formula = self._apply_template(pattern_key, entities_dict)
                confidence = 0.8 if context else 0.6
                return formula, confidence
            except Exception as e:
                return f"Error: Template application failed - {str(e)}", 0.0

        # Fallback: simple operation + target
        if 'OPER' in entities_dict and 'TARGET' in entities_dict:
            op = entities_dict['OPER'][0]
            tgt = entities_dict['TARGET'][0]
            return f"{op}([{tgt}])", 0.5

        return "Error: Insufficient entities to construct formula", 0.0

    def _apply_template(self, pattern_key: tuple, entities_dict: Dict) -> str:
        """Apply template based on entity pattern"""
        template_func = self.templates[pattern_key]

        if pattern_key == ("OPER", "TARGET"):
            return template_func(entities_dict['OPER'][0], entities_dict['TARGET'][0])
        elif pattern_key == ("GROUPBY", "OPER", "TARGET"):
            return template_func(entities_dict['OPER'][0],
                               entities_dict['TARGET'][0],
                               entities_dict['GROUPBY'][0])
        elif pattern_key == ("OBJECT", "OPER", "TARGET"):
            return template_func(entities_dict['OPER'][0],
                               entities_dict['TARGET'][0],
                               entities_dict['OBJECT'][0])

        return "Error: Unknown pattern"

    def _handle_geometric(self, operation: str, target: str, object_name: str) -> str:
        """Handle geometric formulas"""
        if target == 'area' and object_name == 'circle':
            return "A = pi * r^2"
        elif target == 'volume' and object_name == 'sphere':
            return "V = (4/3) * pi * r^3"
        elif target == 'area' and object_name == 'square':
            return "A = a^2"
        elif target == 'perimeter' and object_name == 'circle':
            return "P = 2 * pi * r"
        else:
            return f"{operation}([{target}]) FOR {object_name}"


class TemplateLearningStrategy(MappingStrategy):
    """Learn formula templates from example pairs"""

    def __init__(self):
        self.templates = {}
        self.pattern_examples = defaultdict(list)

    def learn_from_examples(self, desc_formula_pairs: List[Tuple[str, str]]):
        """Extract reusable patterns from training data"""
        for desc, formula in desc_formula_pairs:
            # Generalize description pattern
            desc_pattern = self._generalize_description(desc)

            # Generalize formula template
            formula_template = self._generalize_formula(formula)

            # Store mapping
            self.templates[desc_pattern] = formula_template
            self.pattern_examples[desc_pattern].append((desc, formula))

    def map(self, description: str, context: MappingContext = None,
            ner_entities: Optional[List] = None) -> Tuple[str, float]:
        if not self.templates:
            return "Error: No templates learned yet", 0.0

        # Find best matching pattern
        desc_pattern = self._generalize_description(description)

        if desc_pattern in self.templates:
            template = self.templates[desc_pattern]
            # Fill template with specific values from description
            formula = self._instantiate_template(template, description, context)
            return formula, 0.85

        # Try fuzzy pattern matching
        for pattern, template in self.templates.items():
            similarity = self._pattern_similarity(desc_pattern, pattern)
            if similarity > 0.7:
                formula = self._instantiate_template(template, description, context)
                return formula, 0.6 * similarity

        return "Error: No matching template found", 0.0

    def _generalize_description(self, description: str) -> str:
        """Convert description to generalized pattern"""
        desc_lower = description.lower()

        # Replace specific column names with placeholder
        desc_lower = re.sub(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', 'COLUMN', description)
        desc_lower = desc_lower.lower()

        # Replace numbers with placeholder
        desc_lower = re.sub(r'\b\d+\b', 'NUM', desc_lower)

        return FuzzyMatcher.normalize_text(desc_lower)

    def _generalize_formula(self, formula: str) -> str:
        """Convert formula to generalized template"""
        # Replace column names in brackets with placeholder
        template = re.sub(r'\[([^\]]+)\]', '[COLUMN]', formula)

        # Replace numbers with placeholder
        template = re.sub(r'\b\d+\b', 'NUM', template)

        return template

    def _instantiate_template(self, template: str, description: str,
                             context: MappingContext) -> str:
        """Fill template with actual values"""
        # Extract column names from description
        if context and context.available_columns:
            for col in context.available_columns:
                if col.lower() in description.lower():
                    template = template.replace('[COLUMN]', f'[{col}]', 1)
        else:
            # Extract capitalized words as column names
            columns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', description)
            for col in columns:
                template = template.replace('[COLUMN]', f'[{col}]', 1)

        return template

    def _pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between two patterns"""
        words1 = set(pattern1.split())
        words2 = set(pattern2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)


class SemanticSimilarityStrategy(MappingStrategy):
    """Use semantic similarity for finding similar examples"""

    def __init__(self):
        self.examples = []
        self.embeddings = []

    def add_examples(self, desc_formula_pairs: List[Tuple[str, str]]):
        """Add training examples"""
        self.examples = desc_formula_pairs
        # In production, would use sentence-transformers here
        # self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # self.embeddings = self.model.encode([desc for desc, _ in pairs])

    def map(self, description: str, context: MappingContext = None,
            ner_entities: Optional[List] = None) -> Tuple[str, float]:
        if not self.examples:
            return "Error: No examples available", 0.0

        # Simplified similarity (in production, use embeddings)
        best_match = self._find_most_similar(description)

        if best_match:
            similar_desc, formula = best_match
            # Adapt formula to current description
            adapted = self._adapt_formula(formula, description, context)

            similarity = self._text_similarity(description, similar_desc)
            return adapted, similarity

        return "Error: No similar examples found", 0.0

    def _find_most_similar(self, description: str) -> Optional[Tuple[str, str]]:
        """Find most similar training example"""
        best_score = 0.0
        best_match = None

        desc_lower = description.lower()

        for example_desc, formula in self.examples:
            score = self._text_similarity(desc_lower, example_desc.lower())
            if score > best_score:
                best_score = score
                best_match = (example_desc, formula)

        return best_match if best_score > 0.3 else None

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _adapt_formula(self, formula: str, description: str,
                      context: MappingContext) -> str:
        """Adapt formula from similar example to current description"""
        # Replace column names based on context
        if context and context.available_columns:
            for col in context.available_columns:
                if col.lower() in description.lower():
                    # Replace first column reference
                    formula = re.sub(r'\[([^\]]+)\]', f'[{col}]', formula, count=1)

        return formula


# ============= ENSEMBLE MAPPER =============

class EnsembleMapper:
    """Combine multiple strategies with voting"""

    def __init__(self, context: MappingContext = None):
        self.context = context
        self.strategies = {
            "vocab": EnhancedVocabStrategy(),
            "sentence": EnhancedSentenceStrategy(),
            "regex": EnhancedRegexStrategy(),
            "ner": EnhancedNERStrategy(),
            "template": TemplateLearningStrategy(),
            "semantic": SemanticSimilarityStrategy()
        }

        # Strategy weights (can be tuned)
        self.weights = {
            "vocab": 1.0,
            "sentence": 1.2,
            "regex": 1.0,
            "ner": 1.3,
            "template": 1.1,
            "semantic": 1.0
        }

        # User correction history
        self.correction_history = []

    def map_with_ensemble(self, description: str,
                         strategies: List[str] = None,
                         ner_entities: Optional[List] = None) -> Tuple[str, str, float, List]:
        """
        Map using ensemble of strategies

        Returns:
            (formula, best_strategy, confidence, all_candidates)
        """
        if strategies is None:
            strategies = ["sentence", "regex", "ner", "vocab"]

        candidates = []

        for strategy_name in strategies:
            if strategy_name not in self.strategies:
                continue

            try:
                formula, confidence = self.strategies[strategy_name].map(
                    description, self.context, ner_entities
                )

                # Apply strategy weight
                weighted_confidence = confidence * self.weights.get(strategy_name, 1.0)

                # Additional confidence from context
                if self.context:
                    context_score = ConfidenceScorer.calculate_confidence(
                        formula, description, self.context, strategy_name
                    )
                    weighted_confidence = (weighted_confidence + context_score) / 2

                candidates.append({
                    'formula': formula,
                    'strategy': strategy_name,
                    'confidence': weighted_confidence,
                    'raw_confidence': confidence
                })
            except Exception as e:
                print(f"Warning: Strategy {strategy_name} failed: {e}")
                continue

        if not candidates:
            return "Error: All strategies failed", "none", 0.0, []

        # Sort by confidence
        candidates.sort(key=lambda x: x['confidence'], reverse=True)

        # Check for consensus (multiple strategies agree)
        formula_votes = defaultdict(list)
        for cand in candidates:
            if not cand['formula'].startswith("Error:"):
                normalized = cand['formula'].replace(' ', '').upper()
                formula_votes[normalized].append(cand)

        # If multiple strategies agree, boost confidence
        best = candidates[0]
        normalized_best = best['formula'].replace(' ', '').upper()
        if len(formula_votes.get(normalized_best, [])) > 1:
            best['confidence'] = min(best['confidence'] * 1.2, 1.0)

        return (best['formula'], best['strategy'],
                best['confidence'], candidates)

    def learn_from_correction(self, description: str, correct_formula: str):
        """Learn from user corrections"""
        self.correction_history.append((description, correct_formula))

        # Update sentence strategy with learned pattern
        if 'sentence' in self.strategies:
            self.strategies['sentence'].add_learned_pattern(description, correct_formula)

    def train_template_strategy(self, training_pairs: List[Tuple[str, str]]):
        """Train the template learning strategy"""
        if 'template' in self.strategies:
            self.strategies['template'].learn_from_examples(training_pairs)

    def train_semantic_strategy(self, training_pairs: List[Tuple[str, str]]):
        """Train the semantic similarity strategy"""
        if 'semantic' in self.strategies:
            self.strategies['semantic'].add_examples(training_pairs)


# ============= MAIN CLASS =============

class EnhancedMapDescriptionToFormula:
    """Enhanced main mapping class with all improvements"""

    def __init__(self, context: MappingContext = None):
        self.context = context or MappingContext()
        self.ensemble = EnsembleMapper(self.context)

    def map(self, description: str, strategy: str = "ensemble",
            ner_entities: Optional[List] = None) -> str:
        """Map description to formula"""

        if strategy == "ensemble":
            formula, _, confidence, _ = self.ensemble.map_with_ensemble(
                description, ner_entities=ner_entities
            )
            return formula
        elif strategy in self.ensemble.strategies:
            formula, confidence = self.ensemble.strategies[strategy].map(
                description, self.context, ner_entities
            )
            return formula
        else:
            return f"Error: Unknown strategy '{strategy}'"

    def map_with_all_candidates(self, description: str,
                               ner_entities: Optional[List] = None) -> Dict:
        """Get all candidate formulas with confidence scores"""
        formula, strategy, confidence, candidates = self.ensemble.map_with_ensemble(
            description, ner_entities=ner_entities
        )

        return {
            'best_formula': formula,
            'best_strategy': strategy,
            'confidence': confidence,
            'all_candidates': candidates
        }

    def correct_and_learn(self, description: str, correct_formula: str):
        """Learn from user correction"""
        self.ensemble.learn_from_correction(description, correct_formula)

    def train(self, training_pairs: List[Tuple[str, str]]):
        """Train learnable strategies"""
        self.ensemble.train_template_strategy(training_pairs)
        self.ensemble.train_semantic_strategy(training_pairs)

    def set_context(self, available_columns: List[str],
                    data_types: Dict[str, str] = None):
        """Update context with schema information"""
        self.context.available_columns = available_columns
        if data_types:
            self.context.data_types = data_types
        self.ensemble.context = self.context


# ============= REAL DATASET EXAMPLES =============

def demo_iris_dataset():
    """Demo with Iris dataset"""
    print("="*70)
    print("DEMO: IRIS DATASET")
    print("="*70)

    # Define Iris schema
    iris_columns = ["Sepal Length", "Sepal Width", "Petal Length", "Petal Width", "Species"]
    iris_types = {
        "Sepal Length": "float",
        "Sepal Width": "float",
        "Petal Length": "float",
        "Petal Width": "float",
        "Species": "string"
    }

    context = MappingContext(available_columns=iris_columns, data_types=iris_types)
    mapper = EnhancedMapDescriptionToFormula(context)

    # Training examples
    training_pairs = [
        ("average of Petal Length", "AVG([Petal Length])"),
        ("sum of Sepal Width", "SUM([Sepal Width])"),
        ("count of Species", "COUNT([Species])"),
        ("maximum Petal Width by Species", "MAX([Petal Width]) GROUP BY [Species]"),
    ]

    mapper.train(training_pairs)

    # Test cases
    test_cases = [
        "average of Petal Length",
        "total of Sepal Width",
        "count unique Species",
        "maximum petal width",
        "average sepal length by species",
        "minimum of petal width per species"
    ]

    print("\nTEST RESULTS:")
    print("-"*70)

    for desc in test_cases:
        result = mapper.map_with_all_candidates(desc)

        print(f"\nInput: '{desc}'")
        print(f"Best Formula: {result['best_formula']}")
        print(f"Strategy: {result['best_strategy']}")
        print(f"Confidence: {result['confidence']:.2f}")

        if len(result['all_candidates']) > 1:
            print("Other candidates:")
            for cand in result['all_candidates'][1:3]:  # Show top 3
                if not cand['formula'].startswith("Error:"):
                    print(f"  - {cand['formula']} ({cand['strategy']}: {cand['confidence']:.2f})")
        print("-"*70)


def demo_sales_dataset():
    """Demo with Sales dataset"""
    print("\n" + "="*70)
    print("DEMO: SALES DATASET")
    print("="*70)

    # Define Sales schema
    sales_columns = ["Order ID", "Product", "Category", "Sales", "Quantity",
                     "Profit", "Region", "Customer", "Order Date"]
    sales_types = {
        "Order ID": "string",
        "Product": "string",
        "Category": "string",
        "Sales": "float",
        "Quantity": "int",
        "Profit": "float",
        "Region": "string",
        "Customer": "string",
        "Order Date": "date"
    }

    context = MappingContext(available_columns=sales_columns, data_types=sales_types)
    mapper = EnhancedMapDescriptionToFormula(context)

    # Training examples
    training_pairs = [
        ("total sales by region", "SUM([Sales]) GROUP BY [Region]"),
        ("average profit per customer", "AVG([Profit]) / COUNT([Customer])"),
        ("count of orders", "COUNT([Order ID])"),
        ("sum of quantity by category", "SUM([Quantity]) GROUP BY [Category]"),
    ]

    mapper.train(training_pairs)

    # Test cases with NER entities
    test_cases_with_ner = [
        ("total sales by region", [
            {'text': 'total', 'label': 'OPER'},
            {'text': 'sales', 'label': 'TARGET'},
            {'text': 'region', 'label': 'GROUPBY'}
        ]),
        ("average profit", [
            {'text': 'average', 'label': 'OPER'},
            {'text': 'profit', 'label': 'TARGET'}
        ]),
        ("count unique customers", [
            {'text': 'count', 'label': 'OPER'},
            {'text': 'unique', 'label': 'OPER'},
            {'text': 'customers', 'label': 'TARGET'}
        ]),
    ]

    print("\nTEST RESULTS (with NER entities):")
    print("-"*70)

    for desc, ner_entities in test_cases_with_ner:
        result = mapper.map_with_all_candidates(desc, ner_entities)

        print(f"\nInput: '{desc}'")
        print(f"NER Entities: {[f\"{e['label']}:{e['text']}\" for e in ner_entities]}")
        print(f"Best Formula: {result['best_formula']}")
        print(f"Strategy: {result['best_strategy']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print("-"*70)


def demo_fuzzy_matching():
    """Demo fuzzy column name matching"""
    print("\n" + "="*70)
    print("DEMO: FUZZY COLUMN MATCHING")
    print("="*70)

    columns = ["Customer Name", "Order Date", "Product Category", "Total Sales"]
    types = {col: "string" if "Name" in col or "Category" in col else
             "date" if "Date" in col else "float" for col in columns}

    context = MappingContext(available_columns=columns, data_types=types)
    mapper = EnhancedMapDescriptionToFormula(context)

    # Test with typos and variations
    test_cases = [
        "average of total sale",  # Missing 's'
        "sum of prodcut category",  # Typo
        "count of custmer name",  # Typo
        "total sales by order dat",  # Typo
    ]

    print("\nFUZZY MATCHING RESULTS:")
    print("-"*70)

    for desc in test_cases:
        result = mapper.map_with_all_candidates(desc)
        print(f"\nInput: '{desc}'")
        print(f"Corrected Formula: {result['best_formula']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print("-"*70)


def demo_learning_from_corrections():
    """Demo learning from user corrections"""
    print("\n" + "="*70)
    print("DEMO: LEARNING FROM CORRECTIONS")
    print("="*70)

    context = MappingContext(
        available_columns=["Revenue", "Cost", "Profit", "Year"],
        data_types={"Revenue": "float", "Cost": "float", "Profit": "float", "Year": "int"}
    )
    mapper = EnhancedMapDescriptionToFormula(context)

    # Initial prediction
    description = "net profit by year"
    print("\nBEFORE CORRECTION:")
    result1 = mapper.map_with_all_candidates(description)
    print(f"Input: '{description}'")
    print(f"Predicted: {result1['best_formula']}")
    print(f"Confidence: {result1['confidence']:.2f}")

    # User corrects it
    correct_formula = "(SUM([Revenue]) - SUM([Cost])) GROUP BY [Year]"
    mapper.correct_and_learn(description, correct_formula)
    print(f"\nUser corrects to: {correct_formula}")
    print("System learns from correction...")

    # Same query again
    print("\nAFTER CORRECTION:")
    result2 = mapper.map_with_all_candidates(description)
    print(f"Input: '{description}'")
    print(f"Predicted: {result2['best_formula']}")
    print(f"Confidence: {result2['confidence']:.2f}")
    print(f"Strategy: {result2['best_strategy']}")


def demo_complex_formulas():
    """Demo complex formula generation"""
    print("\n" + "="*70)
    print("DEMO: COMPLEX FORMULAS")
    print("="*70)

    context = MappingContext(
        available_columns=["Sales", "Quantity", "Price", "Region", "Year"],
        data_types={
            "Sales": "float", "Quantity": "int", "Price": "float",
            "Region": "string", "Year": "int"
        }
    )
    mapper = EnhancedMapDescriptionToFormula(context)

    # Complex descriptions
    test_cases = [
        "average sales per region",
        "total quantity by year",
        "maximum price by region",
        "sum of sales where region",
    ]

    print("\nCOMPLEX FORMULA RESULTS:")
    print("-"*70)

    for desc in test_cases:
        result = mapper.map_with_all_candidates(desc)
        print(f"\nInput: '{desc}'")
        print(f"Formula: {result['best_formula']}")
        print(f"Strategy: {result['best_strategy']}")
        print(f"Confidence: {result['confidence']:.2f}")

        # Show alternative interpretations
        if len(result['all_candidates']) > 1:
            print("Alternatives:")
            for i, cand in enumerate(result['all_candidates'][1:3], 1):
                if not cand['formula'].startswith("Error:"):
                    print(f"  {i}. {cand['formula']} "
                          f"({cand['strategy']}: {cand['confidence']:.2f})")
        print("-"*70)


def demo_comparison_with_original():
    """Compare enhanced version with original mapping.py"""
    print("\n" + "="*70)
    print("DEMO: COMPARISON WITH ORIGINAL SYSTEM")
    print("="*70)

    # Import original for comparison
    from mapping import MapDescriptionToFormula as OriginalMapper

    context = MappingContext(
        available_columns=["Petal Length", "Sepal Width", "Species"],
        data_types={"Petal Length": "float", "Sepal Width": "float", "Species": "string"}
    )

    enhanced_mapper = EnhancedMapDescriptionToFormula(context)
    original_mapper = OriginalMapper()

    test_cases = [
        ("average of Petal Length", "vocab"),
        ("sum of sepal width", "vocab"),  # lowercase
        ("total petal lenght", "vocab"),  # typo
    ]

    print("\nCOMPARISON RESULTS:")
    print("-"*70)

    for desc, strategy in test_cases:
        print(f"\nInput: '{desc}'")

        # Original system
        original_result = original_mapper.map(desc, strategy)
        print(f"Original:  {original_result}")

        # Enhanced system
        enhanced_result = enhanced_mapper.map_with_all_candidates(desc)
        print(f"Enhanced:  {enhanced_result['best_formula']}")
        print(f"Confidence: {enhanced_result['confidence']:.2f}")
        print(f"Strategy: {enhanced_result['best_strategy']}")
        print("-"*70)


# ============= MAIN EXECUTION =============

def main():
    print("\n" + "🚀" + "="*68 + "🚀")
    print("   ENHANCED DESCRIPTION-TO-FORMULA MAPPING SYSTEM")
    print("   Features: Ensemble voting, fuzzy matching, learning, context-aware")
    print("🚀" + "="*68 + "🚀")

    # Run all demos
    demo_iris_dataset()
    demo_sales_dataset()
    demo_fuzzy_matching()
    demo_learning_from_corrections()
    demo_complex_formulas()

    print("\n" + "="*70)
    print("✅ ALL DEMOS COMPLETED")
    print("="*70)
    print("\nKEY IMPROVEMENTS:")
    print("1. ✅ Fuzzy column matching (handles typos)")
    print("2. ✅ Context-aware validation (checks schema)")
    print("3. ✅ Ensemble voting (combines strategies)")
    print("4. ✅ Confidence scoring (ranks results)")
    print("5. ✅ Learning from corrections (adapts)")
    print("6. ✅ Template learning (generalizes patterns)")
    print("7. ✅ Multi-entity formulas (GROUP BY, WHERE)")
    print("8. ✅ Real dataset support (Iris, Sales, etc.)")
    print("="*70)


if __name__ == "__main__":
    main()
