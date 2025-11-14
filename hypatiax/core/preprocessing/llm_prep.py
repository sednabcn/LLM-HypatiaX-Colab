"""LLM prompt preprocessing"""
from typing import List, Dict, Any

class LLMPreprocessor:
    """Prepare prompts for LLM models"""
    
    def format_few_shot_prompt(
        self,
        query: str,
        examples: List[Dict[str, str]],
        system_message: str = "You are a mathematical expression mapper."
    ) -> str:
        """Format few-shot learning prompt"""
        prompt_parts = [system_message, ""]
        
        # Add examples
        for i, example in enumerate(examples, 1):
            prompt_parts.append(f"Example {i}:")
            prompt_parts.append(f"Query: {example['query']}")
            prompt_parts.append(f"Expression: {example['expression']}")
            prompt_parts.append("")
        
        # Add current query
        prompt_parts.append("Now, for the following query:")
        prompt_parts.append(f"Query: {query}")
        prompt_parts.append("Expression:")
        
        return "
".join(prompt_parts)
    
    def format_chain_of_thought_prompt(self, query: str) -> str:
        """Format chain-of-thought reasoning prompt"""
        return f"""Let's solve this step by step:

Query: {query}

Step 1: Identify the mathematical operation
Step 2: Extract relevant variables and parameters
Step 3: Construct the mathematical expression
Step 4: Verify the expression is correct

Expression:"""
