# backend/app.py - Fixed Version
import logging
import sys
import time
import traceback

from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add HypatiaX to path
sys.path.append("../hypatiax")

# Global variables for models
MODELS_LOADED = False
nlp_desc = None
nlp_formula = None
map_description_to_formula = None

# Try to load models
try:
    import spacy

    from hypatiax.custom_ner.queries.tableau import (
        custom_tableau_components,
        custom_tableau_desc_components,
        custom_tableau_formulas_components,
    )
    from hypatiax.mappings.mapping import map_description_to_formula

    # Load trained NER models
    nlp_desc = spacy.load("../hypatiax/data_spacy/queries/tableau/ner_tableau_desc")
    nlp_formula = spacy.load(
        "../hypatiax/data_spacy/queries/tableau/ner_tableau_formulas"
    )
    MODELS_LOADED = True
    logger.info("✅ Models loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ Could not load models: {e}")
    logger.warning("Backend will run in demo mode with mock responses")
    MODELS_LOADED = False

app = Flask(__name__)
CORS(app)

# Mock data for demo mode
DEMO_MAPPINGS = {
    "sum": {"formula": "SUM", "confidence": 0.95},
    "average": {"formula": "AVG", "confidence": 0.92},
    "avg": {"formula": "AVG", "confidence": 0.92},
    "count": {"formula": "COUNT", "confidence": 0.90},
    "total": {"formula": "SUM", "confidence": 0.88},
    "max": {"formula": "MAX", "confidence": 0.93},
    "min": {"formula": "MIN", "confidence": 0.93},
    "mean": {"formula": "AVG", "confidence": 0.91},
}


def mock_ner_extraction(text):
    """Mock NER extraction for demo mode"""
    entities = []
    words = text.lower().split()

    # Define entity patterns
    operations = ["sum", "average", "avg", "count", "total", "max", "min", "mean"]
    prepositions = ["of", "by", "per", "for", "across"]
    determiners = ["the", "a", "an", "all"]

    start_pos = 0
    for word in text.split():
        word_lower = word.lower()
        label = None

        if word_lower in operations:
            label = "OPER"
        elif word_lower in prepositions:
            label = "ADP"
        elif word_lower in determiners:
            label = "DET"
        elif word_lower.isdigit():
            label = "NUM"
        else:
            # Assume other words are nouns (field names)
            label = "NOUN"

        if label:
            entities.append(
                {
                    "text": word,
                    "label": label,
                    "start": start_pos,
                    "end": start_pos + len(word),
                }
            )

        start_pos += len(word) + 1

    return entities


def mock_formula_generation(description, method):
    """Mock formula generation for demo mode"""
    desc_lower = description.lower()

    # Find operation
    operation = "SUM"
    confidence = 0.85

    for op, data in DEMO_MAPPINGS.items():
        if op in desc_lower:
            operation = data["formula"]
            confidence = data["confidence"]
            break

    # Extract field name (simple heuristic)
    words = description.split()
    field_name = None

    for i, word in enumerate(words):
        if word.lower() in ["of", "by"]:
            if i + 1 < len(words):
                # Get next word(s) as field name
                remaining = words[i + 1 :]
                # Filter out prepositions
                field_words = [
                    w
                    for w in remaining
                    if w.lower() not in ["by", "per", "for", "the", "a", "an"]
                ]
                if field_words:
                    field_name = field_words[0]
                    break

    # Fallback: use last noun-like word
    if not field_name:
        for word in reversed(words):
            if word.lower() not in [
                "sum",
                "average",
                "avg",
                "count",
                "total",
                "of",
                "by",
                "the",
                "a",
                "an",
            ]:
                field_name = word
                break

    if field_name:
        formula = f"{operation}([{field_name}])"
    else:
        formula = f"{operation}([Field])"

    return formula, confidence


