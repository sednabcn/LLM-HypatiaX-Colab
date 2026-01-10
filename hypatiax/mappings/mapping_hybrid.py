#!/usr/bin/python3
"""
Hybrid Formula Mapping System
Integrates ALL techniques: spaCy NER, Transformers, RAG, LLM, Rule-based, Ensemble
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class HybridConfig:
    """Configuration for hybrid mapping"""

    spacy_model_path: Optional[str] = None
    transformer_model_path: Optional[str] = None
    rag_model_path: Optional[str] = None
    llm_config: Optional[Dict] = None
    use_spacy: bool = True
    use_transformer: bool = True
    use_rag: bool = True
    use_llm: bool = False
    use_ensemble: bool = True
    confidence_threshold: float = 0.7


class HybridFormulaMapper:
    """Unified mapper using all available techniques"""

    def __init__(self, config: HybridConfig = None):
        self.config = config or HybridConfig()
        self.models = {}
        self.prediction_cache = {}

        # Initialize all components
        self._init_spacy()
        self._init_transformer()
        self._init_rag()
        self._init_llm()
        self._init_ensemble()

    def _init_spacy(self):
        """Initialize spaCy NER model"""
        if not self.config.use_spacy or not self.config.spacy_model_path:
            self.models["spacy"] = None
            return

        try:
            import spacy

            self.models["spacy"] = spacy.load(self.config.spacy_model_path)
            print("✅ spaCy NER model loaded")
        except Exception as e:
            print(f"⚠️  Failed to load spaCy model: {e}")
            self.models["spacy"] = None

    def _init_transformer(self):
        """Initialize Transformer model"""
        if not self.config.use_transformer or not self.config.transformer_model_path:
            self.models["transformer"] = None
            return

        try:
            from transformers import AutoTokenizer, T5ForConditionalGeneration

            tokenizer = AutoTokenizer.from_pretrained(
                self.config.transformer_model_path
            )
            model = T5ForConditionalGeneration.from_pretrained(
                self.config.transformer_model_path
            )

            self.models["transformer"] = {"model": model, "tokenizer": tokenizer}
            print("✅ Transformer model loaded")
        except Exception as e:
            print(f"⚠️  Failed to load Transformer model: {e}")
            self.models["transformer"] = None

    def _init_rag(self):
        """Initialize RAG model"""
        if not self.config.use_rag or not self.config.rag_model_path:
            self.models["rag"] = None
            return

        try:
            from training_rag import RAGConfig, RAGTrainer

            rag_config = RAGConfig()
            trainer = RAGTrainer(rag_config)
            trainer.load_model(self.config.rag_model_path)

            self.models["rag"] = trainer
            print("✅ RAG model loaded")
        except Exception as e:
            print(f"⚠️  Failed to load RAG model: {e}")
            self.models["rag"] = None

    def _init_llm(self):
        """Initialize LLM client"""
        if not self.config.use_llm or not self.config.llm_config:
            self.models["llm"] = None
            return

        try:
            from training_llm import LLMConfig, LLMTrainer

            llm_config = LLMConfig(**self.config.llm_config)
            trainer = LLMTrainer(llm_config)

            self.models["llm"] = trainer
            print("✅ LLM client initialized")
        except Exception as e:
            print(f"⚠️  Failed to initialize LLM: {e}")
            self.models["llm"] = None

    def _init_ensemble(self):
        """Initialize ensemble mapper"""
        if not self.config.use_ensemble:
            self.models["ensemble"] = None
            return

        try:
            from mapping_plus import EnhancedMapDescriptionToFormula, MappingContext

            context = MappingContext()
            mapper = EnhancedMapDescriptionToFormula(context)

            self.models["ensemble"] = mapper
            print("✅ Ensemble mapper initialized")
        except Exception as e:
            print(f"⚠️  Failed to initialize ensemble: {e}")
            self.models["ensemble"] = None

    def predict_with_spacy(self, description: str) -> Dict:
        """Extract entities using spaCy NER"""
        if not self.models.get("spacy"):
            return {"entities": [], "confidence": 0.0, "available": False}

        doc = self.models["spacy"](description)

        entities = [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            }
            for ent in doc.ents
        ]

        confidence = 0.8 if entities else 0.0

        return {"entities": entities, "confidence": confidence, "available": True}

    def predict_with_transformer(self, description: str) -> Dict:
        """Generate formula using Transformer"""
        if not self.models.get("transformer"):
            return {"formula": None, "confidence": 0.0, "available": False}

        try:
            import torch

            model_info = self.models["transformer"]
            model = model_info["model"]
            tokenizer = model_info["tokenizer"]

            input_text = f"translate description to formula: {description}"
            inputs = tokenizer(
                input_text, return_tensors="pt", max_length=128, truncation=True
            )

            with torch.no_grad():
                outputs = model.generate(
                    inputs.input_ids, max_length=128, num_beams=4, early_stopping=True
                )

            formula = tokenizer.decode(outputs[0], skip_special_tokens=True)

            return {"formula": formula, "confidence": 0.85, "available": True}
        except Exception as e:
            return {
                "formula": None,
                "confidence": 0.0,
                "available": False,
                "error": str(e),
            }

    def predict_with_rag(self, description: str) -> Dict:
        """Generate formula using RAG"""
        if not self.models.get("rag"):
            return {"formula": None, "confidence": 0.0, "available": False}

        try:
            trainer = self.models["rag"]

            similar_examples = trainer.retrieve(description, k=5)
            formula = trainer.generate_formula(description)

            confidence = 0.8 if similar_examples else 0.3

            return {
                "formula": formula,
                "similar_examples": similar_examples,
                "confidence": confidence,
                "available": True,
            }
        except Exception as e:
            return {
                "formula": None,
                "confidence": 0.0,
                "available": False,
                "error": str(e),
            }

    def predict_with_llm(self, description: str) -> Dict:
        """Generate formula using LLM"""
        if not self.models.get("llm"):
            return {"formula": None, "confidence": 0.0, "available": False}

        try:
            trainer = self.models["llm"]
            formula = trainer.generate_formula(description)

            confidence = 0.9 if not formula.startswith("Error:") else 0.0

            return {"formula": formula, "confidence": confidence, "available": True}
        except Exception as e:
            return {
                "formula": None,
                "confidence": 0.0,
                "available": False,
                "error": str(e),
            }

    def predict_with_ensemble(
        self, description: str, ner_entities: Optional[List] = None
    ) -> Dict:
        """Generate formula using ensemble mapper"""
        if not self.models.get("ensemble"):
            return {"formula": None, "confidence": 0.0, "available": False}

        try:
            mapper = self.models["ensemble"]
            result = mapper.map_with_all_candidates(description, ner_entities)

            return {
                "formula": result["best_formula"],
                "strategy": result["best_strategy"],
                "confidence": result["confidence"],
                "all_candidates": result["all_candidates"],
                "available": True,
            }
        except Exception as e:
            return {
                "formula": None,
                "confidence": 0.0,
                "available": False,
                "error": str(e),
            }

    def predict_hybrid(self, description: str, use_cache: bool = True) -> Dict:
        """
        Hybrid prediction using all available techniques

        Returns:
            Dict with best prediction and all technique results
        """
        # Check cache
        if use_cache and description in self.prediction_cache:
            return self.prediction_cache[description]

        # Collect predictions from all techniques
        results = {}

        # 1. spaCy NER (for entity extraction)
        spacy_result = self.predict_with_spacy(description)
        results["spacy"] = spacy_result
        ner_entities = spacy_result.get("entities", [])

        # 2. Ensemble (rule-based + heuristics)
        ensemble_result = self.predict_with_ensemble(description, ner_entities)
        results["ensemble"] = ensemble_result

        # 3. Transformer
        transformer_result = self.predict_with_transformer(description)
        results["transformer"] = transformer_result

        # 4. RAG
        rag_result = self.predict_with_rag(description)
        results["rag"] = rag_result

        # 5. LLM (if enabled)
        if self.config.use_llm:
            llm_result = self.predict_with_llm(description)
            results["llm"] = llm_result

        # Voting and confidence aggregation
        formulas = []
        for technique, result in results.items():
            if result.get("available") and result.get("formula"):
                formula = result["formula"]
                confidence = result.get("confidence", 0.0)

                if not formula.startswith("Error:"):
                    formulas.append(
                        {
                            "technique": technique,
                            "formula": formula,
                            "confidence": confidence,
                        }
                    )

        # Determine best prediction
        if formulas:
            # Sort by confidence
            formulas.sort(key=lambda x: x["confidence"], reverse=True)
            best = formulas[0]

            # Check for consensus (multiple techniques agree)
            formula_votes = defaultdict(list)
            for f in formulas:
                normalized = f["formula"].replace(" ", "").upper()
                formula_votes[normalized].append(f)

            # If multiple techniques agree, boost confidence
            best_normalized = best["formula"].replace(" ", "").upper()
            if len(formula_votes[best_normalized]) > 1:
                best["confidence"] = min(best["confidence"] * 1.2, 1.0)
                best["consensus"] = True
                best["num_agreeing"] = len(formula_votes[best_normalized])
        else:
            best = {
                "technique": "none",
                "formula": "Error: All techniques failed",
                "confidence": 0.0,
            }

        # Compile final result
        final_result = {
            "input": description,
            "best_prediction": best,
            "all_techniques": results,
            "all_formulas": formulas,
            "ner_entities": ner_entities,
        }

        # Cache result
        if use_cache:
            self.prediction_cache[description] = final_result

        return final_result

    def batch_predict(self, descriptions: List[str]) -> List[Dict]:
        """Predict formulas for multiple descriptions"""
        results = []

        for i, desc in enumerate(descriptions):
            print(f"Processing {i+1}/{len(descriptions)}: {desc}")
            result = self.predict_hybrid(desc)
            results.append(result)

        return results

    def evaluate_techniques(self, test_data: List[Dict]) -> Dict:
        """Evaluate performance of each technique"""

        technique_scores = defaultdict(
            lambda: {"correct": 0, "total": 0, "accuracy": 0.0}
        )

        for example in test_data:
            description = example["description"]
            ground_truth = example["formula"]

            result = self.predict_hybrid(description)

            # Evaluate each technique
            for formula_info in result["all_formulas"]:
                technique = formula_info["technique"]
                predicted = formula_info["formula"]

                technique_scores[technique]["total"] += 1

                if predicted.strip() == ground_truth.strip():
                    technique_scores[technique]["correct"] += 1

        # Calculate accuracies
        for technique in technique_scores:
            total = technique_scores[technique]["total"]
            correct = technique_scores[technique]["correct"]
            technique_scores[technique]["accuracy"] = (
                correct / total if total > 0 else 0.0
            )

        return dict(technique_scores)

    def export_results(self, results: List[Dict], output_path: str):
        """Export prediction results to JSON"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"✅ Results exported to {output_path}")


