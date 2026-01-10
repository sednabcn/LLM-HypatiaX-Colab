#!/usr/bin/env python3
"""
Demo Helpers
Utility functions for HypatiaX demos
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def save_demo_results(
    results: Dict[str, Any], output_path: Optional[Path] = None
) -> Path:
    """
    Save demo results to JSON file

    Args:
        results: Dictionary of demo results
        output_path: Optional path to save to. If None, uses timestamp

    Returns:
        Path where results were saved
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"demo_results_{timestamp}.json")

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Results saved to: {output_path}")
    return output_path


def load_demo_results(input_path: Path) -> Dict[str, Any]:
    """
    Load demo results from JSON file

    Args:
        input_path: Path to JSON file

    Returns:
        Dictionary of demo results
    """
    with open(input_path, "r") as f:
        results = json.load(f)

    print(f"✅ Results loaded from: {input_path}")
    return results


def format_entity(entity: Dict[str, Any]) -> str:
    """
    Format entity for display

    Args:
        entity: Entity dictionary

    Returns:
        Formatted string
    """
    text = entity.get("text", "")
    entity_type = entity.get("type", "UNKNOWN")
    confidence = entity.get("confidence", 0.0)

    return f"{text} ({entity_type}) [{confidence:.2%}]"


def format_intent(intent: Dict[str, Any]) -> str:
    """
    Format intent for display

    Args:
        intent: Intent dictionary

    Returns:
        Formatted string
    """
    intent_type = intent.get("intent", "UNKNOWN")
    confidence = intent.get("confidence", 0.0)

    return f"{intent_type} [{confidence:.2%}]"


def compare_results(result1: Dict[str, Any], result2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two demo results

    Args:
        result1: First result dictionary
        result2: Second result dictionary

    Returns:
        Dictionary with comparison metrics
    """
    comparison = {
        "same_intent": result1.get("intent") == result2.get("intent"),
        "entity_count_diff": len(result1.get("entities", []))
        - len(result2.get("entities", [])),
        "same_output": result1.get("output") == result2.get("output"),
    }

    return comparison


def create_demo_report(results: List[Dict[str, Any]]) -> str:
    """
    Create a text report from demo results

    Args:
        results: List of result dictionaries

    Returns:
        Formatted report string
    """
    report_lines = [
        "=" * 60,
        "HypatiaX Demo Report",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total Results: {len(results)}",
        "",
    ]

    for i, result in enumerate(results, 1):
        report_lines.extend(
            [
                f"\n[Result {i}]",
                f"Input: {result.get('input', 'N/A')}",
                f"Status: {result.get('status', 'N/A')}",
                f"Intent: {format_intent(result.get('intent', {}))}",
                f"Entities: {len(result.get('entities', []))} found",
            ]
        )

        for entity in result.get("entities", []):
            report_lines.append(f"  - {format_entity(entity)}")

        report_lines.append(f"Output: {result.get('output', 'N/A')}")

    report_lines.append("\n" + "=" * 60)

    return "\n".join(report_lines)


def print_demo_summary(results: List[Dict[str, Any]]) -> None:
    """
    Print a summary of demo results

    Args:
        results: List of result dictionaries
    """
    print("\n" + "=" * 60)
    print("Demo Summary")
    print("=" * 60)

    total = len(results)
    successful = sum(1 for r in results if r.get("status") == "processed")
    failed = total - successful

    print(f"Total: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if total > 0:
        print(f"Success Rate: {successful / total:.1%}")

    # Intent distribution
    intents = {}
    for result in results:
        intent = result.get("intent", {}).get("intent", "UNKNOWN")
        intents[intent] = intents.get(intent, 0) + 1

    print("\nIntent Distribution:")
    for intent, count in sorted(intents.items(), key=lambda x: x[1], reverse=True):
        print(f"  {intent}: {count}")

    print("=" * 60)


def validate_demo_result(result: Dict[str, Any]) -> bool:
    """
    Validate that a demo result has required fields

    Args:
        result: Result dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["input", "status", "entities", "intent", "output"]

    for field in required_fields:
        if field not in result:
            print(f"❌ Missing required field: {field}")
            return False

    return True


def benchmark_demo(runner, test_sentences: List[str]) -> Dict[str, Any]:
    """
    Benchmark demo runner performance

    Args:
        runner: DemoRunner instance
        test_sentences: List of sentences to test

    Returns:
        Dictionary with benchmark results
    """
    import time

    start_time = time.time()
    results = []

    for sentence in test_sentences:
        result_start = time.time()
        result = runner.run(sentence, verbose=False)
        result_time = time.time() - result_start

        result["processing_time"] = result_time
        results.append(result)

    total_time = time.time() - start_time
    avg_time = total_time / len(test_sentences) if test_sentences else 0

    benchmark = {
        "total_time": total_time,
        "avg_time": avg_time,
        "num_sentences": len(test_sentences),
        "results": results,
    }

    print(f"\n⏱️  Benchmark Complete:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average time: {avg_time:.2f}s per sentence")
    print(f"   Sentences processed: {len(test_sentences)}")

    return benchmark