@app.route("/", methods=["GET"])
def index():
    """Root endpoint - API information"""
    return jsonify(
        {
            "name": "HypatiaX API",
            "version": "1.0.0",
            "description": "Natural language to Tableau formula mapping",
            "models_loaded": MODELS_LOADED,
            "endpoints": {
                "health": "/api/health",
                "map": "/api/map (POST)",
                "test": "/api/test",
            },
            "usage": {
                "example": 'POST /api/map with JSON: {"description": "sum of sales"}'
            },
        }
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "online",
            "version": "1.0.0",
            "models_loaded": MODELS_LOADED,
            "mode": "production" if MODELS_LOADED else "demo",
            "endpoints": ["/api/health", "/api/map", "/api/test"],
        }
    )


@app.route("/api/map", methods=["POST"])
def map_description():
    """Main mapping endpoint"""
    start_time = time.time()

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        description = data.get("description", "").strip()
        method = data.get("method", "vocab")

        if not description:
            return jsonify({"error": "Description is required"}), 400

        logger.info(f"Processing: '{description}' with method: {method}")

        if MODELS_LOADED:
            # Real processing with loaded models
            try:
                # Process with NER
                doc = nlp_desc(description)
                entities = [
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                    for ent in doc.ents
                ]

                # Generate formula using HypatiaX mapping
                # The mapper is already initialized with the description
                # and should be called without additional parameters
                mapper = map_description_to_formula(description)
                formula = mapper()  # Call without parameters

                # Calculate confidence based on entities found
                confidence = min(0.95, len(entities) / max(len(description.split()), 1))

            except Exception as e:
                logger.error(f"Error in model processing: {e}")
                logger.error(traceback.format_exc())
                # Fallback to mock processing if model fails
                entities = mock_ner_extraction(description)
                formula, confidence = mock_formula_generation(description, method)
                logger.warning("Fell back to mock processing due to model error")
        else:
            # Demo mode with mock processing
            entities = mock_ner_extraction(description)
            formula, confidence = mock_formula_generation(description, method)

        processing_time = (time.time() - start_time) * 1000

        response = {
            "success": True,
            "entities": entities,
            "formula": formula,
            "confidence": round(confidence, 2),
            "method": method,
            "processing_time_ms": round(processing_time, 2),
            "mode": "production" if MODELS_LOADED else "demo",
        }

        logger.info(f"✅ Success: {formula} ({processing_time:.2f}ms)")
        return jsonify(response)

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route("/api/test", methods=["GET"])
def test_endpoint():
    """Test endpoint with sample data"""
    test_cases = [
        "Calculate the total of Petal Lengths",
        "Minimum value of Sepal Length",
        "Entries with Petal Length between 1.5 and 2.5",
    ]

    results = []
    for desc in test_cases:
        try:
            if MODELS_LOADED:
                doc = nlp_desc(desc)
                entities = [{"text": e.text, "label": e.label_} for e in doc.ents]
                try:
                    mapper = map_description_to_formula(desc)
                    formula = mapper(method="vocab")
                except:
                    formula, _ = mock_formula_generation(desc, "vocab")
            else:
                entities = mock_ner_extraction(desc)
                formula, _ = mock_formula_generation(desc, "vocab")

            results.append(
                {"description": desc, "formula": formula, "entities": entities}
            )
        except Exception as e:
            results.append({"description": desc, "error": str(e)})

    return jsonify({"test_results": results, "models_loaded": MODELS_LOADED})


@app.errorhandler(404)
def not_found(e):
    return (
        jsonify(
            {
                "error": "Endpoint not found",
                "available_endpoints": [
                    "/",
                    "/api/health",
                    "/api/map (POST)",
                    "/api/test",
                ],
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 HypatiaX Backend Server")
    print("=" * 60)
    print(f"📊 Models Loaded: {MODELS_LOADED}")
    print(f"🔧 Mode: {'Production' if MODELS_LOADED else 'Demo (Mock Data)'}")
    print(f"🌐 Server: http://localhost:5000")
    print(f"📡 API Base: http://localhost:5000/api")
    print("\n📋 Available Endpoints:")
    print("   GET  /          - API information")
    print("   GET  /api/health  - Health check")
    print("   POST /api/map     - Map description to formula")
    print("   GET  /api/test    - Test with sample data")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    app.run(debug=True, port=5000, host="0.0.0.0")
