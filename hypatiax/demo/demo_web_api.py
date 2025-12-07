Web-based visual demo

Beautiful web interface
Real-time entity extraction
Example buttons
Visual entity display with confidence scores


"""
HypatiaX Web API - Flask REST API Server
Provides HTTP endpoints for the HypatiaX engine
"""

import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

# Add parent directory to path to import HypatiaX modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from demo.engine import HypatiaXEngine
from demo.examples import Example, ExampleManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)  # Enable CORS for all routes

# Initialize HypatiaX components
try:
    engine = HypatiaXEngine(
        desc_model_path='../data_spacy/queries/tableau/ner_tableau_desc',
        formula_model_path='../data_spacy/queries/tableau/ner_tableau_formulas'
    )
    models_loaded = engine.load_models()
    logger.info(f"Models loaded: {models_loaded}")
except Exception as e:
    logger.warning(f"Failed to load models: {e}. Using rule-based processing.")
    engine = HypatiaXEngine()
    models_loaded = False

# Initialize example manager
example_manager = ExampleManager()

# Server stats
server_stats = {
    'start_time': datetime.now(),
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0
}


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve main demo page"""
    return render_template('demo.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns server status and configuration
    """
    uptime = (datetime.now() - server_stats['start_time']).total_seconds()

    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'uptime_seconds': uptime,
        'models_loaded': models_loaded,
        'mode': 'production' if models_loaded else 'demo',
        'stats': {
            'total_requests': server_stats['total_requests'],
            'successful': server_stats['successful_requests'],
            'failed': server_stats['failed_requests']
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/map', methods=['POST'])
def map_description():
    """
    Map natural language description to Tableau formula

    Request JSON:
    {
        "description": "sum of sales by region",
        "method": "vocab"  // optional: vocab, sentence, regex, ner
    }

    Response JSON:
    {
        "success": true,
        "formula": "SUM([Sales])",
        "entities": [...],
        "confidence": 0.95,
        "processing_time": 12.5,
        "method": "vocab"
    }
    """
    server_stats['total_requests'] += 1

    try:
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        description = data.get('description', '').strip()
        if not description:
            return jsonify({
                'success': False,
                'error': 'Description field is required'
            }), 400

        method = data.get('method', 'vocab')
        use_model = data.get('use_model', models_loaded)

        # Process description
        logger.info(f"Processing: '{description}' with method: {method}")
        result = engine.process(
            query=description,
            method=method,
            use_model=use_model
        )

        # Format response
        response = {
            'success': True,
            'formula': result.formula,
            'entities': [
                {
                    'text': e.text,
                    'label': e.label,
                    'start': e.start,
                    'end': e.end,
                    'confidence': e.confidence
                }
                for e in result.entities
            ],
            'confidence': result.confidence,
            'processing_time': result.processing_time,
            'method': result.method,
            'entity_count': len(result.entities),
            'metadata': result.metadata
        }

        server_stats['successful_requests'] += 1
        logger.info(f"Success: {result.formula} (confidence: {result.confidence:.2%})")

        return jsonify(response)

    except Exception as e:
        server_stats['failed_requests'] += 1
        logger.error(f"Error processing request: {e}")
        logger.error(traceback.format_exc())

        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc() if app.debug else None
        }), 500


