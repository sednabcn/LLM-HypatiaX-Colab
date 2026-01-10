#!/usr/bin/python3
"""
LLM-based Formula Mapping
Uses GPT/Claude APIs with few-shot prompting
"""

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


@dataclass
class LLMConfig:
    """Configuration for LLM-based mapping"""

    provider: str = "openai"  # or "anthropic", "openai"
    model: str = "gpt-4"  # or "claude-3-opus-20240229"
    api_key: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 256
    num_examples: int = 5
    output_dir: str = "./models/llm"


class PromptBuilder:
    """Build few-shot prompts for LLM"""

    @staticmethod
    def build_few_shot_prompt(query: str, examples: List[Dict]) -> str:
        """Create few-shot prompt with examples"""

        prompt = """You are an expert at converting natural language descriptions into data formulas.

Given a description, generate the corresponding formula using these functions:
- SUM([column]) - sum values
- AVG([column]) - average values
- COUNT([column]) - count rows
- COUNTD([column]) - count distinct values
- MAX([column]) - maximum value
- MIN([column]) - minimum value
- MEDIAN([column]) - median value
- GROUP BY [column] - group results

Examples:
"""

        # Add examples
        for ex in examples:
            prompt += f"\nDescription: {ex['description']}\n"
            prompt += f"Formula: {ex['formula']}\n"

        # Add query
        prompt += f"\nDescription: {query}\n"
        prompt += "Formula:"

        return prompt

    @staticmethod
    def build_system_prompt() -> str:
        """Create system prompt"""
        return """You are a data formula expert. Convert natural language descriptions
into precise formulas using aggregation functions (SUM, AVG, COUNT, etc.) and
column references in brackets [Column Name]. Be concise and accurate."""


class OpenAIClient:
    """OpenAI API client"""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 256,
    ) -> str:
        """Generate completion"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "Error: API call failed"


class AnthropicClient:
    """Anthropic Claude API client"""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 256,
    ) -> str:
        """Generate completion"""

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"].strip()
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            return "Error: API call failed"


class LLMTrainer:
    """LLM-based formula mapping trainer"""

    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.client = None
        self.examples = []
        self.prompt_builder = PromptBuilder()

        # Initialize API client
        api_key = self.config.api_key or os.getenv(
            "OPENAI_API_KEY"
            if self.config.provider == "openai"
            else "ANTHROPIC_API_KEY"
        )

        if not api_key:
            print(f"Warning: No API key found for {self.config.provider}")
            return

        if self.config.provider == "openai":
            self.client = OpenAIClient(api_key, self.config.model)
        elif self.config.provider == "anthropic":
            self.client = AnthropicClient(api_key, self.config.model)

    def load_examples(self, examples_path: str):
        """Load few-shot examples"""
        with open(examples_path, "r") as f:
            data = json.load(f)

        # Convert to dict format
        self.examples = []
        for item in data:
            if isinstance(item, list) and len(item) == 2:
                self.examples.append({"description": item[0], "formula": item[1]})
            elif isinstance(item, dict):
                self.examples.append(item)

        print(f"Loaded {len(self.examples)} examples")

    def select_examples(self, query: str, k: int = None) -> List[Dict]:
        """Select most relevant examples for few-shot prompting"""
        k = k or self.config.num_examples

        # Simple keyword-based selection
        query_words = set(query.lower().split())

        scored_examples = []
        for ex in self.examples:
            desc_words = set(ex["description"].lower().split())
            overlap = len(query_words.intersection(desc_words))
            scored_examples.append((overlap, ex))

        # Sort by relevance and take top k
        scored_examples.sort(reverse=True, key=lambda x: x[0])
        return [ex for _, ex in scored_examples[:k]]

    def generate_formula(self, query: str) -> str:
        """Generate formula for query using LLM"""

        if not self.client:
            return "Error: No API client initialized"

        # Select relevant examples
        selected_examples = self.select_examples(query)

        # Build prompt
        prompt = self.prompt_builder.build_few_shot_prompt(query, selected_examples)
        system_prompt = self.prompt_builder.build_system_prompt()

        # Generate
        formula = self.client.generate(
            prompt, system_prompt, self.config.temperature, self.config.max_tokens
        )

        return formula

    def batch_generate(self, queries: List[str], delay: float = 1.0) -> List[Dict]:
        """Generate formulas for multiple queries"""

        results = []

        for i, query in enumerate(queries):
            print(f"Processing {i+1}/{len(queries)}: {query}")

            formula = self.generate_formula(query)

            results.append({"query": query, "formula": formula})

            # Rate limiting
            if i < len(queries) - 1:
                time.sleep(delay)

        return results

    def save_results(self, results: List[Dict], output_path: str):
        """Save generation results"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"✅ Results saved to {output_path}")


def evaluate_llm(trainer: LLMTrainer, test_data: List[Dict]) -> Dict:
    """Evaluate LLM-based mapping"""

    correct = 0
    total = len(test_data)
    predictions = []

    for i, example in enumerate(test_data):
        print(f"Evaluating {i+1}/{total}...")

        query = example["description"]
        true_formula = example["formula"]

        predicted_formula = trainer.generate_formula(query)

        is_correct = predicted_formula.strip() == true_formula.strip()

        predictions.append(
            {
                "query": query,
                "true": true_formula,
                "predicted": predicted_formula,
                "correct": is_correct,
            }
        )

        if is_correct:
            correct += 1

        # Rate limiting
        time.sleep(1.0)

    accuracy = correct / total if total > 0 else 0

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "predictions": predictions,
    }


def main():
    """Example usage"""
    print("=" * 70)
    print("LLM-BASED FORMULA MAPPING")
    print("=" * 70)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  No OPENAI_API_KEY found in environment")
        print("Set with: export OPENAI_API_KEY='your-key'")
        print("\nRunning in demo mode with mock responses...")
        return

    # Configuration
    config = LLMConfig(
        provider="openai",
        model="gpt-4",
        temperature=0.1,
        num_examples=5,
        output_dir="./models/llm_formula_mapper",
    )

    # Initialize trainer
    trainer = LLMTrainer(config)

    # Load examples
    print("\nLoading examples...")
    trainer.load_examples("./preprocessed_data/mapping/train_mapping.json")

    # Test queries
    test_queries = [
        "average of Sales",
        "sum of Revenue by Region",
        "count unique customers",
        "maximum price per category",
    ]

    print("\n" + "=" * 70)
    print("GENERATING FORMULAS")
    print("=" * 70)

    results = trainer.batch_generate(test_queries, delay=1.0)

    # Display results
    for result in results:
        print(f"\nQuery: {result['query']}")
        print(f"Formula: {result['formula']}")

    # Save results
    trainer.save_results(results, f"{config.output_dir}/predictions.json")


if __name__ == "__main__":
    main()
