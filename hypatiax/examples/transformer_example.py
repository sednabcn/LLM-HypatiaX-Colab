"""Example: Using Transformer-based mapping"""
from mappings.transformer_mapping import TransformerMapper


def main():
    """Demonstrate transformer mapping"""
    print("Transformer-based Expression Mapping Example
")

    # Initialize mapper
    mapper = TransformerMapper()

    # Example queries
    queries = [
        "Find the integral of x squared",
        "What is the derivative of sine x?",
        "Solve the equation x squared equals 4"
    ]

    for query in queries:
        print(f"Query: {query}")
        result = mapper.map(query)
        print(f"Expression: {result.get('expression', 'N/A')}")
        print(f"Method: {result['method']}")
        print()

if __name__ == "__main__":
    main()
