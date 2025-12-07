"""
Unified Backend API - HypatiaX + DeFi + NER
File: backend/app.py
Version: 2.1.0 (Refactored with Blueprints)
"""

import logging
import os
import sys
import time
import traceback

from flask import Flask, jsonify, request
from flask_cors import CORS

# ============================================================================
# CONFIGURE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log") if os.path.exists("logs") else logging.StreamHandler(),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ============================================================================
# ADD PATHS
# ============================================================================

sys.path.append("../hypatiax")

# ============================================================================
# INITIALIZE FLASK APP
# ============================================================================

app = Flask(__name__)

# Configure CORS
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)

# ============================================================================
# LOAD HYPATIAX MODELS (Tableau NER)
# ============================================================================

HYPATIAX_LOADED = False
nlp_desc = None
nlp_formula = None
map_description_to_formula = None

try:
    import spacy

    from hypatiax.custom_ner.queries.tableau import (
        custom_tableau_components,
        custom_tableau_desc_components,
        custom_tableau_formulas_components,
    )
    from hypatiax.mappings.mapping import map_description_to_formula

    nlp_desc = spacy.load("../hypatiax/data_spacy/queries/tableau/ner_tableau_desc")
    nlp_formula = spacy.load("../hypatiax/data_spacy/queries/tableau/ner_tableau_formulas")
    HYPATIAX_LOADED = True
    logger.info("✅ HypatiaX models loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ HypatiaX models not available: {e}")
    HYPATIAX_LOADED = False

# ============================================================================
# LOAD NER SERVICE (Mathematical Formula Extraction)
# ============================================================================

NER_SERVICE_LOADED = False
try:
    from services.ner_service import NERService

    ner_service = NERService()
    NER_SERVICE_LOADED = True
    logger.info("✅ NER Service loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ NER Service not available: {e}")
    NER_SERVICE_LOADED = False

# ============================================================================
# LOAD DEFI SERVICES
# ============================================================================

DEFI_LOADED = False
try:
    from services.defi_calculator import DeFiCalculator

    defi_calculator = DeFiCalculator()
    DEFI_LOADED = True
    logger.info("✅ DeFi calculator loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ DeFi calculator not available: {e}")
    DEFI_LOADED = False

# ============================================================================
# REGISTER BLUEPRINTS
# ============================================================================

# Register NER routes
try:
    from api.routes.ner_routes import ner_bp

    app.register_blueprint(ner_bp)
    logger.info("✅ NER routes registered at /api/ner")
except Exception as e:
    logger.warning(f"⚠️ NER routes not available: {e}")
    if logger.level == logging.DEBUG:
        traceback.print_exc()

# Register DeFi routes
try:
    from api.routes.defi_routes import defi_bp

    app.register_blueprint(defi_bp)
    logger.info("✅ DeFi routes registered at /api/defi")
except Exception as e:
    logger.warning(f"⚠️ DeFi routes not available: {e}")
    if logger.level == logging.DEBUG:
        traceback.print_exc()

# Register Agent routes (optional)
try:
    from api.routes.agents import agents_bp

    app.register_blueprint(agents_bp)
    logger.info("✅ Agent routes registered")
except Exception as e:
    logger.debug(f"ℹ️ Agent routes not available: {e}")

# ============================================================================
# HELPER FUNCTIONS FOR HYPATIAX MOCK MODE
# ============================================================================

DEMO_MAPPINGS = {
    "sum": {"formula": "SUM", "confidence": 0.95},
    "average": {"formula": "AVG", "confidence": 0.92},
    "avg": {"formula": "AVG", "confidence": 0.92},
    "count": {"formula": "COUNT", "confidence": 0.90},
    "total": {"formula": "SUM", "confidence": 0.88},
    "max": {"formula": "MAX", "confidence": 0.93},
    "min": {"formula": "MIN", "confidence": 0.93},
    "mean": {"formula": "AVG", "confidence": 0.91},
    "maximum": {"formula": "MAX", "confidence": 0.92},
    "minimum": {"formula": "MIN", "confidence": 0.92},
}


