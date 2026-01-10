#!/usr/bin/python3
"""
Deployment Pipeline for Formula Mapping Models
Handles model serving, API creation, and production deployment
"""

import json
import logging
import pickle
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Flask for API
try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS

    FLASK_AVAILABLE = True
except:
    FLASK_AVAILABLE = False
    print("Warning: Flask not available. Install with: pip install flask flask-cors")


@dataclass
class DeploymentConfig:
    """Configuration for deployment"""

    model_dir: str = "./models"
    api_host: str = "0.0.0.0"
    api_port: int = 5000
    log_file: str = "./logs/deployment.log"
    enable_logging: bool = True
    enable_metrics: bool = True


class ModelRegistry:
    """Registry for loading and managing multiple models"""

    def __init__(self, model_dir: str = "./models"):
        self.model_dir = Path(model_dir)
        self.models = {}
        self.metadata = {}

    def register_spacy_model(self, name: str, model_path: str):
        """Register spaCy NER model"""
        try:
            import spacy

            nlp = spacy.load(model_path)
            self.models[name] = {"type": "spacy", "model": nlp, "path": model_path}
            self.metadata[name] = {
                "type": "spacy",
                "loaded_at": datetime.now().isoformat(),
            }
            print(f"✅ Registered spaCy model: {name}")
        except Exception as e:
            print(f"❌ Failed to load spaCy model {name}: {e}")

    def register_transformer_model(self, name: str, model_path: str):
        """Register Transformer model"""
        try:
            from transformers import AutoTokenizer, T5ForConditionalGeneration

            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = T5ForConditionalGeneration.from_pretrained(model_path)

            self.models[name] = {
                "type": "transformer",
                "model": model,
                "tokenizer": tokenizer,
                "path": model_path,
            }
            self.metadata[name] = {
                "type": "transformer",
                "loaded_at": datetime.now().isoformat(),
            }
            print(f"✅ Registered Transformer model: {name}")
        except Exception as e:
            print(f"❌ Failed to load Transformer model {name}: {e}")

    def register_rag_model(self, name: str, model_path: str):
        """Register RAG model"""
        try:
            from training_rag import RAGConfig, RAGTrainer

            config = RAGConfig()
            trainer = RAGTrainer(config)
            trainer.load_model(model_path)

            self.models[name] = {"type": "rag", "model": trainer, "path": model_path}
            self.metadata[name] = {
                "type": "rag",
                "loaded_at": datetime.now().isoformat(),
            }
            print(f"✅ Registered RAG model: {name}")
        except Exception as e:
            print(f"❌ Failed to load RAG model {name}: {e}")

    def register_ensemble_mapper(self, name: str, mapper):
        """Register ensemble mapper"""
        self.models[name] = {"type": "ensemble", "model": mapper}
        self.metadata[name] = {
            "type": "ensemble",
            "loaded_at": datetime.now().isoformat(),
        }
        print(f"✅ Registered Ensemble mapper: {name}")

    def get_model(self, name: str) -> Optional[Dict]:
        """Get registered model"""
        return self.models.get(name)

    def list_models(self) -> List[str]:
        """List all registered models"""
        return list(self.models.keys())

    def get_metadata(self) -> Dict:
        """Get all model metadata"""
        return self.metadata


