"""
HypatiaX Engine - Core Processing Logic
Handles NER model integration, entity extraction, and formula generation
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import spacy

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an extracted entity from text"""

    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class ProcessingResult:
    """Container for processing results"""

    query: str
    entities: List[Entity]
    formula: str
    method: str
    confidence: float
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class HypatiaXEngine:
    """
    Core processing engine for HypatiaX
    Handles model loading, entity extraction, and formula generation
    """

    def __init__(
        self, desc_model_path: Optional[str] = None, formula_model_path: Optional[str] = None, use_gpu: bool = False
    ):
        """
        Initialize the HypatiaX engine

        Args:
            desc_model_path: Path to description NER model
            formula_model_path: Path to formula NER model
            use_gpu: Whether to use GPU acceleration
        """
        self.desc_model_path = desc_model_path
        self.formula_model_path = formula_model_path
        self.use_gpu = use_gpu

        # Model containers
        self.nlp_desc = None
        self.nlp_formula = None

        # Vocab mappings (fallback)
        self.vocab_map = self._load_vocab_mappings()

        # Statistics
        self.stats = {"total_queries": 0, "successful_mappings": 0, "failed_mappings": 0, "avg_processing_time": 0.0}

        logger.info("HypatiaX Engine initialized")

    def load_models(self) -> bool:
        """Load spaCy NER models"""
        try:
            if self.desc_model_path:
                logger.info(f"Loading description model from {self.desc_model_path}")
                self.nlp_desc = spacy.load(self.desc_model_path)

                if self.use_gpu:
                    spacy.prefer_gpu()
                    logger.info("GPU acceleration enabled")

            if self.formula_model_path:
                logger.info(f"Loading formula model from {self.formula_model_path}")
                self.nlp_formula = spacy.load(self.formula_model_path)

            logger.info("Models loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            logger.warning("Falling back to rule-based processing")
            return False

    def _load_vocab_mappings(self) -> Dict[str, str]:
        """Load vocabulary mappings for fallback processing"""
        return {
            # Operations
            "sum": "SUM",
            "total": "SUM",
            "add": "SUM",
            "average": "AVG",
            "avg": "AVG",
            "mean": "AVG",
            "count": "COUNT",
            "number": "COUNT",
            "maximum": "MAX",
            "max": "MAX",
            "minimum": "MIN",
            "min": "MIN",
            "median": "MEDIAN",
            "stdev": "STDEV",
            "variance": "VAR",
            # Common fields (lowercase)
            "sales": "Sales",
            "profit": "Profit",
            "revenue": "Revenue",
            "cost": "Cost",
            "price": "Price",
            "quantity": "Quantity",
            "amount": "Amount",
            "customers": "Customers",
            "orders": "Orders",
            "products": "Products",
            "region": "Region",
            "category": "Category",
            "date": "Date",
            "year": "Year",
            "month": "Month",
            "day": "Day",
        }

    def extract_entities(self, text: str, use_model: bool = True) -> List[Entity]:
        """
        Extract entities from text using NER model or fallback

        Args:
            text: Input text to process
            use_model: Whether to use trained model (True) or rule-based (False)

        Returns:
            List of Entity objects
        """
        entities = []

        if use_model and self.nlp_desc:
            # Use trained NER model
            doc = self.nlp_desc(text)
            entities = [
                Entity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=1.0,  # spaCy doesn't provide per-entity confidence
                )
                for ent in doc.ents
            ]
        else:
            # Fallback: Rule-based entity extraction
            entities = self._extract_entities_rule_based(text)

        return entities

    def _extract_entities_rule_based(self, text: str) -> List[Entity]:
        """Rule-based entity extraction fallback"""
        entities = []
        words = text.lower().split()

        entity_types = {
            "OPER": ["sum", "average", "avg", "count", "max", "min", "total", "median"],
            "ARG": ["sales", "profit", "revenue", "cost", "price", "customers", "orders"],
            "ADP": ["by", "per", "of", "from", "to", "across"],
            "VERB": ["calculate", "find", "show", "display", "get", "compute"],
        }

        pos = 0
        for word in words:
            clean_word = word.strip(".,!?;:")
            for entity_type, keywords in entity_types.items():
                if clean_word in keywords:
                    entities.append(
                        Entity(text=word, label=entity_type, start=pos, end=pos + len(word), confidence=0.8)
                    )
                    break
            pos += len(word) + 1

        return entities

    def generate_formula(self, query: str, entities: List[Entity], method: str = "vocab") -> str:
        """
        Generate Tableau formula from query and entities

        Args:
            query: Original query text
            entities: Extracted entities
            method: Mapping method ('vocab', 'sentence', 'regex', 'ner')

        Returns:
            Generated Tableau formula
        """
        if method == "vocab":
            return self._vocab_mapping(query, entities)
        elif method == "sentence":
            return self._sentence_mapping(query, entities)
        elif method == "regex":
            return self._regex_mapping(query, entities)
        elif method == "ner":
            return self._ner_mapping(query, entities)
        else:
            logger.warning(f"Unknown method: {method}, using vocab")
            return self._vocab_mapping(query, entities)

    def _vocab_mapping(self, query: str, entities: List[Entity]) -> str:
        """Vocabulary-based formula generation"""
        # Find operation
        operation = "SUM"
        for entity in entities:
            if entity.label == "OPER":
                operation = self.vocab_map.get(entity.text.lower(), entity.text.upper())
                break

        # Find field/argument
        field_name = "Field"
        for entity in entities:
            if entity.label == "ARG":
                field_name = self.vocab_map.get(entity.text.lower(), entity.text.capitalize())
                break

        return f"{operation}([{field_name}])"

    def _sentence_mapping(self, query: str, entities: List[Entity]) -> str:
        """Sentence pattern-based formula generation"""
        query_lower = query.lower()

        # Pattern matching for common sentence structures
        patterns = {
            "sum of": ("SUM", 2),
            "average of": ("AVG", 2),
            "count of": ("COUNT", 2),
            "total": ("SUM", 1),
        }

        operation = "SUM"
        field_name = "Field"

        for pattern, (op, offset) in patterns.items():
            if pattern in query_lower:
                operation = op
                # Extract field name after pattern
                idx = query_lower.find(pattern) + len(pattern)
                remaining = query[idx:].strip().split()[0] if idx < len(query) else ""
                if remaining:
                    field_name = remaining.capitalize()
                break

        return f"{operation}([{field_name}])"

    def _regex_mapping(self, query: str, entities: List[Entity]) -> str:
        """Regex-based formula generation"""
        import re

        # Define regex patterns for operations and fields
        op_pattern = r"\b(sum|average|avg|count|max|min|total)\b"
        field_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"

        operation = "SUM"
        field_name = "Field"

        # Find operation
        op_match = re.search(op_pattern, query, re.IGNORECASE)
        if op_match:
            operation = self.vocab_map.get(op_match.group(1).lower(), op_match.group(1).upper())

        # Find field name
        field_match = re.search(field_pattern, query)
        if field_match:
            field_name = field_match.group(1)

        return f"{operation}([{field_name}])"

    def _ner_mapping(self, query: str, entities: List[Entity]) -> str:
        """NER model-based formula generation"""
        # Similar to vocab mapping but prioritizes model predictions
        return self._vocab_mapping(query, entities)

    def calculate_confidence(self, entities: List[Entity], formula: str) -> float:
        """Calculate confidence score for generated formula"""
        if not entities:
            return 0.5

        # Base confidence on entity confidence and count
        avg_entity_conf = sum(e.confidence for e in entities) / len(entities)
        entity_count_factor = min(len(entities) / 5, 1.0)  # Normalize to max 5 entities

        # Bonus for having both operation and argument
        has_oper = any(e.label == "OPER" for e in entities)
        has_arg = any(e.label == "ARG" for e in entities)
        structure_bonus = 0.1 if (has_oper and has_arg) else 0.0

        confidence = avg_entity_conf * 0.7 + entity_count_factor * 0.3 + structure_bonus
        return min(confidence, 1.0)

    def process(self, query: str, method: str = "vocab", use_model: bool = True) -> ProcessingResult:
        """
        Process a query end-to-end

        Args:
            query: Natural language query
            method: Mapping method to use
            use_model: Whether to use trained models

        Returns:
            ProcessingResult object with all outputs
        """
        start_time = time.time()

        try:
            # Extract entities
            entities = self.extract_entities(query, use_model=use_model)

            # Generate formula
            formula = self.generate_formula(query, entities, method=method)

            # Calculate confidence
            confidence = self.calculate_confidence(entities, formula)

            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # ms

            # Update stats
            self.stats["total_queries"] += 1
            self.stats["successful_mappings"] += 1
            self.stats["avg_processing_time"] = (
                self.stats["avg_processing_time"] * (self.stats["total_queries"] - 1) + processing_time
            ) / self.stats["total_queries"]

            return ProcessingResult(
                query=query,
                entities=entities,
                formula=formula,
                method=method,
                confidence=confidence,
                processing_time=processing_time,
                metadata={"use_model": use_model, "entity_count": len(entities)},
            )

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.stats["failed_mappings"] += 1

            # Return minimal result
            return ProcessingResult(
                query=query,
                entities=[],
                formula="ERROR",
                method=method,
                confidence=0.0,
                processing_time=(time.time() - start_time) * 1000,
                metadata={"error": str(e)},
            )

    def batch_process(
        self, queries: List[str], method: str = "vocab", use_model: bool = True
    ) -> List[ProcessingResult]:
        """Process multiple queries"""
        results = []
        for query in queries:
            result = self.process(query, method=method, use_model=use_model)
            results.append(result)
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.stats.copy()

    def export_results(self, results: List[ProcessingResult], output_path: str, format: str = "csv") -> bool:
        """
        Export processing results

        Args:
            results: List of ProcessingResult objects
            output_path: Output file path
            format: Export format ('csv', 'json', 'excel')

        Returns:
            Success status
        """
        try:
            # Convert to DataFrame
            data = []
            for result in results:
                data.append(
                    {
                        "query": result.query,
                        "formula": result.formula,
                        "method": result.method,
                        "confidence": result.confidence,
                        "entity_count": len(result.entities),
                        "processing_time_ms": result.processing_time,
                    }
                )

            df = pd.DataFrame(data)

            # Export based on format
            if format == "csv":
                df.to_csv(output_path, index=False)
            elif format == "json":
                df.to_json(output_path, orient="records", indent=2)
            elif format == "excel":
                df.to_excel(output_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Results exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize engine
    engine = HypatiaXEngine()

    # Test queries
    test_queries = [
        "calculate the sum of sales by region",
        "find average profit per product",
        "show total number of customers",
        "get maximum revenue by year",
    ]

    print("HypatiaX Engine Demo")
    print("=" * 50)

    # Process queries
    for query in test_queries:
        result = engine.process(query, method="vocab", use_model=False)

        print(f"\nQuery: {result.query}")
        print(f"Formula: {result.formula}")
        print(f"Confidence: {result.confidence:.2%}")
        print(f"Entities: {len(result.entities)}")
        print(f"Processing time: {result.processing_time:.2f}ms")

    # Show statistics
    print("\n" + "=" * 50)
    print("Statistics:")
    stats = engine.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
