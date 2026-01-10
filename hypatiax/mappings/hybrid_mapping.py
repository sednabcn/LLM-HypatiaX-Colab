"""Hybrid mapping combining all methods"""

from typing import Any, Dict, List, Optional


class HybridMapper:
    """Ensemble mapper using multiple strategies"""

    def __init__(
        self,
        ner_mapper=None,
        transformer_mapper=None,
        llm_mapper=None,
        agent_mapper=None,
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
        use_agents: bool = False,
    ) -> Dict[str, Any]:
        """Map using multiple strategies and combine results"""
        results = {"query": query, "methods": {}}

        # Try NER-based mapping
        if use_ner and self.ner_mapper:
            try:
                results["methods"]["ner"] = self.ner_mapper.map(query)
            except Exception as e:
                results["methods"]["ner"] = {"error": str(e)}

        # Try transformer-based mapping
        if use_transformer and self.transformer_mapper:
            try:
                results["methods"]["transformer"] = self.transformer_mapper.map(query)
            except Exception as e:
                results["methods"]["transformer"] = {"error": str(e)}

        # Try LLM-based mapping
        if use_llm and self.llm_mapper:
            try:
                results["methods"]["llm"] = self.llm_mapper.map(query)
            except Exception as e:
                results["methods"]["llm"] = {"error": str(e)}

        # Try agent-based mapping
        if use_agents and self.agent_mapper:
            try:
                results["methods"]["agent"] = self.agent_mapper.map(query)
            except Exception as e:
                results["methods"]["agent"] = {"error": str(e)}

        # Select best result (simple strategy: prefer LLM > Transformer > NER)
        results["best_expression"] = self._select_best(results["methods"])

        return results

    def _select_best(self, methods: Dict) -> Optional[str]:
        """Select best expression from multiple methods"""
        # Priority: agent > llm > transformer > ner
        for method in ["agent", "llm", "transformer", "ner"]:
            if method in methods and "expression" in methods[method]:
                expr = methods[method]["expression"]
                if expr:
                    return expr
        return None
