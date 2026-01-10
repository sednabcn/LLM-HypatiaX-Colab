#!/usr/bin/env python3
"""
HypatiaX Demo Runner
Main class for running demonstrations of the HypatiaX pipeline
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from hypatiax.config import ModelConfig, paths


class DemoRunner:
    """
    Runs demonstrations of HypatiaX functionality

    Usage:
        runner = DemoRunner()
        result = runner.run("calculate the area of a circle with radius 5")
    """

    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Initialize the demo runner

        Args:
            config: Optional ModelConfig instance. If None, uses default config.
        """
        self.config = config or ModelConfig()
        self.results_history: List[Dict[str, Any]] = []

    def run(self, input_text: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Run a demo with the given input

        Args:
            input_text: Natural language input to process
            verbose: Whether to print detailed output

        Returns:
            Dictionary containing demo results
        """
        if verbose:
            print("=" * 60)
            print("HypatiaX Demo Runner")
            print("=" * 60)
            print(f"Input: {input_text}")
            print("-" * 60)

        # Placeholder for actual pipeline processing
        result = {
            "input": input_text,
            "status": "processed",
            "entities": self._extract_entities(input_text),
            "intent": self._classify_intent(input_text),
            "output": self._generate_output(input_text),
        }

        self.results_history.append(result)

        if verbose:
            self._print_result(result)

        return result

    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract entities from text (placeholder)"""
        # TODO: Implement actual entity extraction
        return [{"text": "demo", "type": "PLACEHOLDER", "confidence": 0.95}]

    def _classify_intent(self, text: str) -> Dict[str, Any]:
        """Classify intent of text (placeholder)"""
        # TODO: Implement actual intent classification
        return {"intent": "DEMO_INTENT", "confidence": 0.90}

    def _generate_output(self, text: str) -> str:
        """Generate output response (placeholder)"""
        # TODO: Implement actual output generation
        return f"Processed: {text}"

    def _print_result(self, result: Dict[str, Any]) -> None:
        """Pretty print demo results"""
        print("\n📊 Results:")
        print(f"  Status: {result['status']}")
        print(f"\n  🎯 Intent: {result['intent']['intent']}")
        print(f"     Confidence: {result['intent']['confidence']:.2%}")
        print(f"\n  🏷️  Entities: {len(result['entities'])} found")
        for entity in result["entities"]:
            print(f"     - {entity['text']} ({entity['type']})")
        print(f"\n  💬 Output: {result['output']}")
        print("=" * 60)

    def run_batch(
        self, inputs: List[str], verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Run multiple demos in batch

        Args:
            inputs: List of input texts to process
            verbose: Whether to print each result

        Returns:
            List of result dictionaries
        """
        print(f"\n🚀 Running batch demo with {len(inputs)} inputs...")
        results = []

        for i, input_text in enumerate(inputs, 1):
            if verbose:
                print(f"\n[{i}/{len(inputs)}]")
            result = self.run(input_text, verbose=verbose)
            results.append(result)

        print(f"\n✅ Batch complete: {len(results)} results")
        return results

    def get_history(self) -> List[Dict[str, Any]]:
        """Get all demo results from this session"""
        return self.results_history

    def clear_history(self) -> None:
        """Clear demo results history"""
        self.results_history.clear()


def main():
    """Run a simple demo"""
    runner = DemoRunner()

    # Single demo
    runner.run("calculate the area of a circle with radius 5")

    # Batch demo
    print("\n")
    test_inputs = [
        "what is 2 + 2",
        "find the square root of 16",
        "convert 100 celsius to fahrenheit",
    ]
    runner.run_batch(test_inputs, verbose=True)


if __name__ == "__main__":
    main()