def mock_ner_extraction(text):
    """Mock NER extraction for demo mode"""
    entities = []
    words = text.lower().split()

    operations = ["sum", "average", "avg", "count", "total", "max", "min", "mean", "maximum", "minimum"]
    prepositions = ["of", "by", "per", "for", "across", "in", "on"]
    determiners = ["the", "a", "an", "all", "each", "every"]

    start_pos = 0
    for word in text.split():
        word_lower = word.lower().strip(".,!?")
        label = None

        if word_lower in operations:
            label = "OPER"
        elif word_lower in prepositions:
            label = "ADP"
        elif word_lower in determiners:
            label = "DET"
        elif word_lower.replace(".", "").replace(",", "").isdigit():
            label = "NUM"
        else:
            label = "NOUN"

        if label:
            entities.append({"text": word, "label": label, "start": start_pos, "end": start_pos + len(word)})

        start_pos += len(word) + 1

    return entities


def mock_formula_generation(description, method="vocab"):
    """Mock formula generation for demo mode"""
    desc_lower = description.lower()

    # Default operation
    operation = "SUM"
    confidence = 0.85

    # Find operation in description
    for op, data in DEMO_MAPPINGS.items():
        if op in desc_lower:
            operation = data["formula"]
            confidence = data["confidence"]
            break

    # Extract field name
    words = description.split()
    field_name = None

    # Look for field after prepositions
    for i, word in enumerate(words):
        if word.lower() in ["of", "by", "for"]:
            if i + 1 < len(words):
                remaining = words[i + 1 :]
                field_words = [
                    w for w in remaining if w.lower() not in ["by", "per", "for", "the", "a", "an", "in", "on"]
                ]
                if field_words:
                    field_name = field_words[0].strip(".,!?")
                    break

    # Fallback: use last meaningful word
    if not field_name:
        for word in reversed(words):
            clean_word = word.lower().strip(".,!?")
            if clean_word not in [
                "sum",
                "average",
                "avg",
                "count",
                "total",
                "max",
                "min",
                "of",
                "by",
                "the",
                "a",
                "an",
                "calculate",
                "compute",
            ]:
                field_name = word.strip(".,!?")
                break

    # Generate formula
    if field_name:
        # Capitalize first letter for Tableau style
        field_name = field_name.capitalize()
        formula = f"{operation}([{field_name}])"
    else:
        formula = f"{operation}([Field])"

    return formula, confidence


# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================


