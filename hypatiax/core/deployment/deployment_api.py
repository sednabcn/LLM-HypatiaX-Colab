#!/usr/bin/python3
"""
REST API for Formula Generation
Provides endpoints for real-time formula mapping
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS


@dataclass
class DeploymentConfig:
    """Configuration for deployment"""

    model_dir: str = "./models"
    api_host: str = "0.0.0.0"
    api_port: int = 5000
    debug: bool = False
    enable_cors: bool = True


class ModelRegistry:
    """Registry for all available models"""

    def __init__(self):
        self.models = {}
        self.default_model = None

    def register_spacy_model(self, name: str, model_path: str):
        """Register spaCy NER model"""
        try:
            import spacy

            nlp = spacy.load(model_path)
            self.models[name] = {"type": "spacy", "model": nlp, "path": model_path}
            print(f"✅ Registered spaCy model: {name}")
        except Exception as e:
            print(f"⚠️  Failed to register spaCy model {name}: {e}")

    def register_transformer_model(self, name: str, model_path: str):
        """Register Transformer model"""
        try:
            from transformers import AutoTokenizer, T5ForConditionalGeneration

            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = T5ForConditionalGeneration.from_pretrained(model_path)

            self.models[name] = {"type": "transformer", "model": model, "tokenizer": tokenizer, "path": model_path}
            print(f"✅ Registered Transformer model: {name}")
        except Exception as e:
            print(f"⚠️  Failed to register Transformer model {name}: {e}")

    def register_rag_model(self, name: str, model_path: str):
        """Register RAG model"""
        try:
            from training_rag import RAGConfig, RAGTrainer

            config = RAGConfig()
            trainer = RAGTrainer(config)
            trainer.load_model(model_path)

            self.models[name] = {"type": "rag", "model": trainer, "path": model_path}
            print(f"✅ Registered RAG model: {name}")
        except Exception as e:
            print(f"⚠️  Failed to register RAG model {name}: {e}")

    def register_ensemble_mapper(self, name: str, mapper):
        """Register ensemble mapper"""
        self.models[name] = {"type": "ensemble", "model": mapper}
        if not self.default_model:
            self.default_model = name
        print(f"✅ Registered Ensemble mapper: {name}")

    def get_model(self, name: str = None):
        """Get model by name"""
        if name is None:
            name = self.default_model
        return self.models.get(name)

    def list_models(self) -> List[str]:
        """List all registered models"""
        return list(self.models.keys())


class DeploymentAPI:
    """Flask API for formula generation"""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.app = Flask(__name__)

        if config.enable_cors:
            CORS(self.app)

        self.registry = ModelRegistry()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register API endpoints"""

        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint"""
            return jsonify({"status": "healthy", "models": self.registry.list_models()})

        @self.app.route("/models", methods=["GET"])
        def list_models():
            """List available models"""
            models_info = []
            for name in self.registry.list_models():
                model_info = self.registry.get_model(name)
                models_info.append({"name": name, "type": model_info["type"], "path": model_info.get("path", "N/A")})

            return jsonify({"models": models_info, "default": self.registry.default_model})

        @self.app.route("/predict", methods=["POST"])
        def predict():
            """Generate formula from description"""
            try:
                data = request.json
                description = data.get("description")
                model_name = data.get("model", self.registry.default_model)

                if not description:
                    return jsonify({"error": "No description provided"}), 400

                model_info = self.registry.get_model(model_name)
                if not model_info:
                    return jsonify({"error": f"Model {model_name} not found"}), 404

                # Generate formula based on model type
                result = self._generate_formula(description, model_info)

                return jsonify(result)

            except Exception as e:
                self.logger.error(f"Prediction error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/predict/batch", methods=["POST"])
        def predict_batch():
            """Generate formulas for multiple descriptions"""
            try:
                data = request.json
                descriptions = data.get("descriptions", [])
                model_name = data.get("model", self.registry.default_model)

                if not descriptions:
                    return jsonify({"error": "No descriptions provided"}), 400

                model_info = self.registry.get_model(model_name)
                if not model_info:
                    return jsonify({"error": f"Model {model_name} not found"}), 404

                results = []
                for desc in descriptions:
                    result = self._generate_formula(desc, model_info)
                    results.append(result)

                return jsonify({"predictions": results})

            except Exception as e:
                self.logger.error(f"Batch prediction error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/predict/ensemble", methods=["POST"])
        def predict_ensemble():
            """Get predictions from all available models"""
            try:
                data = request.json
                description = data.get("description")

                if not description:
                    return jsonify({"error": "No description provided"}), 400

                results = {}
                for model_name in self.registry.list_models():
                    model_info = self.registry.get_model(model_name)
                    result = self._generate_formula(description, model_info)
                    results[model_name] = result

                return jsonify({"description": description, "predictions": results})

            except Exception as e:
                self.logger.error(f"Ensemble prediction error: {e}")
                return jsonify({"error": str(e)}), 500

    def _generate_formula(self, description: str, model_info: Dict) -> Dict:
        """Generate formula using specified model"""
        model_type = model_info["type"]

        try:
            if model_type == "ensemble":
                mapper = model_info["model"]
                result = mapper.map_with_all_candidates(description)

                return {
                    "description": description,
                    "formula": result["best_formula"],
                    "strategy": result["best_strategy"],
                    "confidence": result["confidence"],
                    "model_type": "ensemble",
                }

            elif model_type == "transformer":
                import torch

                model = model_info["model"]
                tokenizer = model_info["tokenizer"]

                input_text = f"translate description to formula: {description}"
                inputs = tokenizer(input_text, return_tensors="pt", max_length=128, truncation=True)

                with torch.no_grad():
                    outputs = model.generate(inputs.input_ids, max_length=128, num_beams=4, early_stopping=True)

                formula = tokenizer.decode(outputs[0], skip_special_tokens=True)

                return {"description": description, "formula": formula, "confidence": 0.85, "model_type": "transformer"}

            elif model_type == "rag":
                trainer = model_info["model"]
                formula = trainer.generate_formula(description)

                return {"description": description, "formula": formula, "confidence": 0.80, "model_type": "rag"}

            elif model_type == "spacy":
                nlp = model_info["model"]
                doc = nlp(description)

                entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

                return {"description": description, "entities": entities, "model_type": "spacy_ner"}

            else:
                return {"error": f"Unknown model type: {model_type}"}

        except Exception as e:
            return {"error": f"Generation failed: {str(e)}"}

    def run(self):
        """Start the API server"""
        self.logger.info(f"Starting API server on {self.config.api_host}:{self.config.api_port}")
        self.logger.info(f"Available models: {self.registry.list_models()}")

        self.app.run(host=self.config.api_host, port=self.config.api_port, debug=self.config.debug)


def main():
    """Example usage"""
    print("=" * 70)
    print("DEPLOYMENT API")
    print("=" * 70)

    # Configuration
    config = DeploymentConfig(model_dir="./models", api_port=5000, debug=True)

    # Create API
    api = DeploymentAPI(config)

    # Register ensemble mapper (always available)
    from mapping_plus import EnhancedMapDescriptionToFormula, MappingContext

    context = MappingContext()
    mapper = EnhancedMapDescriptionToFormula(context)
    api.registry.register_ensemble_mapper("ensemble", mapper)

    # Try to register other models if available
    spacy_model_path = Path("./models/spacy_ner/model-best")
    if spacy_model_path.exists():
        api.registry.register_spacy_model("ner", str(spacy_model_path))

    transformer_model_path = Path("./models/transformer_formula_mapper")
    if transformer_model_path.exists():
        api.registry.register_transformer_model("transformer", str(transformer_model_path))

    rag_model_path = Path("./models/rag_formula_mapper")
    if rag_model_path.exists():
        api.registry.register_rag_model("rag", str(rag_model_path))

    print("\n📡 Starting API server...")
    print(f"URL: http://localhost:{config.api_port}")
    print("\nAvailable endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /models - List models")
    print("  POST /predict - Single prediction")
    print("  POST /predict/batch - Batch predictions")
    print("  POST /predict/ensemble - All models")
    print("\n" + "=" * 70)

    # Start server
    api.run()


if __name__ == "__main__":
    main()
