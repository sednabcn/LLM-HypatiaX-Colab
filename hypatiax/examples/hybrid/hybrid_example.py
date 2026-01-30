"""Example: Using Hybrid mapping (all methods)"""

import os

from mappings.hybrid_mapping import HybridMapper
from mappings.llm_mapping import LLMMapper
from tools.llm_providers.openai_provider import OpenAIProvider


def main():
    """Demonstrate hybrid mapping combining all methods"""
    print("Hybrid Expression Mapping Example")

    print("This combines NER + Transformer + LLM + Agents")

    # Initialize LLM mapper (if API key available)
    llm_mapper = None
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm = OpenAIProvider(api_key=api_key)
        llm_mapper = LLMMapper(llm_provider=llm)
    else:
        print("OPENAI_API_KEY not set, LLM mapping will be skipped")

    # Initialize hybrid mapper
    hybrid = HybridMapper(llm_mapper=llm_mapper)

    # Example query
    query = "Find the derivative of sin(x) * cos(x)"

    print(f"Query: {query}")

    # Map using all available methods
    result = hybrid.map(
        query,
        use_ner=True,
        use_transformer=True,
        use_llm=bool(llm_mapper),
        use_agents=False,
    )

    print("Results from each method:")
    for method, output in result["methods"].items():
        print(f"  {method.upper()}:")
        if "error" in output:
            print(f"Error: {output['error']}")
        else:
            print(f"Expression: {output.get('expression', 'N/A')}")

    print(f"Best Expression: {result['best_expression']}")


if __name__ == "__main__":
    main()
