"""
Unified Backend API - HypatiaX + DeFi + NER
File: backend/app.py
"""

import os
import sys
import time
import logging
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add paths
sys.path.append('../hypatiax')

# ============================================================================
# INITIALIZE FLASK APP
# ============================================================================

app = Flask(__name__)
CORS(app)

# ============================================================================
# LOAD HYPATIAX MODELS (Tableau NER)
# ============================================================================

HYPATIAX_LOADED = False
nlp_desc = None
nlp_formula = None
map_description_to_formula = None

try:
    from hypatiax.custom_ner.queries.tableau import (
        custom_tableau_desc_components, 
        custom_tableau_formulas_components, 
        custom_tableau_components
    )
    from hypatiax.mappings.mapping import map_description_to_formula
    import spacy
         
    nlp_desc = spacy.load('../hypatiax/data_spacy/queries/tableau/ner_tableau_desc')
    nlp_formula = spacy.load('../hypatiax/data_spacy/queries/tableau/ner_tableau_formulas')
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
    from defi.il_calculator import calculate_il_with_fees
    DEFI_LOADED = True
    logger.info("✅ DeFi calculator loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ DeFi calculator not available: {e}")
    DEFI_LOADED = False

# ============================================================================
# REGISTER BLUEPRINTS (if available)
# ============================================================================

try:
    from api.routes.ner_routes import ner_bp
    app.register_blueprint(ner_bp)
    logger.info("✅ NER routes registered")
except Exception as e:
    logger.warning(f"⚠️ NER routes not available: {e}")

# ============================================================================
# HELPER FUNCTIONS FOR HYPATIAX MOCK MODE
# ============================================================================

DEMO_MAPPINGS = {
    'sum': {'formula': 'SUM', 'confidence': 0.95},
    'average': {'formula': 'AVG', 'confidence': 0.92},
    'avg': {'formula': 'AVG', 'confidence': 0.92},
    'count': {'formula': 'COUNT', 'confidence': 0.90},
    'total': {'formula': 'SUM', 'confidence': 0.88},
    'max': {'formula': 'MAX', 'confidence': 0.93},
    'min': {'formula': 'MIN', 'confidence': 0.93},
    'mean': {'formula': 'AVG', 'confidence': 0.91}
}

def mock_ner_extraction(text):
    """Mock NER extraction for demo mode"""
    entities = []
    words = text.lower().split()
    
    operations = ['sum', 'average', 'avg', 'count', 'total', 'max', 'min', 'mean']
    prepositions = ['of', 'by', 'per', 'for', 'across']
    determiners = ['the', 'a', 'an', 'all']
    
    start_pos = 0
    for word in text.split():
        word_lower = word.lower()
        label = None
        
        if word_lower in operations:
            label = 'OPER'
        elif word_lower in prepositions:
            label = 'ADP'
        elif word_lower in determiners:
            label = 'DET'
        elif word_lower.isdigit():
            label = 'NUM'
        else:
            label = 'NOUN'
        
        if label:
            entities.append({
                'text': word,
                'label': label,
                'start': start_pos,
                'end': start_pos + len(word)
            })
        
        start_pos += len(word) + 1
    
    return entities

def mock_formula_generation(description, method):
    """Mock formula generation for demo mode"""
    desc_lower = description.lower()
    
    operation = 'SUM'
    confidence = 0.85
    
    for op, data in DEMO_MAPPINGS.items():
        if op in desc_lower:
            operation = data['formula']
            confidence = data['confidence']
            break
    
    words = description.split()
    field_name = None
    
    for i, word in enumerate(words):
        if word.lower() in ['of', 'by']:
            if i + 1 < len(words):
                remaining = words[i+1:]
                field_words = [w for w in remaining if w.lower() not in ['by', 'per', 'for', 'the', 'a', 'an']]
                if field_words:
                    field_name = field_words[0]
                    break
    
    if not field_name:
        for word in reversed(words):
            if word.lower() not in ['sum', 'average', 'avg', 'count', 'total', 'of', 'by', 'the', 'a', 'an']:
                field_name = word
                break
    
    if field_name:
        formula = f"{operation}([{field_name}])"
    else:
        formula = f"{operation}([Field])"
    
    return formula, confidence

# ============================================================================
# DEFI CALCULATION FUNCTIONS
# ============================================================================

def calculate_il_percentage(current_price: float, initial_price: float) -> float:
    """Calculate impermanent loss percentage"""
    if initial_price == 0:
        return 0.0
    ratio = current_price / initial_price
    il = (2 * (ratio ** 0.5) / (ratio + 1) - 1) * 100
    return round(il, 4)

