from collections import deque
from typing import Dict, List, Optional

import numpy as np

from hypatiax.tools.llm_providers.llm_interpreter import InterpretationConfig, LLMInterpreter
from hypatiax.tools.symbolic.symbolic_engine import DiscoveryConfig, SymbolicEngine


class HybridDiscoverySystem:
    def __init__(
        self,
        discovery_config: DiscoveryConfig = None,
        interpretation_config: InterpretationConfig = None,
        max_results: Optional[int] = 100,
    ):
        """
        Initialize the hybrid discovery system.

        Args:
            discovery_config: Configuration for symbolic regression
            interpretation_config: Configuration for LLM interpretation
            max_results: Maximum number of results to keep in memory.
                        If None, no limit. Defaults to 100.
        """
        self.symbolic_engine = SymbolicEngine(discovery_config or DiscoveryConfig())
        self.llm_interpreter = LLMInterpreter(interpretation_config or InterpretationConfig())
        self.max_results = max_results

        # Use deque with maxlen for automatic size limiting
        if max_results is not None:
            self.results = deque(maxlen=max_results)
        else:
            self.results = []

    def discover_and_interpret(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str],
        variable_descriptions: Dict[str, str],
        domain: str,
    ) -> Dict:
        """
        Discover symbolic expression and interpret it using LLM.

        Args:
            X: Input features
            y: Target values
            variable_names: Names of variables
            variable_descriptions: Descriptions of what each variable represents
            domain: Domain context (e.g., 'defi', 'risk')

        Returns:
            Dictionary containing discovery results and interpretation
        """
        print(f"Discovering expression from {len(X)} samples...")
        discovery_result = self.symbolic_engine.discover(X, y, variable_names)

        print(f"Interpreting discovered expression...")
        interpretation = self.llm_interpreter.interpret(
            expression=discovery_result["expression"],
            domain=domain,
            variables=variable_descriptions,
            r2=discovery_result["r2_score"],
        )

        complete_result = {**discovery_result, "interpretation": interpretation, "domain": domain}

        self.results.append(complete_result)
        return complete_result

    def clear_results(self):
        """Clear all stored results."""
        if isinstance(self.results, deque):
            self.results.clear()
        else:
            self.results = []

    def get_results(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get stored results.

        Args:
            limit: Maximum number of most recent results to return

        Returns:
            List of result dictionaries
        """
        results_list = list(self.results)
        if limit is not None:
            return results_list[-limit:]
        return results_list

    def get_best_result(self, metric: str = "r2_score") -> Optional[Dict]:
        """
        Get the best result based on a metric.

        Args:
            metric: Metric to use for comparison (default: 'r2_score')

        Returns:
            Best result dictionary or None if no results
        """
        if not self.results:
            return None

        return max(self.results, key=lambda x: x.get(metric, float("-inf")))

    def export_results(self, filepath: str):
        """
        Export results to a JSON file.

        Args:
            filepath: Path to save the JSON file
        """
        import json

        # Convert results to list and handle numpy types
        results_list = []
        for result in self.results:
            serializable_result = {}
            for key, value in result.items():
                if isinstance(value, np.ndarray):
                    serializable_result[key] = value.tolist()
                elif hasattr(value, "__dict__"):
                    serializable_result[key] = str(value)
                else:
                    serializable_result[key] = value
            results_list.append(serializable_result)

        with open(filepath, "w") as f:
            json.dump(results_list, f, indent=2)

        print(f"Exported {len(results_list)} results to {filepath}")