def main():
    """Example usage of hybrid mapper"""
    print("=" * 70)
    print("HYBRID FORMULA MAPPING SYSTEM")
    print("Integrating: spaCy NER + Transformers + RAG + LLM + Ensemble")
    print("=" * 70)

    # Configuration (adjust paths as needed)
    config = HybridConfig(
        spacy_model_path=None,  # "./models/spacy_ner"
        transformer_model_path=None,  # "./models/transformer
        transformer_model_path=None,  # "./models/transformer_formula_mapper"
        rag_model_path=None,  # "./models/rag_formula_mapper"
        llm_config=None,  # {'provider': 'openai', 'model': 'gpt-4'}
        use_spacy=False,  # Set to True if models available
        use_transformer=False,
        use_rag=False,
        use_llm=False,
        use_ensemble=True,  # Always available (rule-based)
    )

    # Initialize hybrid mapper
    mapper = HybridFormulaMapper(config)

    # Test descriptions
    test_descriptions = [
        "average of Sales",
        "sum of Revenue by Region",
        "count unique customers",
        "maximum price per category",
        "total profit by year",
    ]

    print("\n" + "=" * 70)
    print("HYBRID PREDICTIONS")
    print("=" * 70)

    # Make predictions
    for desc in test_descriptions:
        print(f"\n📝 Input: '{desc}'")
        print("-" * 70)

        result = mapper.predict_hybrid(desc)

        best = result["best_prediction"]
        print(f"✅ Best: {best['formula']}")
        print(f"   Technique: {best['technique']}")
        print(f"   Confidence: {best['confidence']:.2f}")

        if best.get("consensus"):
            print(f"   ⭐ Consensus: {best['num_agreeing']} techniques agree")

        # Show all technique results
        print("\n   All Techniques:")
        for technique, tech_result in result["all_techniques"].items():
            if tech_result.get("available"):
                formula = tech_result.get("formula", "N/A")
                conf = tech_result.get("confidence", 0.0)
                print(f"   - {technique:12s}: {formula} (conf: {conf:.2f})")
            else:
                print(f"   - {technique:12s}: Not available")

        print("-" * 70)

    # Batch prediction
    print("\n" + "=" * 70)
    print("BATCH PREDICTION")
    print("=" * 70)

    batch_results = mapper.batch_predict(test_descriptions[:3])

    # Export results
    mapper.export_results(batch_results, "./results/hybrid_predictions.json")

    print("\n" + "=" * 70)
    print("✅ HYBRID MAPPING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