class PredictionService:
    """Service for making predictions"""

    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.prediction_count = 0
        self.prediction_history = []

    def predict_with_spacy(self, model_name: str, text: str) -> Dict:
        """Predict using spaCy NER model"""
        model_info = self.registry.get_model(model_name)
        if not model_info or model_info["type"] != "spacy":
            return {"error": f"Model {model_name} not found or wrong type"}

        nlp = model_info["model"]
        doc = nlp(text)

        entities = [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            }
            for ent in doc.ents
        ]

        return {"model": model_name, "type": "spacy", "entities": entities}

    def predict_with_transformer(self, model_name: str, text: str) -> Dict:
        """Predict using Transformer model"""
        model_info = self.registry.get_model(model_name)
        if not model_info or model_info["type"] != "transformer":
            return {"error": f"Model {model_name} not found or wrong type"}

        import torch

        model = model_info["model"]
        tokenizer = model_info["tokenizer"]

        input_text = f"translate description to formula: {text}"
        inputs = tokenizer(
            input_text, return_tensors="pt", max_length=128, truncation=True
        )

        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids, max_length=128, num_beams=4, early_stopping=True
            )

        formula = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return {"model": model_name, "type": "transformer", "formula": formula}

    def predict_with_rag(self, model_name: str, text: str) -> Dict:
        """Predict using RAG model"""
        model_info = self.registry.get_model(model_name)
        if not model_info or model_info["type"] != "rag":
            return {"error": f"Model {model_name} not found or wrong type"}

        trainer = model_info["model"]

        similar_examples = trainer.retrieve(text, k=5)
        formula = trainer.generate_formula(text)

        return {
            "model": model_name,
            "type": "rag",
            "formula": formula,
            "similar_examples": similar_examples,
        }

    def predict_with_ensemble(
        self, model_name: str, text: str, ner_entities: Optional[List] = None
    ) -> Dict:
        """Predict using ensemble mapper"""
        model_info = self.registry.get_model(model_name)
        if not model_info or model_info["type"] != "ensemble":
            return {"error": f"Model {model_name} not found or wrong type"}

        mapper = model_info["model"]
        result = mapper.map_with_all_candidates(text, ner_entities)

        return {
            "model": model_name,
            "type": "ensemble",
            "best_formula": result["best_formula"],
            "best_strategy": result["best_strategy"],
            "confidence": result["confidence"],
            "all_candidates": result["all_candidates"],
        }

    def predict(
        self, model_name: str, text: str, ner_entities: Optional[List] = None
    ) -> Dict:
        """Universal predict method"""
        model_info = self.registry.get_model(model_name)
        if not model_info:
            return {"error": f"Model {model_name} not found"}

        model_type = model_info["type"]

        if model_type == "spacy":
            result = self.predict_with_spacy(model_name, text)
        elif model_type == "transformer":
            result = self.predict_with_transformer(model_name, text)
        elif model_type == "rag":
            result = self.predict_with_rag(model_name, text)
        elif model_type == "ensemble":
            result = self.predict_with_ensemble(model_name, text, ner_entities)
        else:
            result = {"error": f"Unknown model type: {model_type}"}

        # Log prediction
        self.prediction_count += 1
        self.prediction_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "model": model_name,
                "input": text,
                "output": result,
            }
        )

        return result