@app.route("/", methods=["GET"])
def index():
    """Root endpoint - API information and documentation"""
    return (
        jsonify(
            {
                "name": "Unified Formula API",
                "version": "2.1.0",
                "description": "HypatiaX Tableau NER + Mathematical Formula Extraction + DeFi Analytics",
                "author": "HypatiaX Team",
                "services": {
                    "hypatiax": {
                        "loaded": HYPATIAX_LOADED,
                        "description": "Tableau formula mapping from natural language",
                    },
                    "ner_service": {
                        "loaded": NER_SERVICE_LOADED,
                        "description": "Mathematical formula extraction and parsing",
                    },
                    "defi": {"loaded": DEFI_LOADED, "description": "DeFi analytics and IL calculations"},
                },
                "endpoints": {
                    "health": {"url": "/api/health", "method": "GET", "description": "Service health check"},
                    "hypatiax": {
                        "map": {
                            "url": "/api/hypatiax/map",
                            "method": "POST",
                            "description": "Map natural language to Tableau formula",
                            "example": {"description": "Calculate the total of Sales", "method": "vocab"},
                        },
                        "test": {
                            "url": "/api/hypatiax/test",
                            "method": "GET",
                            "description": "Test HypatiaX with sample queries",
                        },
                    },
                    "ner": {
                        "health": "/api/ner/health",
                        "extract_formula": "/api/ner/extract-formula",
                        "recognize_entities": "/api/ner/recognize-entities",
                        "parse_expression": "/api/ner/parse-expression",
                        "convert_latex": "/api/ner/convert-to-latex",
                        "batch_extract": "/api/ner/batch-extract",
                        "identify_domain": "/api/ner/identify-domain",
                        "validate_syntax": "/api/ner/validate-syntax",
                    },
                    "defi": {
                        "health": "/api/defi/health",
                        "calculate_il": "/api/defi/calculate-il",
                        "quality_score": "/api/defi/calculate-quality-score",
                        "analyze_position": "/api/defi/analyze-position",
                    },
                },
                "status": "online",
                "timestamp": time.time(),
            }
        ),
        200,
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint with detailed service status"""
    return (
        jsonify(
            {
                "status": "online",
                "version": "2.1.0",
                "timestamp": time.time(),
                "services": {
                    "hypatiax": {
                        "loaded": HYPATIAX_LOADED,
                        "status": "operational" if HYPATIAX_LOADED else "demo_mode",
                    },
                    "ner_service": {
                        "loaded": NER_SERVICE_LOADED,
                        "status": "operational" if NER_SERVICE_LOADED else "unavailable",
                    },
                    "defi": {"loaded": DEFI_LOADED, "status": "operational" if DEFI_LOADED else "unavailable"},
                },
                "mode": "production" if (HYPATIAX_LOADED or NER_SERVICE_LOADED or DEFI_LOADED) else "demo",
                "uptime": "operational",
            }
        ),
        200,
    )


# ============================================================================
# HYPATIAX ENDPOINTS (Tableau Formula Mapping)
# ============================================================================


@app.route("/api/hypatiax/map", methods=["POST"])
def hypatiax_map():
    """
    HypatiaX: Map natural language description to Tableau formula

    Request Body:
    {
        "description": "Calculate the total of Sales",
        "method": "vocab"  // optional: vocab, neural, hybrid
    }

    Response:
    {
        "success": true,
        "entities": [...],
        "formula": "SUM([Sales])",
        "confidence": 0.95,
        "method": "vocab",
        "processing_time_ms": 45.2,
        "mode": "production"
    }
    """
    start_time = time.time()

    try:
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        description = data.get("description", "").strip()
        method = data.get("method", "vocab")

        if not description:
            return jsonify({"success": False, "error": "Description field is required"}), 400

        logger.info(f"📊 HypatiaX Processing: '{description}' using method '{method}'")

        # Process with HypatiaX models or fallback to mock
        if HYPATIAX_LOADED:
            try:
                # Extract entities using NER model
                doc = nlp_desc(description)
                entities = [
                    {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
                    for ent in doc.ents
                ]

                # Generate formula using mapping function
                mapper = map_description_to_formula(description)
                formula = mapper()

                # Calculate confidence based on entity extraction
                confidence = min(0.95, len(entities) / max(len(description.split()), 1))

                mode = "production"

            except Exception as e:
                logger.warning(f"Model processing error: {e}, falling back to mock")
                entities = mock_ner_extraction(description)
                formula, confidence = mock_formula_generation(description, method)
                mode = "fallback"
        else:
            # Use mock mode
            entities = mock_ner_extraction(description)
            formula, confidence = mock_formula_generation(description, method)
            mode = "demo"

        processing_time = (time.time() - start_time) * 1000

        response = {
            "success": True,
            "description": description,
            "entities": entities,
            "formula": formula,
            "confidence": round(confidence, 2),
            "method": method,
            "processing_time_ms": round(processing_time, 2),
            "mode": mode,
        }

        logger.info(f"✅ Generated formula: {formula} (confidence: {confidence:.2f})")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"❌ Error in hypatiax_map: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/hypatiax/test", methods=["GET"])
def hypatiax_test():
    """
    HypatiaX: Test endpoint with predefined queries

    Response:
    {
        "test_results": [
            {
                "description": "Calculate the total of Sales",
                "formula": "SUM([Sales])",
                "entities": [...]
            }
        ],
        "hypatiax_loaded": true,
        "total_tests": 5,
        "successful": 5
    }
    """
    test_cases = [
        "Calculate the total of Sales",
        "Average of Profit",
        "Count of Orders",
        "Maximum value of Price",
        "Minimum value of Discount",
    ]

    results = []
    successful = 0

    for desc in test_cases:
        try:
            if HYPATIAX_LOADED:
                # Try production model
                try:
                    doc = nlp_desc(desc)
                    entities = [{"text": e.text, "label": e.label_} for e in doc.ents]
                    mapper = map_description_to_formula(desc)
                    formula = mapper()
                except Exception:
                    entities = mock_ner_extraction(desc)
                    formula, _ = mock_formula_generation(desc, "vocab")
            else:
                # Use mock mode
                entities = mock_ner_extraction(desc)
                formula, _ = mock_formula_generation(desc, "vocab")

            results.append({"description": desc, "formula": formula, "entities": entities, "success": True})
            successful += 1

        except Exception as e:
            results.append({"description": desc, "error": str(e), "success": False})

    return (
        jsonify(
            {
                "test_results": results,
                "hypatiax_loaded": HYPATIAX_LOADED,
                "total_tests": len(test_cases),
                "successful": successful,
                "mode": "production" if HYPATIAX_LOADED else "demo",
            }
        ),
        200,
    )


@app.route("/api/hypatiax/batch", methods=["POST"])
def hypatiax_batch():
    """
    HypatiaX: Batch process multiple descriptions

    Request Body:
    {
        "descriptions": [
            "Sum of Sales",
            "Average of Profit",
            "Count of Orders"
        ],
        "method": "vocab"
    }
    """
    try:
        data = request.get_json()
        if not data or "descriptions" not in data:
            return jsonify({"success": False, "error": "descriptions field is required"}), 400

        descriptions = data.get("descriptions", [])
        method = data.get("method", "vocab")

        if not isinstance(descriptions, list):
            return jsonify({"success": False, "error": "descriptions must be an array"}), 400

        results = []
        for desc in descriptions:
            try:
                if HYPATIAX_LOADED:
                    doc = nlp_desc(desc)
                    entities = [{"text": e.text, "label": e.label_} for e in doc.ents]
                    try:
                        mapper = map_description_to_formula(desc)
                        formula = mapper()
                    except:
                        formula, _ = mock_formula_generation(desc, method)
                else:
                    entities = mock_ner_extraction(desc)
                    formula, _ = mock_formula_generation(desc, method)

                results.append({"description": desc, "formula": formula, "entities": entities, "success": True})
            except Exception as e:
                results.append({"description": desc, "error": str(e), "success": False})

        return (
            jsonify(
                {
                    "success": True,
                    "results": results,
                    "total": len(descriptions),
                    "successful": sum(1 for r in results if r.get("success", False)),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return (
        jsonify(
            {
                "error": "Endpoint not found",
                "status": 404,
                "message": "The requested endpoint does not exist",
                "available_endpoints": "/",
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error", "status": 500, "message": "An unexpected error occurred"}), 500


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return (
        jsonify(
            {"error": "Bad request", "status": 400, "message": "Invalid request format or missing required fields"}
        ),
        400,
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 UNIFIED FORMULA API SERVER")
    print("=" * 80)
    print(f"📊 HypatiaX (Tableau):    {'✅ Loaded' if HYPATIAX_LOADED else '⚠️  Demo Mode'}")
    print(f"🔢 NER Service:           {'✅ Loaded' if NER_SERVICE_LOADED else '❌ Not Available'}")
    print(f"💰 DeFi Calculator:       {'✅ Loaded' if DEFI_LOADED else '❌ Not Available'}")
    print(f"\n🌐 Server: http://localhost:5000")
    print(f"📡 API Documentation: http://localhost:5000/")
    print(f"❤️  Health Check: http://localhost:5000/api/health")
    print(f"\n📋 Endpoint Categories:")
    print(f"   /api/hypatiax/*  - Tableau formula mapping (NLP → Tableau)")
    print(f"   /api/ner/*       - Mathematical formula extraction & parsing")
    print(f"   /api/defi/*      - DeFi calculations & analytics")
    print(f"\n💡 Tips:")
    print(f"   - HypatiaX endpoints work in {'production' if HYPATIAX_LOADED else 'demo'} mode")
    print(f"   - Use POST /api/hypatiax/map for single queries")
    print(f"   - Use POST /api/hypatiax/batch for multiple queries")
    print(f"   - Visit / for full API documentation")
    print(f"\n👨‍💻 Press Ctrl+C to stop")
    print("=" * 80 + "\n")

    # Run the app
    app.run(debug=True, port=5000, host="0.0.0.0", use_reloader=True)
