"""
HypatiaX Demo Package
Demonstration framework for HypatiaX functionality
"""

from .demo_runner import DemoRunner
from .raw_sentences.demo_raw import (
    ALL_DEMO_SENTENCES,
    COMMAND_QUERIES,
    COMPLEX_QUERIES,
    CONVERSION_QUERIES,
    INFO_QUERIES,
    MATH_QUERIES,
    get_demo_sentences,
    get_training_data,
)
from .utils.demo_helpers import (
    benchmark_demo,
    compare_results,
    create_demo_report,
    format_entity,
    format_intent,
    load_demo_results,
    print_demo_summary,
    save_demo_results,
    validate_demo_result,
)

__all__ = [
    "DemoRunner",
    "get_demo_sentences",
    "get_training_data",
    "save_demo_results",
    "load_demo_results",
    "format_entity",
    "format_intent",
    "compare_results",
    "create_demo_report",
    "print_demo_summary",
    "validate_demo_result",
    "benchmark_demo",
    "MATH_QUERIES",
    "CONVERSION_QUERIES",
    "INFO_QUERIES",
    "COMMAND_QUERIES",
    "COMPLEX_QUERIES",
    "ALL_DEMO_SENTENCES",
]
