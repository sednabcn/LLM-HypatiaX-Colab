#!/usr/bin/env python3
"""
Google Gemini API Provider for Formula Generation
Part of HypatiaX tools/llm_providers/google_provider.py
"""
import json
import os
import time
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory


class GoogleProvider:
    """
    Google Gemini integration for formula generation

    Usage:
        provider = GoogleProvider(api_key="your-key")
        result = provider.generate_formula(requirements="...", domain="defi")
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize Google Gemini client"""
        if api_key:
            genai.configure(api_key=api_key)
        else:
            # Try to get from environment
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
            else:
                raise ValueError("Google API key not provided")

        # Try different model names in order of preference
        if model_name:
            self.model = genai.GenerativeModel(model_name)
            print(f"✅ Using specified model: {model_name}")
        else:
            # Get list of actually available models
            available_models = []
            try:
                for model in genai.list_models():
                    if "generateContent" in model.supported_generation_methods:
                        available_models.append(model.name)
            except Exception as e:
                print(f"⚠️  Could not list models: {e}")

            # Preferred models in order (matching actual available names)
            preferred_models = [
                "models/gemini-2.5-flash",
                "models/gemini-2.0-flash",
                "models/gemini-flash-latest",
                "models/gemini-2.5-pro",
                "models/gemini-pro-latest",
                "models/gemini-2.0-flash-exp",
            ]

            # Try preferred models first, then any available model
            models_to_try = []
            for pref in preferred_models:
                if pref in available_models:
                    models_to_try.append(pref)

            # Add remaining available models
            for model in available_models:
                if model not in models_to_try and not any(
                    x in model
                    for x in ["thinking", "tts", "image", "robotics", "computer-use"]
                ):
                    models_to_try.append(model)

            if not models_to_try:
                raise ValueError("No compatible Gemini models found")

            # Test each model until one works
            model_initialized = False
            for model_name in models_to_try:
                try:
                    # Try to create model and do a minimal test
                    test_model = genai.GenerativeModel(model_name)
                    self.model = test_model
                    print(f"✅ Using model: {model_name}")
                    model_initialized = True
                    break
                except Exception as e:
                    print(f"⚠️  Model {model_name} failed: {str(e)[:80]}...")
                    continue

            if not model_initialized:
                raise ValueError(
                    f"Could not initialize any model. Tried: {', '.join(models_to_try[:5])}"
                )

        # Configure generation settings for more deterministic output
        self.generation_config = genai.GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,  # Increased from 2048 to allow longer responses
        )

        # Properly configured safety settings using the SDK enums
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

    def generate_formula(
        self, requirements: str, domain: str = "defi", n_candidates: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Generate analytical formulas using Gemini

        Args:
            requirements: Natural language description
            domain: "defi", "finance", "esg", "risk"
            n_candidates: Number of formula variants

        Returns:
            List of formula dictionaries with structure:
            {
                'formula_latex': LaTeX notation,
                'formula_python': Python implementation,
                'variables': {var: description},
                'explanation': What this measures,
                'constraints': [mathematical constraints],
                'novelty_score': 0-10,
                'advantages': [list],
                'limitations': [list]
            }
        """
        formulas = []

        for i in range(n_candidates):
            prompt = self._build_prompt(requirements, domain, i)

            for attempt in range(2):  # Try twice: once normal, once with fallback
                try:
                    response = self._call_with_retry(prompt, max_retries=3)

                    # Check if response was blocked or incomplete
                    if not response.parts:
                        # Get more detailed error info
                        finish_reason = "UNKNOWN"
                        safety_ratings = []

                        if response.candidates and len(response.candidates) > 0:
                            candidate = response.candidates[0]
                            # Get finish reason name instead of number
                            finish_reason = (
                                candidate.finish_reason.name
                                if hasattr(candidate.finish_reason, "name")
                                else str(candidate.finish_reason)
                            )
                            safety_ratings = (
                                candidate.safety_ratings
                                if hasattr(candidate, "safety_ratings")
                                else []
                            )

                        # Handle MAX_TOKENS specifically
                        if finish_reason == "MAX_TOKENS":
                            print(f"\n⚠️  Response incomplete - hit token limit")
                            print("💡 Trying to extract partial response...")

                            # Try to get partial text if available
                            try:
                                partial_text = ""
                                if response.candidates and len(response.candidates) > 0:
                                    for part in response.candidates[0].content.parts:
                                        if hasattr(part, "text"):
                                            partial_text += part.text

                                if partial_text:
                                    print(
                                        f"📝 Got partial response ({len(partial_text)} chars)"
                                    )
                                    formula = self._parse_response(partial_text)
                                    if (
                                        "error" not in formula
                                        or formula.get("formula_latex") != "Parse error"
                                    ):
                                        print(
                                            "✅ Successfully parsed partial response!"
                                        )
                                        formulas.append(formula)
                                        break
                            except Exception as parse_error:
                                print(
                                    f"❌ Could not parse partial response: {parse_error}"
                                )

                            # If we couldn't parse partial, retry with more concise prompt
                            if attempt == 0:
                                print("🔄 Retrying with more concise prompt...")
                                prompt = self._build_concise_prompt(
                                    requirements, domain
                                )
                                continue

                        print(f"\n⚠️  Response blocked - Finish reason: {finish_reason}")
                        print(f"📝 Prompt used: {prompt[:200]}...")

                        if safety_ratings:
                            print("🛡️  Safety ratings:")
                            for rating in safety_ratings:
                                category_name = (
                                    rating.category.name
                                    if hasattr(rating.category, "name")
                                    else str(rating.category)
                                )
                                probability_name = (
                                    rating.probability.name
                                    if hasattr(rating.probability, "name")
                                    else str(rating.probability)
                                )
                                print(f"  • {category_name}: {probability_name}")
                        else:
                            print("🛡️  No safety ratings available in response")

                        # Try with a more conservative generation config on first attempt
                        if attempt == 0:
                            print("🔄 Retrying with simpler prompt...")
                            prompt = self._build_simple_prompt(requirements, domain)
                            continue
                        else:
                            # Last attempt failed
                            error_details = f"Finish reason: {finish_reason}"
                            if safety_ratings:
                                blocked_categories = []
                                for rating in safety_ratings:
                                    cat_name = (
                                        rating.category.name
                                        if hasattr(rating.category, "name")
                                        else str(rating.category)
                                    )
                                    prob_name = (
                                        rating.probability.name
                                        if hasattr(rating.probability, "name")
                                        else str(rating.probability)
                                    )
                                    blocked_categories.append(
                                        f"{cat_name}: {prob_name}"
                                    )

                                if blocked_categories:
                                    error_details += (
                                        f"\nCategories: {', '.join(blocked_categories)}"
                                    )

                            error_msg = f"Response blocked. {error_details}"
                            formulas.append(
                                {
                                    "formula_latex": "Response blocked",
                                    "formula_python": "# Response was blocked by safety filters",
                                    "error": error_msg,
                                    "variables": {},
                                    "explanation": error_msg,
                                    "novelty_score": 0,
                                }
                            )
                            break
                    else:
                        # Parse response
                        content = response.text
                        formula = self._parse_response(content)
                        formulas.append(formula)
                        break  # Success, exit attempt loop

                except Exception as e:
                    error_str = str(e)
                    print(f"\n❌ Exception occurred: {error_str}")
                    if attempt == 1:  # Last attempt
                        formulas.append(
                            {
                                "formula_latex": "Generation error",
                                "formula_python": "# Error generating formula",
                                "error": error_str,
                                "variables": {},
                                "explanation": f"Failed to generate formula: {error_str}",
                                "novelty_score": 0,
                            }
                        )
                        break
                    else:
                        # Try simpler prompt
                        print(f"⚠️  Attempt {attempt + 1} failed: {error_str[:80]}")
                        print("🔄 Retrying with simpler prompt...")
                        prompt = self._build_simple_prompt(requirements, domain)

        return formulas

    def _call_with_retry(self, prompt: str, max_retries: int = 3):
        """Call API with exponential backoff retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings,
                )
                return response
            except Exception as e:
                error_str = str(e)
                # Check if it's a quota error
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        # Extract retry delay from error if available
                        wait_time = 2**attempt  # Exponential backoff: 1s, 2s, 4s
                        if "retry in" in error_str:
                            try:
                                # Try to extract the suggested wait time
                                import re

                                match = re.search(r"retry in ([\d.]+)s", error_str)
                                if match:
                                    wait_time = float(match.group(1))
                            except:
                                pass

                        print(
                            f"⏳ Rate limit hit. Waiting {wait_time:.1f}s before retry {attempt + 2}/{max_retries}..."
                        )
                        time.sleep(wait_time)
                        continue
                # Re-raise if not a quota error or last attempt
                raise e

        raise Exception("Max retries exceeded")

    def _build_prompt(self, requirements: str, domain: str, variant: int) -> str:
        """Build generation prompt - simplified to avoid triggering safety filters"""
        domain_contexts = {
            "defi": "decentralized finance, liquidity pools, automated market makers",
            "finance": "portfolio optimization, financial metrics, returns analysis",
            "esg": "environmental social governance, sustainability metrics",
            "risk": "risk assessment, value at risk, exposure analysis",
        }

        context = domain_contexts.get(domain, "financial mathematics")

        # Even simpler prompt focused purely on mathematics
        return f"""Create a mathematical formula for the following financial calculation task:

Task: {requirements}
Domain: {domain} ({context})
Variant: {variant + 1}

Provide a JSON response with this structure:
{{
    "formula_latex": "mathematical formula in LaTeX notation",
    "formula_python": "Python function implementation",
    "variables": {{"var_name": "description"}},
    "explanation": "description of what this formula calculates",
    "constraints": ["mathematical constraint"],
    "novelty_score": 5,
    "similar_to": ["related formula name"],
    "advantages": ["benefit"],
    "limitations": ["limitation"]
}}

Requirements:
- Use standard mathematical notation
- Ensure computational stability
- Base on established financial formulas

Return only valid JSON."""

    def _build_simple_prompt(self, requirements: str, domain: str) -> str:
        """Build a very simple prompt to avoid safety filters"""
        return f"""Generate a mathematical formula for: {requirements}

Domain: {domain}

Return JSON:
{{
    "formula_latex": "LaTeX formula",
    "formula_python": "Python code",
    "variables": {{}},
    "explanation": "what it calculates",
    "novelty_score": 5,
    "constraints": [],
    "advantages": [],
    "limitations": []
}}

JSON only, no other text."""

    def _build_concise_prompt(self, requirements: str, domain: str) -> str:
        """Build ultra-concise prompt to minimize token usage"""
        return f"""Task: {requirements}
Domain: {domain}

Output JSON only with these exact fields:
- formula_latex: LaTeX notation
- formula_python: Python function
- variables: dict of variable descriptions
- explanation: brief description
- novelty_score: integer 0-10
- constraints: list
- advantages: list (max 3 items)
- limitations: list (max 3 items)

Keep all text responses brief. Return valid JSON only."""

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Extract JSON from response"""
        try:
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Find JSON in response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON object found in response")

            json_str = content[start:end]
            result = json.loads(json_str)

            # Ensure all required fields
            required = [
                "formula_latex",
                "formula_python",
                "variables",
                "explanation",
                "novelty_score",
            ]
            for field in required:
                if field not in result:
                    result[field] = "N/A"

            # Set defaults
            result.setdefault("constraints", [])
            result.setdefault("advantages", [])
            result.setdefault("limitations", [])
            result.setdefault("similar_to", [])

            return result
        except Exception as e:
            return {
                "formula_latex": "Parse error",
                "formula_python": "# Error parsing response",
                "error": str(e),
                "raw_content": content[:500],  # Limit raw content length
                "variables": {},
                "explanation": "Failed to parse response",
                "novelty_score": 0,
            }

    def refine_formula(self, formula: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Iteratively improve formula based on feedback

        Args:
            formula: Original formula dict
            feedback: User feedback on what to improve

        Returns:
            Refined formula dict
        """
        prompt = f"""Improve this mathematical formula based on feedback.

Original formula: {formula['formula_latex']}
Implementation: {formula['formula_python']}

Feedback: {feedback}

Generate an improved version. Return JSON format:
{{
    "formula_latex": "improved formula",
    "formula_python": "improved code",
    "variables": {{}},
    "explanation": "description",
    "novelty_score": 5,
    "constraints": [],
    "advantages": [],
    "limitations": []
}}"""

        try:
            response = self._call_with_retry(prompt, max_retries=3)

            if not response.parts:
                return {
                    "formula_latex": "Refinement blocked",
                    "formula_python": "# Response was blocked",
                    "error": "Response blocked by safety filters",
                    "variables": {},
                    "explanation": "Failed to refine formula - response blocked",
                    "novelty_score": 0,
                }

            content = response.text
            return self._parse_response(content)
        except Exception as e:
            return {
                "formula_latex": "Refinement error",
                "formula_python": "# Error refining formula",
                "error": str(e),
                "variables": {},
                "explanation": f"Failed to refine formula: {str(e)}",
                "novelty_score": 0,
            }