class DeploymentAPI:
    """REST API for model deployment"""

    def __init__(self, config: DeploymentConfig = None):
        self.config = config or DeploymentConfig()
        self.registry = ModelRegistry(self.config.model_dir)
        self.service = PredictionService(self.registry)

        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            CORS(self.app)
            self._setup_routes()
        else:
            self.app = None
            print("Flask not available. API cannot be started.")

        # Setup logging
        if self.config.enable_logging:
            self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        Path(self.config.log_file).parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint"""
            return jsonify(
                {
                    "status": "healthy",
                    "models_loaded": len(self.registry.list_models()),
                    "predictions_served": self.service.prediction_count,
                }
            )

        @self.app.route("/models", methods=["GET"])
        def list_models():
            """List available models"""
            return jsonify(
                {
                    "models": self.registry.list_models(),
                    "metadata": self.registry.get_metadata(),
                }
            )

        @self.app.route("/predict", methods=["POST"])
        def predict():
            """Main prediction endpoint"""
            data = request.json

            if not data or "text" not in data or "model" not in data:
                return jsonify({"error": "Missing required fields: text, model"}), 400

            text = data["text"]
            model_name = data["model"]
            ner_entities = data.get("ner_entities", None)

            result = self.service.predict(model_name, text, ner_entities)

            if "error" in result:
                return jsonify(result), 404

            return jsonify(result)

        @self.app.route("/predict/spacy", methods=["POST"])
        def predict_spacy():
            """spaCy NER prediction"""
            data = request.json

            if not data or "text" not in data or "model" not in data:
                return jsonify({"error": "Missing required fields"}), 400

            result = self.service.predict_with_spacy(data["model"], data["text"])
            return jsonify(result)

        @self.app.route("/predict/transformer", methods=["POST"])
        def predict_transformer():
            """Transformer prediction"""
            data = request.json

            if not data or "text" not in data or "model" not in data:
                return jsonify({"error": "Missing required fields"}), 400

            result = self.service.predict_with_transformer(data["model"], data["text"])
            return jsonify(result)

        @self.app.route("/predict/rag", methods=["POST"])
        def predict_rag():
            """RAG prediction"""
            data = request.json

            if not data or "text" not in data or "model" not in data:
                return jsonify({"error": "Missing required fields"}), 400

            result = self.service.predict_with_rag(data["model"], data["text"])
            return jsonify(result)

        @self.app.route("/predict/ensemble", methods=["POST"])
        def predict_ensemble():
            """Ensemble prediction"""
            data = request.json

            if not data or "text" not in data or "model" not in data:
                return jsonify({"error": "Missing required fields"}), 400

            result = self.service.predict_with_ensemble(
                data["model"], data["text"], data.get("ner_entities", None)
            )
            return jsonify(result)

        @self.app.route("/metrics", methods=["GET"])
        def metrics():
            """Get prediction metrics"""
            return jsonify(
                {
                    "total_predictions": self.service.prediction_count,
                    "models_loaded": len(self.registry.list_models()),
                    "recent_predictions": self.service.prediction_history[-10:],
                }
            )

    def run(self):
        """Start the API server"""
        if not self.app:
            print("❌ Flask not available. Cannot start API.")
            return

        print(f"\n{'=' * 70}")
        print(f"🚀 Starting Formula Mapping API")
        print(f"{'=' * 70}")
        print(f"Host: {self.config.api_host}")
        print(f"Port: {self.config.api_port}")
        print(f"Models loaded: {len(self.registry.list_models())}")
        print(f"{'=' * 70}\n")

        self.app.run(host=self.config.api_host, port=self.config.api_port, debug=False)


def main():
    """Example deployment"""
    print("=" * 70)
    print("DEPLOYMENT PIPELINE")
    print("=" * 70)

    # Create deployment config
    config = DeploymentConfig(model_dir="./models", api_port=5000)

    # Create API
    api = DeploymentAPI(config)

    # Register models (example - adjust paths as needed)
    # api.registry.register_spacy_model("ner_model", "./models/spacy_ner")
    # api.registry.register_transformer_model("transformer", "./models/transformer_formula_mapper")
    # api.registry.register_rag_model("rag", "./models/rag_formula_mapper")

    # Create and register ensemble mapper
    from mapping_plus import EnhancedMapDescriptionToFormula, MappingContext

    context = MappingContext(
        available_columns=["Sales", "Revenue", "Profit", "Region", "Year"],
        data_types={
            "Sales": "float",
            "Revenue": "float",
            "Profit": "float",
            "Region": "string",
            "Year": "int",
        },
    )
    ensemble_mapper = EnhancedMapDescriptionToFormula(context)

    api.registry.register_ensemble_mapper("ensemble", ensemble_mapper)

    print("\n✅ Models registered successfully")
    print(f"Available models: {api.registry.list_models()}")

    # Start API server
    if FLASK_AVAILABLE:
        print("\nStarting API server...")
        api.run()
    else:
        print("\n⚠️  Flask not installed. Install with: pip install flask flask-cors")
        print("API demonstration mode - showing prediction example:")

        # Demo prediction
        result = api.service.predict("ensemble", "average of Sales by Region")
        print(f"\nExample prediction:")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
