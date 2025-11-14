"""Example: Using LLM-based mapping"""
from tools.llm_providers.openai_provider import OpenAIProvider
from mappings.llm_mapping import LLMMapper
import os

def main():
    """Demonstrate LLM mapping"""
    print("LLM-based Expression Mapping Example
")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return
    
    # Initialize LLM provider
    llm = OpenAIProvider(api_key=api_key)
    
    # Initialize mapper
    mapper = LLMMapper(llm_provider=llm)
    
    # Example queries
    queries = [
        "Find the integral of x squared from 0 to 1",
        "What is the derivative of cos(x)?",
        "Solve dy/dx = 2x"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        result = mapper.map(query, use_few_shot=True)
        print(f"Expression: {result.get('expression', 'N/A')}")
        print(f"Provider: {result.get('provider', 'N/A')}")
        print()

if __name__ == "__main__":
    main()
