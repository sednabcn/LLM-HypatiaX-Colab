"""Example: Using Agent-based mapping"""

from agents.specialists.parser_agent import ParserAgent
from agents.workflows.hybrid_workflow import HybridWorkflow


def main():
    """Demonstrate agent workflow"""
    print("Agent-based Expression Mapping Example")

    # Create workflow
    workflow = HybridWorkflow()

    # Add parser agent
    parser = ParserAgent()
    workflow.add_agent(parser)

    # Example query
    query = "Find the integral of x squared from 0 to 1"

    print(f"Query: {query}")

    # Execute workflow
    result = workflow.execute(query)

    print("Workflow Results:")
    for step in result["steps"]:
        print(f"  Agent: {step['agent']}")
        print(f"  Output: {step['result']}")
        print()


if __name__ == "__main__":
    main()