@app.route('/api/batch', methods=['POST'])
def batch_map():
    """
    Batch process multiple descriptions

    Request JSON:
    {
        "descriptions": ["sum of sales", "average profit"],
        "method": "vocab"  // optional
    }

    Response JSON:
    {
        "success": true,
        "results": [...],
        "total_count": 2,
        "success_count": 2,
        "failed_count": 0
    }
    """
    server_stats['total_requests'] += 1

    try:
        data = request.get_json()
        descriptions = data.get('descriptions', [])
        method = data.get('method', 'vocab')

        if not descriptions:
            return jsonify({
                'success': False,
                'error': 'Descriptions array is required'
            }), 400

        # Process all descriptions
        results = engine.batch_process(descriptions, method=method)

        # Format response
        response = {
            'success': True,
            'results': [
                {
                    'description': r.query,
                    'formula': r.formula,
                    'confidence': r.confidence,
                    'entity_count': len(r.entities),
                    'processing_time': r.processing_time
                }
                for r in results
            ],
            'total_count': len(results),
            'success_count': sum(1 for r in results if r.formula != 'ERROR'),
            'failed_count': sum(1 for r in results if r.formula == 'ERROR')
        }

        server_stats['successful_requests'] += 1
        return jsonify(response)

    except Exception as e:
        server_stats['failed_requests'] += 1
        logger.error(f"Batch processing error: {e}")

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """
    Get example queries

    Query params:
    - category: Filter by category (basic, intermediate, advanced)
    - count: Number of examples to return (default: all)
    - random: If true, return random examples
    """
    try:
        category = request.args.get('category')
        count = request.args.get('count', type=int)
        random_flag = request.args.get('random', 'false').lower() == 'true'

        # Get examples
        if random_flag and count:
            examples = example_manager.get_random_examples(
                count=count,
                category=category
            )
        elif category:
            examples = example_manager.filter_by_category(category)
            if count:
                examples = examples[:count]
        else:
            examples = list(example_manager.examples)
            if count:
                examples = examples[:count]

        # Format response
        return jsonify({
            'success': True,
            'examples': [
                {
                    'id': e.id,
                    'description': e.description,
                    'expected_formula': e.expected_formula,
                    'category': e.category,
                    'difficulty': e.difficulty,
                    'tags': e.tags
                }
                for e in examples
            ],
            'count': len(examples)
        })

    except Exception as e:
        logger.error(f"Error getting examples: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/examples/categories', methods=['GET'])
def get_categories():
    """Get all available example categories"""
    try:
        stats = example_manager.get_statistics()

        return jsonify({
            'success': True,
            'categories': list(stats.get('by_category', {}).keys()),
            'counts': stats.get('by_category', {})
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate_formula():
    """
    Validate a generated formula against expected result

    Request JSON:
    {
        "description": "sum of sales",
        "expected_formula": "SUM([Sales])",
        "method": "vocab"
    }

    Response JSON:
    {
        "success": true,
        "match": true,
        "generated_formula": "SUM([Sales])",
        "expected_formula": "SUM([Sales])",
        "confidence": 0.95
    }
    """
    try:
        data = request.get_json()
        description = data.get('description')
        expected = data.get('expected_formula')
        method = data.get('method', 'vocab')

        # Process description
        result = engine.process(description, method=method)

        # Compare
        match = result.formula == expected

        return jsonify({
            'success': True,
            'match': match,
            'generated_formula': result.formula,
            'expected_formula': expected,
            'confidence': result.confidence,
            'entity_count': len(result.entities)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get engine and server statistics"""
    try:
        engine_stats = engine.get_stats()

        return jsonify({
            'success': True,
            'server': server_stats,
            'engine': engine_stats,
            'examples': example_manager.get_statistics()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/methods', methods=['GET'])
def get_methods():
    """Get available mapping methods"""
    return jsonify({
        'success': True,
        'methods': [
            {
                'name': 'vocab',
                'description': 'Vocabulary-based mapping using predefined dictionaries',
                'speed': 'fast',
                'accuracy': 'high'
            },
            {
                'name': 'sentence',
                'description': 'Sentence pattern matching',
                'speed': 'fast',
                'accuracy': 'medium'
            },
            {
                'name': 'regex',
                'description': 'Regular expression based extraction',
                'speed': 'fast',
                'accuracy': 'medium'
            },
            {
                'name': 'ner',
                'description': 'Named Entity Recognition using ML models',
                'speed': 'medium',
                'accuracy': 'highest'
            }
        ]
    })


@app.route('/api/test', methods=['GET'])
def run_test_suite():
    """
    Run test suite on sample examples
    Returns accuracy metrics for each method
    """
    try:
        # Get test examples
        test_examples = example_manager.filter_by_category('basic')[:5]

        methods = ['vocab', 'sentence', 'regex', 'ner']
        results = {}

        for method in methods:
            correct = 0
            total = len(test_examples)

            for example in test_examples:
                result = engine.process(example.description, method=method)
                if result.formula == example.expected_formula:
                    correct += 1

            results[method] = {
                'accuracy': correct / total if total > 0 else 0,
                'correct': correct,
                'total': total
            }

        return jsonify({
            'success': True,
            'results': results,
            'test_count': len(test_examples)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': str(e)
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(e)
    }), 500


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='HypatiaX Web API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                   HypatiaX Web API Server                     ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  URL: http://{args.host}:{args.port}
    ║  Status: {"PRODUCTION" if models_loaded else "DEMO MODE"}
    ║  Models: {"Loaded" if models_loaded else "Using rule-based"}
    ╚═══════════════════════════════════════════════════════════════╝

    Available Endpoints:
    ────────────────────────────────────────────────────────────────
    GET  /                          - Demo web interface
    GET  /api/health                - Health check
    POST /api/map                   - Map description to formula
    POST /api/batch                 - Batch process descriptions
    GET  /api/examples              - Get example queries
    GET  /api/examples/categories   - Get example categories
    POST /api/validate              - Validate formula
    GET  /api/stats                 - Get statistics
    GET  /api/methods               - Get available methods
    GET  /api/test                  - Run test suite

    Press Ctrl+C to stop the server
    """)

    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
