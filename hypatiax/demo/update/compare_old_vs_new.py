#!/usr/bin/env python3
"""
Comparison Demo: Old Sequential Pipeline vs Modern LLM (2025)
============================================================
Shows side-by-side comparison to demonstrate why LLMs are better.

Usage:
    python compare_old_vs_new.py
"""

import os
import sys
import time
from typing import List, Dict
from dataclasses import dataclass

# Try to import both approaches
try:
    from modern_llm_mapper import ModernLLMMapper
    HAS_MODERN = True
except ImportError:
    HAS_MODERN = False
    print("⚠️  modern_llm_mapper.py not found")

# Simulated old pipeline (replace with your actual training_spacy.py if available)
class OldSequentialPipeline:
    """
    Simulates the old 2018-style NER → Mapping → Generation pipeline
    This is what you were building with training_spacy.py
    """
    
    def __init__(self):
        self.approach = "Sequential NER Pipeline"
        # Simulate trained models
        self.ner_model = "spacy_ner_model"
        self.mapping_rules = "manual_rules"
        self.generator = "template_generator"
    
    def extract_entities(self, text: str) -> Dict:
        """Step 1: NER - Extract entities (70% accuracy)"""
        # Simulate NER extraction with errors
        entities = {}
        
        if "circle" in text.lower():
            entities["shape"] = "circle"
        if "area" in text.lower():
            entities["property"] = "area"
        if "volume" in text.lower():
            entities["property"] = "volume"
        if "sphere" in text.lower():
            entities["shape"] = "sphere"
        
        # Simulate NER failures (30% miss rate)
        import random
        if random.random() < 0.3:
            return {}  # NER failed
        
        return entities
    
    def map_to_formula_type(self, entities: Dict) -> str:
        """Step 2: Mapping - Map entities to formula type (80% accuracy)"""
        if not entities:
            return None
        
        shape = entities.get("shape", "")
        prop = entities.get("property", "")
        
        # Manual mapping rules
        if shape == "circle" and prop == "area":
            return "circle_area"
        elif shape == "sphere" and prop == "volume":
            return "sphere_volume"
        else:
            return None  # Mapping failed
    
    def generate_formula(self, formula_type: str) -> str:
        """Step 3: Generation - Generate formula from type (90% accuracy)"""
        if not formula_type:
            return "ERROR: No formula type"
        
        # Template-based generation
        templates = {
            "circle_area": "A = π*r²",
            "sphere_volume": "V = (4/3)*π*r³",
        }
        
        return templates.get(formula_type, "ERROR: Unknown formula")
    
    def map_single(self, text: str) -> Dict:
        """Full pipeline execution"""
        start_time = time.time()
        
        # Step 1: NER
        entities = self.extract_entities(text)
        if not entities:
            return {
                "input": text,
                "formula": "ERROR: NER extraction failed",
                "confidence": 0.0,
                "method": "sequential_pipeline",
                "steps": ["NER failed ❌"],
                "time": time.time() - start_time
            }
        
        # Step 2: Mapping
        formula_type = self.map_to_formula_type(entities)
        if not formula_type:
            return {
                "input": text,
                "formula": "ERROR: Mapping failed",
                "confidence": 0.0,
                "method": "sequential_pipeline",
                "steps": [
                    f"NER: {entities} ✅",
                    "Mapping failed ❌"
                ],
                "time": time.time() - start_time
            }
        
        # Step 3: Generation
        formula = self.generate_formula(formula_type)
        
        # Calculate compound confidence (70% × 80% × 90% = 50.4%)
        confidence = 0.70 * 0.80 * 0.90
        
        return {
            "input": text,
            "formula": formula,
            "confidence": confidence,
            "method": "sequential_pipeline",
            "steps": [
                f"NER: {entities} ✅",
                f"Mapping: {formula_type} ✅",
                f"Generation: {formula} ✅"
            ],
            "time": time.time() - start_time
        }


@dataclass
class ComparisonResult:
    """Results from comparing both approaches"""
    input_text: str
    old_result: Dict
    new_result: Dict
    
    def print_comparison(self):
        """Pretty print comparison"""
        print("\n" + "="*70)
        print(f"Input: '{self.input_text}'")
        print("="*70)
        
        # Old approach
        print("\n❌ OLD APPROACH (2018 Sequential Pipeline):")
        print(f"   Method: {self.old_result['method']}")
        if "steps" in self.old_result:
            print("   Pipeline Steps:")
            for step in self.old_result['steps']:
                print(f"     - {step}")
        print(f"   Formula: {self.old_result['formula']}")
        print(f"   Confidence: {self.old_result['confidence']:.1%}")
        print(f"   Time: {self.old_result['time']:.3f}s")
        
                # New approach
        print("\n✅ NEW APPROACH (Modern LLM Mapper):")
        if self.new_result:
            print(f"   Method: {self.new_result.get('method', 'modern_llm_mapper')}")
            if "steps" in self.new_result:
                print("   Reasoning Steps:")
                for step in self.new_result['steps']:
                    print(f"     - {step}")
            print(f"   Formula: {self.new_result.get('formula', 'N/A')}")
            print(f"   Confidence: {self.new_result.get('confidence', 0):.1%}")
            print(f"   Time: {self.new_result.get('time', 0):.3f}s")
        else:
            print("   ⚠️  modern_llm_mapper.py not available or failed.")

        # Summary comparison
        print("\n📊 SUMMARY COMPARISON")
        print(f"   Old Confidence: {self.old_result['confidence']:.1%}")
        if self.new_result:
            print(f"   New Confidence: {self.new_result.get('confidence', 0):.1%}")
            delta = self.new_result.get('confidence', 0) - self.old_result['confidence']
            print(f"   Improvement: {delta*100:.1f}%")
        else:
            print("   Unable to compute improvement (missing new result).")


def run_comparison(inputs: List[str]):
    """Runs the comparison between old and new pipelines"""
    old = OldSequentialPipeline()
    results: List[ComparisonResult] = []

    if HAS_MODERN:
        llm = ModernLLMMapper()
    else:
        llm = None

    for text in inputs:
        print("\n🔍 Running comparison for:", text)
        old_res = old.map_single(text)

        new_res = None
        if llm:
            try:
                new_res = llm.map_single(text)
            except Exception as e:
                print(f"⚠️ LLM mapping failed for '{text}': {e}")
                new_res = None

        comparison = ComparisonResult(
            input_text=text,
            old_result=old_res,
            new_result=new_res or {}
        )
        comparison.print_comparison()
        results.append(comparison)

    print("\n✅ Comparison complete for all inputs.")
    return results


def demo_inputs() -> List[str]:
    """Provide default example prompts"""
    return [
        "Find the area of a circle",
        "Compute the volume of a sphere",
        "Calculate the area of a rectangle",
        "What is the formula for the surface area of a cube?",
    ]


if __name__ == "__main__":
    print("=== Comparison Demo: Old Pipeline vs Modern LLM Mapper ===")
    texts = sys.argv[1:] if len(sys.argv) > 1 else demo_inputs()
    run_comparison(texts)

        
