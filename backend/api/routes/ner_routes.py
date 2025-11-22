"""
NER (Named Entity Recognition) Routes for Formula Extraction
File: backend/api/routes/ner_routes.py
"""

from flask import Blueprint, request, jsonify
from api.schemas.ner_schemas import (
    FormulaExtractionSchema,
    EntityRecognitionSchema,
    BatchNERSchema
)
from services.ner_service import NERService
from marshmallow import ValidationError

# Create blueprint
ner_bp = Blueprint('ner', __name__, url_prefix='/api/ner')

# Initialize service
ner_service = NERService()

# Initialize schemas
formula_schema = FormulaExtractionSchema()
entity_schema = EntityRecognitionSchema()
batch_schema = BatchNERSchema()


@ner_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for NER service"""
    return jsonify({
        'status': 'healthy',
        'service': 'ner-formula-extraction',
        'version': '1.0.0'
    }), 200


@ner_bp.route('/extract-formula', methods=['POST'])
def extract_formula():
    """
    Extract mathematical formulas from text
    
    Request:
    {
        "text": "The impermanent loss formula is IL = 2*sqrt(price_ratio)/(price_ratio+1) - 1",
        "domain": "defi",
        "extract_variables": true
    }
    
    Response:
    {
        "formulas": ["IL = 2*sqrt(price_ratio)/(price_ratio+1) - 1"],
        "variables": ["IL", "price_ratio"],
        "latex": "IL = \\frac{2\\sqrt{r}}{r+1} - 1",
        "domain": "defi"
    }
    """
    try:
        # Validate input
        data = formula_schema.load(request.json)
        
        # Extract formulas
        result = ner_service.extract_formulas(
            text=data['text'],
            domain=data.get('domain', 'general'),
            extract_variables=data.get('extract_variables', True)
        )
        
        return jsonify(result), 200
    
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ner_bp.route('/recognize-entities', methods=['POST'])
def recognize_entities():
    """
    Recognize mathematical entities (variables, constants, operators) in text
    
    Request:
    {
        "text": "Calculate daily fees using volume V and fee rate f",
        "entity_types": ["variable", "constant", "operator"]
    }
    
    Response:
    {
        "entities": [
            {"text": "V", "type": "variable", "position": [28, 29]},
            {"text": "f", "type": "variable", "position": [43, 44]}
        ]
    }
    """
    try:
        # Validate input
        data = entity_schema.load(request.json)
        
        # Recognize entities
        result = ner_service.recognize_entities(
            text=data['text'],
            entity_types=data.get('entity_types', ['variable', 'constant', 'operator'])
        )
        
        return jsonify(result), 200
    
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ner_bp.route('/parse-expression', methods=['POST'])
def parse_expression():
    """
    Parse mathematical expression into structured format
    
    Request:
    {
        "expression": "2 * sqrt(price_ratio) / (price_ratio + 1) - 1",
        "output_format": "tree"
    }
    
    Response:
    {
        "parsed": {...},
        "variables": ["price_ratio"],
        "operators": ["*", "/", "+", "-"],
        "functions": ["sqrt"]
    }
    """
    try:
        data = request.json
        
        if not data or 'expression' not in data:
            return jsonify({'error': 'Missing expression field'}), 400
        
        result = ner_service.parse_expression(
            expression=data['expression'],
            output_format=data.get('output_format', 'tree')
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ner_bp.route('/convert-to-latex', methods=['POST'])
def convert_to_latex():
    """
    Convert mathematical expression to LaTeX format
    
    Request:
    {
        "expression": "IL = 2*sqrt(r)/(r+1) - 1",
        "style": "inline"
    }
    
    Response:
    {
        "latex": "IL = \\frac{2\\sqrt{r}}{r+1} - 1",
        "style": "inline"
    }
    """
    try:
        data = request.json
        
        if not data or 'expression' not in data:
            return jsonify({'error': 'Missing expression field'}), 400
        
        result = ner_service.convert_to_latex(
            expression=data['expression'],
            style=data.get('style', 'inline')
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ner_bp.route('/batch-extract', methods=['POST'])
def batch_extract():
    """
    Extract formulas from multiple texts in batch
    
    Request:
    {
        "texts": [
            "IL = 2*sqrt(r)/(r+1) - 1",
            "daily_fees = volume * fee_rate"
        ],
        "domain": "defi"
    }
    
    Response:
    {
        "results": [
            {"text_index": 0, "formulas": [...]},
            {"text_index": 1, "formulas": [...]}
        ]
    }
    """
    try:
        # Validate input
        data = batch_schema.load(request.json)
        
        # Process batch
        results = []
        for idx, text in enumerate(data['texts']):
            try:
                result = ner_service.extract_formulas(
                    text=text,
                    domain=data.get('domain', 'general'),
                    extract_variables=data.get('extract_variables', True)
                )
                result['text_index'] = idx
                result['success'] = True
                results.append(result)
            except Exception as e:
                results.append({
                    'text_index': idx,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'total': len(data['texts']),
            'successful': sum(1 for r in results if r.get('success', False))
        }), 200
    
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ner_bp.route('/identify-domain', methods=['POST'])
def identify_domain():
    """
    Identify mathematical domain from text/formula
    
    Request:
    {
        "text": "Calculate impermanent loss using price ratio"
    }
    
    Response:
    {
        "domain": "defi",
        "confidence": 0.95,
        "keywords": ["impermanent loss", "price ratio"]
    }
    """
    try:
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text field'}), 400
        
        result = ner_service.identify_domain(data['text'])
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ner_bp.route('/validate-syntax', methods=['POST'])
def validate_syntax():
    """
    Validate mathematical expression syntax
    
    Request:
    {
        "expression": "2 * sqrt(r) / (r + 1",
        "strict": true
    }
    
    Response:
    {
        "valid": false,
        "errors": ["Unmatched parentheses"],
        "suggestions": ["Add closing parenthesis"]
    }
    """
    try:
        data = request.json
        
        if not data or 'expression' not in data:
            return jsonify({'error': 'Missing expression field'}), 400
        
        result = ner_service.validate_syntax(
            expression=data['expression'],
            strict=data.get('strict', False)
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Error handlers for this blueprint
@ner_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'NER endpoint not found'}), 404


@ner_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal NER service error'}), 500