def calculate_quality_score(
    daily_volume_usd: float,
    fee_rate: float,
    position_value: float,
    pool_tvl: float,
    il_dollar: float,
    days_elapsed: int
) -> dict:
    """Calculate pool quality score"""
    pool_share = position_value / pool_tvl if pool_tvl > 0 else 0
    daily_fees = daily_volume_usd * fee_rate * pool_share
    daily_il_rate = abs(il_dollar) / days_elapsed if days_elapsed > 0 else 0
    
    if daily_il_rate > 0:
        quality_score = daily_fees / daily_il_rate
    else:
        quality_score = float('inf')
    
    if quality_score > 1.0:
        tier = "GOOD"
        emoji = "✅"
    elif quality_score >= 0.5:
        tier = "MODERATE"
        emoji = "⚠️"
    else:
        tier = "POOR"
        emoji = "❌"
    
    return {
        'daily_fees': round(daily_fees, 2),
        'daily_il_rate': round(daily_il_rate, 2),
        'quality_score': round(quality_score, 3) if quality_score != float('inf') else 'infinite',
        'quality_tier': tier,
        'quality_emoji': emoji,
        'pool_share_percent': round(pool_share * 100, 4)
    }

def calculate_position_analytics(
    initial_token_a: float,
    initial_token_b: float,
    initial_price: float,
    current_price: float,
    days_elapsed: int,
    daily_volume_usd: float,
    pool_tvl_usd: float,
    fee_rate: float = 0.003
) -> dict:
    """Complete LP position analysis"""
    price_ratio = current_price / initial_price
    il_percent = calculate_il_percentage(current_price, initial_price)
    position_value = initial_token_a * current_price + initial_token_b
    il_dollar = position_value * (il_percent / 100)
    
    quality_metrics = calculate_quality_score(
        daily_volume_usd, fee_rate, position_value, 
        pool_tvl_usd, il_dollar, days_elapsed
    )
    
    total_fees = quality_metrics['daily_fees'] * days_elapsed
    net_result = total_fees - abs(il_dollar)
    
    if quality_metrics['daily_fees'] > 0 and il_dollar < 0:
        breakeven_days = abs(il_dollar) / quality_metrics['daily_fees']
    else:
        breakeven_days = float('inf')
    
    return {
        'price_ratio': round(price_ratio, 4),
        'il_percent': il_percent,
        'il_dollar': round(il_dollar, 2),
        'position_value': round(position_value, 2),
        'daily_fees': quality_metrics['daily_fees'],
        'total_fees': round(total_fees, 2),
        'net_result': round(net_result, 2),
        'breakeven_days': round(breakeven_days, 2) if breakeven_days != float('inf') else 'infinite',
        'profitable': net_result > 0,
        'quality_score': quality_metrics['quality_score'],
        'quality_tier': quality_metrics['quality_tier'],
        'quality_emoji': quality_metrics['quality_emoji'],
        'daily_il_rate': quality_metrics['daily_il_rate'],
        'pool_share_percent': quality_metrics['pool_share_percent'],
        'days_elapsed': days_elapsed
    }

# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API information"""
    return jsonify({
        'name': 'Unified Formula API',
        'version': '2.0.0',
        'description': 'HypatiaX + DeFi + NER Formula Processing',
        'services': {
            'hypatiax': HYPATIAX_LOADED,
            'ner_service': NER_SERVICE_LOADED,
            'defi': DEFI_LOADED
        },
        'endpoints': {
            'health': '/api/health',
            'hypatiax': {
                'map': '/api/hypatiax/map (POST)',
                'test': '/api/hypatiax/test (GET)'
            },
            'ner': {
                'extract': '/api/ner/extract-formula (POST)',
                'entities': '/api/ner/recognize-entities (POST)',
                'latex': '/api/ner/convert-to-latex (POST)'
            },
            'defi': {
                'il_percentage': '/api/defi/il-percentage (POST)',
                'quality_score': '/api/defi/quality-score (POST)',
                'analyze': '/api/defi/analyze-position (POST)'
            }
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'version': '2.0.0',
        'services': {
            'hypatiax_loaded': HYPATIAX_LOADED,
            'ner_service_loaded': NER_SERVICE_LOADED,
            'defi_loaded': DEFI_LOADED
        },
        'mode': 'production' if (HYPATIAX_LOADED or NER_SERVICE_LOADED or DEFI_LOADED) else 'demo'
    }), 200

# ============================================================================
# HYPATIAX ENDPOINTS (Tableau Formula Mapping)
# ============================================================================

@app.route('/api/hypatiax/map', methods=['POST'])
def hypatiax_map():
    """HypatiaX: Map natural language to Tableau formula"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        description = data.get('description', '').strip()
        method = data.get('method', 'vocab')
        
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        
        logger.info(f"HypatiaX Processing: '{description}'")
        
        if HYPATIAX_LOADED:
            try:
                doc = nlp_desc(description)
                entities = [
                    {
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    }
                    for ent in doc.ents
                ]
                
                mapper = map_description_to_formula(description)
                formula = mapper()
                confidence = min(0.95, len(entities) / max(len(description.split()), 1))
                
            except Exception as e:
                logger.error(f"Model error: {e}")
                entities = mock_ner_extraction(description)
                formula, confidence = mock_formula_generation(description, method)
        else:
            entities = mock_ner_extraction(description)
            formula, confidence = mock_formula_generation(description, method)
        
        processing_time = (time.time() - start_time) * 1000
        
        return jsonify({
            'success': True,
            'entities': entities,
            'formula': formula,
            'confidence': round(confidence, 2),
            'method': method,
            'processing_time_ms': round(processing_time, 2),
            'mode': 'production' if HYPATIAX_LOADED else 'demo'
        }), 200
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/hypatiax/test', methods=['GET'])
def hypatiax_test():
    """HypatiaX: Test endpoint"""
    test_cases = [
        "Calculate the total of Petal Lengths",
        "Minimum value of Sepal Length",
        "Average of Sales"
    ]
    
    results = []
    for desc in test_cases:
        try:
            if HYPATIAX_LOADED:
                doc = nlp_desc(desc)
                entities = [{'text': e.text, 'label': e.label_} for e in doc.ents]
                try:
                    mapper = map_description_to_formula(desc)
                    formula = mapper()
                except:
                    formula, _ = mock_formula_generation(desc, 'vocab')
            else:
                entities = mock_ner_extraction(desc)
                formula, _ = mock_formula_generation(desc, 'vocab')
            
            results.append({
                'description': desc,
                'formula': formula,
                'entities': entities
            })
        except Exception as e:
            results.append({'description': desc, 'error': str(e)})
    
    return jsonify({
        'test_results': results,
        'hypatiax_loaded': HYPATIAX_LOADED
    }), 200

# ============================================================================
# DEFI ENDPOINTS
# ============================================================================

@app.route('/api/defi/il-percentage', methods=['POST'])
def defi_il_percentage():
    """Calculate IL percentage only"""
    try:
        data = request.json
        required = ['initial_price', 'current_price']
        if not all(f in data for f in required):
            return jsonify({'error': f'Missing fields: {required}'}), 400
        
        result = calculate_il_percentage(
            float(data['current_price']),
            float(data['initial_price'])
        )
        
        return jsonify({
            'il_percent': result,
            'initial_price': float(data['initial_price']),
            'current_price': float(data['current_price'])
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/defi/quality-score', methods=['POST'])
def defi_quality_score():
    """Calculate pool quality score"""
    try:
        data = request.json
        required = ['daily_volume_usd', 'position_value', 'pool_tvl', 'il_dollar', 'days_elapsed']
        if not all(f in data for f in required):
            return jsonify({'error': f'Missing fields: {required}'}), 400
        
        result = calculate_quality_score(
            float(data['daily_volume_usd']),
            float(data.get('fee_rate', 0.003)),
            float(data['position_value']),
            float(data['pool_tvl']),
            float(data['il_dollar']),
            int(data['days_elapsed'])
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/defi/analyze-position', methods=['POST'])
def defi_analyze_position():
    """Complete LP position analysis"""
    try:
        data = request.json
        required = [
            'initial_token_a', 'initial_token_b', 'initial_price',
            'current_price', 'days_elapsed', 'daily_volume_usd', 'pool_tvl_usd'
        ]
        if not all(f in data for f in required):
            return jsonify({'error': f'Missing fields: {required}'}), 400
        
        result = calculate_position_analytics(
            float(data['initial_token_a']),
            float(data['initial_token_b']),
            float(data['initial_price']),
            float(data['current_price']),
            int(data['days_elapsed']),
            float(data['daily_volume_usd']),
            float(data['pool_tvl_usd']),
            float(data.get('fee_rate', 0.003))
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/defi/calculate-il', methods=['POST'])
def defi_calculate_il_legacy():
    """Legacy IL calculation endpoint"""
    try:
        if not DEFI_LOADED:
            return jsonify({'error': 'DeFi calculator not loaded'}), 503
        
        data = request.json
        result = calculate_il_with_fees(**data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 UNIFIED FORMULA API SERVER")
    print("="*80)
    print(f"📊 HypatiaX (Tableau):    {'✅ Loaded' if HYPATIAX_LOADED else '❌ Not Available'}")
    print(f"🔍 NER Service:           {'✅ Loaded' if NER_SERVICE_LOADED else '❌ Not Available'}")
    print(f"💰 DeFi Calculator:       {'✅ Loaded' if DEFI_LOADED else '❌ Not Available'}")
    print(f"\n🌐 Server: http://localhost:5000")
    print(f"📡 API Documentation: http://localhost:5000/")
    print(f"❤️  Health Check: http://localhost:5000/api/health")
    print("\n📋 Endpoint Categories:")
    print("   /api/hypatiax/*  - Tableau formula mapping")
    print("   /api/ner/*       - Mathematical formula extraction")
    print("   /api/defi/*      - DeFi calculations")
    print("\n💡 Press Ctrl+C to stop")
    print("="*80 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
