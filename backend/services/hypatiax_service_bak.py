"""
HypatiaX Service - Tableau Formula Mapping
File: backend/services/hypatiax_service.py
"""

import logging
import time
import re
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class HypatiaXService:
    """Service for mapping natural language to Tableau formulas"""
    
    # Tableau formula operations mapping
    OPERATION_MAP = {
        'sum': 'SUM',
        'total': 'SUM',
        'add': 'SUM',
        'average': 'AVG',
        'avg': 'AVG',
        'mean': 'AVG',
        'count': 'COUNT',
        'number': 'COUNT',
        'max': 'MAX',
        'maximum': 'MAX',
        'highest': 'MAX',
        'min': 'MIN',
        'minimum': 'MIN',
        'lowest': 'MIN',
        'median': 'MEDIAN',
        'stdev': 'STDEV',
        'variance': 'VAR',
        'var': 'VAR'
    }
    
    # Common prepositions and stop words
    PREPOSITIONS = ['of', 'by', 'for', 'in', 'on', 'at', 'from', 'to', 'with']
    STOP_WORDS = ['the', 'a', 'an', 'all', 'each', 'every', 'calculate', 'compute', 'find', 'get', 'show']
    
    def __init__(self, models_loaded: bool = False, nlp_desc=None, nlp_formula=None):
        """
        Initialize HypatiaX service
        
        Args:
            models_loaded: Whether spaCy models are loaded
            nlp_desc: spaCy NER model for descriptions
            nlp_formula: spaCy NER model for formulas
        """
        self.models_loaded = models_loaded
        self.nlp_desc = nlp_desc
        self.nlp_formula = nlp_formula
        
        logger.info(f"HypatiaXService initialized (models_loaded={models_loaded})")
    
    def map_description_to_formula(
        self,
        description: str,
        method: str = 'vocab'
    ) -> Dict[str, Any]:
        """
        Map natural language description to Tableau formula
        
        Args:
            description: Natural language description
            method: Mapping method (vocab, neural, hybrid)
            
        Returns:
            Dictionary with formula, entities, and confidence
        """
        start_time = time.time()
        
        try:
            # Use production models if available
            if self.models_loaded and self.nlp_desc:
                result = self._map_with_models(description, method)
            else:
                # Fallback to rule-based mapping
                result = self._map_with_rules(description, method)
            
            # Add timing information
            result['processing_time_ms'] = round((time.time() - start_time) * 1000, 2)
            result['mode'] = 'production' if self.models_loaded else 'demo'
            
            logger.info(f"Mapped: '{description}' -> {result['formula']} (confidence={result['confidence']:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error mapping description: {e}")
            return {
                'success': False,
                'error': str(e),
                'description': description
            }
    
    def _map_with_models(self, description: str, method: str) -> Dict[str, Any]:
        """Map using spaCy NER models"""
        try:
            # Extract entities using NER model
            doc = self.nlp_desc(description)
            entities = [
                {
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                }
                for ent in doc.ents
            ]
            
            # Extract operation and field
            operation = self._extract_operation_from_entities(entities, description)
            field_name = self._extract_field_from_entities(entities, description)
            
            # Generate formula
            formula = self._generate_formula(operation, field_name)
            
            # Calculate confidence based on entity extraction quality
            confidence = self._calculate_confidence(entities, description)
            
            return {
                'success': True,
                'formula': formula,
                'entities': entities,
                'confidence': confidence,
                'operation': operation,
                'field': field_name,
                'method': method
            }
            
        except Exception as e:
            logger.warning(f"Model mapping failed: {e}, falling back to rules")
            return self._map_with_rules(description, method)
    
    def _map_with_rules(self, description: str, method: str) -> Dict[str, Any]:
        """Map using rule-based approach (fallback)"""
        desc_lower = description.lower()
        
        # Extract operation
        operation = 'SUM'  # Default
        for keyword, op in self.OPERATION_MAP.items():
            if keyword in desc_lower:
                operation = op
                break
        
        # Extract field name
        field_name = self._extract_field_name(description)
        
        # Generate entities for visualization
        entities = self._generate_mock_entities(description)
        
        # Generate formula
        formula = self._generate_formula(operation, field_name)
        
        # Calculate confidence
        confidence = self._calculate_rule_confidence(description, operation, field_name)
        
        return {
            'success': True,
            'formula': formula,
            'entities': entities,
            'confidence': confidence,
            'operation': operation,
            'field': field_name,
            'method': method
        }
    
    def _extract_operation_from_entities(self, entities: List[Dict], description: str) -> str:
        """Extract operation from NER entities"""
        # Look for OPER label in entities
        for entity in entities:
            if entity['label'] == 'OPER':
                text_lower = entity['text'].lower()
                return self.OPERATION_MAP.get(text_lower, 'SUM')
        
        # Fallback to description search
        desc_lower = description.lower()
        for keyword, op in self.OPERATION_MAP.items():
            if keyword in desc_lower:
                return op
        
        return 'SUM'
    
    def _extract_field_from_entities(self, entities: List[Dict], description: str) -> str:
        """Extract field name from NER entities"""
        # Look for NOUN entities that aren't operations
        field_candidates = [
            ent['text'] for ent in entities 
            if ent['label'] == 'NOUN' and ent['text'].lower() not in self.OPERATION_MAP
        ]
        
        if field_candidates:
            # Take the last noun (usually the field name)
            return field_candidates[-1]
        
        # Fallback to rule-based extraction
        return self._extract_field_name(description)
    
    def _extract_field_name(self, description: str) -> str:
        """Extract field name using rules"""
        words = description.split()
        
        # Look for field after prepositions
        for i, word in enumerate(words):
            if word.lower() in self.PREPOSITIONS:
                if i + 1 < len(words):
                    remaining = words[i+1:]
                    field_words = [
                        w for w in remaining 
                        if w.lower() not in self.STOP_WORDS + self.PREPOSITIONS
                    ]
                    if field_words:
                        return field_words[0].strip('.,!?').capitalize()
        
        # Fallback: take last meaningful word
        for word in reversed(words):
            clean_word = word.lower().strip('.,!?')
            if clean_word not in list(self.OPERATION_MAP.keys()) + self.STOP_WORDS + self.PREPOSITIONS:
                return word.strip('.,!?').capitalize()
        
        return 'Field'
    
    def _generate_formula(self, operation: str, field_name: str) -> str:
        """Generate Tableau formula string"""
        # Capitalize field name for Tableau convention
        field_name = field_name.capitalize()
        return f"{operation}([{field_name}])"
    
    def _calculate_confidence(self, entities: List[Dict], description: str) -> float:
        """Calculate confidence score based on entity extraction"""
        if not entities:
            return 0.5
        
        # Base confidence on entity coverage
        total_chars = len(description)
        entity_chars = sum(e['end'] - e['start'] for e in entities)
        coverage = entity_chars / total_chars if total_chars > 0 else 0
        
        # Bonus for operation detection
        has_operation = any(e['label'] == 'OPER' for e in entities)
        operation_bonus = 0.2 if has_operation else 0
        
        # Bonus for field detection
        has_field = any(e['label'] == 'NOUN' for e in entities)
        field_bonus = 0.15 if has_field else 0
        
        confidence = min(0.95, coverage * 0.65 + operation_bonus + field_bonus)
        return round(confidence, 2)
    
    def _calculate_rule_confidence(self, description: str, operation: str, field: str) -> float:
        """Calculate confidence for rule-based mapping"""
        confidence = 0.70  # Base confidence for rule-based
        
        # Bonus if operation was explicitly mentioned
        desc_lower = description.lower()
        op_mentioned = any(
            keyword in desc_lower 
            for keyword, op in self.OPERATION_MAP.items() 
            if op == operation
        )
        if op_mentioned:
            confidence += 0.15
        
        # Bonus if field is not generic
        if field != 'Field':
            confidence += 0.10
        
        return round(min(0.95, confidence), 2)
    
    def _generate_mock_entities(self, description: str) -> List[Dict]:
        """Generate mock entities for demo mode"""
        entities = []
        words = description.split()
        start_pos = 0
        
        for word in words:
            word_lower = word.lower().strip('.,!?')
            label = None
            
            if word_lower in self.OPERATION_MAP:
                label = 'OPER'
            elif word_lower in self.PREPOSITIONS:
                label = 'ADP'
            elif word_lower in self.STOP_WORDS:
                label = 'DET'
            elif word_lower.replace('.', '').replace(',', '').isdigit():
                label = 'NUM'
            else:
                label = 'NOUN'
            
            if label:
                entities.append({
                    'text': word,
                    'label': label,
                    'start': start_pos,
                    'end': start_pos + len(word)
                })
            
            start_pos += len(word) + 1
        
        return entities
    
    def batch_map(
        self,
        descriptions: List[str],
        method: str = 'vocab'
    ) -> List[Dict[str, Any]]:
        """
        Map multiple descriptions in batch
        
        Args:
            descriptions: List of natural language descriptions
            method: Mapping method
            
        Returns:
            List of mapping results
        """
        results = []
        
        for desc in descriptions:
            try:
                result = self.map_description_to_formula(desc, method)
                result['description'] = desc
                results.append(result)
            except Exception as e:
                results.append({
                    'success': False,
                    'description': desc,
                    'error': str(e)
                })
        
        logger.info(f"Batch mapped {len(descriptions)} descriptions")
        
        return results
    
    def validate_formula(self, formula: str) -> Dict[str, Any]:
        """
        Validate a Tableau formula
        
        Args:
            formula: Tableau formula string
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        # Check basic structure
        if not re.match(r'^[A-Z]+\(\[.+\]\)$', formula):
            errors.append('Formula does not match Tableau pattern: OPERATION([Field])')
        
        # Check for balanced brackets
        if formula.count('[') != formula.count(']'):
            errors.append('Unmatched square brackets')
        
        if formula.count('(') != formula.count(')'):
            errors.append('Unmatched parentheses')
        
        # Extract operation
        operation_match = re.match(r'^([A-Z]+)\(', formula)
        if operation_match:
            operation = operation_match.group(1)
            valid_operations = set(self.OPERATION_MAP.values())
            if operation not in valid_operations:
                warnings.append(f'Unknown operation: {operation}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'formula': formula
        }
    
    def suggest_improvements(self, description: str) -> List[str]:
        """
        Suggest improvements for the description
        
        Args:
            description: Natural language description
            
        Returns:
            List of suggestions
        """
        suggestions = []
        desc_lower = description.lower()
        
        # Check if operation is specified
        has_operation = any(keyword in desc_lower for keyword in self.OPERATION_MAP.keys())
        if not has_operation:
            suggestions.append('Consider specifying an operation (sum, average, count, etc.)')
        
        # Check if field is specified
        has_preposition = any(prep in desc_lower for prep in self.PREPOSITIONS)
        if not has_preposition:
            suggestions.append('Consider using "of [field]" to specify the field clearly')
        
        # Check for ambiguity
        if len(description.split()) < 3:
            suggestions.append('Description is very short. Consider adding more detail.')
        
        return suggestions
    
    def get_supported_operations(self) -> Dict[str, List[str]]:
        """
        Get list of supported operations
        
        Returns:
            Dictionary of operations with their keywords
        """
        operations = {}
        for keyword, operation in self.OPERATION_MAP.items():
            if operation not in operations:
                operations[operation] = []
            operations[operation].append(keyword)
        
        return operations