# Example usage and testing
if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        print("💡 Get your API key from: https://aistudio.google.com/")
        exit(1)

    # First, list available models
    print("Available Gemini models:")
    print("=" * 60)
    try:
        genai.configure(api_key=api_key)
        for model in genai.list_models():
            if "generateContent" in model.supported_generation_methods:
                print(f"  • {model.name}")
    except Exception as e:
        print(f"Could not list models: {e}")

    print("\n" + "=" * 60)

    provider = GoogleProvider(api_key=api_key)

    print("Testing Google Gemini Provider...")
    print("=" * 60)

    # Test formula generation
    results = provider.generate_formula(
        requirements="Calculate impermanent loss for Uniswap V2 pools",
        domain="defi",
        n_candidates=1,
    )

    formula = results[0]

    if "error" in formula:
        print(f"\n❌ Error: {formula['error']}")
        if "raw_content" in formula:
            print(f"\nRaw response:\n{formula['raw_content']}")
    else:
        print(f"\n📐 Formula: {formula['formula_latex']}")
        print(f"\n💻 Implementation:\n{formula['formula_python']}")
        print(f"\n📝 Explanation: {formula['explanation']}")
        print(f"\n🎯 Novelty Score: {formula['novelty_score']}/10")
        if formula.get("advantages"):
            print(f"\n✅ Advantages: {', '.join(formula['advantages'])}")
        if formula.get("limitations"):
            print(f"\n⚠️  Limitations: {', '.join(formula['limitations'])}")
        print("\n✅ Test completed!")
