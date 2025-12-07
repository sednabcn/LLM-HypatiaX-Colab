"""Parser agent for query understanding"""

from typing import Any, Dict

from agents.base.agent import BaseAgent


class ParserAgent(BaseAgent):
    """Agent specialized in parsing mathematical queries"""

    def __init__(self, ner_extractor=None):
        super().__init__(name="ParserAgent", role="Mathematical Query Parser")
        self.ner_extractor = ner_extractor

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Parse query and extract mathematical intent"""
        query = task.get("query", "")

        # Extract entities using NER if available
        entities = []
        if self.ner_extractor:
            entities = self.ner_extractor.extract(query)

        # Analyze intent
        intent = self._analyze_intent(query, entities)

        # Remember this interaction
        self.remember({"query": query, "entities": entities, "intent": intent})

        return {"query": query, "entities": entities, "intent": intent, "agent": self.name}

    def _analyze_intent(self, query: str, entities: list) -> Dict[str, Any]:
        """Analyze mathematical intent from query"""
        query_lower = query.lower()

        # Simple heuristics
        operations = []
        if "integral" in query_lower or "integrate" in query_lower:
            operations.append("integration")
        if "derivative" in query_lower or "differentiate" in query_lower:
            operations.append("differentiation")
        if "solve" in query_lower:
            operations.append("equation_solving")
        if "simplify" in query_lower:
            operations.append("simplification")

        return {
            "operations": operations,
            "entity_count": len(entities),
            "complexity": self._estimate_complexity(query, entities),
        }

    def _estimate_complexity(self, query: str, entities: list) -> str:
        """Estimate query complexity"""
        if len(entities) > 5:
            return "high"
        elif len(entities) > 2:
            return "medium"
        return "low"
